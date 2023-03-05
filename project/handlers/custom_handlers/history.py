from telebot.types import Message
from loader import bot
from database.model import *
from states.search_information import UserInfoState


@bot.message_handler(commands=["history"])
def bot_history(message: Message):
    bot.send_message(message.from_user.id, 'Сколько последних поисков вывести?')
    bot.set_state(message.from_user.id, UserInfoState.hi_count)


@bot.message_handler(state=UserInfoState.hi_count)
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
                    answer += '"{}" - ${} за ночь\n'.format(res.hotel_name, res.cost_night)
                answer += '\n'
        bot.send_message(message.from_user.id, answer)
