import sqlite3
import time


class DatabaseManager:
    sql_check_main_tb = "SELECT * FROM sqlite_master WHERE type='table' AND name='chatsInfo'"
    sql_create_main_tb = 'CREATE TABLE chatsInfo (chatId INTEGER PRIMARY KEY, type TEXT, time TEXT, winner INTEGER)'
    sql_check_chat_in_main = "SELECT * FROM chatsInfo WHERE chatId='%s'"
    sql_insert_to_main = "INSERT INTO chatsInfo VALUES (?, ?, ?, ?)"
    sql_check_chat_tb = "SELECT * FROM sqlite_master WHERE type='table' AND name='id%s'"
    sql_insert_to_chat_tb = 'CREATE TABLE id%s (userId INTEGER PRIMARY KEY, firstName TEXT, lastName TEXT,' \
                            'userName TEXT, pidorCount INTEGER, isPidor INTEGER)'
    sql_check_user_exist = "SELECT COUNT(*) FROM id%s WHERE userId='%s'"
    sql_create_user = "INSERT INTO id%s VALUES (?, ?, ?, ?, ?, ?)"
    sql_winner_search = 'SELECT * FROM id%s ORDER BY RANDOM() LIMIT 1;'
    sql_users_count = "SELECT COUNT(*) FROM id%s"
    sql_get_time_from_main = "SELECT time FROM chatsInfo WHERE chatId='%s'"
    sql_get_chat_stat = 'SELECT * FROM id%s ORDER BY pidorCount DESC'
    sql_set_winner_main_info = "UPDATE chatsInfo SET time='%s', winner='%s' WHERE chatId='%s'"
    sql_set_winner_count_info = "UPDATE id%s SET pidorCount='%s' WHERE userId='%s'"
    sql_get_winner_id = "SELECT * FROM chatsInfo WHERE chatId='%s'"
    sql_get_winner_full = "SELECT * FROM id%s WHERE userId='%s'"

    def __init__(self, user_message):
        self.msg = user_message
        self.chat_id = user_message.chat.id
        if self.chat_id < 0:
            self.chat_id = -self.msg.chat.id
        self.con = sqlite3.connect('pidors.db')
        self.check_tables_exists(self.chat_id)
        self.last_time = None

    def __del__(self):
        self.con.close()

    def check_tables_exists(self, table_id):
        cur = self.con.cursor()
        print('check table exist - ' + str(table_id))
        if not cur.execute(self.sql_check_main_tb).fetchone():
            cur.execute(self.sql_create_main_tb)
            self.con.commit()

        if not cur.execute(self.sql_check_chat_in_main % self.chat_id).fetchone():
            values = [self.chat_id,
                      str(self.msg.chat.type),
                      None,
                      None]
            cur.execute(self.sql_insert_to_main, values)
            self.con.commit()

        if not cur.execute(self.sql_check_chat_tb % table_id).fetchone():
            cur.execute(self.sql_insert_to_chat_tb % table_id)
            self.con.commit()

    def create_user(self):
        cur = self.con.cursor()
        print("start search")
        cur.execute(self.sql_check_user_exist % (self.chat_id, self.msg.from_user.id))
        if cur.fetchone()[0] == 0:
            print("not found!")
            values = [self.msg.from_user.id,
                      str(self.msg.from_user.first_name),
                      str(self.msg.from_user.last_name),
                      str(self.msg.from_user.username),
                      0,
                      0]
            cur.executemany(self.sql_create_user % self.chat_id, [values])
            self.con.commit()
            print("user created")
            return True
        return False

    def get_random_pidor(self):
        print("start pidor search")
        cur = self.con.cursor()
        cur.execute(self.sql_winner_search % self.chat_id)
        user = list(cur.fetchone())
        cur.execute(self.sql_set_winner_main_info % (int(time.time()), user[0], self.chat_id))
        self.con.commit()
        return user

    def get_players_count(self):
        print("start pidor count")
        cur = self.con.cursor()
        cur.execute(self.sql_users_count % self.chat_id)
        return cur.fetchone()[0]

    def get_last_time(self):
        cur = self.con.cursor()
        cur.execute(self.sql_get_time_from_main % self.chat_id)
        return cur.fetchone()

    def get_winner(self):
        print('start')
        cur = self.con.cursor()
        cur.execute(self.sql_get_winner_id % self.chat_id)
        winner_id = str(cur.fetchone()[3])
        cur.execute(self.sql_get_winner_full % (self.chat_id, winner_id))
        return cur.fetchone()

    def get_stats(self):
        print('stats tart')
        cur = self.con.cursor()
        cur.execute(self.sql_get_chat_stat % self.chat_id)
        stats = list(cur.fetchall())
        return stats
