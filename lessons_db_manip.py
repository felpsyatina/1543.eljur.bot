# -*- coding: utf-8 -*-
import sqlite3
import time
import logger
from datetime import datetime
import update_schedule_json_file as get_sch

conn = sqlite3.connect('1543.eljur.bot.db')
c = conn.cursor()
current_min_par = 44

classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '6Г', '7А', '7Б', '7В', '7Г', '8А', '8Б', '8В', '8Г', '9А',
                       '9Б', '9В', '9Г', '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']


def cur_date():
    return datetime.today().strftime('%Y%m%d')


class MyCursor(sqlite3.Cursor):
    def __init__(self, connection):
        sqlite3.Cursor.__init__(self, connection)

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

    def gen_query_class_table(self):
        name = f"classes"

        query = f"""
                create table {name}
                (
                    id integer not null
                        primary key autoincrement,
                    paral int not null,
                    letter text not null
                );
                """

        return query

    def gen_query_add_class(self, paral_num, letter):
        query = f"INSERT INTO classes (paral, letter) VALUES({paral_num}, '{letter}')"
        return query

    def gen_query_lesson_table(self):
        name = f"lessons"

        query = f"""
                create table {name}
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
                    comment text
                );
                """
        return query

    def gen_query_del_table(self, table_name):
        query = f'DROP TABLE IF EXISTS {table_name}'
        return query

    def gen_query_get_cls_id(self, class_num, class_letter):
        query = f"""
                SELECT * FROM classes WHERE
                paral = {class_num + current_min_par - 5} AND
                letter = '{class_letter}';
                """

        return query

    def create_classes_db(self, cursor):
        cursor.execute(self.gen_query_class_table())
        logger.log("lesson_db_manip", "created table: 'classes'")

        for paral_num in range(current_min_par, current_min_par + 7):
            for letter in ["А", "Б", "В", "Г"]:
                cursor.execute(self.gen_query_add_class(paral_num=paral_num, letter=letter))
        logger.log("lesson_db_manip", "added classes in 'classes'")

    def create_lessons_date_db(self, cursor):
        cursor.execute(self.gen_query_lesson_table())
        logger.log("lesson_db_manip", "created table: 'lessons'")

    def del_table(self, table, cursor):
        cursor.execute(self.gen_query_del_table(table_name=table))
        logger.log("lesson_db_manip", f"table '{table}' deleted!")

    def get_id_of_class(self, class_name, cursor):
        class_num = int(class_name[:-1])
        class_letter = class_name[-1]
        q = self.gen_query_get_cls_id(class_num=class_num, class_letter=class_letter)

        cursor.execute(q)
        fetch = cursor.fetchone()

        id_of_class = fetch[0]
        return id_of_class

    def add_schedule_from_json(self, schedule=None, class_name=None, cursor=None):
        if schedule is None:
            logger.log("lessons_db_manip", "Пустой ввод в функцию add_schedule_from_json")
            return

        class_id = self.get_id_of_class(class_name, cursor)

        for cur_date in schedule.keys():
            dict_of_this_date = schedule[cur_date]
            day_name = dict_of_this_date["title"]

            for lesson in dict_of_this_date.get("items", []):
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

                query = f"""
                        INSERT INTO lessons (name, number, class_id, day_of_week, room, teacher, date, grp, comment)
                        VALUES (
                        '{lesson_name}', {lesson_num}, {class_id}, '{day_name}', {lesson_room},
                        {lesson_teacher}, {cur_date}, {lesson_grp}, NULL)
                        """

                cursor.execute(query)

    def add_schedules(self, cursor):
        for c in classes:
            self.add_schedule_from_json(get_sch.update(c), c, cursor)

            logger.log("update_schedule_by_json", f"database added {c}")

    def get_schedule_by_date(self, class_name=None, date=None, cursor=None):
        logger.log("lessons_db_manip", f"getting schedule class: {class_name}, date: {date}")

        if class_name is None:
            logger.log("lessons_db_manip", "Пустой ввод класса в функцию get_schedule")
            return

        if date is None:
            date = cur_date()

        class_id = self.get_id_of_class(class_name, cursor=cursor)

        lessons = {}
        for lesson_num in range(0, 10):  # максимально 10 уроков
            query = f"SELECT * FROM lessons WHERE class_id = {class_id} AND date = '{date}' AND number = {lesson_num}"
            cursor.execute(query)
            lesson = cursor.fetchall()

            if not lesson:
                continue

            lessons[lesson_num] = lesson

        logger.log("lessons_db_manip", f"lessons: {lessons}")
        return lessons

    def make_cancel(self, class_name=None, day_date=None, lesson=None, cursor=None):
        if class_name is None:
            logger.log("lessons_db_manip", "Не указан class_name в get_comment")
        if day_date is None:
            logger.log("lessons_db_manip", "Не указан day в get_comment")
        if lesson is None:
            logger.log("lessons_db_manip", "Не указан lesson в get_comment")

        class_id = self.get_id_of_class(class_name, cursor)
        query = f"""
                UPDATE lessons SET comment = 'Урок_отменен' WHERE 
                class_id = '{class_id}'
                AND date = '{day_date}' AND name = '{lesson}'
                """
        cursor.execute(query)
        logger.log("lesson_db_manip", f"canceled lesson: class_id - {class_id}, date - {day_date}, lesson - {lesson}")

    def setup_db(self, adding_schedule=False):
        self.run(self.del_table, "lessons")
        self.run(self.del_table, "classes")
        self.run(self.create_classes_db)
        self.run(self.create_lessons_date_db)
        if adding_schedule:
            self.run(self.add_schedules)


def get_id_of_schedule(class_name):
    class_num = int(class_name[:-1])
    class_letter = class_name[-1].upper()
    c.execute(f"SELECT * FROM classes WHERE class_num = {class_num} AND class_letter = '{class_letter}'")
    fetch = c.fetchone()
    id_of_schedule = fetch[3]
    return id_of_schedule


def get_id_of_class(class_name):  # формат чилсло и одна бука класса (КИРИЛИЦА!) без пробелов: 11A, 5В, 8Г
    class_num = int(class_name[:-1])
    class_letter = class_name[-1]
    c.execute(f"SELECT * FROM classes WHERE class_num = {class_num} AND class_letter = '{class_letter}'")
    fetch = c.fetchone()
    id_of_class = fetch[0]
    return id_of_class


def create_key():
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())  # format: "YYYY-MM-DD HH:MM:SS"
    c.execute("INSERT INTO addition_schedule VALUES (null, '{}')".format(current_date))
    c.execute("SELECT * FROM addition_schedule ORDER BY id DESC LIMIT 1")
    key = c.fetchone()[0]
    conn.commit()
    return key


def add_schedules(schedules=None):
    if schedules is None:
        logger.log("lessons_db_manip", "Пустой ввод в функцию add_schedule")
        return

    for class_name in schedules.keys():
        id_of_class = get_id_of_class(class_name)
        id_of_schedule = create_key()
        c.execute(f"UPDATE classes SET cur_schedule = {id_of_schedule} WHERE id = {id_of_class}")
        schedule = schedules[class_name]
        for day_of_week in schedule.keys():
            all_lessons_in_cur_day = schedule[day_of_week]
            for lesson_num in all_lessons_in_cur_day.keys():
                lesson_name = all_lessons_in_cur_day[lesson_num]
                c.execute(
                    f"INSERT INTO lessons VALUES (NULL, '{lesson_name}', {lesson_num}, {id_of_schedule}, '{day_of_week}', NULL, NULL, NULL, NULL)")

    conn.commit()


def add_schedule_from_json(schedule=None, class_name=None, main_db="lessons_2"):
    if schedule is None:
        logger.log("lessons_db_manip", "Пустой ввод в функцию add_schedule")
        return

    id_of_class = get_id_of_class(class_name)
    id_of_schedule = create_key()
    c.execute(f"UPDATE classes SET cur_schedule = {id_of_schedule} WHERE id = {id_of_class}")

    for cur_date in schedule.keys():
        dict_of_this_date = schedule[cur_date]
        day_name = dict_of_this_date["title"]

        for lesson in dict_of_this_date.get("items", []):
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

            query = f"""INSERT INTO {main_db} VALUES (
                        {get_id_of_class(class_name)}, 
                        '{lesson_name}',
                        {lesson_num},
                        {id_of_schedule},
                        '{day_name}',
                        {lesson_room}, 
                        {lesson_teacher}, 
                        '{cur_date}',
                        '{lesson_grp}', 
                        NULL)
                    """

            c.execute(query)

    conn.commit()


def get_schedule(class_name=None):
    if class_name is None:
        logger.log("lessons_db_manip", "Пустой ввод в функцию get_schedule")
        return
    schedule_id = get_id_of_schedule(class_name)
    schedule = {}
    for day_fo_week in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]:
        lessons = {}
        for lesson_num in range(0, 10):  # максимально 10 уроков
            c.execute(
                f"SELECT * FROM lessons WHERE schedule_id = {schedule_id} AND day_of_week = '{day_fo_week}' AND number = {lesson_num}")
            lesson = c.fetchone()
            if lesson is not None:
                lessons[lesson_num] = lesson
        if len(lessons) != 0:
            schedule[day_fo_week] = lessons
    return schedule


def get_schedule_by_date(class_name=None, date=None):
    logger.log("lessons_db_manip", f"getting schedule class: {class_name}, date: {date}")

    if class_name is None:
        logger.log("lessons_db_manip", "Пустой ввод класса в функцию get_schedule")
        return

    if date is None:
        date = cur_date()

    schedule_id = get_id_of_schedule(class_name)

    #
    # for day_of_week in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]:
    #

    lessons = {}
    for lesson_num in range(0, 10):  # максимально 10 уроков
        c.execute(
            f"SELECT * FROM lessons_2 WHERE schedule_id = {schedule_id} AND date = '{date}' AND number = {lesson_num}")
        lesson = c.fetchall()

        if not lesson:
            continue

        lessons[lesson_num] = lesson

    logger.log("lessons_db_manip", f"lessons: {lessons}")
    return lessons


def get_schedules(classes=None):
    if classes is None:
        logger.log("lessons_db_manip", "Пустой ввод в функцию get_schedules")
        return
    if type(classes) == str:
        logger.log("lessons_db_manip", "Неправильный ввод в функцию get_schedules, см. докумениацию")
        return
    ans = {}
    for class_name in classes:
        ans[class_name] = get_schedule(class_name)
    return ans


def get_comment(class_name=None, day_date=None, lesson=None, comment=None):
    if class_name is None:
        logger.log("lessons_db_manip", "Не указан class_name в get_comment")
    if day_date is None:
        logger.log("lessons_db_manip", "Не указан day в get_comment")
    if lesson is None:
        logger.log("lessons_db_manip", "Не указан lesson в get_comment")
    if comment is None:
        return "Пустой комментарий"
    else:
        query = f"UPDATE lessons SET comment = '{comment}' WHERE schedule_id = '{get_id_of_schedule(class_name)}' AND day_of_week = '{day_date}' AND name = '{lesson}'"
        c.execute(query)
        conn.commit()
        return "Комментарий добавлен"


def get_replacement(class_name=None, day_date=None, lesson=None, another_lesson=None):
    if class_name is None:
        logger.log("lessons_db_manip", "Не указан class_name в get_comment")
    if day_date is None:
        logger.log("lessons_db_manip", "Не указан day в get_comment")
    if lesson is None:
        logger.log("lessons_db_manip", "Не указан lesson в get_comment")
    if another_lesson is None:
        return "Нет урока-замены"
    else:
        query = f"UPDATE lessons SET comment = '{another_lesson}' WHERE schedule_id = '{get_id_of_schedule(class_name)}' AND date = '{day_date}' AND name = '{lesson}'"
        c.execute(query)
        conn.commit()
        return "Урок заменен"


if __name__ == '__main__':
    Req = LessonDbReq()
    Req.setup_db(True)
