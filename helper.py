import re
import datetime as dt
import operator
from datetime import timedelta
from pandas.tseries.offsets import BDay
import pandas as pd


def sort_num_string(data_list):
    """
    Sort Strings that have numerical values by the numeric values
    :param data_list: list of strings
    :return: sorted list
    """
    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        """
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        """
        return [atoi(c) for c in re.split(r'(\d+)', text)]

    data_list.sort(key=natural_keys)
    return data_list


def date_delta(date=None, delta=0, out_fmt="%Y%m%d", in_fmt=None, biz_day=False):
    """
    Get Date or Date difference
    :param date: datetime object or string, date you want to perform operator on, default get current date
    :param delta: int value, add or subtract
    :param out_fmt: string, date output format, e.g. "%Y%m%d", None if out is datetime
    :param in_fmt: string, format of date param, if is string
    :param biz_day: compute delta by using Business Days or not
    :return: output date in string format
    """

    if date is None:
        date = dt.datetime.today()
    elif type(date) is str:
        assert in_fmt is not None
        date = pd.to_datetime(date, in_fmt)

    op = {"add": operator.add, "sub": operator.sub}

    if delta == 0:
        n_date = date
    else:
        key = "add" if delta > 0 else "sub"
        n_date = op[key](date, BDay(abs(delta)) if biz_day else timedelta(days=abs(delta)))

    return n_date if out_fmt is None else n_date.strftime(out_fmt)



