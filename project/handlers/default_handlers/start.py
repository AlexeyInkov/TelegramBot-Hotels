from telebot.types import Message
from loader import bot
from loguru import logger


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    bot.reply_to(
        message,
        f"Привет, {message.from_user.full_name}!\n"
        f"Меня зовут {bot.get_me().full_name}\n"
        f"Я помогу тебе подобрать отель\n"
        f"Чтобы узнать что я могу, набери \help"
    )
    logger.debug('Привет {} (вход)'.format(message.from_user.full_name))
