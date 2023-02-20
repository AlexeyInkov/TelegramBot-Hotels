from telebot.types import Message
from loader import bot


@bot.message_handler(commands=["lowprice"])
def bot_lowprice(message: Message):
    bot.reply_to(message, f"lowprice, {message.from_user.full_name}!")
