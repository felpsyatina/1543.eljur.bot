import logger
import json
import requests

file_name = "eljur_api.py"


def json_converter(json_ans):  # превращает json строку в словарь и возращает его
    json_data = json.loads(json_ans)
    return json_data


def _strip(params, more=[]):
    striped_params = {key: value for key, value in params.items() if key not in ['self'] + more}
    striped_params["out_format"] = "json"
    return striped_params


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


class UserBase(object):
    session_token = ""
    '''
    Необходимый токен, который имеет срок годности. Можно получить, вызвав функции:
    1)login_user() - логинит юзера и получает токен сессии
    2)refresh_session_token() - обновляет токен сессии под логином и паролем из GlobalVariables, если не получилось, 
        то остается тем же и оставляет сообщение в логгере
    '''
    date_of_session_token_expiration = ""

    '''
    Дата истечения срока годности сессионного токена, котырый можно получить, вызвав функции:
    1)login_user() - логинит юзера и получает токен сессии
    2)refresh_session_token() - обновляет токен сессии под логином и паролем из GlobalVariables, если не получилось, 
        то остается тем же и оставляет сообщение в логгере
    '''
    vendor = ""

    '''
    Тип: строка

    Поддомен образовательного учреждения (ОУ) в системе ЭлЖур. 
    Например, если журнал школы №999 расположен по адресу https://999.eljur.ru, то необходимо передать 999.
    Поддомен может содержать цифры, буквы, дефисы, знак нижнего подчеркивания (sch1, school1399, school_46, mou-gymn1).
    '''
    #devkey - что это?
    '''
    Это токен разработчика, наделяющего пользователя правами пользования API. Необходимо просить его у разрабов eljur
    напрямую или через Картавенко.

    Токен лишь наделяет правами какого-то пользователя, а не является админкой. С помощью токена от сервера получется
    сессионный токен для введенного пользователя.
    '''

    @staticmethod
    def make_request(method, params):
        request_adress = f"https://api.eljur.ru/api/{method}?"
        answer = requests.get(request_adress, params)
        if answer.status_code != requests.codes.ok:
            Logger.failed_request("make_request", answer.url, answer.status_code, answer)
        return [answer.status_code == requests.codes.ok, json_converter(answer.text)]

    def __init__(self, devkey=None, login=None, password=None, vendor=None):
        pass
        for param_name, param_value in _strip(locals()).items():
            if not isinstance(param_value, str):
                Logger.false_type_of_var("UserBase.__init__", param_name, type(param_value), str)
                return
        if self.login(devkey, login, password, vendor):
            print(self.session_token)
        else:
            print("Failure")

    def login(self, devkey, login, password, vendor):
        params = _strip(locals())
        answer = self.make_request("auth", params)
        if answer[0]:
            Logger.successful_login(login)
            self.session_token = answer[1]["response"]["result"]["token"]
            return True

# class User():
#     System_Variables:
#
#     def login_user(ad="1231321", same_shit="13232"):
#         print(locals())

Logger = LoggerTemplates()

preset = {"devkey": "518b84cf226921cc75442cab3eb5e225", "vendor": "1543", "password": "***", "login": "***"}

UserBase(**preset)
