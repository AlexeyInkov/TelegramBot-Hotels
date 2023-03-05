from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from loader import bot
from loguru import logger
import json
import datetime

from loader import calendar, calendar_in
from states.search_information import UserInfoState
from utils.misc.api_requests import api_request
from utils.misc.result_output import get_result
from keyboards.reply.chose import y_n
from keyboards.inline.chose import city

highprice_dict = dict()
now = datetime.datetime.now()


@bot.message_handler(commands=["highprice"])
def bot_highprice(message: Message) -> None:
    highprice_dict[message.from_user.id] = {
        'sort': 'PRICE_HIGH_TO_LOW',
        'filters': {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
    }
    logger.debug('{} (вход в highprice)'.format(message.from_user.full_name))
    bot.send_message(message.chat.id, 'Выберите дату заезда:', reply_markup=calendar.create_calendar(
        name=calendar_in.prefix,
        year=now.year,
        month=now.month)
                     )
    bot.set_state(message.from_user.id, UserInfoState.hp_date_in)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_in.prefix), state=UserInfoState.hp_date_in)
def get_date_in(call: CallbackQuery) -> None:
    name, action, year, month, day = call.data.split(calendar_in.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month,
                                           day=day)
    if action == 'DAY':
        logger.debug('{} Заезд {}/{}/{}'.format(call.from_user.full_name, day, month, year))
        highprice_dict[call.from_user.id]['date_in'] = {'day': int(date.strftime("%d")),
                                                        'month': int(date.strftime("%m")),
                                                        'year': int(date.strftime("%Y"))
                                                        }
        bot.send_message(
            chat_id=call.from_user.id,
            text='Выберите дату выезда:',
            reply_markup=calendar.create_calendar(
                name=calendar_in.prefix,
                year=now.year,
                month=now.month
            )
        )
        bot.set_state(call.from_user.id, UserInfoState.hp_date_out)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_in.prefix), state=UserInfoState.hp_date_out)
def get_date_out(call: CallbackQuery) -> None:
    name, action, year, month, day = call.data.split(calendar_in.sep)
    date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month,
                                           day=day)
    if action == 'DAY':
        highprice_dict[call.from_user.id]['date_out'] = {'day': int(date.strftime("%d")),
                                                         'month': int(date.strftime("%m")),
                                                         'year': int(date.strftime("%Y"))
                                                         }
        bot.send_message(call.from_user.id, 'В каком городе будем искать?\n(Россия временно не работает)')
        bot.set_state(call.from_user.id, UserInfoState.hp_city)
        logger.debug('{} Выезд {}/{}/{}'.format(call.from_user.full_name, day, month, year))


@bot.message_handler(state=UserInfoState.hp_city)
def get_city(message: Message) -> None:
    # Переменные запроса
    method_endswith = "locations/v3/search"
    # Запрос поиска города
    response = api_request(method_type="GET",
                           method_endswith=method_endswith,
                           params={"q": message.text, "locale": "ru_RU"})
    highprice_dict[message.from_user.id]['chose_city'] = dict()
    # Поиск с атрибутом CITY
    key = 0
    for answer in response['sr']:
        if answer['type'] == 'CITY':
            highprice_dict[message.from_user.id]['chose_city'][key] = \
                (answer['gaiaId'], answer['regionNames']['displayName'])
            key += 1
    if len(highprice_dict[message.from_user.id]['chose_city']) == 0:
        logger.debug('{} Город не найден.'.format(message.from_user.full_name))
        bot.send_message(message.from_user.id, 'Город не найден. Повторите')
    elif len(highprice_dict[message.from_user.id]['chose_city']) == 1:
        highprice_dict[message.from_user.id]['city'] = highprice_dict[message.from_user.id]['chose_city'][0][0]
        bot.send_message(message.from_user.id, "Сколько вывезти отелей?")
        bot.set_state(message.from_user.id, UserInfoState.hp_count_hotel)
        logger.debug('Запрос от {} id города {}'.format(
            message.from_user.full_name,
            highprice_dict[message.from_user.id]['city'])
        )
    else:
        bot.send_message(message.from_user.id,
                         'Уточните город?',
                         reply_markup=city(highprice_dict[message.from_user.id]['chose_city'])
                         )
        bot.set_state(message.from_user.id, UserInfoState.hp_chose_city)
        logger.debug('{} уточняет город .'.format(message.from_user.full_name))


@bot.callback_query_handler(func=lambda call: True, state=UserInfoState.hp_chose_city)
def chose_city(call: CallbackQuery) -> None:
    for key in highprice_dict[call.from_user.id]['chose_city']:
        if call.data == highprice_dict[call.from_user.id]['chose_city'][key][0]:
            highprice_dict[call.from_user.id]['city'] = call.data
            logger.debug('{} прилетело:{}'.format(call.from_user.full_name, call.data))
            bot.send_message(call.from_user.id, "Сколько вывезти отелей?")
            bot.set_state(call.from_user.id, UserInfoState.hp_count_hotel)
            logger.debug('Запрос от {} id города {}'.format(
                call.from_user.full_name,
                highprice_dict[call.from_user.id]['city']
            ))
    else:
        logger.debug('{} не понял, прилетело: {}'.format(call.from_user.full_name, call.data))


@bot.message_handler(state=UserInfoState.hp_count_hotel)
def get_count_hotel(message: Message) -> None:
    if message.text.isdigit():
        highprice_dict[message.from_user.id]['count_hotel'] = message.text
        bot.send_message(message.from_user.id, 'Нужны фото?', reply_markup=y_n())
        bot.set_state(message.from_user.id, UserInfoState.hp_photo, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Необходимо ввести число')


@bot.message_handler(state=UserInfoState.hp_photo)
def get_photo(message: Message) -> None:
    with open('log/param.json', 'w') as js:
        json.dump(highprice_dict, js, indent=4)
    print(highprice_dict)
    if message.text.lower() == 'yes':
        highprice_dict[message.from_user.id]['photo'] = True
        bot.send_message(
            message.from_user.id,
            'Сколько нужно фото?\nНе более 10 шт.',
            reply_markup=ReplyKeyboardRemove()
        )
        bot.set_state(message.from_user.id, UserInfoState.hp_count_photo, message.chat.id)
    else:
        highprice_dict[message.from_user.id]['photo'] = False
        get_result(message=message, dict_set=highprice_dict)


@bot.message_handler(state=UserInfoState.hp_count_photo)
def get_count_photo(message: Message) -> None:
    if message.text.isdigit():
        if int(message.text) <= 10:
            highprice_dict[message.from_user.id]['count_photo'] = message.text
        else:
            highprice_dict[message.from_user.id]['count_photo'] = 10
        get_result(message=message, dict_set=highprice_dict)
    else:
        bot.send_message(message.from_user.id, 'Необходимо ввести число')
