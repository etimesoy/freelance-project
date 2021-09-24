from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import communication_ways_keyboard, done_keyboard
from keyboards.default.main_menu import main_keyboard
from keyboards.inline import project_budget_keyboard, time_intervals_keyboard, messengers_keyboard
from keyboards.inline.callback_data import project_budget_callback, time_intervals_callback, messengers_callback
from states.answers import DetailedAnswer
from loader import dp


@dp.message_handler(commands="request")
@dp.message_handler(text="Оставить заявку для обсуждения проекта")
async def send_welcome_message(message: types.Message, state: FSMContext):
    await message.answer("""<b>Доброго времени суток!</b>
Очень рады, что Вы решили воспользоваться возможностями нашего бота и оставить отзыв 🙂
Будем благодарны за развернутый отзыв о нашей работе! 

________________________
<b>Пожалуйста, напишите название вашего проекта</b>""", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("request__get_project_name")


@dp.message_handler(state="request__get_project_name")
async def get_project_name(message: types.Message, state: FSMContext):
    await message.answer("Отлично!\n<b>Пожалуйста, напишите, как Вас зовут</b>")
    await state.set_state("request__get_user_name")


@dp.message_handler(state="request__get_user_name")
async def get_communication_way(message: types.Message, state: FSMContext):
    user_name = message.text
    await state.update_data(user_name=user_name)
    await message.answer(f"Приятно познакомиться, {user_name} 🤩\n"
                         f"<b>Пожалуйста, укажите, какой вид связи Вам предпочтительнее</b>",
                         reply_markup=communication_ways_keyboard)
    await state.set_state("request__communication_way")


@dp.message_handler(text="📧 E-mail", state="request__communication_way")
@dp.message_handler(text="📲 Звонок", state="request__communication_way")
@dp.message_handler(text="📱 Написать в мессенджер", state="request__communication_way")
async def get_contact_details(message: types.Message, state: FSMContext):
    communication_way = message.text
    await state.update_data(communication_way=communication_way)
    await message.answer("Договорились! Мы будем придерживаться указанного вида связи!\n"
                         "<b>Пожалуйста, напишите Ваши контактные данные, чтобы мы могли с Вами связаться</b>",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("request__contact_details")


@dp.message_handler(state="request__communication_way")
async def bad_get_contact_details(message: types.Message):
    await message.answer("Пожалуйста, выбрите пункт из меню ниже 🙂\n\n"
                         "___________________\n"
                         "<i>Если Вы передумали, то можно вернуться в Главное Меню введя команду</i> <b>/menu</b>")


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


async def get_user_project_budget(message: types.Message, state: FSMContext):
    await message.answer("Огромное спасибо за предоставленную информацию!\n"
                         "<b>Пожалуйста, укажите Ваш бюджет на проект</b>",
                         reply_markup=project_budget_keyboard)
    await state.set_state("request__get_user_project_budget")


@dp.callback_query_handler(project_budget_callback.filter(), state="request__get_user_project_budget")
async def send_gratitude_response(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    state_data = await state.get_data()
    user_project_budget = callback_data["amount"]
    await state.update_data(user_project_budget=user_project_budget)
    if state_data["communication_way"] == "📧 E-mail":
        message_text = "<b>Благодарим Вас за оставленную заявку!</b>\n" \
                       "Наши сотрудники в ближайшее время ознакомятся с предоставленной информацией " \
                       "и обязательно отправят Вам сообщение на электронную почту."
        await call.message.answer(message_text, reply_markup=main_keyboard)
        # TODO: сохранить все данные пользователя в бд
        await state.reset_state()
    elif state_data["communication_way"] == "📲 Звонок":
        message_text = "<b>Благодарим Вас за оставленную заявку!</b>\n" \
                       "Наши сотрудники в ближайшее время ознакомятся с предоставленной информацией " \
                       "и обязательно Вам перезвонят.\n" \
                       "<b>Пожалуйста, укажите удобное время для звонка (МСК)</b>"
        await call.message.answer(message_text, reply_markup=time_intervals_keyboard)
        await state.set_state("request__choose_time_interval")
    elif state_data["communication_way"] == "📱 Написать в мессенджер":
        message_text = "Благодарим Вас за оставленную заявку!\n" \
                       "Наши сотрудники в ближайшее время ознакомятся с предоставленной информацией " \
                       "и обязательно Вам напишут.\n" \
                       "Пожалуйста, укажите удобный для Вас мессенджер."
        await call.message.answer(message_text, reply_markup=messengers_keyboard)
        await state.set_state("request__choose_messenger")


@dp.callback_query_handler(time_intervals_callback.filter(), state="request__choose_time_interval")
async def send_concluding_message(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    time_interval = callback_data["range"]
    # TODO: сохранить time_interval и все данные пользователя в бд
    await call.message.answer("<b>Спасибо!</b>\n"
                              "Мы обязательно свяжемся с Вами в течение нескольких дней в удобное для Вас время.",
                              reply_markup=main_keyboard)
    await state.reset_state()


@dp.callback_query_handler(messengers_callback.filter(), state="request__choose_messenger")
async def send_concluding_message(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    messenger = callback_data["messenger"]
    # TODO: сохранить messenger и все данные пользователя в бд
    await call.message.answer("<b>Спасибо!</b>\n"
                              f"Мы обязательно напишем Вам в {messenger}, как только ознакомимся с Вашей заявкой.",
                              reply_markup=main_keyboard)
    await state.reset_state()
