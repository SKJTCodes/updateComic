import argparse
import os
from pathlib import Path

import helper as h
from FileManager import FileManager
from Logger import Logger
from UpdateDB import UpdateDB

"""
Image database structure:
    Input Path Folder
        - Author+Title
            - Chapter Number
                - 1.jpg
                - 2.jpg
                - 3.jpg
                - ...
        - Author2+Title2
            - Chapter Num
                - 1.jpg
                - 2.jpg 
"""

""" Initializing Script Parameters """
parser = argparse.ArgumentParser(description="Add Items to Library")
parser.add_argument('input', type=lambda x: Path(x).absolute(),
                    help="Location of Image Database")
parser.add_argument('output', type=lambda x: Path(x).absolute(),
                    help="Path to push out Files to be added to library")
parser.add_argument('--test', action="store_true",
                    help="Do not insert data to mySQL, print query instead")
parser.add_argument('--log_dir', type=lambda x: Path(x).absolute(),
                    default=os.path.realpath(os.path.dirname(__file__)))
args = parser.parse_args()

""" Initializing Logging Properties """
log_path = args.log_dir / "log" / f"debug-{h.date_delta(out_fmt='%Y%m%d-%H%M.%S')}.log"
log = Logger(log_path).get_logger()


def main():
    log.info(f"Log Path: {log_path}")

    fm = FileManager(log, args.output)
    chpt_df, page_df, df = fm.get_file_info(args.input, 'image')

    if chpt_df is not None:
        udb = UpdateDB(log, args.output)
        udb.update_db(df, chpt_df, page_df)
    else:
        log.info(f'Done Processing')


if __name__ == '__main__':
    main()
