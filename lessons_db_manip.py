# -*- coding: utf-8 -*-
import schedule_parser
import sqlite3
import time
import logger

conn = sqlite3.connect('1543.eljur.bot.db')
c = conn.cursor()


def get_id_of_schedule(class_name):
    class_num = int(class_name[:-1])
    class_letter = class_name[-1]
    c.execute(f"SELECT * FROM classes WHERE class_num = {class_num} AND class_letter = '{class_letter}'")
    id_of_schedule = c.fetchone()[3]
    return id_of_schedule


def get_id_of_class(class_name):  # формат чилсло и одна бука класса (КИРИЛИЦА!) без пробелов: 11A, 5В, 8Г
    class_num = int(class_name[:-1])
    class_letter = class_name[-1]
    c.execute(f"SELECT * FROM classes WHERE class_num = {class_num} AND class_letter = '{class_letter}'")
    id_of_class = c.fetchone()[0]
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
    c.execute(f"UPDATE lessons SET comment = 'Урок отменен' WHERE schedule_id = {get_id_of_schedule(class_name)}"
              f"AND day_of_week = {day_of_week} AND name = {lesson})")
    conn.commit()
