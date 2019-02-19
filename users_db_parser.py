import sqlite3
import logger

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
    return cursor.fetchone()


def make_new_user(login=None, parallel=None, name=None, surname=None):
    if login is None:
        logger.log("users_db_parser", "Не указан login в функции make_new_user")
        return
    cursor.execute("INSERT INTO users (login, parallel, name, surname) VALUES (?, ?, ?, ?)", (login, parallel, name, surname))
    conn.commit()


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
