# -*- coding: utf-8 -*-
import sqlite3
import logger
import config
import eljur_api
from json import dumps as jd, loads as jl
from functions import MyCursor, convert_arrays_to_dict, cur_date, classes, preset

current_min_par = config.params['min_par']
student = eljur_api.Student(**preset)


class LessonDbReq:
    def __init__(self, database_name="1543.eljur.bot.db"):
        self.database_name = database_name
        self.cursor = None

    def run_cursor(self):
        if self.cursor is None or not self.cursor.connected:
            self.cursor = MyCursor(sqlite3.connect(self.database_name, isolation_level=None))
        self.cursor.connected += 1
        return self.cursor

    def del_table(self, table_name):
        with self.run_cursor() as cursor:
            query = f'DROP TABLE IF EXISTS {table_name}'
            cursor.execute(query)
            logger.log("lesson_db_manip", f"table '{table_name}' deleted.")

    def create_classes_db(self, table_name="classes"):
        with self.run_cursor() as cursor:
            self.del_table(table_name)

            query = f"""
                create table {table_name}
                (
                    id integer not null
                        primary key autoincrement,
                    parallel int not null,
                    letter text not null,
                    groups text
                );
            """
            cursor.execute(query)
            logger.log("lesson_db_manip", f"table '{table_name}' created.")

            for num in range(current_min_par, current_min_par + 7):
                for let in ["А", "Б", "В", "Г"]:
                    query = f"INSERT INTO classes (parallel, letter, groups) VALUES({num}, '{let}', '{jd({})}')"
                    cursor.execute(query)

            logger.log("lesson_db_manip", f"added classes in '{table_name}'.")

    def get_class_groups(self, class_id):
        with self.run_cursor() as cursor:
            query = f"""
                SELECT groups FROM classes WHERE id = {class_id}
            """
            cursor.execute(query)
            fetch = cursor.fetchone()
        return jl(fetch[0])

    def add_class_groups(self, class_id, lesson, group):
        with self.run_cursor() as cursor:
            groups = self.get_class_groups(class_id)
            if lesson not in groups:
                groups[lesson] = []

            if group not in groups[lesson]:
                groups[lesson].append(group)

                query = f"""
                    UPDATE classes SET groups = '{jd(groups)}' WHERE id = {class_id}
                """
                cursor.execute(query)
                logger.log("lesson_db_manip", f"added group {group} in {class_id}")

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
                    homework text,
                    unsent_change integer,
                    unsent_homework integer
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

        if "grp" in lesson:
            lesson_grp = f"'{lesson['grp']}'"
            self.add_class_groups(class_id, lesson_name, lesson["grp"])
        else:
            lesson_grp = "NULL"

        with self.run_cursor() as cursor:
            query = f"""
                INSERT INTO lessons 
                (name, number, class_id, day_of_week, room, teacher, date, grp, comment, unsent_change, unsent_homework)
                VALUES (
                '{lesson_name}', {lesson_num}, {class_id}, '{day_name}', {lesson_room},
                {lesson_teacher}, {date}, {lesson_grp}, NULL, 0, 0)
            """

            cursor.execute(query)

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

    def get_schedule(self, class_name, date):
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

        return lessons

    def get_schedule_by_subs(self, class_name, date, user_subs):
        logger.log("lessons_db_manip", f"getting schedule by subs class: {class_name}, date: {date}, subs: {user_subs}")

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

                ans_arr = []
                for it in range(len(lesson_arr)):
                    if not lesson_arr[it]:
                        continue

                    tmp = convert_arrays_to_dict(columns, lesson_arr[it])

                    name = tmp['name']
                    if tmp.get('grp', None) is not None and user_subs.get(name, []):
                        if tmp['grp'] not in user_subs[name]:
                            tmp = None

                    if not tmp:
                        continue

                    ans_arr.append(tmp)
                    del tmp

                lessons[lesson_num] = ans_arr
        return lessons

    def edit_lesson(self, class_name, date, lesson_num, name, dict_of_changes=None):
        with self.run_cursor() as cursor:
            class_id = self.get_class_id(class_name)

            edit = [f"{key} = '{item}'" for key, item in dict_of_changes.items()]
            edit_string = ", ".join(edit)

            query = f"""
                UPDATE lessons SET {edit_string} WHERE 
                class_id = '{class_id}'
                AND date = '{date}' 
                AND number = '{lesson_num}'
                AND name = '{name}'
            """
            cursor.execute(query)
            logger.log("lesson_db_manip",
                       f"'{lesson_num}' lesson of {class_name} class in {date} edited: {edit_string}")

    def find_unsent_changes(self, date, class_name):
        ans = []
        sch = self.get_schedule(class_name, date=date)

        for lesson_num, lesson in sch.items():
            for it in range(len(lesson)):
                if not lesson[it]['unsent_change']:
                    ans.append({
                        "name": lesson[it]['name'],
                        "num": lesson[it]['number'],
                        "comment": lesson[it]['comment']
                    })
        return ans

    def erase_unsent_homework(self, date, class_name):
        sch = self.get_schedule(class_name, date=date)

        for lesson_num, lesson in sch.items():
            for it in range(len(lesson)):
                if not lesson[it]['unsent_change']:
                    print(class_name, date, lesson[it]['number'], lesson[it]['name'])

                    self.edit_lesson(class_name, date, lesson[it]['number'],
                                     name=lesson[it]['name'], dict_of_changes={'unsent_homework': 0})

    def find_unsent_homework(self, date, class_name):
        ans = []
        sch = self.get_schedule(class_name, date=date)

        for lesson_num, lesson in sch.items():
            for it in range(len(lesson)):
                if lesson[it]['unsent_homework']:
                    if 'grp' in lesson[it]:
                        ans.append({"name": lesson[it]['name'],
                                    "num": lesson[it]['number'],
                                    "homework": lesson[it]['homework'],
                                    "grp": lesson[it]['grp']})
                    else:
                        ans.append({"name": lesson[it]['name'],
                                    "num": lesson[it]['number'],
                                    "homework": lesson[it]['homework']})

        return ans

    def setup_db(self, adding_schedule=None):

        self.create_classes_db()
        self.create_lessons_db()

        if adding_schedule:
            self.add_schedules()


if __name__ == '__main__':
    req = LessonDbReq()
    req.setup_db()
