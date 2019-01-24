# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import config


print("Token for vk bot is:", config.secret["vk"]["token"])

print("Pause for sleeping between check eljur updates is", config.params["eljur_update_sleeptime"], "seconds")

# Модуль config занимается тем, что из двух json-файлов загружает информацию и хранит в словариках.
# Сами json-файлы с конфигами лежат в директории configs
# Когда вы пишете import config, он уже загружает конфиги из файликов.
# Теперь в любой момент вы можете обратиться к переменной модуля config, например:
# config.secret - это словарик, считанный из файла config_secrets.json.
# В любой момент в этот файл можно добавлять новые параметры, и у словарика config.secret автоматически 
# (при следующем запуске программы) появятся соответствующие поля.

# Я считаю, что все глобальные параметры должны быть сохранены в config.json, и, соответственно, 
# в ваших модулях должен подключаться модуль config, и браться соответствующие поля от config.params.

# А все секретные штуки (типа токенов ботиков, или логинов-паролей куда-нибудь)
# должны сохраняться в config_secrets.py. При этом в github будет коммититься "шаблон" для этого файла 
# (ну примерно как сейчас - чтобы было видно, какие поля в нем нужны). Но НИКОГДА не надо коммитить
# сами секреты (токены)

# Чуть-чуть комментриаев про реализацию. 

# Вот этот файл с примером, в нем в начале есть такие строчки:
# import sys
# sys.path.append("..")
# Они добавляют директорию к пути, где python будет искать подключаемые модули.
# Если файл config.py будет лежать в той же директории, то они не нужны, а так, в строке 3 мы говорим,
# что надо смотреть в директории, которая расположена на уровень вверх относительно текущей.

# В файле config.py может вызвать вопросы строчка
# cur_path = os.path.dirname(os.path.abspath(__file__))
# Она в переменную cur_path получает путь к директории, где лежит сам config.py
# Это нужно для того, чтобы json-файлики с кофигами искать в поддиректории configs относительно config.py,
# а не той директории, которая была текущей при запуске программы