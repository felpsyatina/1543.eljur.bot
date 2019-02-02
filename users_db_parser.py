import sqlite3

class EljUser:
    def __init__(self, _id, login, password_hash, parallel, name, surname, access_level, ban, vk_login, vk_id,
                 tele_login, tele_id):
        self._id = _id
        self.login = login
        self.password_hash = password_hash
        self.parallel = parallel
        self.name = name
        self.surname = surname
        self.access_level = access_level
        self.ban = ban
        self. vk_login = vk_login
        self.vk_id = vk_id
        self.tele_login = tele_login
        self.tele_id = tele_id

    def update_user(self, _id, login, password_hash, parallel, name, surname, access_level, ban, vk_login, vk_id,
                 tele_login, tele_id):
        self._id = _id
        self.login = login
        self.password_hash = password_hash
        self.parallel = parallel
        self.name = name
        self.surname = surname
        self.access_level = access_level
        self.ban = ban
        self. vk_login = vk_login
        self.vk_id = vk_id
        self.tele_login = tele_login
        self.tele_id = tele_id




conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute()