import time
from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from loader import bot
from loguru import logger
import datetime

from loader import calendar, calendar_in
from states.search_information import UserInfoState
from utils.misc.api_requests import api_request
from utils.misc.result_output import get_result
from keyboards.reply.chose import y_n
from keyboards.inline.chose import city


lowprice_dict = dict()
now = datetime.datetime.now()


@bot.message_handler(commands=["lowprice"])
def bot_lowprice(message: Message) -> None:
    lowprice_dict[message.from_user.id] = {
        'command_name': 'lowprice',
        'command_time': now,
        'command_param': {
            'count_photo': 0,
            'price_min': 0,
            'price_max': 0,
            'hotel_distance_min': 0,
            'hotel_distance_max': 0,
            'sort': 'PRICE_LOW_TO_HIGH',
            'filters': {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
        }
    }
    logger.debug('{} (вход в lowprice)'.format(message.from_user.full_name))
    bot.send_message(message.chat.id, 'Выберите дату заезда:', reply_markup=calendar.create_calendar(
        name=calendar_in.prefix,
        year=now.year,
        month=now.month)
    )
    bot.set_state(message.from_user.id, UserInfoState.lp_date_in)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_in.prefix), state=UserInfoState.lp_date_in)
def get_date_in(call: CallbackQuery) -> None:
    name, action, year, month, day = call.data.split(calendar_in.sep)
    # date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month,
    #                                        day=day)
    if action == 'DAY':
        logger.debug('{} Заезд {}/{}/{}'.format(call.from_user.full_name, day, month, year))
        lowprice_dict[call.from_user.id]['command_param']['date_in_dict'] = {
            'day': int(day),
            'month': int(month),
            'year': int(year)
        }
        
        bot.send_message(
            chat_id=call.from_user.id,
            text='Понял заезжаем {}/{}/{}\nВыберите дату выезда:'.format(day, month, year),
            reply_markup=calendar.create_calendar(
                name=calendar_in.prefix,
                year=now.year,
                month=now.month
            )
        )
        
        bot.set_state(call.from_user.id, UserInfoState.lp_date_out)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_in.prefix), state=UserInfoState.lp_date_out)
def get_date_out(call: CallbackQuery) -> None:
    name, action, year, month, day = call.data.split(calendar_in.sep)
    # date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month,
    #                                        day=day)
    if action == 'DAY':
        lowprice_dict[call.from_user.id]['command_param']['date_out_dict'] = {
            'day': int(day),
            'month': int(month),
            'year': int(year)
        }
        date_out = datetime.date(
            lowprice_dict[call.from_user.id]['command_param']['date_out_dict']['year'],
            lowprice_dict[call.from_user.id]['command_param']['date_out_dict']['month'],
            lowprice_dict[call.from_user.id]['command_param']['date_out_dict']['day']
        )
        date_in = datetime.date(
            lowprice_dict[call.from_user.id]['command_param']['date_in_dict']['year'],
            lowprice_dict[call.from_user.id]['command_param']['date_in_dict']['month'],
            lowprice_dict[call.from_user.id]['command_param']['date_in_dict']['day']
        )
        hotel_night = (date_out - date_in).days
        lowprice_dict[call.from_user.id]['command_param']['date_in'] = date_in
        lowprice_dict[call.from_user.id]['command_param']['date_out'] = date_out
        lowprice_dict[call.from_user.id]['command_result'] = {'hotel_night': hotel_night}
        bot.send_message(call.from_user.id, 'Понял выезжаем {}/{}/{}\n'
                                            'Посчитаем сколько ночей\n'.format(day, month, year))
        bot.send_message(call.from_user.id, '...')
        time.sleep(1)  # чтобы не склонять слово день
        bot.send_message(call.from_user.id, '{}\n'
                                            'В каком городе будем искать?\n'
                                            '(Россия временно не работает)'.format(hotel_night))
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
    lowprice_dict[message.from_user.id]['command_param']['chose_city'] = dict()
    # Поиск с атрибутом CITY
    key = 0
    try:
        for answer in response['sr']:
            if answer['type'] == 'CITY':
                lowprice_dict[message.from_user.id]['command_param']['chose_city'][key] =\
                    (answer['gaiaId'], answer['regionNames']['displayName'])
                key += 1
    except TypeError:
        bot.send_message(
            message.from_user.id,
            "{} возникли проблемы с выполнение запроса.\nПопробуйте позже".format(message.from_user.full_name))
    else:
        if len(lowprice_dict[message.from_user.id]['command_param']['chose_city']) == 0:
            logger.debug('{} Город не найден.'.format(message.from_user.full_name))
            bot.send_message(message.from_user.id, 'Город не найден. Повторите')
        elif len(lowprice_dict[message.from_user.id]['command_param']['chose_city']) == 1:
            lowprice_dict[message.from_user.id]['city'] =\
                lowprice_dict[message.from_user.id]['command_param']['chose_city'][0][1]
            lowprice_dict[message.from_user.id]['city_id'] =\
                lowprice_dict[message.from_user.id]['command_param']['chose_city'][0][0]
            bot.send_message(
                message.from_user.id,
                "Понял город {}\nСколько вывезти отелей?".format(lowprice_dict[message.from_user.id]['city']))
            bot.set_state(message.from_user.id, UserInfoState.lp_count_hotel)
            logger.debug('Запрос от {} id города {}'.format(
                message.from_user.full_name,
                lowprice_dict[message.from_user.id]['city_id'])
            )
        else:
            bot.send_message(
                message.from_user.id,
                'Нашлось несколько вариантов\nУточните нужный Вам город.\nНажми на соответствующую кнопку.',
                reply_markup=city(lowprice_dict[message.from_user.id]['command_param']['chose_city'])
            )
            bot.set_state(message.from_user.id, UserInfoState.lp_chose_city)
            logger.debug('{} уточняет город .'.format(message.from_user.full_name))
        

@bot.callback_query_handler(func=lambda call: True, state=UserInfoState.lp_chose_city)
def chose_city(call: CallbackQuery) -> None:
    for key in lowprice_dict[call.from_user.id]['command_param']['chose_city']:
        if call.data == lowprice_dict[call.from_user.id]['command_param']['chose_city'][key][0]:
            lowprice_dict[call.from_user.id]['city_id'] = call.data
            lowprice_dict[call.from_user.id]['city'] =\
                lowprice_dict[call.from_user.id]['command_param']['chose_city'][key][1]
            logger.debug('{} прилетело:{}'.format(call.from_user.full_name, call.data))
            bot.send_message(
                call.from_user.id,
                "Понял город {}\nСколько вывезти отелей?".format(lowprice_dict[call.from_user.id]['city']))
            bot.set_state(call.from_user.id, UserInfoState.lp_count_hotel)
            logger.debug('Запрос от {} id города {}'.format(
                        call.from_user.full_name,
                        lowprice_dict[call.from_user.id]['city_id']
                        )
            )
            break
    else:
        logger.debug('{} не понял, прилетело: {}'.format(call.from_user.full_name, call.data))
        

@bot.message_handler(state=UserInfoState.lp_count_hotel)
def get_count_hotel(message: Message) -> None:
    if message.text.isdigit():
        lowprice_dict[message.from_user.id]['command_param']['count_hotel'] = message.text
        bot.send_message(
            message.from_user.id,
            'Понял выводим ТОП{} недорогих отелей города {}\nДобавить фото?'.format(
                lowprice_dict[message.from_user.id]['command_param']['count_hotel'],
                lowprice_dict[message.from_user.id]['city']
            ),
            reply_markup=y_n()
        )
        bot.set_state(message.from_user.id, UserInfoState.lp_photo, message.chat.id)
        logger.debug('{} запросил ТОП{} недорогих отелей'.format(message.from_user.full_name, message.text))
    else:
        bot.send_message(message.from_user.id, 'Необходимо ввести число')
        logger.debug('{} ввел не корректное число отелей'.format(message.from_user.full_name))
        

@bot.message_handler(state=UserInfoState.lp_photo)
def get_photo(message: Message) -> None:
    if message.text.lower() == 'yes':
        lowprice_dict[message.from_user.id]['command_param']['photo'] = True
        bot.send_message(
            message.from_user.id,
            'А сколько загрузить фото?\nНо не более 10 шт.',
            reply_markup=ReplyKeyboardRemove()
        )
        bot.set_state(message.from_user.id, UserInfoState.lp_count_photo, message.chat.id)
        logger.debug('{} хочет получить фото'.format(message.from_user.full_name))
    else:
        lowprice_dict[message.from_user.id]['command_param']['photo'] = False
        logger.debug('{} делает запрос к API'.format(message.from_user.full_name))
        get_result(message=message, dict_set=lowprice_dict)
    
        
@bot.message_handler(state=UserInfoState.lp_count_photo)
def get_count_photo(message: Message) -> None:
    if message.text.isdigit():
        if int(message.text) <= 10:
            lowprice_dict[message.from_user.id]['command_param']['count_photo'] = message.text
        else:
            lowprice_dict[message.from_user.id]['command_param']['count_photo'] = 10
        logger.debug('{} делает запрос к API'.format(message.from_user.full_name))
        get_result(message=message, dict_set=lowprice_dict)
    else:
        bot.send_message(message.from_user.id, 'Необходимо ввести число')
        logger.debug('{} ввел не корректное число фото'.format(message.from_user.full_name))
