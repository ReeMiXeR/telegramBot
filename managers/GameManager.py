import random
import time as ttime
from datetime import *

import telebot

import dictionary
from key import key
from .DatabaseManager import DatabaseManager


class GameManager:
    def __init__(self, user_message):
        self.dm = DatabaseManager(user_message)
        self.msg = user_message
        self.chat_id = user_message.chat.id
        self.bot = telebot.TeleBot(key)

    def start_game(self):
        # убогий момент начало
        user_count = int(self.dm.get_players_count())
        if user_count == 0:
            self.bot.send_message(self.msg.chat.id, dictionary.need_sign_up)
        elif user_count == 1:
            self.bot.send_message(self.msg.chat.id, dictionary.one_user)
        elif user_count > 1:
            if self.check_time():
                self.get_new_winner()
            else:
                self.get_current_winner()

    def get_stats(self):
        stats = list(self.dm.get_stats())
        print(stats)
        self.make_stats_msg(stats)
        self.bot.send_message(self.msg.chat.id, stats)

    def make_stats_msg(self, stats):
        list(stats)
        response_str = 'Рейтинг пидоров:' + '\n' + '\n'
        for q in range(len(stats)):
            user = self.User(stats[q])
            response_str += str(q) + '. ' + self.choose_winner_name(user) + ' - ' + str(user.pidor_count) + '\n'
        self.bot.send_message(self.msg.chat.id, response_str)

    def check_time(self):
        # костыль исправить
        last_time = self.dm.get_last_time()[0]
        if last_time is not None:
            last_time = datetime.fromtimestamp(float(self.dm.get_last_time()[0]))
            last_time.replace(hour=0, minute=0)
        now = datetime.now()
        if last_time is None:
            return True
        elif now.replace(hour=0, minute=0) - last_time.replace(hour=0, minute=0) > timedelta(days=1):
            return True
        else:
            return False

    def get_new_winner(self):
        pidor = self.User(self.dm.get_random_pidor())
        self.bot.send_message(self.msg.chat.id, random.choice(dictionary.search_start))
        ttime.sleep(1.5)
        self.bot.send_message(self.msg.chat.id, random.choice(dictionary.search_midlle))
        ttime.sleep(1)
        self.bot.send_message(self.msg.chat.id, random.choice(dictionary.search_end))
        ttime.sleep(2)
        name = self.choose_winner_name(pidor)
        self.bot.send_message(self.msg.chat.id, dictionary.game_win + name)

    def get_current_winner(self):
        winner = self.User(self.dm.get_winner())
        self.bot.send_message(self.msg.chat.id, dictionary.last_winner + str(self.choose_winner_name(winner)))

    @staticmethod
    def choose_winner_name(winner):
        if (winner.first_name is not None) & (winner.second_name is not None):
            return winner.first_name + ' ' + winner.second_name
        return winner.user_name

    class User:
        def __init__(self, response):
            self.id = response[0]
            self.first_name = response[1]
            self.second_name = response[2]
            self.user_name = response[3]
            self.pidor_count = response[4]
            self.is_pidor = response[5]
