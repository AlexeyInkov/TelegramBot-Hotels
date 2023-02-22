import telebot
from telebot.types import Message
from loader import bot
from loguru import logger
from states.search_information import UserInfoState
from utils.misc.api_requests import api_request
from utils.misc.result_output import get_result
from keyboards.reply.request_chose import chose_y_n


lowprice_dict = dict()


@bot.message_handler(commands=["lowprice"])
def bot_lowprice(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.lp_city, message.chat.id)
    bot.send_message(message.from_user.id, 'В каком городе будем искать?\n(Россия временно не работает)')
    lowprice_dict[message.from_user.id] = dict()


@bot.message_handler(state=UserInfoState.lp_city)
def get_city(message: Message) -> None:
    # Переменные запроса
    method_endswith = "locations/v3/search"
    querystring = {"q": message.text, "locale": "ru_RU"}
    # Запрос поиска города
    response = api_request(method_type="GET", method_endswith=method_endswith, params=querystring)
    for answer in response['sr']:
        if answer['type'] == 'CITY':
            lowprice_dict[message.from_user.id]['city'] = (answer['gaiaId'], answer['regionNames']['displayName'])
            lowprice_dict[message.from_user.id]['sort'] = 'PRICE_LOW_TO_HIGH'
            break
    try:
        bot.send_message(message.from_user.id, f"Ищем в {lowprice_dict[message.from_user.id]['city'][1]}\n"
                                               f"Сколько вывезти отелей в {message.text}")
        bot.set_state(message.from_user.id, UserInfoState.lp_count_hotel, message.chat.id)
        logger.debug('Запрос от {} в городе {}'.format(message.from_user.full_name,
                                                       lowprice_dict[message.from_user.id]['city'][1])
                     )
    except KeyError:
        logger.debug('{} Город не найден.'.format(message.from_user.full_name))
        bot.send_message(message.from_user.id, 'Город не найден. Повторите')
        


@bot.message_handler(state=UserInfoState.lp_count_hotel)
def get_count_hotel(message: Message) -> None:
    if message.text.isdigit():
        lowprice_dict[message.from_user.id]['count_hotel'] = message.text
        bot.send_message(message.from_user.id, 'Нужны фото?', reply_markup=chose_y_n())
        bot.set_state(message.from_user.id, UserInfoState.lp_photo, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Необходимо ввести число')
        

@bot.message_handler(state=UserInfoState.lp_photo)
def get_photo(message: Message) -> None:
    if message.text.lower() == 'yes':
        lowprice_dict[message.from_user.id]['photo'] = True
        bot.send_message(message.from_user.id, 'Сколько нужно фото?')
        bot.set_state(message.from_user.id, UserInfoState.lp_count_photo, message.chat.id)
    else:
        lowprice_dict[message.from_user.id]['photo'] = False
        get_result(message=message, dict_set=lowprice_dict)
    d = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, '', reply_markup=d)
        

@bot.message_handler(state=UserInfoState.lp_count_photo)
def get_photo(message: Message) -> None:
    if message.text.isdigit():
        lowprice_dict[message.from_user.id]['count_photo'] = message.text
        get_result(message=message, dict_set=lowprice_dict)
    else:
        bot.send_message(message.from_user.id, 'Необходимо ввести число')
