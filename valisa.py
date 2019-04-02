# import user_db_manip
# import lesson_db_manip
import re
# Тестовая версия валисы

def get_home_task(params):
    print("Вот вам dz", params)


def get_schedule(params):
    print("Вот вам расписание", params)


def is_get_home_task(string):
    string = delete_message_from_request(string)

    keywords = ["домашнее задание", "дз"]

    for keyword in keywords:
        if keyword in string:
            return True
    return False


def is_get_schedule(string):
    string = delete_message_from_request(string)

    keywords = ["расписание"]

    for keyword in keywords:
        if keyword in string:
            return True
    return False


def extract_class_(string):
    regex = r"(^|\s)([5-9]{1}|(1[0-1]))([а-гА-Г]|\s[а-гА-Г])"
    result = re.search(regex, string)

    return result
    # if result is not None:
    #     return result


def extract_date(string):
    regex = r"(^|\s)(20[1-9][0-9])([,./\\\s]|)([0][1-9]|[1][0-2])([,./\\\s]|)(0[1-9]|[1-2][0-9]|3[0-1])"
    result = re.search(regex, string)
    if result is not None:
        # result = result.sub(r",./\\\s", "", string)
        return result
    else:
        return None


def delete_message_from_request(string):
    if string.count('"') > 1:
        return string[:string.find('"')] + string[string.rfind('"'):]
    return string


definers = [
    {"definer_func": is_get_home_task,
     "params": ["class_", "date"],
     "run_func": get_home_task},
    {"definer_func": is_get_schedule,
     "params": ["class_", "date"],
     "run_func": get_schedule}
]

params_extracters = {"class_": extract_class_, "date": extract_date}


def get_params(string, needed_params):
    params = {}
    for needed_param in needed_params:
        params[needed_param] = params_extracters[needed_param](string)
    return params


def req(string):
    for cur_definer in definers:
        if cur_definer["definer_func"](string):
            params = get_params(string, cur_definer["params"])
            cur_definer["run_func"](params)


if __name__ == '__main__':
    while True:
        print(req(input()))
