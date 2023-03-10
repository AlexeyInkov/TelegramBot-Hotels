from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def city(city_dict: dict) -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(row_width=1)
	for key, value in city_dict.items():
		keyboard.add(InlineKeyboardButton(text=value, callback_data=str(key)))
	return keyboard
