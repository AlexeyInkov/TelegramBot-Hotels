from telebot.types import Message
from loguru import logger
from database.model import *


def save_in_db(message: Message, dict_set: dict) -> None:
	with db:
		com = Command.create(
			user_id=message.from_user.id,
			command=dict_set[message.from_user.id]['command_name'],
			city_id=dict_set[message.from_user.id]['city_id'],
			city=dict_set[message.from_user.id]['city'],
			command_time=dict_set[message.from_user.id]['command_time']
		)
		logger.debug('{} (Запись таблицы Commands)'.format(message.from_user.full_name))
		param = dict_set[message.from_user.id]['command_param']
		CommandParam(
			date_in=param['date_in'],
			date_out=dict_set[message.from_user.id]['command_param']['date_out'],
			hotel_night=param['hotel_night'],
			count_hotel=param['count_hotel'],
			photo=param['photo'],
			count_photo=param['count_photo'],
			price_min=param['price_min'],
			price_max=param['price_max'],
			hotel_distance_min=param['hotel_distance_min'],
			hotel_distance_max=param['hotel_distance_max'],
			command_id=com
		).save()
		logger.debug('{} (Запись таблицы Command_params)'.format(message.from_user.full_name))
		for count, result in dict_set[message.from_user.id]['command_result'].items():
			CommandResult(
				hotel_id=result['hotel_id'],
				hotel_name=result['hotel_name'],
				hotel_address=result['hotel_address'],
				hotel_distance=round(result['hotel_distance'], 2),
				cost=round(result['cost'], 2),
				cost_night=round(result['cost_night'], 2),
				hotel_url='https://www.hotels.com/h{}.Hotel-Information'.format(result['hotel_id']),
				command_id=com
			).save()
		logger.debug('{} (Запись таблицы Command_results)'.format(message.from_user.full_name))
		