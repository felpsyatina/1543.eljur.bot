import logger
from lessons_db_manip import LessonDbReq, student
from users_db_parser import UserDbReq
import answers_dict as ad
from datetime import datetime
from functions import SUBS, classes, cur_date, del_arr_elem, get_word_by_date, make_lined, ROMANS2, SUB_OPT, preset
import config
from json import loads as jl, dumps as jd
from valisa import Valica


max_subs = config.params['max_subs']

flag_on_PC = config.params['flag_on_PC']


if flag_on_PC:
    lesson_db = LessonDbReq()
    user_db = UserDbReq()
else:
    lesson_db = LessonDbReq("1543.eljur.bot/1543.eljur.bot.db")
    user_db = UserDbReq("1543.eljur.bot/1543.eljur.bot.db")


class ScheduleInfo:
    def __init__(self, schedule_params):
        self.list_of_adds = [0, 1, 2]
        self.add_teacher = 0
        self.add_room = 0

        if schedule_params is not None:
            params = jl(schedule_params)
            self.list_of_adds = params['list_of_adds']
            self.add_teacher = params['add_teacher']
            self.add_room = params['add_room']

    def list_of_dates(self):
        return [int(cur_date(a)) for a in self.list_of_adds]

    def convert(self):
        ans = {
            "list_of_adds": self.list_of_adds,
            "add_teacher": self.add_teacher,
            "add_room": self.add_room
        }
        return jd(ans)


class HomeworkInfo:
    def __init__(self, schedule_params):
        self.list_of_adds = [0, 1, 2]
        self.add_teacher = 0
        self.add_room = 0

        if schedule_params is not None:
            params = jl(schedule_params)
            self.list_of_adds = params['list_of_adds']
            self.add_teacher = params['add_teacher']
            self.add_room = params['add_room']

    def list_of_dates(self):
        return [cur_date(a) for a in self.list_of_adds]

    def convert(self):
        ans = {
            "list_of_adds": self.list_of_adds,
            "add_teacher": self.add_teacher,
            "add_room": self.add_room
        }
        return jd(ans)


class User:
    def __init__(self, user):
        self.id = user['id']
        self.src = user.get('src', 'vk')
        self.normal_text = user['text'].rstrip()
        self.text = user['text'].rstrip().lower()
        self.attachment = user.get('attachment', {})
        self.is_new = False
        self.opt_class = None

        self.first = user.get('first_name', 'Иван')
        self.last = user.get('last_name', 'Иванов')
        self.sex = user.get('sex', 0)

        info = user_db.get_user_info(self.id, self.src)
        if info is None:
            user_db.add_user(self.first, self.last, self.id, self.src)
            info = user_db.get_user_info(self.id, self.src)
            self.is_new = True

        self.subs = info.get('subs', {})
        self.status = info.get('status', 'menu')

        self.schedule_params = ScheduleInfo(info.get('schedule_params', None))
        self.homework_params = HomeworkInfo(info.get('homework_params', None))

        if len(self.status.split()) > 1 and self.status.split()[1] in self.subs:
            self.opt_class = self.status.split()[1]
            self.status = "cls_opt"

        self.parse_functions = {
            "menu": self.parse_menu,
            "subs": self.parse_subs,
            "opt": self.parse_opt,
            "sub_opt": self.parse_sub_opt,
            "cls_opt": self.parse_class_opt
        }

        self.fast_functions = {
            "расписание": self.schedule,
            "дз": self.homework,
            "подписки": self.to_subs,
            "настройка подписок": self.to_opt,
            "настройка расписания": self.to_sub_opt
        }
        logger.log("user_req", f"User: user {self.first} {self.last} created")

    def update_db(self):
        changes = {
            'subs': self.subs,
            'status': self.status,
            'schedule_params': self.schedule_params.convert(),
            'homework_params': self.homework_params.convert()
        }
        user_db.update_user(changes, self.id, self.src)

    @staticmethod
    def generate_return(text):
        if type(text) == str:
            return {"text": text, "buttons": None}
        return text

    def parse_message(self):
        if self.status not in self.parse_functions:
            self.status = "menu"

        my_function = self.parse_functions[self.status]
        ans = my_function()

        if ans is not None:
            return ans
        return self.parse_menu()

    def parse_menu(self):
        if self.text in self.fast_functions:
            function = self.fast_functions[self.text]
            return function()

        ans_buttons = None
        if self.is_new:
            return {
                "text": f"Привет {self.first}, я Элжур Бот! Я могу выдавать расписание "
                f"(например \"расписание 10в на завтра\") и домашнее задание "
                f"(например \"дз 10в 20190404\"). Если возникнут проблемы, напиши Леше (ссылка на стене группы).",
                "buttons": menu_buttons
            }

        valica_parse = Valica(self.text)
        valica_parse.list_of_dates = [int(d) for d in valica_parse.list_of_dates]  # даты инты пока что

        if valica_parse.type == "schedule":
            return self.schedule(list_of_dates=valica_parse.list_of_dates, subs=valica_parse.subs)

        if valica_parse.type == "homework":
            return self.homework(list_of_dates=valica_parse.list_of_dates, subs=valica_parse.subs)

        if self.attachment.get('attach1_type', None) == "sticker":
            return {
                "text": "Ага, стикер!",
                "buttons": ans_buttons,
                "attach": "doc-165897409_472977896",
            }

        try:
            for key, value in ad.quest.items():
                if key in self.text:
                    needed_function = key_words_to_function[value]
                    answer_from_function = needed_function(self.src, self.id, self.text)

                    return self.generate_return(answer_from_function)
                
            if len(self.text.split()) > 7:  # если челик написал целых 7 слов
                return {
                    "text": "Держи в курсе!)",
                    "buttons": None
                }

            logger.log("user_req", f"Запрос не найден. Запрос: {self.text}")
            return {"text": "Запроса не найдено :( ", "buttons": ans_buttons}

        except Exception as err:
            logger.log("user_req", f"Processing error: {err}\n Запрос: {self.text}")
            return {"text": "Видно не судьба :( ", "buttons": ans_buttons}

    def parse_subs(self):
        if self.text == "вернуться в меню":
            return self.to_menu()

        if self.text.upper() in classes:
            return self.change_sub()

        return None

    def parse_opt(self):
        if self.text == "вернуться в меню":
            return self.to_menu()

        return self.to_class_opt()

    def parse_class_opt(self):
        self.status = f"opt {self.opt_class}"

        if self.text == "вернуться в меню":
            return self.to_menu()

        if is_change_grp(self.text):
            return self.change_grp()

        return None

    def parse_sub_opt(self):
        if self.text == "вернуться в меню":
            return self.to_menu()

        return self.change_sch_opt()

    def lessons_parse(self, lessons, _homework):
        if len(lessons) == 0:
            return ""

        num = lessons[0]['number']

        if len(lessons) == 1:
            lesson = lessons[0]
            name = lesson['name']

            _room = self.schedule_params.add_room and lesson['room'] is not None
            _teacher = self.schedule_params.add_teacher and lesson['teacher'] is not None
            _homework = _homework and lesson['homework'] is not None
            _any = _homework or _teacher or _room

            ans = f"{num}. {name}\n"
            if _room:
                ans += f"• Кабинет: {lesson['room']}\n"

            if _teacher:
                ans += f"• Учитель: {lesson['teacher']}\n"

            if _homework:
                ans += f"• Домашнее задание: \n{lesson['homework']}\n"

            if lesson['comment'] is not None:
                ans += f"Комментарий: ({lesson['comment']})\n"

            if _any:
                ans += "\n"

            return ans

        if not (_homework or self.schedule_params.add_teacher or self.schedule_params.add_room):
            return f"{num}. {'/'.join([lesson['name'] for lesson in lessons])}\n"

        ans = f"{num}. "
        for it in range(len(lessons)):
            lesson = lessons[it]
            name = lesson['name']

            _room = self.schedule_params.add_room and lesson['room'] is not None
            _teacher = self.schedule_params.add_teacher and lesson['teacher'] is not None
            _homework = _homework and lesson['homework'] is not None
            _any = _homework or _teacher or _room

            ans += f"{it + 1}) {name}\n"

            if _room and lesson['room'] is not None:
                ans += f"• Кабинет: {lesson['room']}\n"

            if _teacher and lesson['teacher'] is not None:
                ans += f"• Учитель: {lesson['teacher']}\n"

            if _homework and lesson['homework'] is not None:
                ans += f"• Домашнее задание: \n{lesson['homework']}\n"

            if lesson['comment'] is not None:
                ans += f"• Комментарий: ({lesson['comment']})\n"

        ans += "\n"

        return ans

    def lessons_good(self, lessons, class_):
        ans = []
        for lesson in lessons:
            if lesson['grp'] is None:
                ans.append(lesson)
                continue

            if lesson['grp'] in self.subs.get(class_, {}):
                ans.append(lesson)

        if ans:
            return ans
        return lessons

    def day_schedule(self, class_, date, _homework):
        schedule = lesson_db.get_schedule(class_, date)
        answer_arr = []

        for num, lessons in schedule.items():
            user_lessons = self.lessons_good(lessons, class_)
            str_lessons = self.lessons_parse(user_lessons, _homework)

            answer_arr.append(str_lessons)

        return "".join(answer_arr)

    def schedule(self, list_of_dates=None, subs=None):
        logger.log("user_req", f"getting schedule for {self.first} {self.last}")

        if subs is None:
            subs = self.subs

        if not subs:
            return {
                "text": "Ты не подписан ни на один из классов. Чтобы подписаться, нажми на \"подписки\"."
            }

        if list_of_dates is None:
            list_of_dates = self.schedule_params.list_of_dates()

        answer_arr = []

        for c in subs.keys():
            answer_arr.append(f"Класс {c}:\n")
            it = 1
            for d in list_of_dates:
                answer_arr.append(f"{ROMANS2[it]}. {get_word_by_date(d)}:")
                day_schedule = self.day_schedule(c, d, 0)
                if day_schedule:
                    answer_arr.append(day_schedule)
                else:
                    answer_arr.append("Уроков (в моей базе) нет.\n")
                it += 1

        return self.generate_return("\n".join(answer_arr))

    def homework(self, list_of_dates=None, subs=None):
        logger.log("user_req", f"getting schedule for {self.first} {self.last}")

        if subs is None:
            subs = self.subs

        if not subs:
            return {
                "text": "Ты не подписан ни на один из классов. Чтобы подписаться, нажми на \"подписки\"."
            }

        if list_of_dates is None:
            list_of_dates = self.schedule_params.list_of_dates()

        answer_arr = []

        for c in self.subs.keys():
            this_class_homework = ""
            this_class_homework += f"Класс {c}:\n"
            it = 1
            for d in list_of_dates:
                this_class_homework += f"{ROMANS2[it]}. {get_word_by_date(d)}:"
                day_schedule = self.day_schedule(c, d, 1)
                if day_schedule:
                    this_class_homework += day_schedule
                else:
                    this_class_homework += "Уроков (в моей базе) нет.\n"
                it += 1

            answer_arr.append(this_class_homework)

        return {
            "text": answer_arr,
            "buttons": None
        }

    def gen_subs_but(self):
        buttons = []

        for row in SUBS:
            if len(row) == 1:
                buttons.append([[row[0], 1]])
                continue

            new_row = []
            for c in row:
                if c in self.subs:
                    new_row.append([c, 2])
                else:
                    new_row.append([c, 0])

            buttons.append(new_row)

        return buttons

    def gen_cls_opt_but(self):
        buttons = [[["Вернуться в меню", 1]]]
        c = self.opt_class
        lessons = self.subs[c]
        class_id = lesson_db.get_class_id(c)
        class_groups = lesson_db.get_class_groups(class_id)

        for lesson, groups in class_groups.items():
            line = []
            for g in groups:
                if g in lessons.get(lesson, []):
                    line.append([f"{c} {lesson} {g}", color(True)])
                else:
                    line.append([f"{c} {lesson} {g}", color(False)])
            buttons.append(line)

        return buttons

    def gen_sch_opt_but(self):
        buttons = [
            [["Вернуться в меню", 1]],
            [["Учителя", color(self.schedule_params.add_teacher)]],
            [["Кабинеты", color(self.schedule_params.add_room)]]
        ]
        row = []
        it = 1
        for word, add in SUB_OPT.items():
            if add in self.schedule_params.list_of_adds:
                row.append([word, color(True)])
            else:
                row.append([word, color(False)])

            it += 1
            if it % 2:
                buttons.append(row)
                row = []

        if row:
            buttons.append(row)

        return buttons

    def gen_opt_but(self):
        buttons = [[["Вернуться в меню", 1]]]

        for c in self.subs.keys():
            buttons.append([[c, 1]])

        return buttons

    def to_subs(self):
        self.status = "subs"

        user_classes = self.subs.keys()
        if user_classes:
            return {"text": f"Классы, на которые ты подписан: {' '.join(user_classes)}.",
                    "buttons": self.gen_subs_but()}

        return {"text": f"У тебя пока нет подписок на классы.",
                "buttons": self.gen_subs_but()}

    def to_opt(self):
        user_subs = list(self.subs.keys())

        self.status = "opt"

        return {"text": f"Ты подписан на {' '.join(user_subs)}.",
                "buttons": self.gen_opt_but()}

    def to_menu(self):
        self.status = "menu"

        return {"text": f"Ты в главном меню.",
                "buttons": menu_buttons}

    def to_sub_opt(self):
        self.status = "sub_opt"

        return {"text": f"Здесь ты можешь поменять отображение расписания.",
                "buttons": self.gen_sch_opt_but()}

    def to_class_opt(self):
        c = self.text.upper()

        if c not in classes:
            return None

        self.status = f"opt {c}"
        self.opt_class = c

        return {"text": f"Здесь ты можешь поменять группы {c}.",
                "buttons": self.gen_cls_opt_but()}

    def change_grp(self):
        user_class, user_lesson, user_group = self.normal_text.split()
        print(user_group)

        if user_class not in self.subs:
            return {"text": f"Ты не подписан на этот класс.",
                    "buttons": self.gen_cls_opt_but()}

        class_subs = self.subs[user_class]
        lesson_subs = class_subs.get(user_lesson, [])

        if user_group in lesson_subs:
            new_lesson_subs = del_arr_elem(lesson_subs, user_group)
            self.subs[user_class][user_lesson] = new_lesson_subs

            return {"text": f"Ты отписался от \"{user_class} {user_lesson} {user_group}\".",
                    "buttons": self.gen_cls_opt_but()}

        else:
            new_lesson_subs = lesson_subs + [user_group]
            self.subs[user_class][user_lesson] = new_lesson_subs

            return {"text": f"Ты подписался на \"{user_class} {user_lesson} {user_group}\".",
                    "buttons": self.gen_cls_opt_but()}

    def change_sub(self):
        c = self.text.upper()

        if c in self.subs:
            del self.subs[c]

            return {"text": f"Ты отписался от \"{c}\".",
                    "buttons": self.gen_subs_but()}

        else:
            if len(self.subs) >= max_subs:
                return {"text": f"Количество подписок не может превышать {max_subs}.",
                        "buttons": self.gen_subs_but()}

            self.subs[c] = {}

            return {"text": f"Ты подписался на обновления \"{c}\".",
                    "buttons": self.gen_subs_but()}

    def change_sch_opt(self):
        if self.text == "учителя":
            if self.schedule_params.add_teacher == 0:
                self.schedule_params.add_teacher = 1
                return {
                    "text": f"Теперь тебе видны учителя.",
                    "buttons": self.gen_sch_opt_but()
                }
            else:
                self.schedule_params.add_teacher = 0
                return {
                    "text": f"Теперь тебе не видны учителя.",
                    "buttons": self.gen_sch_opt_but()
                }

        if self.text == "кабинеты":
            if self.schedule_params.add_room == 0:
                self.schedule_params.add_room = 1
                return {
                    "text": f"Теперь тебе видны кабинеты.",
                    "buttons": self.gen_sch_opt_but()
                }
            else:
                self.schedule_params.add_room = 0
                return {
                    "text": f"Теперь тебе не видны кабинеты.",
                    "buttons": self.gen_sch_opt_but()
                }

        if self.text.capitalize() in SUB_OPT:
            add = SUB_OPT[self.text.capitalize()]
            if add in self.schedule_params.list_of_adds:
                self.schedule_params.list_of_adds = del_arr_elem(self.schedule_params.list_of_adds, add)
                return {
                    "text": f"Теперь тебе не видно расписание на {self.text}.",
                    "buttons": self.gen_sch_opt_but()
                }

            else:
                self.schedule_params.list_of_adds.append(add)
                self.schedule_params.list_of_adds.sort()
                return {
                    "text": f"Теперь тебе видно расписание на {self.text}.",
                    "buttons": self.gen_sch_opt_but()
                }

        return None


def update_schedule():
    lesson_db.add_schedules()
    return


def color(bl=True):
    if bl:
        return 2
    else:
        return 0


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


def get_schedule_from_subs(class_name, user_subs, list_of_dates, a_room=False, a_teacher=False, a_homework=False):
    if list_of_dates is None:
        list_of_dates = [cur_date()]

    answer_string = ""
    for date in list_of_dates:
        temp = lesson_db.get_schedule_by_subs(class_name, date, user_subs)

        if not temp:
            lesson_db.add_schedule(class_name, date)

        day_schedule = lesson_db.get_schedule_by_subs(class_name, date, user_subs)

        answer_string += f"{make_lined(get_word_by_date(date), symbol='̲')}:\n\n"

        if not day_schedule:
            answer_string += f"Уроков (в моей базе) нет.\n"
            continue

        for lesson_num, lesson in day_schedule.items():
            tmp = []
            for it in range(len(lesson)):
                tmp.append(f"{lesson[it]['name']}")
                if a_homework or a_room or a_teacher:
                    tmp[it] += "\n"

                if a_room and lesson[it]['room'] is not None:
                    tmp[it] += f"Кабинет: {lesson[it]['room']}\n"

                if a_teacher and lesson[it]['teacher'] is not None:
                    tmp[it] += f"Учитель: {lesson[it]['teacher']}\n"

                if a_homework and lesson[it]['homework'] is not None:
                    tmp[it] += f"Домашнее задание: \n{lesson[it]['homework']}\n"

                if lesson[it]['comment'] is not None:
                    tmp[it] += f"Комментарий: ({lesson[it]['comment']})\n"

            if a_homework or a_room or a_teacher:
                answer_string += "\n"

            answer_string += f"{lesson_num}. {'/'.join(tmp).rstrip()}.\n"
        answer_string += '\n'

    return answer_string


def get_schedule(src, user_id, text):
    logger.log("user_req", f"getting schedule in {text}")

    class_name = get_class_name_from_text(text.upper())
    dates = [cur_date(), cur_date(1)]

    return get_schedule_from_class(class_name, dates, add_room=True, add_teacher=True)


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


def send_acc_information(src, user_id, text):
    logger.log("user_req", "request for acc data")
    ans_mes = user_db.get_user_info(user_id, src)

    if ans_mes is None:
        logger.log("user_req", "user " + str(user_id) + " is not in the database")
        answer_message = "К сожалению вас пока нет в нашей базе данных"
    else:
        answer_message = f"Имя: {ans_mes['first_name']}\nФамилия: {ans_mes['last_name']}\n" \
            f"Класс: {ans_mes['subs'].keys()}\n vk_id: {ans_mes['vk_id']}"
    return answer_message


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
    logger.log("user_req", f"getting hometask of {text}")
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


def send_commands(src, user_id, text):
    logger.log("user_req", "commands request")
    ans = "Из доступных команд у меня пока есть: расписание <класс вида: число буква>, мой аккаунт"
    return ans


def fast_schedule(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    ans_msg = ""
    user_subs = info['subs']

    if len(user_subs) == 0:
        return {"text": "Вы не подписаны ни на один из классов.",
                "buttons": menu_buttons}

    list_of_dates = [cur_date(), cur_date(1), cur_date(2)]

    for c, subs in user_subs.items():
        ans_msg += f"\nКласс {c}:\n"
        ans_msg += get_schedule_from_subs(c, subs, list_of_dates)

    return {
        "text": ans_msg,
        "buttons": menu_buttons
    }


def fast_hometask(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    ans_msg = ""
    user_subs = info['subs']

    if len(user_subs) == 0:
        return {"text": "Вы не подписаны ни на один из классов.",
                "buttons": menu_buttons}

    list_of_dates = [cur_date(), cur_date(1), cur_date(2)]

    for c, subs in user_subs.items():
        ans_msg += f"\nКласс {c}:\n"
        ans_msg += get_schedule_from_subs(c, subs, list_of_dates, a_homework=True)

    return {"text": ans_msg,
            "buttons": menu_buttons}


def gen_subs_but(src, user_id, text):
    info = user_db.get_user_info(user_id, src)
    user_subs = info['subs'].keys()

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
            for g in groups:
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
    user_lesson = user_lesson.capitalize()
    user_group = user_group.capitalize()

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


def send_sausage(src, user_id, text):
    return {"text": f"Вот твои сосиски!",
            "attach": "photo-177204484_456239027"}


def parse_menu(src, user_id, text):
    if text in fast_query.keys():
        function = fast_query[text]
        return function(src, user_id, text)

    try:
        for key, value in ad.quest.items():
            if key in text:
                needed_function = key_words_to_function[value]
                answer_from_function = needed_function(src, user_id, text)

                return {
                    "text": answer_from_function,
                    "buttons": None
                }
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


def process_message_from_user(user_dict):
    logger.log("user_req", "process request")

    user = User(user_dict)

    answer = user.parse_message()
    user.update_db()

    return answer


def parse_message_from_user(ud):
    logger.log(
        "request_save",
        f"Request\n {ud['src']} {ud['id']} {ud['first_name']} {ud['last_name']}\n{ud['text']}"
    )
    logger.log("textofrequest_save", ud['text'])
    res = process_message_from_user(ud)
    logger.log("request_save", f"Answer for {ud['src']} {ud['id']}\n {res.get('text', '')}")
    return res


key_words_to_function = {
    "schedule": get_schedule,
    "account": send_acc_information,
    "replacement": replace_lesson,
    "comment": comment_lesson,
    # "support": support_message,
    "commands": send_commands,
    "hometask": get_hometask,
    "sausage": send_sausage
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

menu_buttons = [[["Расписание", 1]], [["ДЗ", 1]], [["Подписки"]], [["Настройка подписок"]], [["Настройка расписания"]]]

if __name__ == '__main__':
    pass
