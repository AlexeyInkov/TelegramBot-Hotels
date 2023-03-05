from telebot.types import Message
from loader import bot
from database.model import *


@bot.message_handler(commands=["history"])
def bot_history(message: Message):
    answer = ''
    with db:
        for com in Command.select().where(Command.user_id == message.from_user.id).order_by(Command.command_time).limit(1):
            answer += ' '.join([str(Command.command), str(Command.city), str(Command.command_time)]) + '\n'
            for res in CommandResult.select().where(CommandResult.command_id == com):
                answer += ' '.join([str(res.hotel_name), str(res.cost_night)]) + '\n'
    bot.send_message(message.from_user.id, answer)
