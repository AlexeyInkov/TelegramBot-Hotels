from telebot.types import Message
from loader import bot
from loguru import logger


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!")
    logger.debug('Привет {} (вход)'.format(message.from_user.full_name))
