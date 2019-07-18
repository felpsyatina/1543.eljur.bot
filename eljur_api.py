# -*- coding: utf-8 -*-
import json

import requests

import functions
import logger

file_name = "eljur_api.py"


def _json_converter(json_ans):  # превращает json строку в словарь и возращает его
    json_data = json.loads(json_ans)
    return json_data


def _strip(params, more=None):
    if more is None:
        more = []
    striped_params = {_strip_key(key): value for key, value in params.items() if key not in ['self'] + more}
    return striped_params


def _strip_key(key):
    if key[-1] == "_":
        return key[:-1]
    else:
        return key


def _strip_server_info(answer):
    return answer["response"]["result"]


class LoggerTemplates(object):
    @staticmethod
    def make_log(message="Empty message to logger", module_name=file_name):
        logger.log(module_name, message)

    def error(self, error):
        self.make_log(f"Error log: {error}")

    def empty_param(self, func_name, param_name):
        self.make_log(f"Empty parameter: '{param_name} in function '{func_name}'")

    def false_type_of_var(self, func_name, param_name, given_type, right_types):
        self.make_log(
            f"Given to"
            f" function '{func_name}' parameter '{param_name}' has wrong type '{given_type}', must be one of them "
            f"'{right_types}'")

    def failed_request(self, func_name, request, error, content):
        self.make_log(
            f"Failed request '{request}' in function '{func_name}', error log: '{error}, \n Response: \n '{content}'")

    def successful_login(self, login):
        self.make_log(f"User with a login: '{login}' successfully received auth token")

    def failed_login(self, login):
        self.make_log(f"User with a login: '{login}' failed attempt to receive auth token")

    def strip_failed(self, response_text):
        self.make_log(f"Failed attempt to strip request: '{response_text}'")


class _UserBase(object):
    auth_token = ""
    '''
    Необходимый токен, который имеет срок годности. Можно получить, вызвав функции:
    login() - логинит юзера и получает токен сессии
    '''
    date_of_auth_token_expiration = ""
    '''
    Дата истечения срока годности сессионного токена, котырый можно получить, вызвав функции:
    login() - логинит юзера и получает токен сессии
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

    def _make_request(self, method, params=None):
        if not params:
            params = {}
        request_adress = f"https://api.eljur.ru/api/{method}"
        params = self._default_params(params)
        response = requests.get(request_adress, params)
        if response.status_code != requests.codes.ok:
            Logger.failed_request("make_request", response.url, response.status_code, response.text)
        try:
            answer = _strip_server_info(_json_converter(response.text))
            return answer
        except Exception as exc:
            Logger.error(exc)
            Logger.strip_failed(response.text)

    def _default_params(self, params):
        params.update(
            {"devkey": self.devkey, "out_format": "json", "vendor": self.vendor, "auth_token": self.auth_token})
        return params

    def __init__(self, devkey=None, login=None, password=None, vendor=None):
        for param_name, param_value in _strip(locals()).items():
            if not isinstance(param_value, str):
                Logger.false_type_of_var("UserBase.__init__", param_name, type(param_value), str)
                return
        if self.login(login, password, vendor, devkey):
            Logger.successful_login(login)
            self.update_rules()
        else:
            Logger.failed_login(login)

    def login(self, login, password, vendor, devkey):
        params = _strip(locals())
        params["out_format"] = "json"
        response = requests.get("https://api.eljur.ru/api/auth", params)
        if response.status_code == requests.codes.ok:
            answer = _strip_server_info(_json_converter(response.text))
            self.auth_token = answer["token"]
            self.date_of_auth_token_expiration = answer["expires"]
            self.devkey = devkey
            self.vendor = vendor
            return True

    def get_rules(self):
        answer = self._make_request("getrules")
        return answer

    def update_rules(self):
        self.rules = self.get_rules()


class Student(_UserBase):

    def __init__(self, devkey=None, login=None, password=None, vendor=None):
        super(Student, self).__init__(devkey, login, password, vendor)

    def get_schedule(self, class_=None, days=None, ring=None):
        params = _strip(locals())
        answer = self._make_request("getschedule", params)
        return answer

    def get_hometask(self, class_=None, days=None, ring=None):
        params = _strip(locals())
        answer = self._make_request("gethomework", params)
        return answer

    def get_assessments(self, student=None, days=None):
        params = _strip(locals())
        answer = self._make_request("getassessments", params)
        return answer

    def get_finalassessments(self, student=None):
        params = _strip(locals())
        answer = self._make_request("getfinalassessments", params)
        return answer

    def get_diary(self, student=None, days=None, rings=None):
        params = _strip(locals())
        answer = self._make_request("getdiary", params)
        return answer

    def get_updates(self, student=None, limit=None, page=None):
        params = _strip(locals())
        answer = self._make_request("getupdates", params)
        return answer

    def get_periods(self, student=None, weeks=None, show_disabled=None):
        params = _strip(locals())
        answer = self._make_request("getperiods", params)
        return answer

    def get_marks(self, student=None, days=None):
        params = _strip(locals())
        answer = self._make_request("getmarks", params)
        return answer

    def get_messagereceivers(self):
        answer = self._make_request("getmessagereceivers")
        return answer

    def get_messageinfo(self, id_=None):
        if id_ is None:
            Logger.empty_param("get_messageinfo", "id")
            return None
        params = _strip(locals())
        answer = self._make_request("getmessageinfo", params)
        return answer

    def get_messages(self, folder=None, unreadonly=None, limit=None, page=None):
        params = _strip(locals())
        answer = self._make_request("getmessages", params)
        return answer

    def send_message(self, subject=None, text=None, users_to=None):
        if subject is None:
            Logger.empty_param("send_message", "subject")
            return False
        if text is None:
            Logger.empty_param("send_message", "text")
            return False
        params = _strip(locals())
        self._make_request("sendmessage", params)
        return True

    def send_replymessage(self, replyto=None, text=None):
        if replyto is None:
            Logger.empty_param("send_replymessage", "replyto")
            return False
        if text is None:
            Logger.empty_param("send_replymessage", "text")
            return False
        params = _strip(locals())
        self._make_request("sendreplymessage", params)
        return True


Logger = LoggerTemplates()

if __name__ == '__main__':
    preset = functions.preset
    student1 = Student(**preset)
    print(student1.get_assessments())
