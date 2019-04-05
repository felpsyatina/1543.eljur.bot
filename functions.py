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

ROMANS = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]

ROMANS2 = ["", "Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ"]

SUB_OPT = {
    "Позавчера": -2,
    "Вчера": -1,
    "Сегодня": 0,
    "Завтра": 1,
    "Послезавтра": 2,
    "Через два дня": 3,
    "Через три дня": 4
}

MONTH_TO_NUM = {"январь": 0,
                "января": 0,
                "февраль": 1,
                "февраля": 1,
                "март": 2,
                "марта": 2,
                "апрель": 3,
                "апреля": 3,
                "май": 4,
                "мая": 4,
                "июнь": 5,
                "июня": 5,
                "июль": 6,
                "июля": 6,
                "август": 7,
                "августа": 7,
                "сентебрь": 8,
                "сентебря": 8,
                "октябрь": 9,
                "октября": 9,
                "ноябрь": 10,
                "ноября": 10,
                "декабрь": 11,
                "декабря": 11,
                }

preset = {"devkey": config.secret['eljurapi']['devkey'], "vendor": "1543",
          "password": config.secret['eljurapi']['password'],
          "login": config.secret['eljurapi']['login']}


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
