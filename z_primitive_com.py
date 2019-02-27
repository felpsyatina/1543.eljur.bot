# -*- coding: utf-8 -*-

from time import sleep
from primitive_commands import update_schedule, schedule_xml_to_array
import Vk_bot


Vk_bot.run()
users_pos = {}
users_req = {}
BACK_MSG_OUT = "Назад"
BACK_MSG = "назад"

DAYS = {
    "понедельник" : 1,
    "вторник" : 2,
    "среда" : 3,
    "четверг" : 4,
    "пятница" : 5,
    "суббота" : 6
}


UPPER_LET = {
    "а" : "А",
    "б" : "Б",
    "в" : "В",
    "г" : "Г"
}


while True:
    d = Vk_bot.get_next()
    if d == None:
        sleep(0.05)
        continue

    message = d["message"]
    user_id = d["user_id"]

    users_pos[user_id] = users_pos.get(user_id, 0)
    if users_pos[user_id] == 0:
        users_req[user_id] = []

    user_name = Vk_bot._get_users_info_from_vk_ids([user_id])[0]["first_name"]
    message = message.lower()

    if message == "привет" or message == "privet":
        if user_name == "untitled":
            Vk_bot.write_msg(user_id, "Привет!")
        else:
            Vk_bot.write_msg(user_id, f"Привет, {user_name}!")
        users_pos[user_id] = 0
        continue

    if message == BACK_MSG:
        users_pos[user_id] = 0
        
    print(message, users_pos[user_id])
    if users_pos[user_id] == 0:
        key = Vk_bot.make_key_fast("Узнать_Расписание")
        users_pos[user_id] = 1

        Vk_bot.write_key(user_id, key, "Выберите функцию")
        continue

    if users_pos[user_id] == 1 and message in ["узнать_расписание"]:
        key = Vk_bot.make_key_fast("5 6 7 8", "9 10 11", BACK_MSG_OUT)
        users_pos[user_id] = 2
        users_req[user_id] = []
        
        Vk_bot.write_key(user_id, key, "Выберите класс")
        continue
        
    if users_pos[user_id] == 2 and message in ["5", "6", "7", "8", "9", "10", "11"]:
        key = Vk_bot.make_key_fast("А Б В Г", BACK_MSG_OUT)
        users_pos[user_id] = 3
        users_req[user_id].append(message)
        
        Vk_bot.write_key(user_id, key, "Выберите букву")
        continue

    if users_pos[user_id] == 3 and message in ["а", "б", "в", "г"]:
        key = Vk_bot.make_key_fast("Понедельник Вторник Среда", "Четверг Пятница Суббота", BACK_MSG_OUT)
        users_pos[user_id] = 4
        users_req[user_id].append(UPPER_LET[message])

        Vk_bot.write_key(user_id, key, "Выберите день")
        continue

        
    if users_pos[user_id] == 4 and message in ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]:
        req = users_req[user_id]
        update_schedule.update(str(req[0]) + str(req[1])) # Заменить расписание в файле schedule.xml для текущего класса

        cur_schedule = schedule_xml_to_array.from_xml_to_text()[DAYS[message]]
        # print(cur_schedule)
        cur_num_les = 0

        first_lesson = 0
        last_lesson = 0

        for lesson in cur_schedule:
            if lesson != []:
                last_lesson = cur_num_les
                if first_lesson == 0:
                    first_lesson = cur_num_les

            cur_num_les += 1


        output_msg = ""
        for ind in range(first_lesson, last_lesson + 1):
            cur_les = cur_schedule[ind]
            if cur_les == []:
                output_msg += f"{ind}: Окно\n"
            else:
                cur_les_str = "/".join(cur_les)
                output_msg += f"{ind}: {cur_les_str}\n"

        Vk_bot.write_msg(user_id, output_msg)
        users_pos[user_id] = 0


    key = Vk_bot.make_key_fast("Узнать_Расписание")
    users_pos[user_id] = 1

    Vk_bot.write_key(user_id, key, "Выберите функцию")

    # elif message == "клава" or message == "klava":
    #     key = Vk_bot.make_key_fast("one two three", "privet klava привет", "lol kek cheburek")
    #     Vk_bot.write_key(user_id, key, "Пример клавы")
    # elif message in ["one", "two", "three", "four", "five", "Lol", "kek", "cheburek"]:
    #     Vk_bot.write_msg(user_id, "Ого, ты умеешь нажимать на кнопки")
    # else:
    #     Vk_bot.write_msg(user_id, "Данная информация мной не воспринимается. (Только то, что на кнопках)")
