from typing import Dict, Any
from telebot.types import Message, InputMediaPhoto
from loader import bot
from utils.misc.api_requests import api_request
from utils.misc.db_save import save_in_db
from utils.misc.currency import get_currency_price
from keyboards.inline.link import link
from loguru import logger


def get_result(message: Message, dict_set: dict) -> None:
	# Запрос списка отелей по сортировке
	resp_list = api_request(
		method_type="POST",
		method_endswith="properties/v2/list",
		params=dict_set['command_param']['properties-v2-list']
	)
	logger.debug('{} город {} запрос списка отелей'.format(
		message.from_user.full_name,
		dict_set['command_param']['properties-v2-list']['destination']['regionId']
		)
	)
	if resp_list is None:
		bot.send_message(
			message.from_user.id,
			'{} получен не корректный ответ. Придется начать с начала'. format(message.from_user.full_name)
		)
		return
	currency = get_currency_price()
	
	count = 0
	result: Dict[int, Dict[str, Any]] = {}
	for elem in resp_list['data']['propertySearch']['properties']:
		# Запрос подробностей
		result[count] = {'hotel_id': elem['id']}
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
		if (dict_set['command_param']['hotel_distance']['min'] >
			elem['destinationInfo']['distanceFromDestination']['value']) or\
			(dict_set['command_param']['hotel_distance']['max'] <
			elem['destinationInfo']['distanceFromDestination']['value']):
			continue
		elif dict_set['command_param']['hotel_count'] < count + 1:
			break
		result[count]['hotel_name'] = elem['name']
		result[count]['hotel_address'] = response3['data']['propertyInfo']['summary']['location']['address']['addressLine']
		result[count]['hotel_distance'] = elem['destinationInfo']['distanceFromDestination']['value']
		result[count]['cost_night'] = elem["price"]['lead']['amount'] * currency
		cost = result[count]['cost_night'] * dict_set['command_param']['hotel_night']
		result[count]['cost'] = cost
		answer = """
		Название: {hotel_name}\n
		Адрес: {hotel_address}\n
		Расстояние от центра: {hotel_distance}км\n
		Цена за ночь: {cost_night} руб.\n
		Стоимость за {hotel_night} ночей: {cost} руб.\n
		""".format(
			hotel_name=result[count]['hotel_name'],
			hotel_address=result[count]['hotel_address'],
			hotel_distance=round(result[count]['hotel_distance'], 2),
			cost=round(result[count]['cost'], 2),
			cost_night=round(result[count]['cost_night'], 2),
			hotel_night=dict_set['command_param']['hotel_night'],
		)
		url = 'https://www.hotels.com/h{hotel_id}.Hotel-Information'.format(hotel_id=result[count]['hotel_id'])
		bot.send_message(message.from_user.id, answer, reply_markup=link(url))
		logger.debug('{} в городе {} запрос подробностей id отеля {}'.format(
			message.from_user.full_name,
			dict_set['command_param']['city'],
			result[count]['hotel_id']
			)
		)
		if dict_set['command_param']['photo']:
			logger.debug('{} в городе {} выводим фото для id отеля {}'.format(
				message.from_user.full_name,
				dict_set['command_param']['city'],
				result[count]['hotel_id']
				)
			)
			index = 0
			photo = []
			while index < int(dict_set['command_param']['count_photo']):
				photo.append(InputMediaPhoto(
					response3['data']['propertyInfo']['propertyGallery']['images'][index]['image']['url'])
				)
				index += 1
			bot.send_media_group(message.chat.id, photo)
		count += 1
	dict_set['command_result'] = result
	if len(result) < dict_set['command_param']['hotel_count']:
		bot.send_message(
			message.from_user.id,
			'По Вашему запросу нашлось меньше ответов, чем хотелось\n'
			'(или не нашлось совсем, по причине экономии запросов).\n'
			'Измените параметры поиска'
		)
	save_in_db(message, dict_set)
	