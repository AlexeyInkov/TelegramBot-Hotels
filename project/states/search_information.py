from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    reset = State()
    city = State()
    chose_city = State()
    date_in = State()
    date_out = State()
    hotel_price = State()
    hotel_distance = State()
    hotel_count = State()
    photo = State()
    photo_count = State()
    history_count = State()
