from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    reset = State()
    lp_date_in = State()
    lp_date_out = State()
    lp_city = State()
    lp_chose_city = State()
    lp_count_hotel = State()
    lp_photo = State()
    lp_count_photo = State()
