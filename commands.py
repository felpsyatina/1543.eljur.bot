# -*- coding: utf-8 -*-

import Vk_bot
from time import sleep

Vk_bot.run()

while True:
    d = Vk_bot.get_info()
    if d == None:
        sleep(0.05)
        continue
    message = d['message']
    user_id = d['user_id']
    user_name = Vk_bot._get_users_info_from_vk_ids([user_id])[0]["first_name"]
    message = message.lower()
    if message == 'привет' or message == 'privet':
        if user_name == 'untitled':
            Vk_bot.write_msg(user_id, "Привет")
        else:
            Vk_bot.write_msg(user_id, "Привет, " + user_name)
    elif message == 'клава' or message == 'klava':
        key = Vk_bot.make_key_fast("one two three", "privet klava привет", "lol kek cheburek")
        Vk_bot.write_key(user_id, key, "Пример клавы")
    elif message in ['one', 'two', 'three', 'four', 'five', 'Lol', 'kek', 'cheburek']:
        Vk_bot.write_msg(user_id, "Ого, ты умеешь нажимать на кнопки")
    else:
        Vk_bot.write_msg(user_id, "Данная информация мной не воспринимается. (Только то, что на кнопках)")
