import json
from telebot.types import Message, InputMediaPhoto
from loader import bot
from utils.misc.api_requests import api_request
from loguru import logger
from urllib.request import urlopen


def get_result(message: Message, dict_set: dict) -> None:
	method_endswith = "properties/v2/list"
	payload = {
		'currency': 'USD',
		'eapid': 1,
		'locale': 'ru_RU',
		'siteId': 300000001,
		'destination': {
			'regionId': dict_set[message.from_user.id]['city']
		},
		'checkInDate': dict_set[message.from_user.id]['date_in'],
		'checkOutDate': dict_set[message.from_user.id]['date_out'],
		'rooms': [{'adults': 1}],
		'resultsStartingIndex': 0,
		'resultsSize': int(dict_set[message.from_user.id]['count_hotel']),
		'sort': dict_set[message.from_user.id]['sort'],
		'filters': dict_set[message.from_user.id]['filters']
	}
	
	# Запрос списка отелей по сортировке
	response2 = api_request(method_type="POST", method_endswith=method_endswith, params=payload)
	logger.debug('{} id города {} запрос списка отелей'.format(
		message.from_user.full_name,
		dict_set[message.from_user.id]['city']
	)
	)
	for elem in response2['data']['propertySearch']['properties']:
		# Запрос подробностей
		id_hotel = elem['id']
		response3 = api_request(
			method_type="POST",
			method_endswith='properties/v2/detail',
			params={"currency": "USD", "eapid": 1, "locale": "ru_RU", "siteId": 300000001, "propertyId": id_hotel})
		name_hotel = elem['name']
		address_hotel = response3['data']['propertyInfo']['summary']['location']['address']['addressLine']
		far_centr = elem['destinationInfo']['distanceFromDestination']['value']
		cost = elem["price"]['displayMessages'][0]['lineItems'][0]['price']['formatted']
		# ["price"]['options'][0]['strikeOut']['amount']
		answer = f"""
		id Отеля: {id_hotel}\n
		Отель: {name_hotel}\n
		Адрес отеля: {address_hotel}\n
		Расстояние до центра: {far_centr}км\n
		Стоимость за ночь: {cost}\n
		https://www.hotels.com/ho{id_hotel}\n
		"""
		bot.send_message(message.from_user.id, answer)
		logger.debug('{} id города {} запрос подробностей id отеля {}'.format(
			message.from_user.full_name,
			dict_set[message.from_user.id]['city'],
			id_hotel
		)
		)
		if dict_set[message.from_user.id]['photo']:
			logger.debug('{} id города {} выводим фото для id отеля {}'.format(
				message.from_user.full_name,
				dict_set[message.from_user.id]['city'],
				id_hotel
			)
			)
			index = 0
			photo = []
			while index < int(dict_set[message.from_user.id]['count_photo']):
				photo.append(InputMediaPhoto(
					response3['data']['propertyInfo']['propertyGallery']['images'][index]['image']['url'])
				)
				index += 1
			bot.send_media_group(message.chat.id, photo)
			