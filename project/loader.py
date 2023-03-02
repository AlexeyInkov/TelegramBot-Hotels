from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from loguru import logger
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE


storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_in = CallbackData('calendar_in', 'action', 'year', 'month', 'day')
logger.add('log/info.log', format='{time} {level} {message}', compression='zip')
