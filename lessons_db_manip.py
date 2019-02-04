import schedule_parser
import sqlite3
import time

conn = sqlite3.connect('1543.eljur.bot.db')
c = conn.cursor()


def create_key():
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())  # format: "YYYY-MM-DD HH:MM:SS"
    c.execute("INSERT INTO addition_schedule VALUES (null, '{}')".format(current_date))
    c.execute("SELECT * FROM addition_schedule ORDER BY id DESC LIMIT 1")
    key = c.fetchone()[0]
    conn.commit()
    return key


def add_schedule(id_of_class, schedule):
    pass
    #Записывает данное функции расписание в базу данных с полученным ключом

