import sys
sys.path.append("..")

import config
import requests

elj_devkey = config.secret["eljurapi"]["devkey"]
elj_token = config.secret["eljurapi"]["token"]


def update(class_="10В"):
    address = f"https://1543.eljur.ru/api/getschedule/?devkey={elj_devkey}&auth_token={elj_token}&class={class_}&vendor=1543"
    r = requests.get(address)

    with open("schedule.xml", "w", encoding="UTF-8") as file_out:
        print(r.text, file=file_out)


if __name__ == '__main__':
    update()