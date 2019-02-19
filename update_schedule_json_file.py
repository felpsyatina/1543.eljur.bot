import sys
from json import loads, dumps
from datetime import datetime
sys.path.append("..")

import config
import requests
import lessons_db_manip as ldb

classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '6Г', '7А', '7Б', '7В', '7Г', '8А', '8Б', '8В', '8Г', '9А', '9Б',
           '9В', '9Г', '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']

elj_devkey = config.secret["eljurapi"]["devkey"]
elj_token = config.secret["eljurapi"]["token"]


def cur_date(time=None):
    if time is None:
        time = str(datetime.now())
    return time[:10]


def update(class_="10В", date=None):
    if date is None:
        date = cur_date()

    address = f"https://1543.eljur.ru/api/getschedule/?devkey={elj_devkey}&auth_token={elj_token}&date={date}&class={class_}&vendor=1543&out_format=json"
    req = requests.get(address).text

    schedule_dict = loads(req)["response"]["result"]["days"]
    print(schedule_dict)

    ldb.add_schedule_from_json(schedule_dict, class_)

    # with open(f"{cur_date()}schedule{class_}.json", "w", encoding="UTF-8") as file_out:
    #     print(r.text, file=file_out)


if __name__ == '__main__':
    for cur_class in classes:
        print(cur_class)
        update(cur_class)
