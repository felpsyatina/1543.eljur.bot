from lessons_db_manip import LessonDbReq as Ldb
from users_db_parser import UserDbReq as Udb
from datetime import datetime, timedelta
from datetime import date as st_date
import time
import Alerts

lesson_db = Ldb()
user_db = Udb()

classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '6Г', '7А', '7Б', '7В', '7Г', '8А', '8Б', '8В', '8Г', '9А',
           '9Б', '9В', '9Г', '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']

def cur_date(add=0):
    return (datetime.today() + timedelta(days=add)).strftime('%Y%m%d')


def get_word_by_date(date):
    if len(str(date)) != 8:
        logger.log("user_req", "ERROR: get wrong date!")
        return f"{date}"

    date = str(date)
    if date == cur_date():
        return "Сегодня"
    if date == cur_date(1):
        return "Завтра"
    if date == cur_date(2):
        return "Послезавтра"
    if date == cur_date(-1):
        return "Вчера"
    if date == cur_date(-2):
        return "Позавчера"

    y = int(date[:4])
    m = int(date[4:6])
    d = int(date[6:8])

    formed_date = st_date(y, m, d)
    return f"{formed_date}"


def if_it_is_time_to_work():
    day = time.gmtime()[2]
    hour = time.gmtime()[3]
    minutes = time.gmtime()[4]
    if 22 > hour > 7:
        return True
    else:
        return False


def get_changes(to_date, for_class):
    alerts = lesson_db.find_unsent(to_date, for_class)
    message = ""
    for alert in alerts:
        comment = alert['comment']
        lesson = alert['lesson']
        number = alert['number']
        date = get_word_by_date(to_date)
        message += f"{date} изменения {number} урока {lesson}: {comment}"
    return message


def send_changes(for_date, to_class):
    class_participants = user_db.get_users_by_class(to_class)
    message = get_changes(for_date, to_class)
    Alerts.send_alerts(class_participants, message)


def get_and_send_for_all():
    for c in classes:
        for date in [cur_date(), cur_date(1), cur_date(2)]:
            send_changes(date, c)


if __name__ == '__main__':
    get_and_send_for_all()
