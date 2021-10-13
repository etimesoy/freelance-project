from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from handlers.users.user_info import save_project_name_get_user_name, send_gratitude_response
from keyboards.default import done_keyboard
from keyboards.inline import project_budget_keyboard
from keyboards.inline.callback_data import project_budget_callback
from states.answers import DetailedAnswer
from loader import dp, db


@dp.message_handler(Command("request"))
@dp.message_handler(text="Оставить заявку для обсуждения проекта")
async def send_welcome_message(message: types.Message, state: FSMContext):
    await state.update_data(command="request")
    await state.update_data(table_name="requests")
    await state.update_data(user_tg_username=message.from_user.username)
    await message.answer("""<b>Доброго времени суток!</b>
Очень рады, что Вы решили воспользоваться возможностями нашего бота и оставить заявку тут 🙂
Как только мы обработаем Вашу заявку, мы обязательно с Вами свяжемся 📲
Будем признательны за развернутые ответы о Вашем проекте! 

________________________
<b>Пожалуйста, напишите название вашего проекта</b>""", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("request__get_project_name")


@dp.message_handler(state="request__get_project_name")
async def get_user_name(message: types.Message, state: FSMContext):
    await save_project_name_get_user_name(message, state)


@dp.message_handler(state="partnership__contact_details")
@dp.message_handler(state="request__contact_details")
async def get_user_project_info(message: types.Message, state: FSMContext):
    contact_details = message.text
    await state.update_data(contact_details=contact_details)
    await message.answer("""Отлично!

<b>Пожалуйста, расскажите о Вашем проекте как можно подробнее
Вы также можете прикрепить файлы к Вашим сообщениям

<i>Вы можете писать несколькими сообщениями. Когда закончите, просто отправьте отдельным сообщением “Готово” 
или выберите соответствующий пункт в меню.</i></b>
""", reply_markup=done_keyboard)
    await state.update_data(action="get_user_project_info")
    await DetailedAnswer.gather_files_and_messages.set()

    state_data = await state.get_data()
    if state_data["command"] == "request":
        appeal_id = db.add_request_beginning(state_data["user_tg_username"], state_data["user_name"],
                                             state_data["project_name"], state_data["communication_way"],
                                             contact_details)
    else:  # state_data["command"] == "partnership"
        appeal_id = db.add_partnership_type_1_beginning(state_data["user_tg_username"], state_data["user_name"],
                                                        state_data["project_name"], state_data["communication_way"],
                                                        contact_details)
    await state.update_data(appeal_id=appeal_id)


async def get_user_project_budget(message: types.Message, state: FSMContext):
    await message.answer("Огромное спасибо за предоставленную информацию!\n"
                         "<b>Пожалуйста, укажите Ваш бюджет на проект</b>",
                         reply_markup=project_budget_keyboard)
    await state.set_state("request__get_user_project_budget")


@dp.callback_query_handler(project_budget_callback.filter(), state="request__get_user_project_budget")
async def save_user_project_budget(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.message.edit_reply_markup()
    project_budget = callback_data["amount"]
    await state.update_data(project_budget=project_budget)
    await send_gratitude_response(call.message, state, project_budget)
