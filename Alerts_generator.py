from lessons_db_manip import LessonDbReq as Ldb
from users_db_parser import UserDbReq as Udb
import logger
import Alerts
import config

from functions import classes, cur_date, get_word_by_date, student, tm, del_op


DATES_ADD = [0, 1, 2, 3]
flag_on_PC = config.params['flag_on_PC']


if flag_on_PC:
    lesson_db = Ldb()
    user_db = Udb()
else:
    lesson_db = Ldb("1543.eljur.bot/1543.eljur.bot.db")
    user_db = Udb("1543.eljur.bot/1543.eljur.bot.db")


def is_time_to_work():
    hour = tm().hour + 3
    if 7 <= hour < 22:
        return True
    else:
        return False


def update_homework():
    dates = [cur_date(d) for d in DATES_ADD]
    last = max(dates)

    for class_name in classes:
        for date in dates:
            r = student.get_hometask(class_name, date)
            add_dict = {}
            if r:
                homework = r['days'][date]['items']
                for lesson in homework:
                    temp = ""
                    lesson_name = lesson['name']

                    if 'homework' in lesson.keys():
                        task = lesson['homework']
                        temp += f"{task['1']['value']}\n"

                    if 'files' in lesson.keys():
                        temp += "Файлы:\n"
                        for file in lesson['files']['file']:
                            temp += f"{file['filename']}: {file['link']}\n"

                    if temp:
                        add_dict[lesson_name] = temp

            temp = lesson_db.get_schedule(class_name, date)
            if not temp:
                lesson_db.add_schedule(class_name, date)

            schedule = lesson_db.get_schedule(class_name, date)
            for num, lessons in schedule.items():
                for lesson in lessons:
                    if lesson['name'] in add_dict.keys() and add_dict[lesson['name']]:
                        if '\'' in add_dict[lesson['name']]:
                            add_dict[lesson['name']] = del_op(add_dict[lesson['name']])
                        if add_dict[lesson['name']] != lesson['homework']:
                            if date != last:
                                lesson_db.edit_lesson(class_name, date, num, lesson['name'],
                                                      {'homework': add_dict[lesson['name']],
                                                       'unsent_homework': 1})
                            else:
                                lesson_db.edit_lesson(class_name, date, num, lesson['name'],
                                                      {'homework': add_dict[lesson['name']]})

                        add_dict[lesson['name']] = None
            logger.log("alerts", f"{class_name} on {date} added")


def erase_flags():
    dates = [cur_date(d) for d in DATES_ADD]

    for class_name in classes:
        for date in dates:
            lesson_db.erase_unsent_homework(date, class_name)

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

    title = f"Выложено дз на {date_word}:\n"
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
    dates = [cur_date(d) for d in DATES_ADD]
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
    update_homework()
    if is_time_to_work():
        get_and_send_for_all()
        erase_flags()
