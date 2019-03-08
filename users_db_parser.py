import sqlite3
import logger
import answers_dict as ad


class MyCursor(sqlite3.Cursor):
    def __init__(self, connection):
        super(MyCursor, self).__init__(connection)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        self.close()


class UserDbReq:
    def __init__(self, database_name="1543.eljur.bot.db"):
        self.database_name = database_name

    def run(self, function=None, *args):
        with sqlite3.connect(self.database_name, isolation_level=None) as connection, MyCursor(connection) as cursor:
            if function is not None:
                ans = function(*args, cursor=cursor)
                connection.commit()
                if ans is not None:
                    return ans

    def create_users_db(self, cursor):
        name = "users"

        query = f"""
            create table {name}
            (
                id integer not null
                   primary key autoincrement,
                first_name text not null,
                last_name text not null,
                class text,
                confirmed int not null, 
                status text not null,
                request text,
                vk_id int unique,
                tg_id int unique 
            );
        """

        cursor.execute(query)
        logger.log("user_db_manip", f"created table: '{name}'")

    def del_table(self, table, cursor):
        query = f'DROP TABLE IF EXISTS {table}'

        cursor.execute(query)
        logger.log("user_db_manip", f"table '{table}' deleted!")

    def add_user(self, first_name, last_name, vk_id="NULL", tg_id="NULL", cursor=None):
        query = f"""
            INSERT INTO users (first_name, last_name, class, confirmed, status, vk_id, tg_id) 
            VALUES('{first_name}', '{last_name}', null, 0, 'reg0', {vk_id}, {tg_id})
        """
        cursor.execute(query)
        logger.log("user_db_manip", f"user '{first_name} {last_name}' created!")

    def get_columns_info(self, table="users", cursor=None):
        query = f"""
            PRAGMA table_info({table})
        """

        cursor.execute(query)
        description = cursor.fetchall()
        return description

    def get_user_info(self, vk_id=None, tg_id=None, cursor=None):
        if vk_id is not None:
            query = f"""
                SELECT * FROM users WHERE
                vk_id = {vk_id};
            """
            cursor.execute(query)
            users_fetch = cursor.fetchone()

            if users_fetch is None:
                return None

            column_desc = self.get_columns_info(cursor=cursor)

            if len(users_fetch) != len(column_desc):
                logger.log("user_db_manip", f"Каким-то чудом длины не совпадают!")
                return

            ans_dict = {}
            for it in range(len(users_fetch)):
                ans_dict[column_desc[it][1]] = users_fetch[it]

            return ans_dict

        if tg_id is not None:
            query = f"""
                            SELECT * FROM users WHERE
                            tg_id = {tg_id};
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
                ans_dict[column_desc[it][1]] = users_fetch[it]

            return ans_dict


    def get_user_info_by_global_id(self, global_id=None, cursor=None):
        if global_id is not None:
            query = f"""
                SELECT * FROM users WHERE
                id = {global_id};
            """
            cursor.execute(query)
            users_fetch = cursor.fetchone()

            if users_fetch is None:
                return None

            column_desc = self.get_columns_info(cursor=cursor)

            if len(users_fetch) != len(column_desc):
                logger.log("user_db_manip", f"Каким-то чудом длины не совпадают!")
                return

            ans_dict = {}
            for it in range(len(users_fetch)):
                ans_dict[column_desc[it][1]] = users_fetch[it]

            return ans_dict


    def update_user(self, dict_of_changes, vk_id=None, tg_id=None, cursor=None):
        for key, value in dict_of_changes.items():
            query = f"""UPDATE users SET {key}='{value}' WHERE vk_id={vk_id}"""
            cursor.execute(query)
        logger.log("user_db_manip", f"{vk_id} updated")

    def setup_db(self):
        self.run(self.del_table, "users")
        self.run(self.create_users_db)


if __name__ == '__main__':
    req = UserDbReq()
    req.setup_db()
