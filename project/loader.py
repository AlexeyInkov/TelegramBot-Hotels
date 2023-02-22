from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from loguru import logger


storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
logger.add('/log/info.log', format='{time} {level} {message}', rotation='10:00', compression='zip')