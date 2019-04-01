import shutil as sh
import datetime
import os
import config
import logger


def new_db_copy():
    file_path = config.db_copies_path
    today = str(datetime.datetime.now())[:10]
    sh.copy2('1543.eljur.bot.db', file_path + '/database_' + today + '.db')


def delete_db():
    file_path = config.db_copies_path
    today = str(datetime.datetime.now())[:10]
    copies_of_db = os.listdir(file_path)
    for db in copies_of_db:
        if int(today[5:7]) - int(db[14:16]) == 2 or int(today[5:7]) - int(db[14:16]) == -10:
            os.remove(file_path + "/" + db)


if __name__ == '__main__':
    try:
        cur_time = str(datetime.datetime.now())[11:13]
        if cur_time == "01":
            new_db_copy()
            delete_db()
    except Exception as ex:
        logger.log("db_copier", f"error {ex}")
