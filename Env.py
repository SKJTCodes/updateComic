class Env:
    IMG_FILE_TYPES = ['.jpg', '.jpeg', '.jpe', '.jif', '.jfif', '.jfi',
                      '.png', '.gif', '.webp', '.tiff', '.tif', '.psd',
                      '.raw', '.arw', '.cr2', '.nrw', '.k25', '.bmp',
                      '.dib', '.heif', '.heic', '.ind', '.indd', '.indt',
                      '.jp2', '.j2k', '.jpf', '.jpx', '.jpm', '.mj2'
                      '.svg', '.svgz', '.ai', '.eps', '.pdf']

    """ mySQL Params """
    HOST = "raspberrypi.local"
    USER = "remote"
    PWD = "admin"
    DB = "web_test"

    """ Title DF Columns """
    TITLE_DF_COLS = ['item_id', 'item2_paths', 'title', 'maker', 'item_type', 'date_created',
                     'cover_path', 'total_entries']

    """ Page DF Columns """
    PAGE_DF_COLS = ['page_id', 'chpt_id', 'page_path', 'img_type']

    """ Chapter DF columns """
    CHAPT_DF_COLS = ['chpt_id', 'chpt_no', 'total_pages', 'date_created', 'item_id', 'chpt_title']


