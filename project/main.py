""" Alexhelper_bot """
import telebot
import os
from hello import hello
#  import loguru  # TODO добавить логирование
from dotenv import load_dotenv


load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == "привет" or message.text == '/hello-world':
        hello(bot, message)
    elif message.text.lower() == "/start":
        bot.send_message(message.from_user.id, "Привет меня зовут Alexhelper")  # TODO добавить подстановку имени
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши привет или /hello-world")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


bot.polling(none_stop=True, interval=0)
