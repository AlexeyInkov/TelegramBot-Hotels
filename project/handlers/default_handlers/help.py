from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS, CUSTOMS_COMMANDS
from loader import bot


@bot.message_handler(commands=["help"])
def bot_help(message: Message):
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS] + [f"/{command} - {desk}" for command, desk in CUSTOMS_COMMANDS]

    bot.reply_to(message, "\n".join(text))
