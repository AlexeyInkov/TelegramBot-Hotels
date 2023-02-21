from telebot.types import Message
from loader import bot
from states.search_information import UserInfoState
from utils.misc.api_requests import api_request
import json


@bot.message_handler(commands=["lowprice"])
def bot_lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.lp_city, message.chat.id)
    bot.send_message(message.from_user.id, 'В каком городе будем искать?')


@bot.message_handler(state=UserInfoState.lp_city)
def get_city(message: Message) -> None:
    # params = dict()
    # params['q'] = message.text
    # params["locale"] = "ru_RU"
    # response = api_request(method_type='GET', method_endswith='locations/v3/search', params=params).json
    # id_sity = response['sr'][0]['gaiaId']
    # short_name_city = response['sr'][0]['regionNames']['shortName']
    # bot.send_message(message.from_user.id, f'{short_name_city}?')
    bot.send_message(message.from_user.id, f'Сколько вывезти отелей в {message.text}')
    bot.set_state(message.from_user.id, UserInfoState.lp_count_hotel, message.chat.id)


@bot.message_handler(state=UserInfoState.lp_count_hotel)
def get_count_hotel(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Нужны фото?')
    bot.set_state(message.from_user.id, UserInfoState.lp_photo, message.chat.id)


@bot.message_handler(state=UserInfoState.lp_photo)
def get_photo(message: Message) -> None:

    if message.text.lower() == 'да':
        bot.send_message(message.from_user.id, 'Сколько нужно фото?')
        bot.set_state(message.from_user.id, UserInfoState.lp_count_photo, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'печать результата без фото')


@bot.message_handler(state=UserInfoState.lp_count_photo)
def get_photo(message: Message) -> None:
    bot.send_message(message.from_user.id, 'печать результата c фото')
