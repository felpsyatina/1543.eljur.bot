# -*- coding: utf-8 -*-
import sqlite3
import logger
import config
from datetime import datetime
import eljur_api as ea

current_min_par = 44

classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '6Г', '7А', '7Б', '7В', '7Г', '8А', '8Б', '8В', '8Г', '9А',
           '9Б', '9В', '9Г', '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']

preset = {"devkey": config.secret['eljurapi']['devkey'], "vendor": "1543",
              "password": config.secret['eljurapi']['password'],
              "login": config.secret['eljurapi']['login']}
student = ea.Student(**preset)


def cur_date():
    return datetime.today().strftime('%Y%m%d')


def is_token_exists():
    elj_token = config.secret["eljurapi"]["token"]
    if elj_token == "":
        return False
    else:
        return True


def convert_arrays_to_dict(arr1, arr2):
    if len(arr1) != len(arr2):
        return False

    length = len(arr1)
    return {arr1[it]: arr2[it] for it in range(length)}


class MyCursor(sqlite3.Cursor):
    def __init__(self, connection):
        super(MyCursor, self).__init__(connection)
        self.connected = 1

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if ex_type is not None:
            logger.log("lessons_db_manip", f"SQLite ERROR: ex_type - {ex_type}!")

        if self.connected:
            self.connection.commit()
            self.close()
            self.connection.close()
            self.connected = 0


class LessonDbReq:
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
            logger.log("lesson_db_manip", f"table '{table_name}' deleted.")

    def create_classes_db(self, table_name="classes"):
        self.del_table(table_name)

        with self.run_cursor() as cursor:
            query = f"""
                create table {table_name}
                (
                    id integer not null
                        primary key autoincrement,
                    parallel int not null,
                    letter text not null
                );
            """
            cursor.execute(query)
            logger.log("lesson_db_manip", f"table '{table_name}' created.")

            for num in range(current_min_par, current_min_par + 7):
                for let in ["А", "Б", "В", "Г"]:
                    query = f"INSERT INTO classes (parallel, letter) VALUES({num}, '{let}')"
                    cursor.execute(query)

            logger.log("lesson_db_manip", f"added classes in '{table_name}'.")

    def create_lessons_db(self, table_name="lessons"):
        self.del_table(table_name)

        with self.run_cursor() as cursor:
            query = f"""
                create table {table_name}
                (
                    id integer not null
                            primary key autoincrement,
                    name text,
                    number int not null,
                    class_id int,
                    day_of_week text not null,
                    room text,
                    teacher text,
                    date text,
                    grp text,
                    comment text,
                    homework text
                );
            """

            cursor.execute(query)
            logger.log("lesson_db_manip", f"table '{table_name}' created.")

    def get_class_id(self, class_name):
        class_name = class_name.upper()

        with self.run_cursor() as cursor:
            class_num = int(class_name[:-1])
            class_letter = class_name[-1]

            query = f"""
                SELECT * FROM classes WHERE
                parallel = {class_num + current_min_par - 5} AND
                letter = '{class_letter}';
            """

            cursor.execute(query)
            fetch = cursor.fetchone()

            id_of_class = fetch[0]
            return id_of_class

    def get_columns_info(self, table="lessons"):
        with self.run_cursor() as cursor:
            query = f"""
                PRAGMA table_info({table})
            """

            cursor.execute(query)
            description = cursor.fetchall()
        return description

    def get_columns_names(self, table="lessons"):
        columns_info = self.get_columns_info(table=table)
        names = []
        for column in columns_info:
            names.append(column[1])

        return names

    def add_lesson(self, lesson, class_id, day_name, date):
        lesson_name = lesson["name"]
        lesson_num = lesson["num"]

        if lesson["room"]:
            lesson_room = f"'{lesson['room']}'"
        else:
            lesson_room = "NULL"

        if lesson["teacher"]:
            lesson_teacher = f"'{lesson['teacher']}'"
        else:
            lesson_teacher = "NULL"

        if lesson.get("grp", 0):
            lesson_grp = f"'{lesson['grp']}'"
        else:
            lesson_grp = "NULL"

        with self.run_cursor() as cursor:
            query = f"""
                INSERT INTO lessons (name, number, class_id, day_of_week, room, teacher, date, grp, comment)
                VALUES (
                '{lesson_name}', {lesson_num}, {class_id}, '{day_name}', {lesson_room},
                {lesson_teacher}, {date}, {lesson_grp}, NULL, NULL)
            """

            cursor.execute(query)

    def add_homework(self, hometask):
        with self.run_cursor() as cursor:
            query = f"""
                 UPDATE lessons SET homework = {hometask} WHERE 
        
        
        
            """

    def add_schedule(self, class_name=None, date=None):
        class_name = class_name.upper()

        schedule = student.get_schedule(class_name, date)
        schedule = schedule['days']
        if not schedule:
            return

        class_id = self.get_class_id(class_name)

        for date, dict_of_this_date in schedule.items():
            day_name = dict_of_this_date["title"]

            for lesson in dict_of_this_date.get("items", []):
                self.add_lesson(lesson, class_id=class_id, day_name=day_name, date=date)

        logger.log("lessons_db_manip", f"schedule of class '{class_name}' on {date} added.")

    def add_schedules(self):
        for c in classes:
            self.add_schedule(c)
        logger.log("lessons_db_manip", f"all classes schedules added.")

    def get_schedule(self, class_name, date=None):
        logger.log("lessons_db_manip", f"getting schedule class: {class_name}, date: {date}")

        if date is None:
            date = cur_date()

        class_id = self.get_class_id(class_name)
        columns = self.get_columns_names()
        lessons = {}

        with self.run_cursor() as cursor:
            for lesson_num in range(0, 10):  # максимально 10 уроков
                query = f"""
                    SELECT * FROM lessons WHERE class_id = {class_id} AND date = '{date}' AND number = {lesson_num}
                """
                cursor.execute(query)
                lesson_arr = cursor.fetchall()

                if not lesson_arr:
                    continue

                for it in range(len(lesson_arr)):
                    tmp = convert_arrays_to_dict(columns, lesson_arr[it])
                    if not tmp:
                        logger.log("lessons_db_manip", f"Длины разные!!!")
                        continue
                    lesson_arr[it] = tmp
                    del tmp

                lessons[lesson_num] = lesson_arr

        logger.log("lessons_db_manip", f"output lessons: {lessons}")
        return lessons

    def edit_lesson(self, class_name, date, lesson_num, dict_of_changes=None):
        with self.run_cursor() as cursor:
            class_id = self.get_class_id(class_name)

            edit = [f"{key} = '{item}'" for key, item in dict_of_changes]
            edit_string = ", ".join(edit)

            query = f"""
                UPDATE lessons SET {edit_string} WHERE 
                class_id = '{class_id}'
                AND date = '{date}' AND name = '{lesson_num}'
            """
            cursor.execute(query)
            logger.log("lesson_db_manip", f"'{lesson_num}' lesson of {class_name} class in {date} edited: {edit_sting}")

    def setup_db(self, adding_schedule=None):
        if adding_schedule is None:
            adding_schedule = is_token_exists()

        self.create_classes_db()
        self.create_lessons_db()

        if adding_schedule:
            self.add_schedules()


if __name__ == '__main__':
    req = LessonDbReq()
    req.setup_db(False)
