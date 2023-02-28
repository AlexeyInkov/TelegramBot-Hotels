import json
from telebot.types import Message
from loader import bot
from utils.misc.api_requests import api_request
from loguru import logger


def get_result(message: Message, dict_set: dict) -> None:
	method_endswith = "properties/v2/list"
	payload = dict(
		currency='USD', eapid=1, locale='ru_RU', siteId=300000001,
		destination={'regionId': str(dict_set[message.from_user.id]['city'])},
		checkInDate=dict_set[message.from_user.id]['date_in'],
		checkOutDate=dict_set[message.from_user.id]['date_out'],
		rooms=[{'adults': 1}],
		resultsStartingIndex=0,
		resultsSize=int(dict_set[message.from_user.id]['count_hotel']),
		sort=dict_set[message.from_user.id]['sort'],
		filters=dict_set[message.from_user.id]['filters']
	)
	
	# Запрос списка отелей по сортировке
	response2 = api_request(method_type="POST", method_endswith=method_endswith, params=payload)
	
	for elem in response2['data']['propertySearch']['properties']:
		id_hotel = elem['id']
		method_endswith = 'properties/v2/detail'
		payload = {"currency": "USD", "eapid": 1, "locale": "ru_RU", "siteId": 300000001, "propertyId": id_hotel}
		# Запрос подробностей
		response3 = api_request(method_type="POST", method_endswith=method_endswith, params=payload)
		name_hotel = elem['name']
		address_hotel = response3['data']['propertyInfo']['summary']['location']['address']['addressLine']
		if elem['destinationInfo']['distanceFromDestination']['unit'] == 'KILOMETER':
			far_centr = elem['destinationInfo']['distanceFromDestination']['value']
		else:
			far_centr = round(elem['destinationInfo']['distanceFromDestination']['value'] * 1.61, 2)
		cost = elem["price"]['displayMessages'][0]['lineItems'][0]['price'][
			'formatted']  # ["price"]['options'][0]['strikeOut']['amount']
		answer = f"""
		id Отеля: {id_hotel}\n
		Отель: {name_hotel}\n
		Адрес отеля: {address_hotel}\n
		Расстояние до центра: {far_centr}км\n
		Стоимость за ночь: {cost}\n
		https://www.hotels.com/ho{id_hotel}\n
		"""
		bot.send_message(message.from_user.id, answer)
		logger.debug('Запрос от {} {} в городе {}'.format(
			message.from_user.first_name,
			message.from_user.last_name,
			dict_set[message.from_user.id]['city'][1])
		)
		if dict_set[message.from_user.id]['photo']:
			index = 0
			photo = []
			while index < int(dict_set[message.from_user.id]['count_photo']):
				photo.append(response3['data']['propertyInfo']['propertyGallery']['images'][index]['image']['url'])
				index += 1
			bot.send_media_group(message.chat.id, photo)
			