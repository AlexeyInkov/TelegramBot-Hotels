import datetime

import loguru
from telebot.types import Message, InputMediaPhoto
from loader import bot
from utils.misc.api_requests import api_request
from loguru import logger
from database.model import *


@logger.catch
def get_result(message: Message, dict_set: dict) -> None:
	method_endswith = "properties/v2/list"
	payload = {
		'currency': 'USD',
		'eapid': 1,
		'locale': 'ru_RU',
		'siteId': 300000001,
		'destination': {
			'regionId': dict_set[message.from_user.id]['city_id']
		},
		'checkInDate': dict_set[message.from_user.id]['command_param']['date_in'],
		'checkOutDate': dict_set[message.from_user.id]['command_param']['date_out'],
		'rooms': [{'adults': 1}],
		'resultsStartingIndex': 0,
		'resultsSize': int(dict_set[message.from_user.id]['command_param']['count_hotel']),
		'sort': dict_set[message.from_user.id]['command_param']['sort'],
		'filters': dict_set[message.from_user.id]['command_param']['filters']
	}
	
	# Запрос списка отелей по сортировке
	response2 = api_request(method_type="POST", method_endswith=method_endswith, params=payload)
	logger.debug('{} id города {} запрос списка отелей'.format(
		message.from_user.full_name,
		dict_set[message.from_user.id]['city_id']
		)
	)
	with db:
		lp = Command.create(
			user_id=message.from_user.id,
			command=dict_set[message.from_user.id]['command_name'],
			city_id=dict_set[message.from_user.id]['city_id'],
			city=dict_set[message.from_user.id]['city'],
			command_time=dict_set[message.from_user.id]['command_time']
			)
		
		for elem in response2['data']['propertySearch']['properties']:
			# Запрос подробностей
			dict_set[message.from_user.id]['command_result']['hotel_id'] = elem['id']
			response3 = api_request(
				method_type="POST",
				method_endswith='properties/v2/detail',
				params={
					"currency": "USD",
					"eapid": 1,
					"locale": "ru_RU",
					"siteId": 300000001,
					"propertyId": dict_set[message.from_user.id]['command_result']['hotel_id']
				}
			)
			dict_set[message.from_user.id]['command_result']['hotel_name'] = elem['name']
			dict_set[message.from_user.id]['command_result']['hotel_address'] = \
				response3['data']['propertyInfo']['summary']['location']['address']['addressLine']
			dict_set[message.from_user.id]['command_result']['far_centr'] = \
				elem['destinationInfo']['distanceFromDestination']['value']
			dict_set[message.from_user.id]['command_result']['cost_night'] = \
				elem["price"]['lead']['amount']
			cost = dict_set[message.from_user.id]['command_result']['cost_night'] * \
				dict_set[message.from_user.id]['command_result']['hotel_days']
			dict_set[message.from_user.id]['command_result']['cost'] = cost
			answer = """
			Отель: {hotel_name}\n
			Адрес отеля: {hotel_address}\n
			Расстояние до центра: {hotel_distance}км\n
			Стоимость Общая: {cost}\n
			Стоимость за ночь: {cost_night}\n
			https://www.hotels.com/ho{hotel_id}\n
			""".format(
				hotel_name= dict_set[message.from_user.id]['command_result']['hotel_name'],
				hotel_address=dict_set[message.from_user.id]['command_result']['hotel_address'],
				hotel_distance=dict_set[message.from_user.id]['command_result']['far_centr'],
				cost=dict_set[message.from_user.id]['command_result']['cost'],
				cost_night=dict_set[message.from_user.id]['command_result']['cost_night'],
				hotel_id=dict_set[message.from_user.id]['command_result']['hotel_id']
			)
			bot.send_message(message.from_user.id, answer)
			logger.debug('{} id города {} запрос подробностей id отеля {}'.format(
				message.from_user.full_name,
				dict_set[message.from_user.id]['city_id'],
				dict_set[message.from_user.id]['command_result']['hotel_id']
				)
			)
			result = CommandResult.create(
				hotel_id=dict_set[message.from_user.id]['command_result']['hotel_id'],
				hotel_name=dict_set[message.from_user.id]['command_result']['hotel_name'],
				hotel_address=dict_set[message.from_user.id]['command_result']['hotel_address'],
				hotel_distance=dict_set[message.from_user.id]['command_result']['far_centr'],
				cost=dict_set[message.from_user.id]['command_result']['cost'],
				cost_night=dict_set[message.from_user.id]['command_result']['cost_night'],
				hotel_days=dict_set[message.from_user.id]['command_result']['hotel_days'],
				hotel_url='https://www.hotels.com/ho{}'.format(
					dict_set[message.from_user.id]['command_result']['hotel_id']
				),
				command_id=lp
			)
			if dict_set[message.from_user.id]['command_param']['photo']:
				logger.debug('{} id города {} выводим фото для id отеля {}'.format(
					message.from_user.full_name,
					dict_set[message.from_user.id]['city'],
					dict_set[message.from_user.id]['command_result']['hotel_id']
					)
				)
				index = 0
				photo = []
				while index < int(dict_set[message.from_user.id]['command_param']['count_photo']):
					photo.append(InputMediaPhoto(
						response3['data']['propertyInfo']['propertyGallery']['images'][index]['image']['url'])
					)
					index += 1
				bot.send_media_group(message.chat.id, photo)
			