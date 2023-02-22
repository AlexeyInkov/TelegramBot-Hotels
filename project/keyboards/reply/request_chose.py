from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def chose_y_n() -> ReplyKeyboardMarkup:
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2,)
	keyboard.add(KeyboardButton('yes'), KeyboardButton('no'))
	return keyboard

