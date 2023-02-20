from telebot.types import Message
from loader import bot


@bot.message_handler(commands=["hello"], content_types=['Привет'])
def bot_hello(message: Message):
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!")
