import sqlite3
import logger
import config
from json import dumps as jd, loads as jl
from functions import MyCursor, convert_arrays_to_dict

first_status = config.params['fir_stat']


class UserDbReq:
    def __init__(self, database_name="1543.eljur.bot.test.db"):
        self.database_name = database_name
        self.cursor = None

    def run_cursor(self):
        if self.cursor is None or not self.cursor.connected:
            self.cursor = MyCursor(sqlite3.connect(self.database_name, isolation_level=None))
        return self.cursor

    def del_table(self, table_name):
        with self.run_cursor() as cursor:
            query = f'DROP TABLE IF EXISTS {table_name}'

            cursor.execute(query)
            logger.log("user_db_manip", f"table '{table_name}' deleted.")

    def create_users_db(self, table_name="users"):
        self.del_table(table_name)
        with self.run_cursor() as cursor:
            query = f"""
                create table {table_name}
                (
                    id integer not null
                       primary key autoincrement,
                    first_name text not null,
                    last_name text not null,
                    confirmed int not null, 
                    status text not null,
                    request text,
                    vk_id int unique,
                    tg_id int unique, 
                    alice_id text unique, 
                    subs text,
                    schedule_params text,
                    homework_params text
                );
            """

            cursor.execute(query)
            logger.log("user_db_manip", f"table: '{table_name}' created.")

    def create_debts_db(self, table_name="debts"):
        self.del_table(table_name)
        with self.run_cursor() as cursor:
            query = f"""
                create table {table_name}
                (
                    id integer not null
                       primary key autoincrement,
                    user_id int,
                    text text,
                    subject text,
                    deadline int,
                    is_active int
                );
            """

            cursor.execute(query)
            logger.log("user_db_manip", f"table: '{table_name}' created.")

    def add_user(self, first_name, last_name, user_id, src):
        vk_id = "NULL"
        tg_id = "NULL"
        alice_id = "NULL"

        if src == "vk":
            vk_id = user_id

        if src == "tg":
            tg_id = user_id

        if src == "alice":
            alice_id = self.parse_string_in_query(user_id)

        with self.run_cursor() as cursor:
            query = f"""
                INSERT INTO users (first_name, last_name, confirmed, status, vk_id, tg_id, alice_id, subs) 
                VALUES('{first_name}', '{last_name}', 0, '{first_status}', {vk_id}, {tg_id}, {alice_id}, '{jd({})}')
            """
            cursor.execute(query)
            logger.log("user_db_manip", f"user '{first_name} {last_name}' created!")

    def add_debt(self, user_id, src, text, subject=None, deadline=None):

        global_id = self.get_global_id_by_user_id(user_id, src)

        with self.run_cursor() as cursor:
            query = f"""
                INSERT INTO debts (id, user_id, text, subject, deadline, is_active) 
                VALUES(null, {global_id}, '{text}', '{subject}', '{deadline}', 1)
            """
            cursor.execute(query)
            logger.log("user_db_manip", f"user {user_id}, new debt created!")

    @staticmethod
    def parse_string_in_query(string):
        if type(string) == str:
            return f"'{string}'"

        if string is None:
            return "NULL"

        return string

    def get_columns_info(self, table="users"):
        with self.run_cursor() as cursor:
            query = f"""
                PRAGMA table_info({table})
            """

            cursor.execute(query)
            description = cursor.fetchall()
        return description

    def get_columns_names(self, table="users"):
        columns_info = self.get_columns_info(table=table)
        names = []
        for column in columns_info:
            names.append(column[1])

        return names

    def get_user_info(self, user_id, src):
        vk_id = None
        tg_id = None
        alice_id = None

        if src == "vk":
            vk_id = user_id

        if src == "tg":
            tg_id = user_id

        if src == "alice":
            alice_id = user_id

        with self.run_cursor() as cursor:
            query = None
            if vk_id is not None:
                query = f"""
                    SELECT * FROM users WHERE
                    vk_id = {vk_id};
                """

            elif tg_id is not None:
                query = f"""
                    SELECT * FROM users WHERE
                    tg_id = {tg_id};
                """

            elif alice_id is not None:
                query = f"""
                    SELECT * FROM users WHERE
                    alice_id = '{alice_id}';
                """

            cursor.execute(query)
            users_fetch = cursor.fetchone()

            if users_fetch is None:
                return None

            column_desc = self.get_columns_info()

            if len(users_fetch) != len(column_desc):
                logger.log("user_db_manip", f"Каким-то чудом длины не совпадают!")
                return

            ans_dict = {}
            for it in range(len(users_fetch)):
                if column_desc[it][1] == "subs":
                    ans_dict[column_desc[it][1]] = jl(users_fetch[it])
                else:
                    ans_dict[column_desc[it][1]] = users_fetch[it]

            logger.log("users_db_parser", f"returning info: {ans_dict}")
            return ans_dict

    def get_global_id_by_user_id(self, user_id, src):
        vk_id = None
        tg_id = None
        alice_id = None

        if src == "vk":
            vk_id = user_id

        if src == "tg":
            tg_id = user_id

        if src == "alice":
            alice_id = user_id

        with self.run_cursor() as cursor:
            query = None
            if vk_id is not None:
                query = f"""
                    SELECT id FROM users WHERE
                    vk_id = {vk_id};
                """

            elif tg_id is not None:
                query = f"""
                    SELECT id FROM users WHERE
                    tg_id = {tg_id};
                """

            elif alice_id is not None:
                query = f"""
                    SELECT id FROM users WHERE
                    alice_id = '{alice_id}';
                """

            cursor.execute(query)
            users_fetch = cursor.fetchone()

            if users_fetch is None:
                return None
            users_fetch = users_fetch[0]
            logger.log("users_db_parser", f"returning global_id: {users_fetch}")
            return users_fetch

    def get_user_info_by_global_id(self, global_id=None):
        with self.run_cursor() as cursor:
            if global_id is not None:
                query = f"""
                    SELECT * FROM users WHERE
                    id = {global_id};
                """
                cursor.execute(query)
                users_fetch = cursor.fetchone()

                if users_fetch is None:
                    return None

                column_desc = self.get_columns_info()

                if len(users_fetch) != len(column_desc):
                    logger.log("user_db_manip", f"Каким-то чудом длины не совпадают!")
                    return

                ans_dict = {}
                for it in range(len(users_fetch)):
                    if column_desc[it][1] == "subs":
                        ans_dict[column_desc[it][1]] = jl(users_fetch[it])
                    else:
                        ans_dict[column_desc[it][1]] = users_fetch[it]

                return ans_dict

    def update_user(self, dict_of_changes, user_id, src):
        upd_key = ""

        if src == "vk":
            upd_key = f"vk_id={user_id}"

        if src == "tg":
            upd_key = f"tg_id={user_id}"

        if src == "alice":
            upd_key = f"alice_id='{user_id}'"

        if upd_key == "":
            logger.log("user_db_manip", f"update_user: tg_id and vk_id are None!")
            return None

        with self.run_cursor() as cursor:
            for key, value in dict_of_changes.items():
                if key == "subs":
                    query = f"""UPDATE users SET {key}='{jd(value)}' WHERE {upd_key}"""
                else:
                    query = f"""UPDATE users SET {key}='{value}' WHERE {upd_key}"""
                cursor.execute(query)
            logger.log("user_db_manip", f"{upd_key} updated")

    def get_users_by_subs(self, class_name, lesson=None, group=None):
        ans = []

        with self.run_cursor() as cursor:
            query = f"""
                    SELECT * FROM users;
                """

            cursor.execute(query)
            users_fetch = cursor.fetchall()

            columns = self.get_columns_names()

            for user in users_fetch:
                info = convert_arrays_to_dict(columns, user)
                if info['subs']:
                    if class_name in info['subs'].keys():
                        if group is None:
                            ans.append(info['id'])
                        else:
                            if group in info['subs'].get(lesson, []):
                                ans.append(info['id'])

        return ans

    def get_all_users(self):
        with self.run_cursor() as cursor:
            query = f"""
                SELECT id FROM users;
            """

            cursor.execute(query)
            users_fetch = cursor.fetchall()

            ans = []

            for user_id in users_fetch:
                ans.append(self.get_user_info_by_global_id(user_id[0]))

            return ans

    def get_debts(self, user_id, src):
        global_id = self.get_global_id_by_user_id(user_id, src)

        with self.run_cursor() as cursor:
            query = f"""
                SELECT * FROM debts WHERE user_id = {global_id} and is_active = 1;
            """

            cursor.execute(query)
            debts_fetch = cursor.fetchall()

            ans = []

            for elem in debts_fetch:
                debt = {}
                for field_name, field_val in zip(self.get_columns_names("debts"), elem):
                    debt[field_name] = field_val
                ans.append(debt)

            return ans

    def disable_debt(self, user_id, src, debt_id):
        global_id = self.get_global_id_by_user_id(user_id, src)

        with self.run_cursor() as cursor:
            query = f"""UPDATE debts SET is_active=0 WHERE user_id = {global_id} and id = {debt_id}"""
            cursor.execute(query)
        logger.log("user_db_manip", f"{debt_id} disabled")

    def setup_db(self, activate=True):
        if activate:
            self.create_users_db()
            self.create_debts_db()


if __name__ == '__main__':
    req = UserDbReq()
    req.setup_db(False)
    # req.add_debt(400, "vk", "Бля, долги по литре", "Литра", "20190808")
