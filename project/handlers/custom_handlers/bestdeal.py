from telebot.types import Message
from loader import bot


@bot.message_handler(commands=["bestdeal"])
def bot_bestdeal(message: Message):
    bot.reply_to(message, f"bestdeal, {message.from_user.full_name}!")
