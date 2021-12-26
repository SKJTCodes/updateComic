import shutil
from pathlib import Path

from tqdm import tqdm

from AccessSql import SQL
from Env import Env as env


class UpdateDB:
    def __init__(self, log, out_dir):
        self.log = log
        self.mysql = SQL(env.USER, env.PWD, env.HOST, env.DB)
        self.out_dir = Path(out_dir) if isinstance(out_dir, str) else out_dir

    def update_db(self, title_df, chpt_df, page_df, _type="image"):
        for i, entry in tqdm(title_df.iterrows(), total=title_df.shape[0], desc="Updating Database"):
            self._update_lib(entry)

            c_df = chpt_df.loc[chpt_df['item_id'] == entry['item_id']]
            list_of_c_ids = c_df['chpt_id'].tolist()
            self._update_chapt(c_df)

            if _type == "image":
                p_df = page_df.loc[page_df['chpt_id'].isin(list_of_c_ids)]
                self._update_pages(p_df)
                self._copy_files(c_df, p_df, entry['cover_path'])
            else:
                self.log.warning("Not implemented for Video Yet.")

    def _copy_files(self, c_df, p_df, cover_path):
        for chapter in c_df.itertuples():
            page_dir = self.out_dir / str(chapter.item_id) / str(chapter.chpt_id)
            page_dir.mkdir(parents=True, exist_ok=True)

            pages = p_df.loc[p_df['chpt_id'] == chapter.chpt_id].copy()
            for page in pages.itertuples():
                shutil.copy(page.src_path, page_dir / Path(page.page_path).name)

        shutil.copy(cover_path, self.out_dir / str(c_df.iloc[0]['item_id']) / f'cover{Path(cover_path).suffix}')

    def _update_pages(self, page_df):
        q_str = f"""
        INSERT INTO Pages(PageId, Path, ChptId, ImgType)
        VALUES
        """
        val_str = []
        for i, entry in page_df.iterrows():
            val_str.append(f"({entry['page_id']}, '{entry['page_path']}', {entry['chpt_id']}, '{entry['img_type']}')")

        val_str = ",".join(val_str)
        q_str = q_str + val_str
        self.mysql.query(q_str)
        self.mysql.set_update()

    def _update_chapt(self, chpt_df):
        q_str = f"""
        INSERT INTO Chapters(ChptId, ChapterNo, TotalPages, DateCreated, ItemId, ChapterTitle)
        VALUES
        """
        val_str = []
        for i, entry in chpt_df.iterrows():
            val_str.append(f"({entry['chpt_id']}, {entry['chpt_no']}, {entry['total_pages']}, "
                           f"'{entry['date_created']}', {entry['item_id']}, '{entry['chpt_title']}')")

        val_str = ",".join(val_str)
        q_str = q_str + val_str
        self.mysql.query(q_str)
        self.mysql.set_update()

    def _update_lib(self, entry):
        q_str = f"""
        INSERT INTO Library_Items(ItemId, Title, Maker, ItemType, DateCreated, CoverPath, TotalEntries)
        VALUES
        ({entry['item_id']}, '{entry['title']}', '{entry['maker']}', '{entry['item_type']}', '{entry['date_created']}', 
        'comic/{entry['item_id']}/cover{entry['cover_path'].suffix}', {entry['total_entries']})
        """ if not entry['item_exist'] else f"""
        UPDATE Library_Items
        SET DateCreated='{entry['date_created']}', TotalEntries={entry['total_entries']}
        WHERE ItemId={entry['item_id']}
        """
        self.mysql.query(q_str)
        self.mysql.set_update()
