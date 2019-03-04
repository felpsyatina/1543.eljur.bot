# -*- coding: utf-8 -*-
import sqlite3
import time
import logger
from datetime import datetime
import update_schedule_json_file as get_sch


class MyCursor(sqlite3.Cursor):
    def __init__(self, connection):
        super().__init__(self, connection)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        self.close()


class LessonDbReq:
    def __init__(self, database_name="1543.eljur.bot.db"):
        self.database_name = database_name
        self.curr = None

    def run(self, function=None, *args):
        with sqlite3.connect(self.database_name, isolation_level=None) as connection, MyCursor(connection) as cursor:
            if function is not None:
                ans = function(*args, cursor=cursor)
                connection.commit()
                return ans