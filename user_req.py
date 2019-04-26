import logger
import random
from lessons_db_manip import LessonDbReq, student
from users_db_parser import UserDbReq
import answers_dict as ad
from datetime import datetime
from functions import SUBS, classes, cur_date, del_arr_elem, get_word_by_date, make_lined, ROMANS2, SUB_OPT
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


class Menu:
    def __init__(self, user):
        self.user = user

        self.fast_functions = {
            "расписание": self.user.schedule,
            "дз": self.user.homework,
        }

        self.change_status_class = {
            "подписки": Subs,
            "настройка подписок": Opt,
            "настройка расписания": ScheduleOpt
        }

    def buttons(self):
        self.user.answer_buttons = [
            [["Расписание", 1]],
            [["ДЗ", 1]],
            [["Подписки"]],
            [["Настройка подписок"]],
            [["Настройка расписания"]]
        ]
        return self.user.answer_buttons

    def to(self):
        self.user.status = "menu"
        self.user.answer_text = "Ты в главном меню."
        return {
            "text": self.user.answer_text,
            "buttons": self.buttons()
        }

    def parse(self):
        if self.user.text in self.fast_functions:
            function = self.fast_functions[self.user.text]
            return function()

        if self.user.text in self.change_status_class:
            class_ = self.change_status_class[self.user.text]
            another_answer = class_(self.user)

            return another_answer.to()

        ans_buttons = None
        if self.user.is_new:
            return {
                "text": f"Привет {self.user.first}, я Элжур Бот! Я могу выдавать расписание "
                f"(например \"расписание 10в на завтра\") и домашнее задание "
                f"(например \"дз 10в 20190404\"). Если возникнут проблемы, напиши Леше (ссылка на стене группы).",
                "buttons": self.buttons()
            }

        valica_parse = Valica(self.user.text)
        if valica_parse.list_of_dates is not None:
            valica_parse.list_of_dates = [int(d) for d in valica_parse.list_of_dates]  # даты инты пока что

        if valica_parse.type == "schedule":
            return self.user.schedule(list_of_dates=valica_parse.list_of_dates, subs=valica_parse.subs)

        if valica_parse.type == "homework":
            return self.user.homework(list_of_dates=valica_parse.list_of_dates, subs=valica_parse.subs)

        if "стикер" in self.user.text:
            return {
                "text": "Вот тебе стикер!",
                "buttons": ans_buttons,
                "sticker": "random"
            }

        if self.user.attachment.get('attach1_type', None) == "sticker":
            return {
                "text": "Ага, стикер!",
                "buttons": ans_buttons,
                "sticker": 6167
            }

        try:
            for key, value in ad.quest.items():
                if key in self.user.text:
                    needed_function = key_words_to_function[value]
                    answer_from_function = needed_function(self.user.src, self.user.id, self.user.text)

                    return self.user.generate_return(answer_from_function)

            if len(self.user.text.split()) > 7:  # если челик написал целых 7 слов
                return {
                    "text": "Держи в курсе!)",
                    "buttons": None
                }

            logger.log("user_req", f"Запрос не найден. Запрос: {self.user.text}")
            return {"text": "Запроса не найдено :( ", "buttons": ans_buttons}

        except Exception as err:
            logger.log("user_req", f"Processing error: {err}\n Запрос: {self.user.text}")
            return {"text": "Видно не судьба :( ", "buttons": ans_buttons}


class Subs:
    def __init__(self, user):
        self.user = user

        self.fast_functions = [
            {"definer_function": self.define_change, "run_function": self.run_change}
        ]

        self.change_status_class = [
            {"definer_function": self.define_to_menu, "class": Menu}
        ]

    def buttons(self):
        buttons = []

        for row in SUBS:
            if len(row) == 1:
                buttons.append([[row[0], 1]])
                continue

            new_row = []
            for c in row:
                if c in self.user.subs:
                    new_row.append([c, 2])
                else:
                    new_row.append([c, 0])

            buttons.append(new_row)

        self.user.answer_buttons = buttons
        return self.user.answer_buttons

    def to(self):
        self.user.status = "subs"
        subs_classes = list(self.user.subs.keys())
        if subs_classes:
            self.user.answer_text = f"Ты подписан на {', '.join(subs_classes)}"
        else:
            self.user.answer_text = "Ты пока не подписан ни на один из классов."
        return {
            "text": self.user.answer_text,
            "buttons": self.buttons()
        }

    def parse(self):
        for fast_func in self.fast_functions:
            if fast_func["definer_function"]():
                return fast_func["run_function"]()

        for status_class in self.change_status_class:
            if status_class["definer_function"]():
                change_class = status_class["class"](self.user)
                return change_class.to()

        return None

    def define_to_menu(self):
        return self.user.text == "вернуться в меню"

    def define_change(self):
        return self.user.text.upper() in classes

    def run_change(self):
        class_ = self.user.text.upper()

        if class_ in self.user.subs:
            del self.user.subs[class_]

            return {"text": f"Ты отписался от \"{class_}\".",
                    "buttons": self.buttons()}

        else:
            if len(self.user.subs) >= max_subs:
                return {"text": f"Количество подписок не может превышать {max_subs}.",
                        "buttons": self.buttons()}

            self.user.subs[class_] = {}

            return {"text": f"Ты подписался на обновления \"{class_}\".",
                    "buttons": self.buttons()}


class Opt:
    def __init__(self, user):
        self.user = user

        self.fast_functions = [
            {"definer_function": self.define_to_class_options, "run_function": self.to_class_options}
        ]

        self.change_status_class = [
            {"definer_function": self.define_to_menu, "class": Menu},
        ]

    def buttons(self):
        buttons = [[["Вернуться в меню", 1]]]

        for c in self.user.subs.keys():
            buttons.append([[c, 1]])

        self.user.answer_buttons = buttons
        return self.user.answer_buttons

    def to(self):
        self.user.status = "opt"
        subs_classes = list(self.user.subs.keys())
        self.user.answer_text = f"Ты подписан на {', '.join(subs_classes)}"
        return {
            "text": self.user.answer_text,
            "buttons": self.buttons()
        }

    def parse(self):
        for fast_func in self.fast_functions:
            if fast_func["definer_function"]():
                return fast_func["run_function"]()

        for status_class in self.change_status_class:
            if status_class["definer_function"]():
                change_class = status_class["class"](self.user)
                return change_class.to()

        return None

    def define_to_menu(self):
        return self.user.text == "вернуться в меню"

    def define_to_class_options(self):
        return self.user.text.upper() in self.user.subs

    def to_class_options(self):
        self.user.status = f"opt {self.user.text.upper()}"
        answer_class = ClsOpt(self.user)
        return answer_class.to()


class ClsOpt:
    def __init__(self, user):
        self.user = user
        self.cls = self.user.status.split()[1]

        self.fast_functions = [
            {"definer_function": self.define_change, "run_function": self.change_group}
        ]

        self.change_status_class = [
            {"definer_function": self.define_to_menu, "class": Menu}
        ]

    def buttons(self):
        buttons = [[["Вернуться в меню", 1]]]
        lessons = self.user.subs[self.cls]
        class_id = lesson_db.get_class_id(self.cls)
        class_groups = lesson_db.get_class_groups(class_id)

        for lesson, groups in class_groups.items():
            line = []
            for g in groups:
                if g in lessons.get(lesson, []):
                    line.append([f"{self.cls} {lesson} {g}", button_color_by_boolean(True)])
                else:
                    line.append([f"{self.cls} {lesson} {g}", button_color_by_boolean(False)])
            buttons.append(line)

        self.user.answer_buttons = buttons
        return buttons

    def to(self):
        lessons_list = list(self.user.subs[self.cls].keys())
        self.user.answer_text = f"Здесь ты можешь поменять группы этих уроков {', '.join(lessons_list)}"
        return {
            "text": self.user.answer_text,
            "buttons": self.buttons()
        }

    def parse(self):
        for fast_func in self.fast_functions:
            if fast_func["definer_function"]():
                return fast_func["run_function"]()

        for status_class in self.change_status_class:
            if status_class["definer_function"]():
                change_class = status_class["class"](self.user)
                return change_class.to()

        return None

    def define_to_menu(self):
        return self.user.text == "вернуться в меню"

    def define_change(self):
        split_text = self.user.text.split()
        return len(split_text) == 3 and split_text[0].upper() in classes

    def change_group(self):
        user_class, user_lesson, user_group = self.user.normal_text.split()

        if user_class not in self.user.subs:
            return {"text": f"Ты не подписан на этот класс.",
                    "buttons": self.buttons()}

        class_subs = self.user.subs[user_class]
        lesson_subs = class_subs.get(user_lesson, [])

        if user_group in lesson_subs:
            new_lesson_subs = del_arr_elem(lesson_subs, user_group)
            self.user.subs[user_class][user_lesson] = new_lesson_subs

            return {"text": f"Ты отписался от \"{user_class} {user_lesson} {user_group}\".",
                    "buttons": self.buttons()}

        else:
            new_lesson_subs = lesson_subs + [user_group]
            self.user.subs[user_class][user_lesson] = new_lesson_subs

            return {"text": f"Ты подписался на \"{user_class} {user_lesson} {user_group}\".",
                    "buttons": self.buttons()}


class ScheduleOpt:
    def __init__(self, user):
        self.user = user

        self.fast_functions = [
            {"definer_function": self.define_change, "run_function": self.change_option}
        ]

        self.change_status_class = [
            {"definer_function": self.define_to_menu, "class": Menu}
        ]

    def buttons(self):
        buttons = [
            [["Вернуться в меню", 1]],
            [["Учителя", button_color_by_boolean(self.user.schedule_params.add_teacher)]],
            [["Кабинеты", button_color_by_boolean(self.user.schedule_params.add_room)]]
        ]
        row = []
        it = 1
        for word, add in SUB_OPT.items():
            if add in self.user.schedule_params.list_of_adds:
                row.append([word, button_color_by_boolean(True)])
            else:
                row.append([word, button_color_by_boolean(False)])

            it += 1
            if it % 2:
                buttons.append(row)
                row = []

        if row:
            buttons.append(row)

        self.user.answer_buttons = buttons
        return buttons

    def to(self):
        self.user.status = "sch opt"
        self.user.answer_text = f"Здесь ты можешь поменять настройки выдачи расписания."
        return {
            "text": self.user.answer_text,
            "buttons": self.buttons()
        }

    def parse(self):
        for fast_func in self.fast_functions:
            if fast_func["definer_function"]():
                return fast_func["run_function"]()

        for status_class in self.change_status_class:
            if status_class["definer_function"]():
                change_class = status_class["class"](self.user)
                return change_class.to()

        return None

    def define_to_menu(self):
        return self.user.text == "вернуться в меню"

    def define_change(self):
        return self.user.normal_text in SUB_OPT or self.user.text == "учителя" or self.user.text == "кабинеты"

    def change_option(self):
        if self.user.text == "учителя":
            if self.user.schedule_params.add_teacher == 0:
                self.user.schedule_params.add_teacher = 1
                return {
                    "text": f"Теперь тебе видны учителя.",
                    "buttons": self.buttons()
                }
            else:
                self.user.schedule_params.add_teacher = 0
                return {
                    "text": f"Теперь тебе не видны учителя.",
                    "buttons": self.buttons()
                }

        if self.user.text == "кабинеты":
            if self.user.schedule_params.add_room == 0:
                self.user.schedule_params.add_room = 1
                return {
                    "text": f"Теперь тебе видны кабинеты.",
                    "buttons": self.buttons()
                }
            else:
                self.user.schedule_params.add_room = 0
                return {
                    "text": f"Теперь тебе не видны кабинеты.",
                    "buttons": self.buttons()
                }

        if self.user.text.capitalize() in SUB_OPT:
            add = SUB_OPT[self.user.text.capitalize()]
            if add in self.user.schedule_params.list_of_adds:
                self.user.schedule_params.list_of_adds = del_arr_elem(self.user.schedule_params.list_of_adds, add)
                return {
                    "text": f"Теперь тебе не видно расписание на {self.user.text}.",
                    "buttons": self.buttons()
                }

            else:
                self.user.schedule_params.list_of_adds.append(add)
                self.user.schedule_params.list_of_adds.sort()
                return {
                    "text": f"Теперь тебе видно расписание на {self.user.text}.",
                    "buttons": self.buttons()
                }

        return None


class User:
    def __init__(self, user):
        self.id = user['id']
        self.src = user.get('src', 'vk')
        self.normal_text = user['text'].rstrip()
        self.text = user['text'].rstrip().lower()
        self.attachment = user.get('attachment', {})
        self.is_new = False
        self.opt_class = None

        self.answer_buttons = None
        self.answer_text = None

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

        self.class_by_status = [
            {"definer_function": lambda status: status == "menu", "class": Menu},
            {"definer_function": lambda status: status == "subs", "class": Subs},
            {"definer_function": lambda status: status == "opt", "class": Opt},
            {"definer_function": lambda status: (status != "opt" and "opt" in status), "class": ClsOpt},
            {"definer_function": lambda status: status == "sch opt", "class": ScheduleOpt},
        ]

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
        for answer_class in self.class_by_status:
            if answer_class['definer_function'](self.status):
                answer_obj = answer_class['class'](self)
                answer = answer_obj.parse()
                if answer is not None:
                    return answer

        answer_obj = Menu(self)
        return answer_obj.parse()

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

    def help(self):
        text = "Ты можешь общаться со мной кнопками, а можешь просто писать запрос в свободной форме." \
               "Кнопками ты можешь настраивать свой акканунт и делать запросы.\n" \
               "Свободным же запросом ты можешь запросить расписание или домашнее. Примеры таких запросов:\n" \
               "расписание 8Б 9В на завтра и три дня вперед\n" \
               "дз послезавтра 8Б\n" \
               "8Б дз через 3 дня\n" \
               "Пиши так, как хочешь. Прошу прощения, если вас не пойму, я только учусь."
        return {
            "text": text,
            "buttons": None,
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


def button_color_by_boolean(bl=True):
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


def send_sausage(src, user_id, text):
    return {"text": f"Вот твои сосиски!",
            "attach": "photo-177204484_456239027"}


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


if __name__ == '__main__':
    pass
