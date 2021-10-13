from typing import List

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default.main_menu import main_keyboard
from keyboards.inline import time_intervals_keyboard, messengers_keyboard
from keyboards.inline.callback_data import skill_name_callback, time_intervals_callback, messengers_callback
from keyboards.default import done_keyboard, communication_ways_keyboard
from states.answers import DetailedAnswer
from loader import dp, db
from utils.misc import rate_limit


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

    state_data = await state.get_data()
    if state_data["command"] == "partnership":
        appeal_id = db.add_partnership_type_2_beginning(state_data["user_tg_username"], state_data["user_name"],
                                                        state_data["employment_type"], state_data.get("company_name"),
                                                        user_skill_name)
    else:  # state_data["command"] == "work"
        appeal_id = db.add_work_beginning(state_data["user_tg_username"], state_data["user_name"], user_skill_name)
    await state.update_data(appeal_id=appeal_id)


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
    state_data = await state.get_data()
    current_command_is_work = state_data["command"] == "work"
    if current_command_is_work:
        message_text = "<b>Благодарим Вас за отклик, обязательно напишем Вам, " \
                       "как только ознакомимся с Вашими данными!</b>"
    else:
        message_text = "<b>Благодарим Вас за оставленную заявку, обязательно напишем Вам, " \
                       "как только ознакомимся с Вашими данными!</b>"
    await message.answer(message_text, reply_markup=main_keyboard)
    await state.reset_state()
    if current_command_is_work:
        db.add_work_ending(state_data["appeal_id"], user_contact_details)
    elif state_data["partnership_type"] == "Получить проект":
        db.add_partnership_type_2_ending(state_data["appeal_id"], user_contact_details)


async def save_project_name_get_user_name(message: types.Message, state: FSMContext):
    project_name = message.text
    await state.update_data(project_name=project_name)
    await message.answer("Отлично!\n<b>Пожалуйста, напишите, как Вас зовут</b>")
    await state.set_state("user_info__get_user_name")


@dp.message_handler(state="user_info__get_user_name")
async def get_communication_way(message: types.Message, state: FSMContext):
    user_name = message.text
    await state.update_data(user_name=user_name)
    await message.answer(f"Приятно познакомиться, {user_name} 🤩\n"
                         f"<b>Пожалуйста, укажите, какой вид связи Вам предпочтительнее</b>",
                         reply_markup=communication_ways_keyboard)
    await state.set_state("user_info__communication_way")


@dp.message_handler(text="📧 E-mail", state="user_info__communication_way")
@dp.message_handler(text="📲 Звонок", state="user_info__communication_way")
@dp.message_handler(text="📱 Написать в мессенджер", state="user_info__communication_way")
async def get_contact_details(message: types.Message, state: FSMContext):
    communication_way = message.text
    await state.update_data(communication_way=communication_way)
    await message.answer("Договорились! Мы будем придерживаться указанного вида связи!\n"
                         "<b>Пожалуйста, напишите Ваши контактные данные, чтобы мы могли с Вами связаться</b>",
                         reply_markup=types.ReplyKeyboardRemove())
    state_data = await state.get_data()
    await state.set_state(f"{state_data['command']}__contact_details")


@dp.message_handler(state="user_info__communication_way")
async def bad_get_contact_details(message: types.Message):
    await message.answer("Пожалуйста, выбрите пункт из меню ниже 🙂\n\n"
                         "___________________\n"
                         "<i>Если Вы передумали, то можно вернуться в Главное Меню введя команду</i> <b>/menu</b>")


@rate_limit(limit=180)
async def send_gratitude_response(message: types.Message, state: FSMContext, project_budget=""):
    state_data = await state.get_data()
    command = state_data["command"]
    if command == "request":
        gratitude_prefix = "<b>Благодарим Вас за оставленную заявку!</b>\n"
    else:  # command == "question"
        gratitude_prefix = "<b>Спасибо за Ваш вопрос!</b>\n"
    if project_budget:
        project_budget = f"<i>Вы выбрали: {project_budget}</i>\n"
    if state_data["communication_way"] == "📧 E-mail":
        message_text = project_budget + gratitude_prefix
        message_text += "Наши сотрудники в ближайшее время ознакомятся с предоставленной информацией " \
                        "и обязательно отправят Вам сообщение на электронную почту."
        await message.answer(message_text, reply_markup=main_keyboard)
        await state.reset_state()
        if command == "request":
            add_new_request_to_db(state_data)
        else:  # command == "question"
            add_new_question_to_db(state_data)
    elif state_data["communication_way"] == "📲 Звонок":
        message_text = project_budget + gratitude_prefix
        message_text += "Наши сотрудники в ближайшее время ознакомятся с предоставленной информацией " \
                        "и обязательно Вам перезвонят.\n" \
                        "<b>Пожалуйста, укажите удобное время для звонка (МСК)</b>"
        await message.answer(message_text, reply_markup=time_intervals_keyboard)
        await state.set_state("user_info__choose_time_interval")
    elif state_data["communication_way"] == "📱 Написать в мессенджер":
        message_text = project_budget + gratitude_prefix
        message_text += "Наши сотрудники в ближайшее время ознакомятся с предоставленной информацией " \
                        "и обязательно Вам напишут.\n" \
                        "<b>Пожалуйста, укажите удобный для Вас мессенджер.</b>"
        await message.answer(message_text, reply_markup=messengers_keyboard)
        await state.set_state("user_info__choose_messenger")


@dp.callback_query_handler(time_intervals_callback.filter(), state="user_info__choose_time_interval")
async def send_concluding_message(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.message.edit_reply_markup()
    time_interval = callback_data["range"]
    state_data = await state.get_data()

    prefix = f"<i>Вы выбрали: {time_interval}</i>\n"
    message_text = prefix + "<b>Спасибо!</b>\n"
    message_text += "Мы обязательно свяжемся с Вами в течение нескольких дней в удобное для Вас время."

    await call.message.answer(message_text, reply_markup=main_keyboard)
    await state.reset_state()
    if state_data["command"] == "request":
        add_new_request_to_db(state_data, time_interval=time_interval)
    else:  # state_data["command"] == "question"
        add_new_question_to_db(state_data, time_interval=time_interval)


@dp.callback_query_handler(messengers_callback.filter(), state="user_info__choose_messenger")
async def send_concluding_message(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.message.edit_reply_markup()
    messenger = callback_data["messenger"]
    state_data = await state.get_data()

    prefix = f"<i>Вы выбрали: {messenger}</i>\n"
    message_text = prefix + "<b>Спасибо!</b>\n"
    message_text += f"Мы обязательно напишем Вам в {messenger}, как только ознакомимся с Вашей заявкой."

    await call.message.answer(message_text, reply_markup=main_keyboard)
    await state.reset_state()
    if state_data["command"] in ["request", "partnership"]:
        add_new_request_to_db(state_data, messenger=messenger)
    else:  # state_data["command"] == "question"
        add_new_question_to_db(state_data, messenger=messenger)


def add_new_feedback_to_db(state_data: dict, discount_code: str = None, desire: str = None):
    db.add_feedback_ending(state_data["appeal_id"], discount_code=discount_code, desire=desire)


def add_new_request_to_db(state_data: dict, time_interval: str = None, messenger: str = None):
    data = dict(
        appeal_id=state_data["appeal_id"],
        project_budget=state_data["project_budget"],
        messenger=messenger, call_time=time_interval
    )
    if state_data.get("partnership_type"):
        db.add_partnership_type_1_ending(**data)
    else:
        db.add_request_ending(**data)


def add_new_question_to_db(state_data: dict, messenger: str = None, time_interval: str = None):
    db.add_question_ending(state_data["appeal_id"], messenger=messenger, call_time=time_interval)


def get_attached_files_links(state_data: dict) -> List[str]:
    files_count = int(state_data.get("files_count", 0))
    return [state_data["file_" + str(idx)] for idx in range(1, files_count + 1)]
