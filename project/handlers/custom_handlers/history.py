from telebot.types import Message
from loguru import logger
from loader import bot
from database.model import *
from states.search_information import UserInfoState


@bot.message_handler(commands=["history"])
def bot_history(message: Message):
    bot.send_message(message.from_user.id, 'Сколько последних поисков вывести?')
    bot.set_state(message.from_user.id, UserInfoState.history_count)
    logger.debug('{} (Вход в history)'.format(message.from_user.full_name))


@bot.message_handler(state=UserInfoState.history_count)
def result_history(message: Message):
    if message.text.isdigit():
        if int(message.text) > 5:
            lim = 5
        else:
            lim = message.text
        answer = 'Ваши последние поиски:\n'
        with db:
            for com in Command.select().where(
                    Command.user_id == message.from_user.id
            ).order_by(Command.command_time.desc()).limit(lim):
                answer += '{} "{}" в {}\n'.format(com.command_time.strftime('%d/%m/%Y %H:%M:%S'), com.command, com.city)
                for res in com.result:
                    answer += '"{}" - {} руб. за ночь\n'.format(res.hotel_name, res.cost_night)
                answer += '\n'
        bot.send_message(message.from_user.id, answer)
    bot.set_state(message.from_user.id, UserInfoState.reset)
    logger.debug('{} (Вывод результата history)'.format(message.from_user.full_name))