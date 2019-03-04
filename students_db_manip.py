# -*- coding: utf-8 -*-
import sqlite3
import time
import logger
from datetime import datetime
import update_schedule_json_file as get_sch


class MyCursor(sqlite3.Cursor):
    def __init__(self, connection):
        sqlite3.Cursor.__init__(self, connection)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        self.connection.commit()
        self.close()
        self.connection.close()


class StudentsDbReq:
    def __init__(self, database_name="1543.eljur.bot.db"):
        self.database_name = database_name
        self.curr = None

    def run_cursor(self):
        return MyCursor(sqlite3.connect(self.database_name, isolation_level=None))

    def del_table(self, table_name="students"):
        with self.run_cursor() as cursor:
            query = f'DROP TABLE IF EXISTS {table_name}'
            cursor.execute(query)
            logger.log("students_db_manip", f"table '{table_name}' deleted!")

    def create_students_db(self, table_name="students"):
        with self.run_cursor() as cursor:
            query = f"""
                create table {table_name}
                (
                    id integer not null
                            primary key autoincrement,
                    first_name text,
                    last_name text,
                    class_id int,
                    notes text
                );
            """

            cursor.execute(query)
            logger.log("students_db_manip", f"table '{table_name}' created!")

    def setup_db(self):
        self.del_table()
        self.create_students_db()


if __name__ == '__main__':
    req = StudentsDbReq()
    req.setup_db()
