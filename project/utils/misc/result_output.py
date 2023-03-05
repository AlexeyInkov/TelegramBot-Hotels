from telebot.types import Message, InputMediaPhoto
from loader import bot
from utils.misc.api_requests import api_request
from loguru import logger
from database.model import *


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
		'checkInDate': dict_set[message.from_user.id]['command_param']['date_in_dict'],
		'checkOutDate': dict_set[message.from_user.id]['command_param']['date_out_dict'],
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
		com = Command.create(
			user_id=message.from_user.id,
			command=dict_set[message.from_user.id]['command_name'],
			city_id=dict_set[message.from_user.id]['city_id'],
			city=dict_set[message.from_user.id]['city'],
			command_time=dict_set[message.from_user.id]['command_time']
			)
		par = CommandParam.create(
			date_in=dict_set[message.from_user.id]['command_param']['date_in'],
			date_out=dict_set[message.from_user.id]['command_param']['date_out'],
			count_hotel=dict_set[message.from_user.id]['command_param']['count_hotel'],
			photo=dict_set[message.from_user.id]['command_param']['photo'],
			count_photo=dict_set[message.from_user.id]['command_param']['count_photo'],
			price_min=dict_set[message.from_user.id]['command_param']['price_min'],
			price_max=dict_set[message.from_user.id]['command_param']['price_max'],
			hotel_distance_min=dict_set[message.from_user.id]['command_param']['hotel_distance_min'],
			hotel_distance_max=dict_set[message.from_user.id]['command_param']['hotel_distance_max'],
			command_id=com
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
			dict_set[message.from_user.id]['command_result']['hotel_distance'] = \
				elem['destinationInfo']['distanceFromDestination']['value']
			dict_set[message.from_user.id]['command_result']['cost_night'] = \
				elem["price"]['lead']['amount']
			cost = dict_set[message.from_user.id]['command_result']['cost_night'] * \
				dict_set[message.from_user.id]['command_result']['hotel_night']
			dict_set[message.from_user.id]['command_result']['cost'] = cost
			answer = """
			Отель: {hotel_name}\n
			Адрес отеля: {hotel_address}\n
			Расстояние до центра: {hotel_distance}км\n
			Стоимость за {hotel_night} ночей: ${cost}\n
			Стоимость за ночь: ${cost_night}\n
			https://www.hotels.com/ho{hotel_id}\n
			""".format(
				hotel_name=dict_set[message.from_user.id]['command_result']['hotel_name'],
				hotel_address=dict_set[message.from_user.id]['command_result']['hotel_address'],
				hotel_distance=round(dict_set[message.from_user.id]['command_result']['hotel_distance'], 2),
				cost=round(dict_set[message.from_user.id]['command_result']['cost'], 2),
				cost_night=round(dict_set[message.from_user.id]['command_result']['cost_night'], 2),
				hotel_night=dict_set[message.from_user.id]['command_result']['hotel_night'],
				hotel_id=dict_set[message.from_user.id]['command_result']['hotel_id']
			)
			bot.send_message(message.from_user.id, answer)
			logger.debug('{} id города {} запрос подробностей id отеля {}'.format(
				message.from_user.full_name,
				dict_set[message.from_user.id]['city_id'],
				dict_set[message.from_user.id]['command_result']['hotel_id']
				)
			)
			res = CommandResult.create(
				hotel_id=dict_set[message.from_user.id]['command_result']['hotel_id'],
				hotel_name=dict_set[message.from_user.id]['command_result']['hotel_name'],
				hotel_address=dict_set[message.from_user.id]['command_result']['hotel_address'],
				hotel_distance=round(dict_set[message.from_user.id]['command_result']['hotel_distance'], 2),
				cost=round(dict_set[message.from_user.id]['command_result']['cost'], 2),
				cost_night=round(dict_set[message.from_user.id]['command_result']['cost_night'], 2),
				hotel_night=dict_set[message.from_user.id]['command_result']['hotel_night'],
				hotel_url='https://www.hotels.com/ho{}'.format(
					dict_set[message.from_user.id]['command_result']['hotel_id']
				),
				command_id=com
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
			