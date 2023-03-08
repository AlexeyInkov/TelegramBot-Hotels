from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def link(url: str) -> InlineKeyboardMarkup:
	keyboard = InlineKeyboardMarkup(row_width=1)
	keyboard.add(InlineKeyboardButton(text='Перейти на страницу отеля', url=url))
	return keyboard
