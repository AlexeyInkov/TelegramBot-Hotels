from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    lp_city = State()
    lp_count_hotel = State()
    lp_photo = State()
    lp_count_photo = State()
