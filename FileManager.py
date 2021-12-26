import re
from pathlib import Path

import pandas as pd
from PIL import Image
from tqdm import tqdm

import helper as h
from AccessSql import SQL
from Env import Env as env


class FileManager:
    def __init__(self, log, output):
        self.log = log
        self.output = output
        self.mysql = SQL(env.USER, env.PWD, env.HOST, env.DB)

    def get_file_info(self, in_path, _type):
        self.log.info(f"Currently Processing {_type}")

        input_path = Path(in_path) if isinstance(in_path, str) else in_path
        df = self._process_titles(input_path, _type)
        df = self._process_chapt_epi(df, _type)
        df = self._assign_item_id(df)
        if df.empty:
            return None, None, None
        if _type == "image":
            chpt_df, page_df, df = self._get_chapters_and_pages(df)
            return chpt_df, page_df, df

    def _process_titles(self, input_path, _type, sep="+="):
        self.log.info(f"Processing Titles ...")
        title_df = pd.DataFrame(columns=env.TITLE_DF_COLS)

        items = [x for x in input_path.iterdir() if x.is_dir() and x.name != "0. Author+Title"]
        for item in tqdm(items, total=len(items), desc="Get Titles From Folders"):
            if sep not in str(item.name):
                self.log.warning(f"Folder name don't have '{sep}' ({item.name})")
                continue
            elif item.name.count(sep) > 1:
                self.log.warning(f"Folder name have more than 1 '{sep}' ({item.name})")
                continue

            self.log.debug(f"Get Info from structure: ({item.name})")
            maker, title = item.name.split(sep)

            maker = maker.replace("'", "''").lower()
            title = title.replace("'", "''").lower()

            # if title exist, add itemId
            sql_obj = self.mysql.query(f"""
                SELECT ItemId, CoverPath, TotalEntries 
                FROM Library_Items WHERE Title='{title}' AND Maker='{maker}'
            """)
            assert len(sql_obj) <= 1, f"There are multiple entries with same title='{title}' and maker='{maker}'"

            # Chapter / Episode
            item2_paths = h.sort_num_string([str(x) for x in item.iterdir() if x.is_dir()])
            data = dict(item_id=None if len(sql_obj) == 0 else sql_obj[0][0], title=title, maker=maker,
                        cover_path=None if len(sql_obj) == 0 else sql_obj[0][1],
                        total_entries=0 if len(sql_obj) == 0 else sql_obj[0][2],
                        item_type="img" if _type == 'image' else "vid", item2_paths=item2_paths,
                        date_created=h.date_delta(out_fmt="%Y-%m-%d %H:%M:%S"),
                        item_exist=False if len(sql_obj) == 0 else True)
            title_df = title_df.append(data, ignore_index=True)

        return title_df

    def _process_chapt_epi(self, title_df, _type, sep="+="):
        self.log.info("Processing Chapters / Episodes ...")

        def get_pages(row):
            page_paths = {}
            for index, path in enumerate(row['item2_paths']):
                path, chapter = Path(path), index + 1

                chapt_title = ""
                try:
                    chapt_num = float(path.name)
                except ValueError:
                    if sep in path.name:
                        chapt_num, chapt_title = path.name.split(sep)
                        chapt_num = float(chapt_num)
                        chapt_title = chapt_title.replace("'", "''").lower()
                    else:
                        self.log.warning(f"Chapter Folder name does not contain either a "
                                         f"number only or a number{sep}Chapter_Title. ({row['title']})")
                        chapt_num = float(chapter)

                # Check if Chapter Exist
                exist = False
                if row['item_id'] is not None:
                    sql_obj = self.mysql.query(f"""
                        SELECT * FROM Chapters WHERE ChapterNo={chapt_num} AND ItemId={row['item_id']}
                    """)
                    assert len(sql_obj) <= 1, f"Multiple Chapter Rows, ChapterNo={chapt_num} " \
                                              f"and ItemId={row['item_id']}"
                    if len(sql_obj) == 1:
                        exist = True

                # Chapter Title, Page Paths
                if not exist:
                    page_paths.update({chapt_num: (chapt_title, path)})
            return page_paths

        if _type == "image":
            title_df['item2_paths'] = title_df[['item_id', 'item2_paths', 'title']].apply(get_pages, axis=1)
            title_df = title_df.loc[title_df['item2_paths'] != dict()]
        else:
            self.log.warning("Not implemented yet. Process EP folders/files")

        return title_df

    def _assign_item_id(self, df):
        max_id = self.mysql.query(f"SELECT MAX(ItemId) FROM Library_Items")[0][0]
        new_id = 1 if max_id is None else max_id + 1

        for row in df.itertuples():
            if row.item_id is not None:
                continue

            df.loc[row.Index, 'item_id'] = new_id
            new_id += 1

        return df

    def _get_chapters_and_pages(self, df):
        self.log.info(f"Processing Chapters & Pages ... ")

        page_df = pd.DataFrame(columns=env.PAGE_DF_COLS)
        chpt_df = pd.DataFrame(columns=env.CHAPT_DF_COLS)

        max_chpt_id = self.mysql.query("SELECT MAX(ChptId) FROM Chapters")[0][0]
        new_chpt_id = 1 if max_chpt_id is None else max_chpt_id + 1

        max_page_id = self.mysql.query("SELECT MAX(PageId) FROM Pages")[0][0]
        new_page_id = 1 if max_page_id is None else max_page_id + 1

        img_ext_pat = "|".join([fr".*\{x}" for x in env.IMG_FILE_TYPES])

        for row in tqdm(df.itertuples(), total=df.shape[0],
                        desc="Get Chapter Info", leave=True, position=0):
            item_id = row.item_id

            for item2, (chapt_title, path) in row.item2_paths.items():
                page_count = 0

                pages = h.sort_num_string([str(x) for x in path.iterdir()])
                for index, page_path in enumerate(pages):
                    page_path = Path(page_path)

                    if re.match(img_ext_pat, page_path.name) is None or page_path.is_dir():
                        continue

                    if index == 0:
                        df.loc[df['item_id'] == item_id, 'cover_path'] = page_path

                    with Image.open(page_path) as im:
                        width, height = im.size

                    data = {
                        "page_id": new_page_id,
                        'chpt_id': new_chpt_id,
                        'page_path': f"comic/{item_id}/{new_chpt_id}/{page_path.name}",
                        'img_type': "landscape" if width > height else "portrait",
                        'src_path': page_path
                    }

                    page_df = page_df.append(data, ignore_index=True)
                    new_page_id += 1
                    page_count += 1

                chpt_data = {
                    "chpt_id": new_chpt_id,
                    "chpt_no": item2,
                    'total_pages': page_count,
                    'date_created': h.date_delta(out_fmt="%Y-%m-%d %H:%M:%S"),
                    'item_id': item_id,
                    "chpt_title": chapt_title
                }

                chpt_df = chpt_df.append(chpt_data, ignore_index=True)
                new_chpt_id += 1

        df['total_entries'] = df.apply(lambda x: x['total_entries'] + chpt_df.loc[chpt_df['item_id'] ==
                                                                                  x['item_id']].shape[0], axis=1)

        return chpt_df, page_df, df
