from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def city(city_dict: dict) -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(row_width=1)
	for key in city_dict:
		keyboard.add(InlineKeyboardButton(text=city_dict[key][1], callback_data=str(city_dict[key][0])))
	return keyboard
