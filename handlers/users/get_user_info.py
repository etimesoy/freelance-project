from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default.main_menu import main_keyboard
from keyboards.inline.callback_data import skill_name_callback
from keyboards.default import done_keyboard
from states.answers import DetailedAnswer
from loader import dp


@dp.callback_query_handler(skill_name_callback.filter(), state="partnership__get_user_skill_name")
@dp.callback_query_handler(skill_name_callback.filter(), state="work__get_user_skill_name")
async def get_user_skill_description(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.message.edit_reply_markup()
    user_skill_name = callback_data["name"]
    await state.update_data(user_skill_name=user_skill_name)
    prefix = f"<i>Вы выбрали: {user_skill_name}</i>\n"
    message_text = prefix + "Отлично!\n\n" \
                   "<b>Пожалуйста, подробно распишите Ваши навыки и компетенции\n" \
                   "Будет отлично, если Вы также прикрепите свое портфолио\n\n" \
                   "<i>Вы можете писать несколькими сообщениями. Когда закончите, просто отправьте " \
                   "отдельным сообщением “Готово” или выберите соответствующий пункт в меню.</i></b>"
    await call.message.answer(message_text, reply_markup=done_keyboard)
    await state.update_data(action="get_user_skill_description")
    await DetailedAnswer.gather_files_and_messages.set()


async def get_user_contact_details(message: types.Message, state: FSMContext):
    message_text = "Огромное спасибо за Ваше резюме!\n\n" \
                   "<b>Пожалуйста, напишите Ваши контактные данные, " \
                   "чтобы мы могли с Вами связаться (e-mail/номер телефона)</b>"
    # TODO: может сюда нужно еще добавить мессенджер как способ связи?
    await message.answer(message_text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("get_user_contact_details")


@dp.message_handler(state="get_user_contact_details")
async def send_concluding_message(message: types.Message, state: FSMContext):
    user_contact_details = message.text
    # TODO: сохранить все данные пользователя в бд
    message_text = "<b>Благодарим Вас за оставленную заявку, обязательно напишем Вам, " \
                   "как только ознакомимся с Вашими данными!</b>"
    await message.answer(message_text, reply_markup=main_keyboard)
    await state.reset_state()
