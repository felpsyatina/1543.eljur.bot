from lessons_db_manip import LessonDbReq as Ldb
from users_db_parser import UserDbReq as Udb
from eljur_api import Student
import logger
import Alerts
import config

from functions import cur_date, get_word_by_date, preset, tm

student = Student(**preset)

DATES_ADD = [0, 1, 2, 3]
flag_on_PC = config.params['flag_on_PC']

if flag_on_PC:
    lesson_db = Ldb()
    user_db = Udb()
else:
    lesson_db = Ldb("1543.eljur.bot/1543.eljur.bot.db")
    user_db = Udb("1543.eljur.bot/1543.eljur.bot.db")


def is_time_to_work():
    hour = tm().hour

    if not flag_on_PC:
        hour += 3

    if 7 <= hour < 22:
        return True
    else:
        return False


def list_of_adding_dates():
    hour = tm().hour + 3

    if 15 <= hour:
        return [cur_date(d) for d in [1, 2, 3, 4]]

    return [cur_date(d) for d in [0, 1, 2, 3, 4]]


def update_information():
    lesson_db.add_schedules(list_of_dates=list_of_adding_dates())


def parse_one_lesson(lesson):
    return f"{lesson['name']} ({lesson['number']} урок):\n{lesson['homework']}\n"


def create_homework_message(schedule, user_subs):
    ans = ""

    for lesson_number, lessons in schedule.items():
        for lesson in lessons:
            if lesson['homework'] is None or not lesson['unsent_homework']:
                continue

            if lesson['grp'] is None:
                ans += parse_one_lesson(lesson)

            elif not user_subs.get(lesson['name'], []):
                ans += parse_one_lesson(lesson)

            elif lesson['grp'] in user_subs[lesson['name']]:
                ans += parse_one_lesson(lesson)

        if ans:
            return ans


def create_changes_message(schedule):
    ans = ""

    for lesson_number, lessons in schedule.items():
        for lesson in lessons:
            if lesson['unsent_change']:
                ans += f"{lesson['name']} ({lesson['number']} урок):\n"

        if ans:
            return ans


def parse_message_for_user(user):
    answer_string = ""
    dates = list_of_adding_dates()

    for user_class, user_subs in user['subs'].items():
        this_class_answer_string = ""
        for date in dates:
            date_word = get_word_by_date(date)
            schedule = lesson_db.get_schedule(user_class, date)
            created_homework_message = create_homework_message(schedule, user_subs)
            created_changes_message = create_changes_message(schedule)

            if created_homework_message is not None:
                this_class_answer_string += f"• Выложено домашнее задание на {date_word.lower()}:\n"
                this_class_answer_string += created_homework_message
                this_class_answer_string += "\n"

            if created_changes_message is not None:
                this_class_answer_string += f"• Изменения уроков на {date_word.lower()}:\n"
                this_class_answer_string += created_changes_message
                this_class_answer_string += "\n"

        if this_class_answer_string:
            answer_string += f"Класс {user_class}:\n\n"
            answer_string += this_class_answer_string

    logger.log("alerts", f"parsed message for user {user['first_name']} {user['last_name']}, ans: {answer_string}")
    return answer_string


def get_and_send_for_all():
    sent_alerts_counter = 0
    users = user_db.get_all_users()

    for user in users:
        title = "ОБНОВЛЕНИЕ ДЗ И РАСПИСАНИЯ.\n\n"
        answer = parse_message_for_user(user)

        if answer:
            Alerts.send_alerts([user['id']], title + answer)
            sent_alerts_counter += 1

    logger.log("alerts", f"Bot has sent {sent_alerts_counter} alerts!")


if __name__ == '__main__':
    update_information()
    if is_time_to_work():
        get_and_send_for_all()
        lesson_db.erase_unsent_list(date_list=list_of_adding_dates())
