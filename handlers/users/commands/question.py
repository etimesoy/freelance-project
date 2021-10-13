from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from handlers.users.user_info import save_project_name_get_user_name
from keyboards.default import done_keyboard
from loader import dp, db
from states.answers import DetailedAnswer


@dp.message_handler(Command("question"))
@dp.message_handler(text="Задать вопрос")
async def send_welcome_message(message: types.Message, state: FSMContext):
    await state.update_data(command="question")
    await state.update_data(table_name="questions")
    await state.update_data(user_tg_username=message.from_user.username)
    message_text = "<b>Доброго времени суток!</b>\n" \
                   "Очень рады, что Вы решили воспользоваться возможностями нашего бота и задать вопрос тут 🙂"\
                   "Как только мы обработаем Вашу заявку, мы обязательно с Вами свяжемся 📲\n" \
                   "________________________\n" \
                   "<b>Пожалуйста, напишите название вашего проекта</b>"
    await message.answer(message_text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("question__get_project_name")


@dp.message_handler(state="question__get_project_name")
async def get_user_name(message: types.Message, state: FSMContext):
    await save_project_name_get_user_name(message, state)


@dp.message_handler(state="question__contact_details")
async def get_user_question_info(message: types.Message, state: FSMContext):
    contact_details = message.text
    await state.update_data(contact_details=contact_details)
    message_text = "Отлично!\n\n" \
                   "<b>Пожалуйста, напишите Ваш вопрос как можно подробнее, чтобы мы могли смогли помочь Вам</b>\n\n" \
                   "<b><i>Вы можете писать несколькими сообщениями. " \
                   "Когда закончите, просто отправьте отдельным сообщением “Готово” " \
                   "или выберите соответствующий пункт в меню.</i></b>"
    await message.answer(message_text, reply_markup=done_keyboard)
    await state.update_data(action="get_user_question_info")
    await DetailedAnswer.gather_files_and_messages.set()

    state_data = await state.get_data()
    appeal_id = db.add_question_beginning(
        state_data["user_tg_username"], state_data["user_name"],
        state_data["project_name"], state_data["communication_way"],
        contact_details
    )
    await state.update_data(appeal_id=appeal_id)
