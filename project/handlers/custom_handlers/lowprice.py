import telebot.types
from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from loader import bot
from loguru import logger

import datetime

from loader import calendar, calendar_in, calendar_out
from states.search_information import UserInfoState
from utils.misc.api_requests import api_request
from utils.misc.result_output import get_result
from keyboards.reply.chose import y_n
from keyboards.inline.chose import city


lowprice_dict = dict()
now = datetime.datetime.now()


@bot.message_handler(commands=["lowprice"])
def bot_lowprice(message: Message) -> None:
    lowprice_dict[message.from_user.id] = dict()
    lowprice_dict[message.from_user.id]['sort'] = 'PRICE_LOW_TO_HIGH',
    lowprice_dict[message.from_user.id]['filters'] = {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
    logger.debug('{} (вход в lowprice)'.format(message.from_user.full_name))
    bot.send_message(message.chat.id, 'Выберите дату заезда:', reply_markup=calendar.create_calendar(
        name=calendar_in.prefix,
        year=now.year,
        month=now.month)
                     )
    bot.set_state(message.from_user.id, UserInfoState.lp_date_in)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_in.prefix))
def get_date_in(call: CallbackQuery) -> None:
    name, action, year, month, day = call.data.split(calendar_in.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month,
                                           day=day)
    if action == 'DAY':
        logger.debug('{} Заезд {}/{}/{}'.format(call.from_user.full_name, day, month, year))
        lowprice_dict[call.from_user.id]['date_in'] = {'day': int(date.strftime("%d")),
                                                       'month': int(date.strftime("%m")),
                                                       'year': int(date.strftime("%Y"))
                                                       }
        bot.send_message(
            chat_id=call.from_user.id,
            text='Выберите дату выезда:',
            reply_markup=calendar.create_calendar(
                name=calendar_out.prefix,
                year=now.year,
                month=now.month
            )
        )
        bot.set_state(call.from_user.id, UserInfoState.lp_date_out)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_out.prefix))
def get_date_out(call: CallbackQuery) -> None:
    name, action, year, month, day = call.data.split(calendar_out.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month,
                                           day=day)
    if action == 'DAY':
        lowprice_dict[call.from_user.id]['date_out'] = {'day': int(date.strftime("%d")),
                                                        'month': int(date.strftime("%m")),
                                                        'year': int(date.strftime("%Y"))
                                                        }
        bot.send_message(call.from_user.id, 'В каком городе будем искать?\n(Россия временно не работает)')
        bot.set_state(call.from_user.id, UserInfoState.lp_city)
        logger.debug('{} Выезд {}/{}/{}'.format(call.from_user.full_name, day, month, year))


@bot.message_handler(state=UserInfoState.lp_city)
def get_city(message: Message) -> None:
    # Переменные запроса
    method_endswith = "locations/v3/search"
    # Запрос поиска города
    response = api_request(method_type="GET",
                           method_endswith=method_endswith,
                           params={"q": message.text, "locale": "ru_RU"})
    lowprice_dict[message.from_user.id]['chose_city'] = dict()
    # Поиск с атрибутом CITY
    key = 0
    for answer in response['sr']:
        if answer['type'] == 'CITY':
            lowprice_dict[message.from_user.id]['chose_city'][key] =\
                (answer['gaiaId'], answer['regionNames']['displayName'])
            key += 1
    if len(lowprice_dict[message.from_user.id]['chose_city']) == 0:
        logger.debug('{} Город не найден.'.format(message.from_user.full_name))
        bot.send_message(message.from_user.id, 'Город не найден. Повторите')
    elif len(lowprice_dict[message.from_user.id]['chose_city']) == 1:
        lowprice_dict[message.from_user.id]['city'] = lowprice_dict[message.from_user.id]['chose_city'][0][0]
        bot.send_message(message.from_user.id, "Сколько вывезти отелей?")
        bot.set_state(message.from_user.id, UserInfoState.lp_count_hotel)
        logger.debug('Запрос от {} id города {}'.format(
            message.from_user.full_name,
            lowprice_dict[message.from_user.id]['city'])
        )
    else:
        bot.send_message(message.from_user.id,
                         'Уточните город?',
                         reply_markup=city(lowprice_dict[message.from_user.id]['chose_city'])
                         )
        bot.set_state(message.from_user.id, UserInfoState.lp_chose_city)
        logger.debug('{} уточняет город .'.format(message.from_user.full_name))
        

@bot.callback_query_handler(func=lambda call: True)
def chose_city(call: CallbackQuery) -> None:
    print(lowprice_dict[call.from_user.id]['chose_city'])
    for key in lowprice_dict[call.from_user.id]['chose_city']:
        if call.data == lowprice_dict[call.from_user.id]['chose_city'][key][0]:
            lowprice_dict[call.from_user.id]['city'] = call.data
            logger.debug('{} прилетело:{}'.format(call.from_user.full_name, call.data))
            bot.send_message(call.from_user.id, "Сколько вывезти отелей?")
            bot.set_state(call.from_user.id, UserInfoState.lp_count_hotel)
            logger.debug('Запрос от {} id города {}'.format(
                        call.from_user.full_name,
                        lowprice_dict[call.from_user.id]['city']
                    ))
    else:
        logger.debug('{} не понял, прилетело: {}'.format(call.from_user.full_name, call.data))
        
@bot.message_handler(state=UserInfoState.lp_count_hotel)
def get_count_hotel(message: Message) -> None:
    if message.text.isdigit():
        lowprice_dict[message.from_user.id]['count_hotel'] = message.text
        bot.send_message(message.from_user.id, 'Нужны фото?', reply_markup=y_n())
        bot.set_state(message.from_user.id, UserInfoState.lp_photo, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Необходимо ввести число')
    
        

@bot.message_handler(state=UserInfoState.lp_photo)
def get_photo(message: Message) -> None:
    if message.text.lower() == 'yes':
        lowprice_dict[message.from_user.id]['photo'] = True
        bot.send_message(message.from_user.id, 'Сколько нужно фото?\nНе более 10 шт.', reply_markup=None)
        bot.set_state(message.from_user.id, UserInfoState.lp_count_photo, message.chat.id)
    else:
        lowprice_dict[message.from_user.id]['photo'] = False
        get_result(message=message, dict_set=lowprice_dict)
    
        
@bot.message_handler(state=UserInfoState.lp_count_photo)
def get_count_photo(message: Message) -> None:
    if message.text.isdigit():
        if int(message.text) <= 10:
            lowprice_dict[message.from_user.id]['count_photo'] = message.text
        else:
            lowprice_dict[message.from_user.id]['count_photo'] = 10
        get_result(message=message, dict_set=lowprice_dict)
    else:
        bot.send_message(message.from_user.id, 'Необходимо ввести число')
