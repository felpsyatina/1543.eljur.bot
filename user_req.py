import logger
from lessons_db_manip import LessonDbReq
from users_db_parser import UserDbReq
import answers_dict as ad
from datetime import datetime
from datetime import date as st_date
from functions import SUBS, classes, cur_date, student, del_arr_elem
import config

lesson_db = LessonDbReq()
user_db = UserDbReq()

max_subs = config.params['max_subs']


def update_schedule():
    lesson_db.add_schedules()
    return


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


def get_schedule_from_class(class_name, list_of_dates=None, add_room=False, add_teacher=False):
    if list_of_dates is None:
        list_of_dates = [cur_date()]

    answer_string = ""
    for date in list_of_dates:

        temp = lesson_db.get_schedule(class_name, date)

        if not temp:
            lesson_db.add_schedule(class_name, date)

        day_schedule = lesson_db.get_schedule(class_name, date)

        answer_string += f"{get_word_by_date(date)}:\n"

        if not day_schedule:
            answer_string += f"Уроков (в моей базе) нет.\n"
            continue

        for lesson_num, lesson in day_schedule.items():
            tmp = []
            for it in range(len(lesson)):
                tmp.append(f"{lesson[it]['name']}")

                if add_room and lesson[it]['room'] is not None:
                    tmp[it] += f", кабинет: {lesson[it]['room']}"

                if add_teacher and lesson[it]['teacher'] is not None:
                    tmp[it] += f", учитель: {lesson[it]['teacher']}"

                if lesson[it]['comment'] is not None:
                    tmp[it] += f" ({lesson[it]['comment']})"

            answer_string += f"{lesson_num}. {'/'.join(tmp)}.\n"
    return answer_string


def get_schedule(src, user_id, text):
    logger.log("user_req", f"getting schedule in {text}")

    class_name = get_class_name_from_text(text.upper())
    dates = [cur_date(), cur_date(1)]

    return get_schedule_from_class(class_name, dates, add_room=True, add_teacher=True)


def register_new_user(src, user_id, text):  # регистрация login name surname parallel
    text = text.split()
    if len(text) >= 5:
        login = text[1]
        name = text[2]
        surname = text[3]
        parallel = text[4]
        if src == "vk":
            return user_db.add_user(name, surname, user_id, src)
        return user_db.add_user(name, surname, user_id, src)

    else:
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


def make_date(n):
    s = datetime.isoformat(n)
    s = s.split(sep='T')
    s = s[0]
    s = s.split(sep='-')
    s = s[0] + s[1] + s[2]
    return s


def get_day_and_class_name_from_text(text):
    t = text.split()
    for i in range(len(t)):
        if t[i] in ['дз', 'домашнее', 'задание', 'домашка']:
            continue
        else:
            ind = i
            break
    else:
        return ['', '']
    now = datetime.now()
    today = make_date(now)
    tomorrow = make_date(datetime.fromordinal(datetime.toordinal(now) + 1))
    yesterday = make_date(datetime.fromordinal(datetime.toordinal(now) - 1))
    w = now.weekday()
    mon = datetime.fromordinal(datetime.toordinal(now) - w)
    sun = datetime.fromordinal(datetime.toordinal(now) - w + 5)
    monday = make_date(mon)
    sunday = make_date(sun)
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
    ans_mes = user_db.get_user_info(user_id, src)

    if ans_mes is None:
        logger.log("user_req", "user " + str(user_id) + " is not in the database")
        answer_message = "К сожалению вас пока нет в нашей базе данных"
    else:
        answer_message = f"Имя: {ans_mes['first_name']}\nФамилия: {ans_mes['last_name']}\nКласс: {ans_mes['class']}\n" \
            f"Класс: {ans_mes['class']}\n vk_id: {ans_mes['vk_id']}"
    return answer_message


def cancel_lesson(src, user_id, text):
    logger.log("user_req", "cancelling a lesson")
    day, lesson, class_name = get_day_and_lesson_and_class_name_from_text(text)
    lesson_db.make_cancel(class_name, day, lesson)
    return "Урок отменен"


def comment_lesson(src, user_id, text):  # комментарий lesson в day у class_name comment
    logger.log("user_req", "commenting a lesson")
    day, lesson, class_name = get_day_and_lesson_and_class_name_from_text(text)
    comment = " ".join(text.split()[6:])
    return lesson_db.get_comment(class_name, day, lesson, comment)


def replace_lesson(src, user_id, text):  # замена lesson в day у class_name another_lesson
    logger.log("user_req", "replacing a lesson")
    day, lesson, class_name = get_day_and_lesson_and_class_name_from_text(text)
    another_lesson = text.split()[6]
    return lesson_db.get_replacement(class_name, day, lesson, another_lesson)


def get_hometask(src, user_id, text):
    logger.log("user_req", "getting hometask")
    day, class_name = get_day_and_class_name_from_text(text)
    r = student.get_hometask(class_name, day)
    logger.log("user_req", "response get: " + str(r))
    if not r:
        return "Вы неправильно ввели класс или дату, или на этот(и) день(и) расписания в eljur нет."
    d = r['days']
    ans = ""
    for info in d.values():
        ans += '\n'
        ans += ("--<" + info['title'] + '>--' + '\n')
        for lesson in info['items']:
            ans += lesson['name']
            if 'grp' in lesson.keys():
                ans += (" группа " + lesson['grp'] + '\n')
            else:
                ans += '\n'
            if 'homework' in lesson.keys():
                ans += (lesson['homework']['1']['value'] + '\n')
            try:
                ans += (lesson['files']['file'][0]['link'] + '\n')
            except Exception:
                pass
            ans += "-" * 20 + "\n"
    return ans


def user_reg0(src, user_id, text):
    user_db.update_user({"status": "reg1"}, user_id, src)

    return {"text": "Выберите класс.\nЕсли хотите продолжить без введения класса, нажмите \"Отмена\"",
            "buttons": [[5, 6, 7, 8], [9, 10, 11], ["Отмена"]]}


def user_reg1(src, user_id, text):
    if text == "отмена":
        user_db.update_user({"class": "null", "status": "reg0"}, user_id, src)

        return user_reg0(src, user_id, text)
    if text in ["5", "6", "7", "8", "9", "10", "11"]:
        user_db.update_user({"class": text, "status": "reg2"}, user_id, src)

        return {"text": "Выберите букву класса.\nЕсли хотите продолжить без введения класса, нажмите \"Отмена\"",
                "buttons": [["А", "Б", "В", "Г"], ["Отмена"]]}
    return {"text": "Выберите класс.\nЕсли хотите продолжить без введения класса, нажмите \"Отмена\"",
            "buttons": [[5, 6, 7, 8], [9, 10, 11], ["Отмена"]]}


def user_reg2(src, user_id, text):
    if text == "отмена":
        user_db.update_user({"class": "null", "status": "reg0"}, user_id, src)
        return user_reg0(src, user_id, text)
    if text in ["а", "б", "в", "г"]:
        info = user_db.get_user_info(user_id, src)
        user_db.update_user({"class": info['class'] + text, "status": "menu"}, user_id, src)

        return {"text": "Теперь вы можете узнавать расписание или дз, нажимая лишь на одну кнопку. \n"
                        "Вы можете сбросить класс, нажав \"разлогиниться\".",
                "buttons": menu_buttons}
    return {"text": "Выберите букву класса.\nЕсли хотите продолжить без введения класса, нажмите \"Отмена\"",
            "buttons": [["А", "Б", "В", "Г"], ["Отмена"]]}


def user_sch0(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    user_db.update_user({"class": info['class'], "status": "rasp1"}, user_id, src)
    return {"text": "Выберите время",
            "buttons": [["Сегодня"], ["Завтра"], ["Неделя"], ["Отмена"]]}


def send_commands(src, user_id, text):
    logger.log("user_req", "commands request")
    ans = "Из доступных команд у меня пока есть: расписание <класс вида: число буква>, мой аккаунт"
    return ans


def fast_schedule(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    ans_msg = ""
    user_subs = info['subs'].keys()

    if len(user_subs) == 0:
        return {"text": "Вы не подписаны ни на один из классов.",
                "buttons": menu_buttons}

    list_of_dates = [cur_date(), cur_date(1), cur_date(2)]

    for c in user_subs:
        ans_msg += f"\nКласс {c}:\n"
        ans_msg += get_schedule_from_class(c, list_of_dates=list_of_dates)

    return {
        "text": ans_msg,
        "buttons": menu_buttons
    }


def fast_hometask(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    ans_msg = ""
    user_subs = info['subs'].keys()

    if len(user_subs) == 0:
        return {"text": "Вы не подписаны ни на один из классов.",
                "buttons": menu_buttons}

    for c in user_subs:
        ans_msg += f"\nКласс {c}:\n"
        ans_msg += get_hometask(src, user_id, c + " неделя")

    return {"text": ans_msg,
            "buttons": menu_buttons}


def cancel_menu(src, user_id, text):
    user_db.update_user({"class": "null", "status": "reg0"}, user_id, src)
    return user_reg0(src, user_id, text)


def gen_subs_but(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    user_subs = list(info['subs'].keys())

    buttons = []

    for row in SUBS:
        if len(row) == 1:
            buttons.append([[row[0], 1]])
            continue

        new_row = []
        for c in row:
            if c in user_subs:
                new_row.append([c, 2])
            else:
                new_row.append([c, 0])

        buttons.append(new_row)

    return buttons


def gen_opt_but(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    subs = info['subs']

    buttons = [[["Вернуться в меню", 1]]]
    for c, lessons in subs.items():
        class_id = lesson_db.get_class_id(c)
        class_groups = lesson_db.get_class_groups(class_id)

        for lesson, groups in class_groups.items():
            line = []
            lesson = lesson.lower()
            for g in groups:
                g = g.lower()
                if g in lessons.get(lesson, []):
                    line.append([f"{c} {lesson} {g}", 2])
                else:
                    line.append([f"{c} {lesson} {g}", 0])
            buttons.append(line)

    return buttons


def to_subs(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    user_subs = list(info['subs'].keys())

    user_db.update_user({'status': 'subs'}, user_id, src)

    if user_subs:
        return {"text": f"Классы, на которые ты подписан: {' '.join(user_subs)}.",
                "buttons": gen_subs_but(src, user_id, text)}

    return {"text": f"У тебя пока нет подписок на классы.",
            "buttons": gen_subs_but(src, user_id, text)}


def change_sub(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    user_subs = info['subs']
    c = text.upper()

    if c in user_subs.keys():
        new_user_subs = user_subs
        del new_user_subs[c]
        user_db.update_user({'subs': new_user_subs}, user_id, src)

        return {"text": f"Ты отписался от \"{c}\".",
                "buttons": gen_subs_but(src, user_id, text)}

    else:
        if len(user_subs) >= max_subs:
            return {"text": f"Количество подписок не может превышать {max_subs}.",
                    "buttons": gen_subs_but(src, user_id, text)}

        new_user_subs = user_subs
        new_user_subs[c] = {}
        user_db.update_user({'subs': new_user_subs}, user_id, src)

        return {"text": f"Ты подписался на обновления \"{c}\".",
                "buttons": gen_subs_but(src, user_id, text)}


def is_change_grp(text):
    text = text.split()
    if len(text) != 3:
        return False

    if text[0].upper() not in classes:
        return False

    return True


def change_grp(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    user_subs = info['subs']
    user_class, user_lesson, user_group = text.split()
    user_class = user_class.upper()

    if user_class not in user_subs:
        return {"text": f"Ты не подписан на этот класс.",
                "buttons": gen_opt_but(src, user_id, text)}

    class_subs = user_subs[user_class]
    lesson_subs = class_subs.get(user_lesson, [])

    if user_group in lesson_subs:
        new_lesson_subs = del_arr_elem(lesson_subs, user_group)
        user_subs[user_class][user_lesson] = new_lesson_subs

        user_db.update_user({'subs': user_subs}, user_id, src)

        return {"text": f"Ты отписался от \"{user_class} {user_lesson} {user_group}\".",
                "buttons": gen_opt_but(src, user_id, text)}

    else:
        new_lesson_subs = lesson_subs + [user_group]
        user_subs[user_class][user_lesson] = new_lesson_subs

        user_db.update_user({'subs': user_subs}, user_id, src)

        return {"text": f"Ты подписался на \"{user_class} {user_lesson} {user_group}\".",
                "buttons": gen_opt_but(src, user_id, text)}


def to_menu(src, user_id, text):
    user_db.update_user({'status': 'menu'}, user_id, src)

    return {"text": f"Ты в главном меню.",
            "buttons": menu_buttons}


def to_opt(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    user_subs = list(info['subs'].keys())

    if len(user_subs) >= 2:
        return {"text": f"Пока не поддерживается управление подписками сразу двух классов.",
                "buttons": menu_buttons}

    user_db.update_user({'status': 'opt'}, user_id, src)

    return {"text": f"Ты подписан на {user_subs[0]}.",
            "buttons": gen_opt_but(src, user_id, text)}


def parse_menu(src, user_id, text):
    if text in fast_query.keys():
        function = fast_query[text]
        return function(src, user_id, text)

    try:
        for key, value in ad.quest.items():
            if key in text:
                needed_function = key_words_to_function[value]
                answer_from_function = needed_function(src, user_id, text)

                return generate_return(answer_from_function)
        logger.log("user_req", f"Запрос не найден. Запрос: {text}")
        return {"text": "Запроса не найдено :( ", "buttons": None}

    except Exception as err:
        logger.log("user_req", f"Processing error: {err}\n Запрос: {text}")
        return {"text": "Видно не судьба :( ", "buttons": None}


def parse_subs(src, user_id, text):
    if text == "вернуться в меню":
        return to_menu(src, user_id, text)

    if text.upper() in classes:
        return change_sub(src, user_id, text)

    return None


def parse_opt(src, user_id, text):
    if text == "вернуться в меню":
        return to_menu(src, user_id, text)

    if is_change_grp(text):
        return change_grp(src, user_id, text)

    return None


def process_message_from_user(src, user_id, text, name):
    logger.log("user_req", "process request")
    text = text.strip().lower()

    if user_db.get_user_info(user_id, src) is None:
        user_db.add_user(name['first_name'], name['last_name'], user_id, src)

    if user_db.get_user_info(user_id, src)['subs'] is None:
        user_db.update_user({'subs': ""}, user_id, src)

    logger.log("user_req", "requesting info")
    info = user_db.get_user_info(user_id, src)

    if info['status'] not in parse_functions.keys():
        user_db.update_user({'status': 'menu'}, user_id, src)
        info = user_db.get_user_info(user_id, src)

    parse_func = parse_functions[info['status']]

    answer = parse_func(src, user_id, text)
    if answer is not None:
        return answer

    return parse_menu(src, user_id, text)


def parse_message_from_user(src, user_id, text, name):
    logger.log("request_save", "Request\n" + src + " " + str(user_id) + " " + str(name) + "\n" + text)
    logger.log("textofrequest_save", text)
    res = process_message_from_user(src, user_id, text, name)
    logger.log("request_save", "Answer for " + src + " " + str(user_id) + "\n" + res.get("text", ""))
    return res


key_words_to_function = {
    "schedule": get_schedule,
    "registration": register_new_user,
    "account": send_acc_information,
    "cancel": cancel_lesson,
    "replacement": replace_lesson,
    "comment": comment_lesson,
    # "support": support_message,
    "commands": send_commands,
    "hometask": get_hometask
}

parse_functions = {
    "menu": parse_menu,
    "subs": parse_subs,
    "opt": parse_opt
}

fast_query = {
    "расписание": fast_schedule,
    "дз": fast_hometask,
    "подписки": to_subs,
    "настройка подписок": to_opt
}

menu_buttons = [[["Расписание", 1]], [["ДЗ", 1]], [["Подписки"]], [["Настройка подписок"]]]

if __name__ == '__main__':
    pass
