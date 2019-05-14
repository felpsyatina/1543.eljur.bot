# -*- coding: utf-8 -*-
import sqlite3
import logger
import config
from eljur_api import Student
from json import dumps as jd, loads as jl
from functions import MyCursor, convert_arrays_to_dict, cur_date, classes, preset, make_lined, del_op

current_min_par = config.params['min_par']
student = Student(**preset)


class LessonDbReq:
    def __init__(self, database_name="1543.eljur.bot.db"):
        self.database_name = database_name
        self.cursor = None
        self.lesson_table_name = "lessons"
        self.classes_table_name = "classes"

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

    def create_classes_db(self):
        with self.run_cursor() as cursor:
            self.del_table(self.classes_table_name)

            query = f"""
                create table {self.classes_table_name}
                (
                    id integer not null
                        primary key autoincrement,
                    parallel int not null,
                    letter text not null,
                    groups text
                );
            """
            cursor.execute(query)
            logger.log("lesson_db_manip", f"table '{self.classes_table_name}' created.")

            for num in range(current_min_par, current_min_par + 7):
                for let in ["А", "Б", "В", "Г"]:
                    query = f"""
                        INSERT INTO classes 
                        (parallel, letter, groups) 
                        VALUES({num}, '{let}', '{jd({})}')
                    """
                    cursor.execute(query)

            logger.log("lesson_db_manip", f"added classes in '{self.classes_table_name}'.")

    def get_class_groups(self, class_id):
        with self.run_cursor() as cursor:
            query = f"""
                SELECT groups FROM classes WHERE id = {class_id}
            """
            cursor.execute(query)
            fetch = cursor.fetchone()
        return jl(fetch[0])

    def get_class_name(self, class_id):
        with self.run_cursor() as cursor:
            query = f"""
                SELECT parallel, letter FROM classes WHERE id = {class_id}
            """
            cursor.execute(query)
            fetch = cursor.fetchone()

        return str(int(fetch[0]) - current_min_par + 5) + fetch[1]

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

    def create_lessons_db(self):
        self.del_table(self.lesson_table_name)

        with self.run_cursor() as cursor:
            query = f"""
                create table {self.lesson_table_name}
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
                    unsent_homework integer,
                    is_updated integer
                );
            """

            cursor.execute(query)
            logger.log("lesson_db_manip", f"table '{self.lesson_table_name}' created.")

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

    def get_lesson(self, class_id, date, num, grp=None):
        add_str = ""
        if grp == "NULL":
            grp = None

        if grp is not None:
            add_str += f"AND grp = {self.parse_string_in_query(grp)}"

        with self.run_cursor() as cursor:
            columns = self.get_columns_names()

            query = f"""
                SELECT * FROM lessons 
                WHERE class_id = {class_id} 
                AND date = '{date}' 
                AND number = {num} 
                {add_str}
            """
            cursor.execute(query)
            lesson_arr = cursor.fetchall()

            if not lesson_arr:
                return None

            for it in range(len(lesson_arr)):
                tmp = convert_arrays_to_dict(columns, lesson_arr[it])
                if not tmp:
                    logger.log("lessons_db_manip", f"Длины разные!!!")
                    continue
                lesson_arr[it] = tmp
                del tmp

            return lesson_arr

    @staticmethod
    def parse_homework(homework, lesson_name, lesson_grp=None):
        if not homework:
            return {}

        homework = homework['items']
        for lesson in homework:
            this_lesson_name = lesson['name']
            this_lesson_grp = lesson.get('grp', None)

            if this_lesson_name == lesson_name and this_lesson_grp == lesson_grp:

                old_homework = ""
                if 'homework' in lesson.keys():
                    task = lesson['homework']
                    old_homework += f"{task['1']['value']}\n"

                if 'files' in lesson.keys():
                    old_homework += "Файлы:\n"
                    for file in lesson['files']['file']:
                        old_homework += f"{file['filename']}: {file['link']}\n"
                return old_homework

        return None

    @staticmethod
    def parse_string_in_query(string):
        if type(string) == str:
            string = del_op(string)
            return f"'{string}'"

        if string is None:
            return "NULL"

        return string

    def add_lesson(self, lesson, homework, class_id, day_name, date):
        lesson_name = lesson["name"]
        lesson_num = lesson["num"]

        if lesson_name == "Cancel":
            lesson_name = "Урок отменен!"

        lesson_room = "NULL"
        lesson_teacher = "NULL"
        lesson_grp = None
        lesson_homework = None

        if lesson["room"]:
            lesson_room = f"'{lesson['room']}'"

        if lesson["teacher"]:
            lesson_teacher = f"'{lesson['teacher']}'"

        if "grp" in lesson:
            lesson_grp = f"{lesson['grp']}"
            self.add_class_groups(class_id, lesson_name, lesson["grp"])

        if homework:
            temp_homework = self.parse_homework(homework[date], lesson_name, lesson_grp)
            if temp_homework is not None:
                lesson_homework = f"{del_op(temp_homework).rstrip()}"

        grp_string = self.parse_string_in_query(lesson_grp)

        grp_add = ""
        if grp_string != "NULL":
            grp_add = f"AND grp = {grp_string}"

        old_lessons = self.get_lesson(class_id, date, lesson_num, grp=lesson_grp)

        if old_lessons and len(old_lessons) > 1:
            for old_les in old_lessons:
                if old_les['name'] == lesson_name:
                    old_lessons = [old_les]
                    break
            else:
                old_lessons = []

        if old_lessons and old_lessons[0]['homework']:
            old_lessons[0]['homework'] = old_lessons[0]['homework'].strip()

        homework_changed = old_lessons and lesson_homework and lesson_homework != old_lessons[0]['homework']

        if homework_changed and old_lessons[0]["is_updated"]:
            if date == cur_date(1):
                is_unsent = 1
            else:
                is_unsent = 0

            with self.run_cursor() as cursor:
                query = f"""
                    UPDATE lessons SET
                    homework = {self.parse_string_in_query(lesson_homework)},
                    unsent_homework = {is_unsent} WHERE 
                    class_id = '{class_id}'
                    AND date = '{date}' 
                    AND number = '{lesson_num}'
                    AND name = '{old_lessons[0]['name']}'   
                    {grp_add}
                """
                cursor.execute(query)

                logger.log(
                    "lessons_db_manip",
                    f"changed homework {class_id}, {date}, {lesson_num} "
                    f"from {old_lessons[0]['homework']} to {lesson_homework}"
                )

        if old_lessons and lesson_name != old_lessons[0]['name'] and "Урок отменен!" not in old_lessons[0]['name'] \
                and old_lessons[0]["is_updated"]:
            new_lesson_name = f"{make_lined(old_lessons[0]['name'])} {lesson_name}"

            with self.run_cursor() as cursor:
                query = f"""
                    UPDATE lessons SET name = '{new_lesson_name}', unsent_change = 1 WHERE 
                    class_id = '{class_id}'
                    AND date = '{date}' 
                    AND number = '{lesson_num}'
                    AND name = '{old_lessons[0]['name']}'
                    {grp_add}
                """

                cursor.execute(query)

        if old_lessons and old_lessons[0]["is_updated"]:
            return

        lesson_homework = self.parse_string_in_query(lesson_homework)
        with self.run_cursor() as cursor:
            query = f"""
                INSERT INTO lessons 
                (name, number, class_id, day_of_week, room, teacher,
                 date, grp, comment, unsent_change, unsent_homework, is_updated, homework)
                VALUES (
                '{lesson_name}', {lesson_num}, {class_id}, '{day_name}', {lesson_room},
                {lesson_teacher}, {date}, {grp_string}, NULL, 0, 0, 0, {lesson_homework})
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
            homework = student.get_hometask(class_name, date)
            if homework:
                homework = homework.get('days', None)

            day_name = dict_of_this_date["title"]

            for lesson in dict_of_this_date.get("items", []):
                self.add_lesson(lesson, homework, class_id=class_id, day_name=day_name, date=date)

            with self.run_cursor() as cursor:
                query = f"""
                    UPDATE lessons SET is_updated = 1 WHERE 
                    class_id = '{class_id}'
                    AND date = '{date}'
                """
                cursor.execute(query)

        logger.log("lessons_db_manip", f"schedule of class '{class_name}' on {date} added.")

    def add_schedules(self, list_of_dates=None):
        for c in classes:
            if list_of_dates is None:
                self.add_schedule(c)
                continue

            for date in list_of_dates:
                self.add_schedule(c, date)

        logger.log("lessons_db_manip", f"all classes schedules added.")

    def get_schedule(self, class_name, date):
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

        logger.log("lessons_db_manip", f"returning schedule for class {class_name}, date {date}: len - {len(lessons)}")
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

    def edit_lesson(self, class_name, date, lesson_num, name, dict_of_changes=None, grp=None):
        if grp == "NULL":
            grp = None

        with self.run_cursor() as cursor:
            class_id = self.get_class_id(class_name)

            edit = [f"{key} = '{item}'" for key, item in dict_of_changes.items()]
            edit_string = ", ".join(edit)

            grp_add = ""
            if grp is not None:
                grp_add = f"AND grp = '{grp}'"
            query = f"""
                UPDATE lessons SET {edit_string} WHERE 
                class_id = '{class_id}'
                AND date = '{date}' 
                AND number = '{lesson_num}'
                AND name = '{name}'
                {grp_add}
            """
            cursor.execute(query)
            logger.log("lesson_db_manip",
                       f"'{lesson_num}' lesson of {class_name} class in {date} edited: {edit_string}")

    def erase_unsent(self, date, class_name):
        sch = self.get_schedule(class_name, date=date)

        for lesson_num, lesson in sch.items():
            for it in range(len(lesson)):
                if lesson[it]['unsent_homework']:
                    self.edit_lesson(class_name, date, lesson[it]['number'],
                                     name=lesson[it]['name'], dict_of_changes={'unsent_homework': 0})

                if lesson[it]['unsent_change']:
                    self.edit_lesson(class_name, date, lesson[it]['number'],
                                     name=lesson[it]['name'], dict_of_changes={'unsent_change': 0})

    def erase_unsent_list(self, date_list, classes_list=None):
        if classes_list is not None:
            for class_ in classes_list:
                for date_ in date_list:
                    self.erase_unsent(date_, class_)
            return

        for date in date_list:
            with self.run_cursor() as cursor:
                query = f"""
                    UPDATE lessons SET unsent_change = 0, unsent_homework = 0 
                    WHERE date = '{date}'
                """
                cursor.execute(query)

        logger.log("lessons_db_manip", f"deleted all 'unsent' in {date_list}")

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

    def find_unsent_changes(self, date, class_name):
        ans = []
        sch = self.get_schedule(class_name, date=date)

        for lesson_num, lesson in sch.items():
            for it in range(len(lesson)):
                if lesson[it]['unsent_changes']:
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

    def get_lessons_by_date_and_lesson_number(self, date, lesson_number):

        columns = self.get_columns_names()
        lessons = []

        with self.run_cursor() as cursor:
            query = f"""
                    SELECT * FROM lessons WHERE date = '{date}' AND number = {lesson_number}
                """
            cursor.execute(query)
            lesson_arr = cursor.fetchall()

            for lesson in lesson_arr:
                tmp = convert_arrays_to_dict(columns, lesson)
                lessons.append(tmp)

        return lessons

    def add_field_class_name_to_list_of_lessons(self, lessons):

        for lesson in lessons:
            lesson['class_name'] = self.get_class_name(lesson['class_id'])

        return lessons

    def get_beautified_lessons_for_desk(self, number=1, date=cur_date()):
        return self.add_field_class_name_to_list_of_lessons(
            self.get_lessons_by_date_and_lesson_number(date, number))


if __name__ == '__main__':
    req = LessonDbReq()
    req.setup_db()
