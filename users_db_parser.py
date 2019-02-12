import sqlite3

conn = sqlite3.connect("1543.eljur.bot.db")
cursor = conn.cursor()



def get_user_by_id(src, user_id):
    if src == "vk":
        cursor.execute('SELECT * FROM users WHERE vk_id=:_id', {'_id': user_id})
    else:
        cursor.execute('SELECT * FROM users WHERE tele_id=:_id', {'_id': user_id})
    return cursor.fetchone()


def make_new_user(login, parallel, name, surname):
    cursor.execute("INSERT INTO users (login, parallel, name, surname) VALUES (?, ?, ?, ?)", (login, parallel, name, surname))

def update_user(src, user_id, dict_of_changes):
    if src == "vk":
        for key, value in dict_of_changes.items():
            cursor.execute(f"UPDATE users SET {key}={value} WHERE vk_id={user_id})")
    else:
        for key, value in dict_of_changes.items():
            cursor.execute(f"UPDATE users SET {key}={value} WHERE tele_id={user_id})")


print(get_user_by_id("vk", 127845402))