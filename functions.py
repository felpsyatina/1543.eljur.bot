import logger
import sqlite3
from datetime import datetime, timedelta, date as st_date
import config
import eljur_api

classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '6Г', '7А', '7Б', '7В', '7Г', '8А', '8Б', '8В', '8Г', '9А',
           '9Б', '9В', '9Г', '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']

SUBS = [["Вернуться в меню"], ['5А', '5Б', '5В', '5Г'], ['6А', '6Б', '6В', '6Г'], ['7А', '7Б', '7В', '7Г'],
        ['8А', '8Б', '8В', '8Г'], ['9А', '9Б', '9В', '9Г'], ['10А', '10Б', '10В', '10Г'], ['11А', '11Б', '11В', '11Г']]

COLORS = ["default", "primary", "positive", "negative"]


preset = {"devkey": config.secret['eljurapi']['devkey'], "vendor": "1543",
          "password": config.secret['eljurapi']['password'],
          "login": config.secret['eljurapi']['login']}
student = eljur_api.Student(**preset)


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


def del_arr_elem(arr, obj):
    if obj not in arr:
        return False

    new_arr = []
    for e in arr:
        if e != obj:
            new_arr.append(e)

    return new_arr


def convert_arrays_to_dict(arr1, arr2):
    if len(arr1) != len(arr2):
        return False

    length = len(arr1)
    return {arr1[it]: arr2[it] for it in range(length)}


def del_op(s, sym='\''):
    ans = ""
    for let in s:
        if let == sym:
            ans += ' '
        else:
            ans += let
    return ans


def cur_date(add=0):
    return (datetime.today() + timedelta(days=add)).strftime('%Y%m%d')


def get_word_by_date(date):
    if len(str(date)) != 8:
        logger.log("functions", "ERROR: get wrong date!")
        return f"{date}"

    date = str(date)
    if date == cur_date():
        return "Сегодня"
    if date == cur_date(1):
        return "Завтра"
    if date == cur_date(2):
        return "Послезавтра"
    if date == cur_date(-1):
        return "Вчера"
    if date == cur_date(-2):
        return "Позавчера"

    y = int(date[:4])
    m = int(date[4:6])
    d = int(date[6:8])

    formed_date = st_date(y, m, d)
    return f"{formed_date}"


def tm():
    return datetime.now()


if __name__ == '__main__':
    print(tm().hour, tm().minute, tm().second)
