# -*- coding: utf-8 -*-
import sqlite3
import time
import logger
from datetime import datetime

conn = sqlite3.connect('1543.eljur.bot.db')
c = conn.cursor()


def cur_date(time=None):
    if time is None:
        time = str(datetime.now())
    return time[:10]


def create_lessons_date_db():
    name = f"lessons 2"

    c.execute('CREATE TABLE IF NOT EXISTS lessons_2 ('
                ' id INTEGER,'
                ' name TEXT,'
                ' number INTEGER,'
                ' schedule_id INTEGER,'
                ' day_of_week TEXT,'
                ' cabinet TEXT,'
                ' teacher TEXT,'
                ' date TEXT,'
                ' grp TEXT,'
                ' comment TEXT)'
                )

    conn.commit()


def del_table(table):
    query = f'DROP TABLE IF EXISTS {table}'
    print(query)
    c.execute(query)
    conn.commit()


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

            query = f"INSERT INTO {main_db} VALUES ({get_id_of_class(class_name)}, '{lesson_name}', {lesson_num}, {id_of_schedule}, '{day_name}', {lesson_room}, {lesson_teacher}, {cur_date}, {lesson_grp}, NULL)"
            # print(query)

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
    if class_name is None:
        logger.log("lessons_db_manip", "Пустой ввод класса в функцию get_schedule")
        return

    if date is None:
        logger.log("lessons_db_manip", "Пустой ввод даты в функцию get_schedule")
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


def get_cancel(class_name=None, day_of_week=None, lesson=None):
    if class_name is None:
        logger.log("lessons_db_manip", "Не указан class_name в get_comment")
    if day_of_week is None:
        logger.log("lessons_db_manip", "Не указан day в get_comment")
    if lesson is None:
        logger.log("lessons_db_manip", "Не указан lesson в get_comment")
    query = f"UPDATE lessons SET comment = 'Урок_отменен' WHERE schedule_id = '{get_id_of_schedule(class_name)}' AND day_of_week = '{day_of_week}' AND name = '{lesson}'"
    c.execute(query)
    conn.commit()


if __name__ == '__main__':
    del_table("lessons_2")
    create_lessons_date_db()
