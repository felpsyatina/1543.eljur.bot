import logger
from lessons_db_manip import LessonDbReq
import schedule_parser as sp
import answers_dict as ad
import users_db_parser as ud
from datetime import datetime, timedelta
import eljur_api as ea
import config
import datetime


req = LessonDbReq()
preset = {"devkey": config.secret['eljurapi']['devkey'], "vendor": "1543",
              "password": config.secret['eljurapi']['password'],
              "login": config.secret['eljurapi']['login']}
student = ea.Student(**preset)


def update_schedule():
    req.run(req.add_schedules)
    return


def cur_date(add=0):
    return (datetime.today() + timedelta(days=add)).strftime('%Y%m%d')


def get_schedule(scr, user_id, text):
    schedule = {"Сегодня": req.run(req.get_schedule_by_date, get_class_name_from_text(text.upper()), cur_date()),
                "Завтра": req.run(req.get_schedule_by_date, get_class_name_from_text(text.upper()), cur_date(1))}

    logger.log("user_req", f"current_user_schedule {schedule}")

    answer_string = ""
    for day_date, day_schedule in schedule.items():
        answer_string += f"{day_date.title()}\n"
        for lesson_num, lesson in day_schedule.items():

            for it in range(len(lesson)):
                if lesson[it][9] is not None:
                    lesson[it] = f"{lesson[it][1]} ({lesson[it][9]})"
                    # 2-ой элемент массива lesson[it] - название урока
                    # 9-ый - коммент к уроку
                else:
                    lesson[it] = lesson[it][1]  # 2-ой элемент массива lesson[it] - название урока

            answer_string += f"{lesson_num}. {'/'.join(lesson)}\n"
    return answer_string


def register_new_user(scr, user_id, text):    # регистрация login name surname parallel
    text = text.split()
    try:
        login = text[1]
        name = text[2]
        surname = text[3]
        parallel = text[4]
        return ud.make_new_user(login, parallel, name, surname, scr, user_id)

    except Exception:
        return "Чтобы зарегистрироваться вводите (без кавычек):\n регистрация \"твой логин\" " \
               "\"твое имя\" \"твоя фамилия\" \"твой класс\""


def get_class_name_from_text(text):
    class_name = text.split()[1]
    return class_name


def get_day_and_lesson_and_class_name_from_text(text):
    day = text.split()[3].capitalize()
    lesson = text.split()[1].capitalize()
    class_name = text.split()[5]
    return day, lesson, class_name


def makedate(n):
    s = datetime.datetime.isoformat(n)
    s = s.split(sep='T')
    s = s[0]
    s = s.split(sep='-')
    s = s[0] + s[1] + s[2]
    return s


def get_day_and_class_name_from_text(text):
    t = text.split()
    ind = 0
    class_name = ''
    day = ''
    for i in range(len(t)):
        if t[i] in ['дз', 'домашнее', 'задание', 'домашка']:
            continue
        else:
            ind = i
            break
    else:
        return ['', '']
    now = datetime.datetime.now()
    today = makedate(now)
    tomorrow = makedate(datetime.datetime.fromordinal(datetime.datetime.toordinal(now) + 1))
    yesterday = makedate(datetime.datetime.fromordinal(datetime.datetime.toordinal(now) - 1))
    w = now.weekday()
    mon = datetime.datetime.fromordinal(datetime.datetime.toordinal(now) - w)
    sun = datetime.datetime.fromordinal(datetime.datetime.toordinal(now) - w + 5)
    monday = makedate(mon)
    sunday = makedate(sun)
    week = monday + '-' + sunday
    try:
        class_name = t[ind]
        day = t[ind + 1]
    except Exception:
        return [today, t[ind]]
    class_name = class_name.upper()
    if day == 'сегодня':
        day = today
    elif day == 'завтра':
        day = tomorrow
    elif day == 'вчера':
        day = yesterday
    elif day == 'неделя':
        day = week
    return [day, class_name]



def generate_return(text):
    return {"text": text, "buttons": None}


def send_acc_information(src, user_id, text):
    logger.log("user_req", "request for acc data")
    ans_mes = ud.get_user_by_id(src, user_id)
    if ans_mes is None:
        logger.log("user_req", "user " + str(user_id) + " is not in the database")
        answer_message = "К сожалению вас пока нет в нашей базе данных"
    else:
        answer_message = f"Логин: {ans_mes['login']}\nИмя: {ans_mes['name']}\nФамилия: {ans_mes['surname']}\nПараллель: {ans_mes['parallel']}"
    return answer_message


def cancel_lesson(src, user_id, text):
    logger.log("user_req", "cancelling a lesson")
    day, lesson, class_name = get_day_and_lesson_and_class_name_from_text(text)
    req.make_cancel(class_name, day, lesson)
    return "Урок отменен"


def comment_lesson(src, user_id, text):      # комментарий lesson в day у class_name comment
    logger.log("user_req", "commenting a lesson")
    day, lesson, class_name = get_day_and_lesson_and_class_name_from_text(text)
    comment = " ".join(text.split()[6:])
    return req.get_comment(class_name, day, lesson, comment)


def replace_lesson(src, user_id, text):      # замена lesson в day у class_name another_lesson
    logger.log("user_req", "replacing a lesson")
    day, lesson, class_name = get_day_and_lesson_and_class_name_from_text(text)
    another_lesson = text.split()[6]
    return req.get_replacement(class_name, day, lesson, another_lesson)


def get_hometask(scr, user_id, text):
    logger.log("user_req", "getting hometask")
    day, class_name = get_day_and_class_name_from_text(text)
    r = student.get_hometask(class_name, day)
    logger.log("user_req", "response get: " + str(r['response']))
    r = r['response']
    if r['error'] is not None:
        logger.log("user_req", "error while getting the hometask")
        return "Возникла какая-то ошибка. Возможно скоро мы ее исправим."
    if r['result'] == []:
        return "Вы неправильно ввели класс или дату"
    d = r['result']['days']
    ans = ""
    for info in d.values():
        ans += ("--<" + info['title'] + '>--' + '\n')
        ans += '\n'
        for lesson in info['items']:
            ans += lesson['name']
            if 'grp' in lesson.keys():
                ans += (" группа " + lesson['grp'] + '\n')
            else:
                ans += '\n'
            ans += (lesson['homework']['1']['value'] + '\n')
            try:
                ans += (lesson['files']['file'][0]['link'] + '\n')
            except Exception:
                pass
            ans += "------------\n"
    return ans



def send_commands(src, user_id, text):
    logger.log("user_req", "commands request")
    ans = "Из доступных команд у меня пока есть: расписание <класс вида: число буква>, мой аккаунт"
    return ans


def parse_message_from_user(scr, user_id, text):
    logger.log("user_req", "process request")
    text = text.strip().lower()
    try:
        for key, value in ad.quest.items():
            if key in text:
                needed_function = key_words_to_function[value]
                answer_from_function = needed_function(scr, user_id, text)

                return generate_return(answer_from_function)
        logger.log("user_req", f"Запрос не найден. Запрос: {text}")
        return {"text": "Запроса не найдено :( ", "buttons": None}

    except Exception as err:
        logger.log("user_req", f"Processing error: {err}\n Запрос: {text}")
        return {"text": "Видно не судьба :( ", "buttons": None}


key_words_to_function = {"schedule": get_schedule,
                         "registration": register_new_user,
                         "account": send_acc_information,
                         "cancel": cancel_lesson,
                         "replacement": replace_lesson,
                         "comment": comment_lesson,
                         # "support": support_message,
                         "commands": send_commands,
                         "hometask": get_hometask
                         }


if __name__ == '__main__':
    print(parse_message_from_user("lolka2", "kekka2", "расписание 10в")['text'])
