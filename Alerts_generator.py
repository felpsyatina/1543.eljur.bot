from lessons_db_manip import LessonDbReq as Ldb
from users_db_parser import UserDbReq as Udb
import eljur_api
import logger
import Alerts
import config

from functions import classes, cur_date, get_word_by_date, preset, tm, del_op
student = eljur_api.Student(**preset)

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


def dates_add():
    hour = tm().hour + 3
    minutes = tm().minute

    if 15 <= hour and 30 <= minutes:
        return [1, 2, 3]

    return [0, 1, 2, 3]


def parse_schedule(new_schedule):
    new_schedule = new_schedule['days']
    new_schedule_dict = {}
    for date, dict_of_this_date in new_schedule.items():
        for lesson in dict_of_this_date.get("items", []):
            lesson_name = lesson["name"]
            lesson_num = lesson["num"]
            new_schedule_dict[lesson_num] = lesson_name
    return new_schedule_dict


def parse_homework(r, date):
    new_homework_dict = {}
    if not r:
        return {}

    homework = r['days'][date]['items']
    for lesson in homework:
        old_homework = ""
        lesson_name = lesson['name']

        if 'homework' in lesson.keys():
            task = lesson['homework']
            old_homework += f"{task['1']['value']}\n"

        if 'files' in lesson.keys():
            old_homework += "Файлы:\n"
            for file in lesson['files']['file']:
                old_homework += f"{file['filename']}: {file['link']}\n"

        if old_homework:
            new_homework_dict[lesson_name] = old_homework

    return new_homework_dict


def update_schedule_for_class(class_name, date, last):

    new_homework = student.get_hometask(class_name, date)
    new_homework_dict = parse_homework(new_homework, date)
    new_schedule = student.get_schedule(class_name, date)
    old_schedule = lesson_db.get_schedule(class_name, date)
    new_schedule_dict = parse_schedule(new_schedule)

    if not old_schedule:
        lesson_db.add_schedule(class_name, date)
    for num, lessons in old_schedule.items():
        for lesson in lessons:
            if num not in new_schedule_dict.keys() or new_schedule_dict[num] != lesson['name']:
                lesson_db.edit_lesson(class_name, date, num, lesson['name'],
                                      {'name': new_schedule_dict[num],
                                       'unsent_change': 1})
            if lesson['name'] in new_homework_dict.keys() and new_homework_dict[lesson['name']]:
                if '\'' in new_homework_dict[lesson['name']]:
                    new_homework_dict[lesson['name']] = del_op(new_homework_dict[lesson['name']])
                if new_homework_dict[lesson['name']] != lesson['homework']:
                    if date != last:
                        lesson_db.edit_lesson(class_name, date, num, lesson['name'],
                                              {'homework': new_homework_dict[lesson['name']],
                                               'unsent_homework': 1})
                    else:
                        lesson_db.edit_lesson(class_name, date, num, lesson['name'],
                                              {'homework': new_homework_dict[lesson['name']]})
                new_homework_dict[lesson['name']] = None


def update_information():
    dates = [cur_date(d) for d in dates_add()]
    last = max(dates)

    for class_name in classes:
        for date in dates:
            update_schedule_for_class(class_name, date, last)

            logger.log("alerts", f"{class_name} on {date} added")


def erase_flags():
    dates = [cur_date(d) for d in dates_add()]

    for class_name in classes:
        for date in dates:
            lesson_db.erase_unsent(date, class_name)

    logger.log("alerts", "flags deleted")


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


def send_to_user(user, date, c, schedule):
    subs = user['subs']

    if c not in subs:
        return

    date_word = get_word_by_date(date)

    title = f"Выложено домашнее задание на {date_word.lower()}:\n"
    ans = ""

    for lesson in schedule:
        if 'grp' not in lesson:
            ans += f"{lesson['name']}:\n{lesson['homework']}\n"
        else:
            if lesson['grp'] in subs[c].get(lesson['name'], []) or lesson['grp'] is None:
                ans += f"{lesson['name']}:\n{lesson['homework']}\n"

    if ans:
        Alerts.send_alerts([user['id']], title + ans)


def get_and_send_for_all():
    dates = [cur_date(d) for d in dates_add()]
    users = user_db.get_all_users()

    for date in dates:
        for c in classes:
            schedule = lesson_db.find_unsent_homework(date, c)
            if not schedule:
                continue

            for user in users:
                send_to_user(user, date, c, schedule)

    logger.log("alerts", "alerts are sent")


if __name__ == '__main__':
    update_information()
    if is_time_to_work():
        get_and_send_for_all()
        erase_flags()
