from telebot.types import Message
from loader import bot


@bot.message_handler(commands=["hello"])
def bot_hello(message: Message):
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!")
