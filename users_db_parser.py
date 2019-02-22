import sqlite3
import logger
import answers_dict as ad

conn = sqlite3.connect("1543.eljur.bot.db")
cursor = conn.cursor()


def get_user_by_id(src=None, user_id=None):
    if src is None:
        logger.log("users_db_parser", "Не указан src в функции get_user_by_id")
        return
    if user_id is None:
        logger.log("users_db_parser", "Не указан user_id в функции get_user_by_id")
        return
    if src == "vk":
        cursor.execute('SELECT * FROM users WHERE vk_id=:_id', {'_id': user_id})
    else:
        cursor.execute('SELECT * FROM users WHERE tele_id=:_id', {'_id': user_id})
    fetch = cursor.fetchone()
    if fetch is not None:
        answer = dict.fromkeys(ad.users_table_fields)
        i = 0
        for key in answer.keys():
            answer[key] = fetch[i]
            i += 1
        return answer
    return


def get_user_by_global_id(id):
    cursor.execute('SELECT * FROM users WHERE _id=:id', {'id': id})
    fetch = cursor.fetchone()
    if fetch is not None:
        answer = dict.fromkeys(ad.users_table_fields)
        i = 0
        for key in answer.keys():
            answer[key] = fetch[i]
            i += 1
        return answer
    return


def make_new_user(login=None, parallel=None, name=None, surname=None, src=None, user_id=None):
    if login is None:
        logger.log("users_db_parser", "Не указан login в функции make_new_user")
        return
    if src is None:
        logger.log("users_db_parser", "Не указан src в функции make_new_user")
    if user_id is None:
        logger.log("users_db_parser", "Не указан id в функции make_new_user")
    if get_user_by_id(src, user_id) is None:
        if src == 'vk':
            query = f"INSERT INTO users (login, parallel, name, surname, vk_id) VALUES ('{login}', '{parallel}', '{name}', '{surname}', '{user_id}')"
        else:
            query = f"INSERT INTO users (login, parallel, name, surname, tele_id) VALUES ('{login}', '{parallel}', '{name}', '{surname}', '{user_id}')"
        cursor.execute(query)
        conn.commit()
        answer = "Пользователь зарегистрирован"
    else:
        answer = "Похоже, у вас уже есть аккаунт"
    return answer


def update_user(src=None, user_id=None, dict_of_changes=None):
    if src is None:
        logger.log("users_db_parser", "Не указан src в функции update_user")
        return
    if user_id is None:
        logger.log("users_db_parser", "Не указан user_id в функции update_user")
        return
    if user_id is None:
        logger.log("users_db_parser", "Не указан dict_of_changes в функции update_user")
        return
    if src == "vk":
        for key, value in dict_of_changes.items():
            cursor.execute(f"UPDATE users SET {key}={value} WHERE vk_id={user_id}")
    else:
        for key, value in dict_of_changes.items():
            cursor.execute(f"UPDATE users SET {key}={value} WHERE tele_id={user_id}")
    conn.commit()
