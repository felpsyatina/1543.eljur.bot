from functions import cur_date
import logger
import re
# Тестовая версия валисы


class Valica:
    def __init__(self, string):
        self.definers = [
            {"definer_func": self.is_get_home_task,
             "params": ["subs", "list_of_dates"],
             "run_func": self.get_home_task},
            {"definer_func": self.is_get_schedule,
             "params": ["subs", "list_of_dates"],
             "run_func": self.get_schedule}
        ]

        self.type = None
        self.subs = None
        self.list_of_dates = None

        self.params_extractors = {"subs": self.extract_class_, "list_of_dates": self.extract_date}

        for cur_definer in self.definers:
            if cur_definer["definer_func"](string):
                self.params = self.get_params(string, cur_definer["params"])
                cur_definer["run_func"]()
        logger.log("valisa", f"parse message status: {self.type}, {self.subs}, {self.list_of_dates}")

    def get_home_task(self):
        self.type = "homework"

    def get_schedule(self):
        self.type = "schedule"

    def is_get_home_task(self, string):
        string = self.delete_message_from_request(string)
        keywords = ["домашнее задание", "дз", "домашка"]

        for keyword in keywords:
            if keyword in string:
                return True
        return False

    def is_get_schedule(self, string):
        string = self.delete_message_from_request(string)

        keywords = ["расписание", "расп"]

        for keyword in keywords:
            if keyword in string:
                return True
        return False

    def extract_class_(self, string):
        regex = r"(^|\s)([5-9]{1}|(1[0-1]))([а-гА-Г]|\s[а-гА-Г])"
        result = re.search(regex, string)

        if result is None:
            return None

        self.subs = {result.group().strip().upper(): {}}

    def extract_date(self, string):
        regex = r"(^|\s)(20[1-9][0-9])([,./\\\s]|)([0][1-9]|[1][0-2])([,./\\\s]|)(0[1-9]|[1-2][0-9]|3[0-1])"
        result = re.search(regex, string)

        if result:
            self.list_of_dates = [result.group().strip()]

        add = -2
        for word in ["позавчера", "вчера", "сегодня", "завтра", "послезавтра"]:
            if word in string.lower().split():
                self.list_of_dates = [cur_date(add=add)]
                return
            add += 1

        return None

    @staticmethod
    def delete_message_from_request(string):
        if string.count('"') > 1:
            return string[:string.find('"')] + string[string.rfind('"'):]
        return string

    def get_params(self, string, needed_params):
        params = {}
        for needed_param in needed_params:
            params[needed_param] = self.params_extractors[needed_param](string)
        return params


if __name__ == '__main__':
    while 1:
        req = Valica(input())
        print(req.type, req.subs, req.list_of_dates)
