import time
import datetime

from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from loguru import logger
from typing import Dict, Any

from loader import bot, calendar, data_calendar
from states.search_information import UserInfoState
from utils.misc.api_requests import api_request
from utils.misc.result_output import get_result
from utils.misc.currency import get_currency_price
from keyboards.reply.choice import yes_or_no
from keyboards.inline.choice import city

command_dict: Dict[int, Dict[str, Any]] = {}


@bot.message_handler(commands=["lowprice", "highprice", "bestdeal"])
def choose_command(message: Message) -> None:
	command_dict[message.from_user.id] = {
		'command_time': datetime.datetime.now(),
		'command_param': {
			'properties-v2-list': {
				'currency': 'USD',
				'eapid': 1,
				'locale': 'ru_RU',
				'siteId': 300000001,
				'destination': {
					'regionId': ''
				},
				'checkInDate': {},
				'checkOutDate': {},
				'rooms': [{'adults': 1}],
				'resultsStartingIndex': 0,
				'resultsSize': 0,
				'sort': '',
				'filters': {
					"price": {
						"max": 1000000,
						"min": 1
					}
				}
			},
			'count_photo': 0,
			'hotel_distance': {
				'min': 0,
				'max': 1000
			}
		}
	}
	if message.text == '/lowprice':
		command_dict[message.from_user.id]['command_name'] = 'lowprice'
		command_dict[message.from_user.id]['command_param']['properties-v2-list']['sort'] = 'PRICE_LOW_TO_HIGH'
	elif message.text == '/highprice':
		command_dict[message.from_user.id]['command_name'] = 'highprice'
		command_dict[message.from_user.id]['command_param']['properties-v2-list']['sort'] = 'PRICE_HIGH_TO_LOW'
	else:
		command_dict[message.from_user.id]['command_name'] = 'bestdeal'
		command_dict[message.from_user.id]['command_param']['properties-v2-list']['sort'] = 'PRICE_LOW_TO_HIGH'
	logger.debug('{} ввел команду {}'.format(message.from_user.full_name, message.text))
	bot.send_message(
		message.from_user.id,
		'{} в каком городе будем подбирать отель?\n(РОССИЯ ВРЕМЕННО НЕ РАБОТАЕТ)'.format(message.from_user.first_name))
	bot.set_state(message.from_user.id, UserInfoState.city)


@bot.message_handler(state=UserInfoState.city)
def get_city(message: Message) -> None:
	now = datetime.datetime.now()
	resp_city = api_request(
		method_type="GET",
		method_endswith="locations/v3/search",
		params={"q": message.text, "locale": "ru_RU"}
	)
	# Поиск с атрибутом CITY
	command_dict[message.from_user.id]['command_param']['chose_city'] = dict()
	try:
		for answer in resp_city['sr']:
			if answer['type'] == 'CITY':
				command_dict[message.from_user.id]['command_param']['chose_city'][answer['gaiaId']] = \
					answer['regionNames']['displayName']
	except TypeError:
		bot.send_message(
			message.from_user.id,
			"{} возникли проблемы с выполнение запроса.\nПопробуйте позже".format(message.from_user.full_name))
	else:
		if len(command_dict[message.from_user.id]['command_param']['chose_city']) == 0:
			logger.debug('{} Город не найден.'.format(message.from_user.full_name))
			bot.send_message(message.from_user.id, 'Город не найден. Повторите')
		elif len(command_dict[message.from_user.id]['command_param']['chose_city']) == 1:
			city_id = list(command_dict[message.from_user.id]['command_param']['chose_city'].keys())[0]
			command_dict[message.from_user.id]['command_param']['properties-v2-list']['destination']['regionId'] = city_id
			command_dict[message.from_user.id]['command_param']['city'] = \
				command_dict[message.from_user.id]['command_param']['chose_city'][city_id]
			bot.send_message(
				message.chat.id,
				'Понял город {}\nВыберите дату заезда:'.format(
					command_dict[message.from_user.id]['command_param']['city']
				),
				reply_markup=calendar.create_calendar(
					name=data_calendar.prefix,
					year=now.year,
					month=now.month
				)
			)
			bot.set_state(message.from_user.id, UserInfoState.date_in)
			logger.debug('Запрос от {} город {}'.format(
					message.from_user.full_name,
					command_dict[message.from_user.id]['command_param']['city']
				)
			)
		else:
			bot.send_message(
				message.from_user.id,
				'Нашлось несколько вариантов\nУточните нужный Вам город.\nНажми на соответствующую кнопку.',
				reply_markup=city(command_dict[message.from_user.id]['command_param']['chose_city'])
			)
			bot.set_state(message.from_user.id, UserInfoState.chose_city)
			logger.debug('{} будет уточнять город .'.format(message.from_user.full_name))
	

@bot.callback_query_handler(func=lambda call: True, state=UserInfoState.chose_city)
def chose_city(call: CallbackQuery) -> None:
	now = datetime.datetime.now()
	for city_id, city_value in command_dict[call.from_user.id]['command_param']['chose_city'].items():
		if call.data == city_id:
			command_dict[call.from_user.id]['command_param']['properties-v2-list']['destination']['regionId'] = city_id
			command_dict[call.from_user.id]['command_param']['city'] = city_value
			logger.debug('{} прилетело:{}'.format(call.from_user.full_name, call.data))
			bot.send_message(
				call.from_user.id,
				'Понял город {}\nВыберите дату заезда:'.format(
					command_dict[call.from_user.id]['command_param']['city']
				),
				reply_markup=calendar.create_calendar(
					name=data_calendar.prefix,
					year=now.year,
					month=now.month
				)
			)
			bot.set_state(call.from_user.id, UserInfoState.date_in)
			logger.debug('Запрос от {} город {}'.format(
					call.from_user.full_name,
					command_dict[call.from_user.id]['command_param']['city']
				)
			)
			break
	else:
		logger.debug('{} не понял, прилетело: {}'.format(call.from_user.full_name, call.data))
	
	
@bot.callback_query_handler(func=lambda call: call.data.startswith(data_calendar.prefix), state=UserInfoState.date_in)
def get_date_in(call: CallbackQuery) -> None:
	now = datetime.datetime.now()
	name, action, year, month, day = call.data.split(data_calendar.sep)
	if action == 'DAY':
		logger.debug('{} Заезд {}/{}/{}'.format(call.from_user.full_name, day, month, year))
		command_dict[call.from_user.id]['command_param']['properties-v2-list']['checkInDate'] = {
			'day': int(day),
			'month': int(month),
			'year': int(year)
		}
		bot.send_message(
			chat_id=call.from_user.id,
			text='Понял заезжаем {}/{}/{}\nВыберите дату выезда:'.format(day, month, year),
			reply_markup=calendar.create_calendar(
				name=data_calendar.prefix,
				year=now.year,
				month=now.month
			)
		)
		bot.set_state(call.from_user.id, UserInfoState.date_out)


@bot.callback_query_handler(func=lambda call: call.data.startswith(data_calendar.prefix), state=UserInfoState.date_out)
def get_date_out(call: CallbackQuery) -> None:
	now = datetime.datetime.now()
	name, action, year, month, day = call.data.split(data_calendar.sep)
	if action == 'DAY':
		command_dict[call.from_user.id]['command_param']['properties-v2-list']['checkOutDate'] = {
			'day': int(day),
			'month': int(month),
			'year': int(year)
		}
		date_in = datetime.date(
			command_dict[call.from_user.id]['command_param']['properties-v2-list']['checkInDate']['year'],
			command_dict[call.from_user.id]['command_param']['properties-v2-list']['checkInDate']['month'],
			command_dict[call.from_user.id]['command_param']['properties-v2-list']['checkInDate']['day']
		)
		date_out = datetime.date(
			command_dict[call.from_user.id]['command_param']['properties-v2-list']['checkOutDate']['year'],
			command_dict[call.from_user.id]['command_param']['properties-v2-list']['checkOutDate']['month'],
			command_dict[call.from_user.id]['command_param']['properties-v2-list']['checkOutDate']['day']
		)
		hotel_night = (date_out - date_in).days
		if hotel_night > 0:
			command_dict[call.from_user.id]['command_param']['date_in'] = date_in
			command_dict[call.from_user.id]['command_param']['date_out'] = date_out
			command_dict[call.from_user.id]['command_param']['hotel_night'] = hotel_night
			bot.send_message(
				call.from_user.id,
				'Понял выезжаем {}/{}/{}\nПосчитаем сколько ночей\n'.format(day, month, year))
			bot.send_message(call.from_user.id, '...')
			time.sleep(1)  # чтобы не склонять слово день
			if command_dict[call.from_user.id]['command_name'] == 'bestdeal':
				bot.send_message(
					call.from_user.id,
					'{}\n'
					'Введите через пробел минимальную и максимальную стоимость отеля в рублях за ночь'.format(hotel_night)
				)
				bot.set_state(call.from_user.id, UserInfoState.hotel_price)
			else:
				bot.send_message(call.from_user.id, '{}\nСколько вывезти отелей?'.format(hotel_night))
				bot.set_state(call.from_user.id, UserInfoState.hotel_count)
			logger.debug('{} Выезд {}/{}/{}'.format(call.from_user.full_name, day, month, year))
		else:
			bot.send_message(
				call.from_user.id,
				'Начнем с начала\nВыберите дату заезда:'.format(
					command_dict[call.from_user.id]['command_param']['city']
				),
				reply_markup=calendar.create_calendar(
					name=data_calendar.prefix,
					year=now.year,
					month=now.month
				)
			)
			bot.set_state(call.from_user.id, UserInfoState.date_in)
			logger.debug('{} город дата заезда позже выезда'.format(call.from_user.full_name))


@bot.message_handler(state=UserInfoState.hotel_price)
def get_hotel_price(message: Message) -> None:
	try:
		currency = get_currency_price()
		price = message.text.split()
		price_min = int(price[0])
		price_max = int(price[1])
		if price_max < price_min:
			price_min, price_max = price_max, price_min
		price_min_usd = round(price_min / currency, 2)
		price_max_usd = round(price_max / currency, 2)
		
		if price_max == price_min:
			raise ValueError
	except (ValueError, IndexError):
		bot.send_message(message.from_user.id, 'Некорректные данные, повторите ввод')
		logger.debug('{} ввел некорректную стоимость отеля'.format(message.from_user.full_name))
	else:
		price = command_dict[message.from_user.id]['command_param']['properties-v2-list']['filters']['price']
		
		price['min'] = price_min_usd
		price['max'] = price_max_usd

		bot.send_message(
			message.from_user.id,
			'Понял подбираем отели от {} до {} руб в городе {}\n'
			'Введите через пробел минимальное и максимальное расстояние от отеля до центра в МЕТРАХ'
			'(в километре 1000 метров)'.format(
				price_min,
				price_max,
				command_dict[message.from_user.id]['command_param']['city']
			)
		)
		bot.set_state(message.from_user.id, UserInfoState.hotel_distance, message.chat.id)
		logger.debug(
			'{} запросил отели от {} до {} руб в городе {}'.format(
				message.from_user.full_name,
				price_min,
				price_max,
				command_dict[message.from_user.id]['command_param']['city']
			)
		)


@bot.message_handler(state=UserInfoState.hotel_distance)
def get_hotel_distance(message: Message) -> None:
	try:
		distance = message.text.split()
		distance_min = int(distance[0]) / 1000
		distance_max = int(distance[1]) / 1000
		if distance_max < distance_min:
			distance_min, distance_max = distance_max, distance_min
		if distance_max == distance_min or distance_max < 0.1:
			raise ValueError
	except (ValueError, IndexError):
		bot.send_message(message.from_user.id, 'Некорректные данные, повторите ввод')
		logger.debug('{} ввел некорректные расстояния от отеля'.format(message.from_user.full_name))
	else:
		distance = command_dict[message.from_user.id]['command_param']['hotel_distance']
		distance['min'] = distance_min
		distance['max'] = distance_max
		bot.send_message(
			message.from_user.id,
			'Понял подбираем отели на расстоянии от {} до {} километров от центра города {}\n'
			'Сколько вывезти отелей?'.format(
				distance['min'],
				distance['max'],
				command_dict[message.from_user.id]['command_param']['city']
			)
		)
		bot.set_state(message.from_user.id, UserInfoState.hotel_count, message.chat.id)
		logger.debug(
			'{} запросил отели на расстоянии от {} до {} километров от центра города {}'.format(
				message.from_user.full_name,
				distance['min'],
				distance['max'],
				command_dict[message.from_user.id]['command_param']['city']
			)
		)


@bot.message_handler(state=UserInfoState.hotel_count)
def get_hotel_count(message: Message) -> None:
	if message.text.isdigit():
		command_dict[message.from_user.id]['command_param']['hotel_count'] = int(message.text)
		command_dict[message.from_user.id]['command_param']['properties-v2-list']['resultsSize'] = int(message.text)
		if command_dict[message.from_user.id]['command_name'] == 'lowprice':
			comm = 'недорогих отелей'
		elif command_dict[message.from_user.id]['command_name'] == 'highprice':
			comm = 'дорогих отелей'
		else:
			comm = 'отелей по параметрам'
			command_dict[message.from_user.id]['command_param']['properties-v2-list']['resultsSize'] = int(message.text) * 100
		bot.send_message(
			message.from_user.id,
			'Понял выводим ТОП{} {} города {}\nДобавить фото?'.format(
				command_dict[message.from_user.id]['command_param']['hotel_count'],
				comm,
				command_dict[message.from_user.id]['command_param']['city']
			),
			reply_markup=yes_or_no()
		)
		bot.set_state(message.from_user.id, UserInfoState.photo, message.chat.id)
		logger.debug('{} запросил ТОП{} {}'.format(message.from_user.full_name, message.text, comm))
	else:
		bot.send_message(message.from_user.id, 'Необходимо ввести число')
		logger.debug('{} ввел не корректное число отелей'.format(message.from_user.full_name))


@bot.message_handler(state=UserInfoState.photo)
def get_photo(message: Message) -> None:
	if message.text.lower() == 'yes':
		command_dict[message.from_user.id]['command_param']['photo'] = True
		bot.send_message(
			message.from_user.id,
			'А сколько загрузить фото?\nНо не более 10 шт.',
			reply_markup=ReplyKeyboardRemove()
		)
		bot.set_state(message.from_user.id, UserInfoState.photo_count, message.chat.id)
		logger.debug('{} хочет получить фото'.format(message.from_user.full_name))
	else:
		command_dict[message.from_user.id]['command_param']['photo'] = False
		logger.debug('{} отказался от фото(молодец экономит запросы)'.format(message.from_user.full_name))
		logger.debug('{} делает запрос к API'.format(message.from_user.full_name))
		get_result(message=message, dict_set=command_dict[message.from_user.id])
		bot.set_state(message.from_user.id, UserInfoState.reset)


@bot.message_handler(state=UserInfoState.photo_count)
def get_count_photo(message: Message) -> None:
	if message.text.isdigit():
		if int(message.text) <= 10:
			command_dict[message.from_user.id]['command_param']['count_photo'] = message.text
		else:
			command_dict[message.from_user.id]['command_param']['count_photo'] = 10
		logger.debug('{} хочет получить {} по каждому отелю'.format(message.from_user.full_name, message.text))
		logger.debug('{} делает запрос к API'.format(message.from_user.full_name))
		get_result(message=message, dict_set=command_dict[message.from_user.id])
		bot.set_state(message.from_user.id, UserInfoState.reset)
	else:
		bot.send_message(message.from_user.id, 'Необходимо ввести число')
		logger.debug('{} ввел не корректное число фото'.format(message.from_user.full_name))
