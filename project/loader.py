from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from loguru import logger
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from config_data import config


storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
calendar = Calendar(language=RUSSIAN_LANGUAGE)
data_calendar = CallbackData('calendar_in', 'action', 'year', 'month', 'day')
logger.add('../log/info.log', format='{time} {level} {message}', rotation='1 MB', compression='zip')
