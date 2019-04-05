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
        return [cur_date(d) for d in [1, 2, 3]]

    return [cur_date(d) for d in [0, 1, 2, 3]]


def update_information():
    lesson_db.add_schedules(list_of_dates=list_of_adding_dates())


def get_changes(to_date, for_class):
    alerts = lesson_db.find_unsent_changes(to_date, for_class)
    message = ""
    for alert in alerts:
        comment = alert['comment']
        lesson = alert['lesson']
        number = alert['number']
        date = get_word_by_date(to_date)
        message += f"{date} изменения {number} урока {lesson}: {comment}"
    return message


def get_homework_and_send(to_date, for_class):
    alerts = lesson_db.find_unsent_homework(to_date, for_class)
    message = ""
    for alert in alerts:
        homework = alert['homework']
        name = alert['name']
        date = get_word_by_date(to_date)
        message += f"Выложено дз по {name} на {date}:\n {homework}\n"


def send_changes(for_date, to_class):
    class_participants = user_db.get_users_by_subs(to_class)
    message = get_changes(for_date, to_class)
    Alerts.send_alerts(class_participants, message)


def create_message(schedule, user_class, user_subs):
    if user_class not in user_subs:
        return

    ans = ""

    for lesson in schedule:
        if lesson['grp'] is None:
            ans += f"{lesson['name']}:\n{lesson['homework']}\n"

        elif not user_subs[user_class].get(lesson['name'], []):
            ans += f"{lesson['name']}:\n{lesson['homework']}\n"

        elif lesson['grp'] in user_subs[user_class][lesson['name']]:
            ans += f"{lesson['name']}:\n{lesson['homework']}\n"

    return ans


def parse_message_for_user(user):
    answer_string = ""
    dates = list_of_adding_dates()

    for user_class, user_subs in user['subs'].items():
        this_class_answer_string = ""
        for date in dates:
            date_word = get_word_by_date(date)
            schedule = lesson_db.get_schedule(user_class, date)
            created_message = create_message(schedule, user_class, user_subs)

            if created_message is not None:
                this_class_answer_string += f"• Выложено домашнее задание на {date_word.lower()}:\n\n"

                this_class_answer_string += created_message
                this_class_answer_string += "\n"

        if this_class_answer_string:
            answer_string += f"Класс {user_class}:\n\n"
            answer_string += this_class_answer_string

    logger.log("alerts", f"parsed message for user {user['first_name']} {user['last_name']}, ans: {answer_string}")
    return answer_string


def get_and_send_for_all():
    users = user_db.get_all_users()

    for user in users:
        answer = parse_message_for_user(user)

        if answer:
            Alerts.send_alerts([user['id']], answer)

    logger.log("alerts", "alerts are sent")


if __name__ == '__main__':
    update_information()
    if is_time_to_work():
        get_and_send_for_all()
        lesson_db.erase_unsent_list(date_list=list_of_adding_dates())
