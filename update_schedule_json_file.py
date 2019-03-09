import sys
from json import loads
from datetime import datetime
sys.path.append("..")

import config
import requests


classes = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '6Г', '7А', '7Б', '7В', '7Г', '8А', '8Б', '8В', '8Г', '9А', '9Б',
           '9В', '9Г', '10А', '10Б', '10В', '10Г', '11А', '11Б', '11В', '11Г']

elj_devkey = config.secret["eljurapi"]["devkey"]
elj_token = config.secret["eljurapi"]["token"]


def cur_date(time=None):
    if time is None:
        time = str(datetime.now())
    return time[:10]


def update(class_="10В", date=None):
    address = f"https://1543.eljur.ru/api/getschedule/?devkey={elj_devkey}&auth_token={elj_token}&class={class_}&vendor=1543&out_format=json"

    if date is not None:
        address += f"&days={date}"

    req = requests.get(address).text

    schedule_dict = loads(req)["response"]["result"]["days"]

    return schedule_dict


if __name__ == '__main__':
    print(update(date=20190309))

