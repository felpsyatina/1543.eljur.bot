import logger
import re
import datetime


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
        self.list_of_dates = []

        self.params_extractors = {"subs": self.extract_class_, "list_of_dates": self.extract_dates}

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

        regexes = [r"домашняя работа", r"дз"]

        for regex in regexes:
            result = re.search(regex, string)
            if result is not None:
                return True
        return False

    def is_get_schedule(self, string):
        string = self.delete_message_from_request(string)

        regexes = [r"расписание", r"расп"]

        for regex in regexes:
            result = re.search(regex, string)
            if result is not None:
                return True
        return False

    def extract_class_(self, string):
        regex = r"(^|\s)([5-9]{1}|(1[0-1]))([а-гА-Г]|\s[а-гА-Г])"
        result = re.search(regex, string)

        if result is None:
            return None

        self.subs = {result.group().strip().upper(): {}}

    def extract_dates(self, string):
        # full date is YYYMMDD
        regex_full_date = r"(((\d{4})(0[13578]|10|12)(0[1-9]|[12][0-9]|3[01]))|((\d{4})(0[469]|11)([0][1-9]|[12][0-9]|30))|((\d{4})(02)(0[1-9]|1[0-9]|2[0-8]))|(([02468][048]00)(02)(29))|(([13579][26]00) (02)(29))|(([0-9][0-9][0][48])(02)(29))|(([0-9][0-9][2468][048])(02)(29))|(([0-9][0-9][13579][26])(02)(29))|(00000000)|(88888888)|(99999999))"
        result = re.search(regex_full_date, string)

        if result is not None:
            self.list_of_dates.append(result.group(0))

        special_dates = [(r"сегодня", 0),
                         (r"вчера", -1),
                         (r"завтра", 1),
                         (r"позавчера", -2),
                         (r"послезавтра", 2)]

        for regex, delta in special_dates:
            result = re.search(regex, string)
            if result is not None:
                self.list_of_dates.append(self.get_cur_date(delta))

        regex_custom_delta = [
            (r"(через|спустя) (-)?[0-9][1-9]* (дня|дней|суток|сутка|сутки)", r"(-)?[0-9][1-9]*", False),
            (r"(-)?[0-9][1-9]* (дня|дней|суток|сутка|сутки) (до|назад)", r"(-)?[0-9][1-9]*", True)]

        for regex, delta_extract, is_reversed in regex_custom_delta:
            result = re.search(regex, string)
            if result is not None:
                delta = int(re.search(delta_extract, result.group(0)).group(0))
                if is_reversed:
                    delta *= -1
                self.list_of_dates.append(self.get_cur_date(delta))

    def get_params(self, string, needed_params):
        params = {}
        for needed_param in needed_params:
            params[needed_param] = self.params_extractors[needed_param](string)
        return params

    @staticmethod
    def get_cur_date(delta):
        return (datetime.datetime.today() + datetime.timedelta(days=delta)).strftime('%Y%m%d')

    @staticmethod
    def delete_message_from_request(string):
        if string.count('"') > 1:
            return string[:string.find('"')] + string[string.rfind('"'):]
        return string


if __name__ == '__main__':
    while 1:
        req = Valica(input())
        print(req.type, req.subs, req.list_of_dates)
