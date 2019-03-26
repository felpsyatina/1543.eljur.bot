# -*- coding: utf-8 -*-
import sqlite3
import logger
from functions import MyCursor
from json import dumps, loads


class StudentsDbReq:
    def __init__(self, database_name="1543.eljur.bot.db"):
        self.database_name = database_name
        self.cursor = None

    def run_cursor(self):
        if self.cursor is None or not self.cursor.connected:
            self.cursor = MyCursor(sqlite3.connect(self.database_name, isolation_level=None))
        return self.cursor

    def del_table(self, table_name):
        with self.run_cursor() as cursor:
            query = f'DROP TABLE IF EXISTS {table_name}'

            cursor.execute(query)
            logger.log("students_db_manip", f"table '{table_name}' deleted.")

    def create_users_db(self, table_name="students"):
        with self.run_cursor() as cursor:
            self.del_table(table_name)

            query = f"""
                create table {table_name}
                (
                    id integer not null
                       primary key autoincrement,
                    first_name text not null,
                    last_name text not null,
                    class text,
                    grp text
                );
            """

            cursor.execute(query)
            logger.log("students_db_manip", f"table: '{table_name}' created.")

    def add_student(self, first_name, last_name, student_class, groups):
        with self.run_cursor() as cursor:
            query = f"""
                INSERT INTO students (first_name, last_name, class, grp) 
                VALUES('{first_name}', '{last_name}', '{student_class}', '{dumps(groups)}')
            """
            cursor.execute(query)
            logger.log("students_db_manip", f"user '{first_name} {last_name}' created!")

    def get_student_id(self, first_name, last_name, student_class=None):
        with self.run_cursor() as cursor:
            if student_class is None:
                query = f"""
                    SELECT id FROM students WHERE 
                    first_name = '{first_name}' and 
                    last_name = '{last_name}'
                """
            else:
                query = f"""
                    SELECT id FROM students WHERE 
                    first_name = '{first_name}' and 
                    last_name = '{last_name}' and 
                    class = '{student_class}'
                """

            cursor.execute(query)
            fetch = cursor.fetchall()
            return [e[0] for e in fetch]

    def get_columns_info(self, table="students"):
        with self.run_cursor() as cursor:
            query = f"""
                PRAGMA table_info({table})
            """

            cursor.execute(query)
            description = cursor.fetchall()
        return description

    def get_columns_names(self, table="students"):
        columns_info = self.get_columns_info(table=table)
        names = []
        for column in columns_info:
            names.append(column[1])

        return names

    def get_student_info_by_id(self, student_id):
        with self.run_cursor() as cursor:
            query = f"""
                SELECT * FROM students WHERE
                id = {student_id};
            """

            cursor.execute(query)
            users_fetch = cursor.fetchone()

            if users_fetch is None:
                return None

            column_desc = self.get_columns_info()

            if len(users_fetch) != len(column_desc):
                logger.log("students_db_manip", f"Каким-то чудом длины не совпадают!")
                return

            ans_dict = {}
            for it in range(len(users_fetch)):
                if column_desc[it][1] == 'grp':
                    ans_dict[column_desc[it][1]] = loads(users_fetch[it])
                else:
                    ans_dict[column_desc[it][1]] = users_fetch[it]

            logger.log("users_db_parser", f"returning info: {ans_dict}")
            return ans_dict

    def get_student_info(self, first_name, last_name, student_class=None):
        student_ids = self.get_student_id(first_name, last_name, student_class)

        if len(student_ids) == 0:
            return False

        if len(student_ids) == 1:
            return self.get_student_info_by_id(student_ids[0])

        ans = []
        for student_id in student_ids:
            ans.append(self.get_student_info_by_id(student_id))

        return ans

    def update_user(self, dict_of_changes, student_id):
        with self.run_cursor() as cursor:
            for key, value in dict_of_changes.items():
                query = f"""UPDATE users SET {key}='{value}' WHERE id = {student_id}"""
                cursor.execute(query)
            logger.log("students_db_manip", f"{student_id} updated")

    def setup_db(self):
        self.create_users_db()


if __name__ == '__main__':
    req = StudentsDbReq()
    req.setup_db()
