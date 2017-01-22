import telebot
from key import key

from .DatabaseManager import DatabaseManager


class RegistrationManager:
    def __init__(self, user_message):
        self.dm = DatabaseManager(user_message)
        self.msg = user_message
        self.chat_id = user_message.chat.id

    def create_user(self):
        bot = telebot.TeleBot(key)
        print('start user creation')
        if self.dm.create_user():
            bot.send_message(self.chat_id, 'Голубок готов к игре!')
        else:
            bot.send_message(self.chat_id, 'Такой уже есть!')
