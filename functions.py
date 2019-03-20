import logger
import sqlite3
from datetime import datetime

classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '6Г', '7А', '7Б', '7В', '7Г', '8А', '8Б', '8В', '8Г', '9А',
           '9Б', '9В', '9Г', '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']


class MyCursor(sqlite3.Cursor):
    def __init__(self, connection):
        super(MyCursor, self).__init__(connection)
        self.connected = 0

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type is not None:
            logger.log("lessons_db_manip", f"SQLite ERROR: traceback - {str(ex_traceback)}!")

        self.connected -= 1
        if not self.connected:
            self.connection.commit()
            self.close()
            self.connection.close()


def make_lined(s, symbol="̶"):
    ans = ""
    for x in s:
        ans += symbol
        ans += x
    return ans


def convert_arrays_to_dict(arr1, arr2):
    if len(arr1) != len(arr2):
        return False

    length = len(arr1)
    return {arr1[it]: arr2[it] for it in range(length)}


def cur_date():
    return datetime.today().strftime('%Y%m%d')




