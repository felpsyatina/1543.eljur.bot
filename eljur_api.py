import logger
import json
import requests

file_name = "eljur_api.py"


def _json_converter(json_ans):  # превращает json строку в словарь и возращает его
    json_data = json.loads(json_ans)
    return json_data


def _strip(params, more=[]):
    striped_params = {_strip_key(key): value for key, value in params.items() if key not in ['self'] + more}
    return striped_params


def _strip_key(key):
    if key[-1] == "_":
        return key[:-1]
    else:
        return key


class LoggerTemplates(object):
    @staticmethod
    def make_log(message="Сообщение логгеру не поступило", module_name=file_name, ):
        logger.log(module_name, message)

    def empty_var(self, func_name, param_name):
        self.make_log(f"Не введен параметр: '{param_name} в функции '{func_name}'")

    def false_type_of_var(self, func_name, param_name, given_type, right_types):
        self.make_log(
            f"Переданный функции '{func_name}' параметр '{param_name}' имеет неправильный тип '{given_type}', должен быть одним из этих '{right_types}'")

    def failed_request(self, func_name, request, error, content):
        self.make_log(
            f"Проваленный запрос '{request}' в функции '{func_name}', статус код: '{error}, \n Содержимое ответа: \n '{content}'")

    def successful_login(self, login):
        self.make_log(f"Пользователь под логином '{login}' успешно получил токен сессии")

    def failed_login(self, login):
        self.make_log(f"Пользователю под логином '{login}' не ролучилось получить токен сессии")


class _UserBase(object):
    auth_token = ""
    '''
    Необходимый токен, который имеет срок годности. Можно получить, вызвав функции:
    1)login_user() - логинит юзера и получает токен сессии
    2)refresh_auth_token() - обновляет токен сессии под логином и паролем из GlobalVariables, если не получилось, 
        то остается тем же и оставляет сообщение в логгере
    '''
    date_of_auth_token_expiration = ""
    '''
    Дата истечения срока годности сессионного токена, котырый можно получить, вызвав функции:
    1)login_user() - логинит юзера и получает токен сессии
    2)refresh_auth_token() - обновляет токен сессии под логином и паролем из GlobalVariables, если не получилось, 
        то остается тем же и оставляет сообщение в логгере
    '''
    vendor = ""
    '''
    Тип: строка

    Поддомен образовательного учреждения (ОУ) в системе ЭлЖур. 
    Например, если журнал школы №999 расположен по адресу https://999.eljur.ru, то необходимо передать 999.
    Поддомен может содержать цифры, буквы, дефисы, знак нижнего подчеркивания (sch1, school1399, school_46, mou-gymn1).
    '''
    devkey = ""
    '''
    Это токен разработчика, наделяющего пользователя правами пользования API. Необходимо просить его у разрабов eljur
    напрямую или через Картавенко.

    Токен лишь наделяет правами какого-то пользователя, а не является админкой. С помощью токена от сервера получется
    сессионный токен для введенного пользователя.
    '''
    rules = {}
    '''
    Информация о пользователе, запрошенную методом /getrules (функция update_rules и get_rules)
    '''

    def _make_request(self, method, params={}):
        request_adress = f"https://api.eljur.ru/api/{method}"
        params = self.default_params(params)
        answer = requests.get(request_adress, params)
        print(answer.url)
        if answer.status_code != requests.codes.ok:
            Logger.failed_request("make_request", answer.url, answer.status_code, answer.text)
        return [answer.status_code == requests.codes.ok, _json_converter(answer.text)]

    def default_params(self, params):
        params.update(
            {"devkey": self.devkey, "out_format": "json", "vendor": self.vendor, "auth_token": self.auth_token})
        return params

    def __init__(self, devkey=None, login=None, password=None, vendor=None):
        for param_name, param_value in _strip(locals()).items():
            if not isinstance(param_value, str):
                Logger.false_type_of_var("UserBase.__init__", param_name, type(param_value), str)
                return
        self.devkey = devkey
        self.vendor = vendor
        if self.login(login, password, vendor, devkey):
            Logger.successful_login(login)
            self.update_rules()
        else:
            Logger.failed_login(login)

    def login(self, login, password, vendor, devkey):
        params = _strip(locals())
        params["out_format"] = "json"
        answer = requests.get("https://api.eljur.ru/api/auth", params)
        if answer.status_code == requests.codes.ok:
            answer_json = _json_converter(answer.text)
            self.auth_token = answer_json["response"]["result"]["token"]
            return True

    def get_rules(self):
        answer = self._make_request("getrules")
        return answer

    def update_rules(self):
        self.rules = self.get_rules()


class Student(_UserBase):
    # student_id = -1

    def __init__(self, devkey=None, login=None, password=None, vendor=None):
        super(Student, self).__init__(devkey, login, password, vendor)
        # self.update_student_id()

    # def get_student_id(self):
    #     return self.rules["response"]["result"]["relations"]["name"]
    #
    # def update_student_id(self):
    #     self.student_id = self.get_student_id()

    def get_schedule(self, class_=None, days=None, ring=None):
        params = _strip(locals())
        answer = self._make_request("getschedule", params)
        return answer[1]


Logger = LoggerTemplates()

preset = {"devkey": "***", "vendor": "1543", "password": "***",
          "login": "***"}

student = Student(**preset)

s = {'response': {'state': 200, 'error': None, 'result': {'students': {'2637': {'name': '2637', 'title': 'Кабаков Иван',
                                                                                'days': {
                                                                                    '20190211': {'name': '20190211',
                                                                                                 'title': 'Понедельник',
                                                                                                 'items': {'1': {
                                                                                                     'name': 'География',
                                                                                                     'num': '1',
                                                                                                     'room': '',
                                                                                                     'teacher': 'Виленский Виктор Михайлович'},
                                                                                                     '2': {
                                                                                                         'name': 'Физика',
                                                                                                         'num': '2',
                                                                                                         'room': '9',
                                                                                                         'teacher': 'Волохов Александр Юльевич',
                                                                                                         'grp_short': 'В',
                                                                                                         'grp': 'В'},
                                                                                                     '3': {
                                                                                                         'name': 'Физика',
                                                                                                         'num': '3',
                                                                                                         'room': '9',
                                                                                                         'teacher': 'Волохов Александр Юльевич',
                                                                                                         'grp_short': 'В',
                                                                                                         'grp': 'В'},
                                                                                                     '4': {
                                                                                                         'name': 'Биология',
                                                                                                         'num': '4',
                                                                                                         'room': '',
                                                                                                         'teacher': 'Волкова Полина Андреевна'},
                                                                                                     '5': {
                                                                                                         'name': 'Физкультура',
                                                                                                         'num': '5',
                                                                                                         'room': '',
                                                                                                         'teacher': 'Ермаков Андрей Анатольевич',
                                                                                                         'grp_short': 'М',
                                                                                                         'grp': 'М'},
                                                                                                     '6': {
                                                                                                         'name': 'Английский',
                                                                                                         'num': '6',
                                                                                                         'room': '',
                                                                                                         'teacher': 'Романова Ольга Игоревна',
                                                                                                         'grp_short': 'Р',
                                                                                                         'grp': 'Р'}}},
                                                                                    '20190212': {'name': '20190212',
                                                                                                 'title': 'Вторник',
                                                                                                 'alert': 'today',
                                                                                                 'items': {'1': {
                                                                                                     'name': 'Информатика',
                                                                                                     'num': '1',
                                                                                                     'room': '',
                                                                                                     'teacher': 'Матюхин Виктор Александрович',
                                                                                                     'grp_short': 'А',
                                                                                                     'grp': 'А'}, '2': {
                                                                                                     'name': 'Информатика',
                                                                                                     'num': '2',
                                                                                                     'room': '',
                                                                                                     'teacher': 'Матюхин Виктор Александрович',
                                                                                                     'grp_short': 'А',
                                                                                                     'grp': 'А'}, '3': {
                                                                                                     'name': 'Обществознание',
                                                                                                     'num': '3',
                                                                                                     'room': '',
                                                                                                     'teacher': 'Лоскутова Ирина Мироновна'},
                                                                                                     '4': {
                                                                                                         'name': 'Немецкий',
                                                                                                         'num': '4',
                                                                                                         'room': '',
                                                                                                         'teacher': 'Крысанова Маргарита Валерьевна',
                                                                                                         'grp_short': 'Нем',
                                                                                                         'grp': 'Нем'},
                                                                                                     '5': {
                                                                                                         'name': 'Спецкурс',
                                                                                                         'num': '5',
                                                                                                         'room': '18',
                                                                                                         'teacher': 'Раскина Инесса Владимировна',
                                                                                                         'grp_short': 'А',
                                                                                                         'grp': 'А'}},
                                                                                                 'items_extday': [{
                                                                                                     'name': 'Подготовка к сдаче экзамена на сертификат',
                                                                                                     'grp': 'подготовка к сдаче экзамена на сертификат',
                                                                                                     'grp_short': 'IELTS',
                                                                                                     'starttime': '17:00:00',
                                                                                                     'endtime': '18:30:00',
                                                                                                     'topic': '',
                                                                                                     'teacher': 'Панфилова Катерина Павловна'}]},
                                                                                    '20190213': {'name': '20190213',
                                                                                                 'title': 'Среда',
                                                                                                 'items': {'1': {
                                                                                                     'name': 'Немецкий',
                                                                                                     'num': '1',
                                                                                                     'room': '207',
                                                                                                     'teacher': 'Крысанова Маргарита Валерьевна',
                                                                                                     'grp_short': 'Нем',
                                                                                                     'grp': 'Нем'},
                                                                                                     '2': {
                                                                                                         'name': 'Русский язык',
                                                                                                         'num': '2',
                                                                                                         'room': '',
                                                                                                         'teacher': 'Штейн Виктория Владимировна'},
                                                                                                     '3': {
                                                                                                         'name': 'Алгебра',
                                                                                                         'num': '3',
                                                                                                         'room': 'зал 2',
                                                                                                         'teacher': 'Хачатурян Александр Вячеславович',
                                                                                                         'grp_short': 'А',
                                                                                                         'grp': 'А'},
                                                                                                     '4': {
                                                                                                         'name': 'Алгебра',
                                                                                                         'num': '4',
                                                                                                         'room': '',
                                                                                                         'teacher': 'Хачатурян Александр Вячеславович',
                                                                                                         'grp_short': 'А',
                                                                                                         'grp': 'А'},
                                                                                                     '5': {
                                                                                                         'name': 'Литература',
                                                                                                         'num': '5',
                                                                                                         'room': '301',
                                                                                                         'teacher': 'Кукина Маргарита Анатольевна'},
                                                                                                     '6': {
                                                                                                         'name': 'Литература',
                                                                                                         'num': '6',
                                                                                                         'room': '301',
                                                                                                         'teacher': 'Кукина Маргарита Анатольевна'},
                                                                                                     '7': {
                                                                                                         'name': 'История',
                                                                                                         'num': '7',
                                                                                                         'room': '21',
                                                                                                         'teacher': 'Зарипова Лилия Рафисовна'}}},
                                                                                    '20190214': {'name': '20190214',
                                                                                                 'title': 'Четверг',
                                                                                                 'items': {'1': {
                                                                                                     'name': 'Геометрия',
                                                                                                     'num': '1',
                                                                                                     'room': '',
                                                                                                     'teacher': 'Сысоева Татьяна Юрьевна',
                                                                                                     'grp_short': 'А',
                                                                                                     'grp': 'А'}, '2': {
                                                                                                     'name': 'Геометрия',
                                                                                                     'num': '2',
                                                                                                     'room': '',
                                                                                                     'teacher': 'Сысоева Татьяна Юрьевна',
                                                                                                     'grp_short': 'А',
                                                                                                     'grp': 'А'}, '3': {
                                                                                                     'name': 'Английский',
                                                                                                     'num': '3',
                                                                                                     'room': '',
                                                                                                     'teacher': 'Романова Ольга Игоревна',
                                                                                                     'grp_short': 'Р',
                                                                                                     'grp': 'Р'}, '4': {
                                                                                                     'name': 'Физика',
                                                                                                     'num': '4',
                                                                                                     'room': '9',
                                                                                                     'teacher': 'Волохов Александр Юльевич',
                                                                                                     'grp_short': 'В',
                                                                                                     'grp': 'В'}, '5': {
                                                                                                     'name': 'Физика',
                                                                                                     'num': '5',
                                                                                                     'room': '9',
                                                                                                     'teacher': 'Волохов Александр Юльевич',
                                                                                                     'grp_short': 'В',
                                                                                                     'grp': 'В'}, '6': {
                                                                                                     'name': 'Химия',
                                                                                                     'num': '6',
                                                                                                     'room': '34',
                                                                                                     'teacher': 'Степанова Марина Леонидовна'}}},
                                                                                    '20190215': {'name': '20190215',
                                                                                                 'title': 'Пятница',
                                                                                                 'items': {'1': {
                                                                                                     'name': 'Алгебра',
                                                                                                     'num': '1',
                                                                                                     'room': '',
                                                                                                     'teacher': 'Хачатурян Александр Вячеславович',
                                                                                                     'grp_short': 'А',
                                                                                                     'grp': 'А'}, '2': {
                                                                                                     'name': 'Алгебра',
                                                                                                     'num': '2',
                                                                                                     'room': '',
                                                                                                     'teacher': 'Хачатурян Александр Вячеславович',
                                                                                                     'grp_short': 'А',
                                                                                                     'grp': 'А'}, '3': {
                                                                                                     'name': 'Химия',
                                                                                                     'num': '3',
                                                                                                     'room': '34',
                                                                                                     'teacher': 'Степанова Марина Леонидовна'},
                                                                                                     '4': {
                                                                                                         'name': 'Литература',
                                                                                                         'num': '4',
                                                                                                         'room': '',
                                                                                                         'teacher': 'Кукина Маргарита Анатольевна'},
                                                                                                     '5': {
                                                                                                         'name': 'Английский',
                                                                                                         'num': '5',
                                                                                                         'room': '',
                                                                                                         'teacher': 'Романова Ольга Игоревна',
                                                                                                         'grp_short': 'Р',
                                                                                                         'grp': 'Р'},
                                                                                                     '6': {
                                                                                                         'name': 'Биология',
                                                                                                         'num': '6',
                                                                                                         'room': 'зал 2',
                                                                                                         'teacher': 'Волкова Полина Андреевна'},
                                                                                                     '7': {
                                                                                                         'name': 'История',
                                                                                                         'num': '7',
                                                                                                         'room': '',
                                                                                                         'teacher': 'Зарипова Лилия Рафисовна'}}},
                                                                                    '20190216': {'name': '20190216',
                                                                                                 'title': 'Суббота',
                                                                                                 'items': {'2': {
                                                                                                     'name': 'Литература',
                                                                                                     'num': '2',
                                                                                                     'room': '',
                                                                                                     'teacher': 'Кукина Маргарита Анатольевна'},
                                                                                                     '3': {
                                                                                                         'name': 'Литература',
                                                                                                         'num': '3',
                                                                                                         'room': '',
                                                                                                         'teacher': 'Кукина Маргарита Анатольевна'},
                                                                                                     '4': {
                                                                                                         'name': 'Физкультура',
                                                                                                         'num': '4',
                                                                                                         'room': 'Спортзал',
                                                                                                         'teacher': 'Ермаков Андрей Анатольевич',
                                                                                                         'grp_short': 'М',
                                                                                                         'grp': 'М'},
                                                                                                     '5': {
                                                                                                         'name': 'Спецкурс',
                                                                                                         'num': '5',
                                                                                                         'room': '18',
                                                                                                         'teacher': 'Раскина Инесса Владимировна',
                                                                                                         'grp_short': 'А',
                                                                                                         'grp': 'А'},
                                                                                                     '7': {
                                                                                                         'name': 'Обществознание',
                                                                                                         'num': '7',
                                                                                                         'room': 'зал 2',
                                                                                                         'teacher': 'Лоскутова Ирина Мироновна'}}}}}}}}}

print(student.get_schedule(class_="7Г"))