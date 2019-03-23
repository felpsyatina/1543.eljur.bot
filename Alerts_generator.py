from lessons_db_manip import LessonDbReq as Ldb
from users_db_parser import UserDbReq as Udb
import logger
import Alerts

from functions import classes, cur_date, get_word_by_date, student, tm

lesson_db = Ldb()
user_db = Udb()


def is_time_to_work():
    hour = tm().hour + 3
    if 7 <= hour < 22:
        return True
    else:
        return False


def update_homework():
    for class_name in ["10В"]:
        for date in [cur_date(), cur_date(1), cur_date(2)]:
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
                        for file in lesson['files']['file']:
                            temp += f"   {file['filename']}: {file['link']}\n"

                    if temp:
                        add_dict[lesson_name] = temp

            temp = lesson_db.get_schedule(class_name, date)
            if not temp:
                lesson_db.add_schedule(class_name, date)

            schedule = lesson_db.get_schedule(class_name, date)
            for num, lessons in schedule.items():
                for lesson in lessons:
                    if lesson['name'] in add_dict.keys() and add_dict[lesson['name']]:
                        if add_dict[lesson['name']] != lesson['homework']:
                            lesson_db.edit_lesson(class_name, date, num, lesson['name'],
                                                  {'homework': add_dict[lesson['name']],
                                                   'unsent_homework': 1})
                        add_dict[lesson['name']] = None


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


def get_homework(to_date, for_class):
    alerts = lesson_db.find_unsent_homework(to_date, for_class)
    print(alerts)
    message = ""
    for alert in alerts:
        print(alert)
        homework = alert['homework']
        name = alert['name']
        date = get_word_by_date(to_date)
        message += f"Выложено дз по {name} на {date}:\n {homework}\n"
    return message


def send_changes(for_date, to_class):
    class_participants = user_db.get_users_by_subs(to_class)
    message = get_changes(for_date, to_class)
    Alerts.send_alerts(class_participants, message)


def get_and_send_for_all():
    for c in ["10В"]:
        class_participants = user_db.get_users_by_subs(c)
        message = ""
        for date in [cur_date(), cur_date(1), cur_date(2)]:
            message += get_homework(date, c)
            message += "\n"
        Alerts.send_alerts(class_participants, message)


if __name__ == '__main__':
    update_homework()
    if is_time_to_work():
        get_and_send_for_all()
