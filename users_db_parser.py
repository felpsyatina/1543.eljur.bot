import sqlite3

conn = sqlite3.connect("1543.eljur.bot.db")
cursor = conn.cursor()



def get_user_by_id(_id):
    cursor.execute('SELECT * FROM users WHERE _id=:_id', {'_id': _id})
    return cursor.fetchone()


def make_new_user(login, parallel, name, surname):
    cursor.execute("INSERT INTO users (login, parallel, name, surname) VALUES (?, ?, ?, ?)", (login, parallel, name, surname))

def update_user(_id, dict_of_changes):

    for key, value in dict_of_changes.items():
        cursor.execute(f"UPDATE users SET {key}={value} WHERE _id={_id})")

