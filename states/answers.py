from aiogram.dispatcher.filters.state import StatesGroup, State


class DetailedAnswer(StatesGroup):
    first_answer = State()
    second_answer = State()
    third_answer = State()
    fourth_answer = State()
