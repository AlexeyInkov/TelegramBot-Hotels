from typing import Dict, Any
from telebot.types import Message, InputMediaPhoto
from loader import bot
from utils.misc.api_requests import api_request
from utils.misc.db_save import save_in_db
from utils.misc.currency import get_currency_price
from loguru import logger


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
	if response2 is None:
		bot.send_message(
			message.from_user.id,
			'{} получен не корректный ответ. Придется начать с начала'. format(message.from_user.full_name)
		)
		return
	currency = get_currency_price()
	count = 0
	for elem in response2['data']['propertySearch']['properties']:
		# Запрос подробностей
		result: Dict[int, dict[str, Any]] = {count: {'hotel_id': elem['id']}}
		response3 = api_request(
			method_type="POST",
			method_endswith='properties/v2/detail',
			params={
				"currency": "USD",
				"eapid": 1,
				"locale": "ru_RU",
				"siteId": 300000001,
				"propertyId": result[count]['hotel_id']
			}
		)
		if response3 is None:
			bot.send_message(
				message.from_user.id,
				'{} получен не корректный ответ. Придется начать с начала'.format(message.from_user.full_name)
			)
			return
		result[count]['hotel_name'] = elem['name']
		result[count]['hotel_address'] = response3['data']['propertyInfo']['summary']['location']['address']['addressLine']
		result[count]['hotel_distance'] = elem['destinationInfo']['distanceFromDestination']['value']
		result[count]['cost_night'] = elem["price"]['lead']['amount'] * currency
		cost = result[count]['cost_night'] * dict_set[message.from_user.id]['command_param']['hotel_night']
		result[count]['cost'] = cost
		answer = """
		Название: {hotel_name}\n
		Адрес: {hotel_address}\n
		Расстояние от центра: {hotel_distance}км\n
		Цена за ночь: {cost_night} руб.\n
		Стоимость за {hotel_night} ночей: {cost} руб.\n\n
		Ссылка: https://www.hotels.com/h{hotel_id}.Hotel-Information\n
		""".format(
			hotel_name=result[count]['hotel_name'],
			hotel_address=result[count]['hotel_address'],
			hotel_distance=round(result[count]['hotel_distance'], 2),
			cost=round(result[count]['cost'], 2),
			cost_night=round(result[count]['cost_night'], 2),
			hotel_night=dict_set[message.from_user.id]['command_param']['hotel_night'],
			hotel_id=result[count]['hotel_id']
		)
		bot.send_message(message.from_user.id, answer)
		logger.debug('{} id города {} запрос подробностей id отеля {}'.format(
			message.from_user.full_name,
			dict_set[message.from_user.id]['city_id'],
			result[count]['hotel_id']
			)
		)
		if dict_set[message.from_user.id]['command_param']['photo']:
			logger.debug('{} id города {} выводим фото для id отеля {}'.format(
				message.from_user.full_name,
				dict_set[message.from_user.id]['city'],
				result[count]['hotel_id']
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
		count += 1
	dict_set[message.from_user.id]['command_result'] = result
	save_in_db(message, dict_set)
	