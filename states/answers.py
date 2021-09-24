from aiogram.dispatcher.filters.state import StatesGroup, State


class DetailedAnswer(StatesGroup):
    gather_files_and_messages = State()
