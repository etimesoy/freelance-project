from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.commands.feedback import send_gratitude_response
from handlers.users.commands.request import get_user_project_budget
from states.answers import DetailedAnswer
from loader import dp


@dp.message_handler(text="Готово", state=DetailedAnswer.second_answer)
@dp.message_handler(text="Готово", state=DetailedAnswer.third_answer)
@dp.message_handler(text="Готово", state=DetailedAnswer.fourth_answer)
async def stop_receiving_files(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    if state_data["action"] == "get_feedback":
        await send_gratitude_response(message, state)
    elif state_data["action"] == "get_user_project_info":
        await get_user_project_budget(message, state)


@dp.message_handler(state=DetailedAnswer.first_answer,
                    content_types=types.ContentTypes.TEXT | types.ContentTypes.DOCUMENT | types.ContentTypes.PHOTO)
async def get_first_file(message: types.Message):
    # TODO: сохранить сообщение/документ/фото в бд
    await DetailedAnswer.second_answer.set()


@dp.message_handler(state=DetailedAnswer.second_answer,
                    content_types=types.ContentTypes.TEXT | types.ContentTypes.DOCUMENT | types.ContentTypes.PHOTO)
async def get_second_file(message: types.Message):
    # TODO: сохранить сообщение/документ/фото в бд
    await DetailedAnswer.third_answer.set()


@dp.message_handler(state=DetailedAnswer.third_answer,
                    content_types=types.ContentTypes.TEXT | types.ContentTypes.DOCUMENT | types.ContentTypes.PHOTO)
async def get_third_file(message: types.Message):
    # TODO: сохранить сообщение/документ/фото в бд
    await DetailedAnswer.fourth_answer.set()


@dp.message_handler(state=DetailedAnswer.fourth_answer)
async def show_warning(message: types.Message, state: FSMContext):
    await message.answer("""К сожалению, нельзя прикрепить больше файлов 😞
Вы можете перенести их в облако и продублировать ссылку в сообщении
Также Вы можете прикрепить архив с вашими файлами (Максимальный вес: 50 МБ)""")
    # TODO: что нужно сделать с уже присланными файлами, если пользователь получил это предупреждение?
    pass
