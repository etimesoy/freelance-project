from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import done_keyboard
from keyboards.default.main_menu import main_keyboard
from keyboards.inline.callback_data import partnership_project_callback, employment_type_callback, skill_name_callback
from loader import dp
from states.answers import DetailedAnswer


@dp.message_handler(commands="partnership")
@dp.message_handler(text="Связаться по поводу сотрудничества")
async def send_welcome_message(message: types.Message):
    message_text = "<b>Доброго времени суток!</b>\n" \
                   "Очень рады, что Вы решили воспользоваться возможностями нашего бота 🙂\n\n" \
                   "Мы имеем как подрядный, так и субподрядный опыт работы.\n\n" \
                   "________________________\n" \
                   "<b>Пожалуйста, укажите, какое сотрудничество Вас интересует</b>"
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton("Я хочу отдать проект на подряд",
                                       callback_data=partnership_project_callback.new(choice="Give"))
        ],
        [
            types.InlineKeyboardButton("Я хочу получить проект на подряд",
                                       callback_data=partnership_project_callback.new(choice="Get"))
        ]
    ])
    await message.answer(message_text, reply_markup=keyboard)


@dp.callback_query_handler(partnership_project_callback.filter(choice="Give"))
async def get_project_name(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.message.edit_reply_markup()
    prefix = "<i>Вы выбрали: Я хочу отдать проект на подряд</i>\n"
    message_text = prefix + "<b>Пожалуйста, напишите название вашего проекта</b>"
    await call.message.answer(message_text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("request__get_project_name")


@dp.callback_query_handler(partnership_project_callback.filter(choice="Get"))
async def get_user_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    prefix = "<i>Вы выбрали: Я хочу получить проект на подряд</i>\n"
    message_text = prefix + "Отлично!\n\n<b>Пожалуйста, напишите, как Вас зовут</b>"
    await call.message.answer(message_text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("partnership__get_user_name")


@dp.message_handler(state="partnership__get_user_name")
async def get_user_employment_type(message: types.Message, state: FSMContext):
    user_name = message.text
    await state.update_data(user_name=user_name)
    message_text = f"Приятно познакомиться, {user_name} 🤩\n\n<b>Пожалуйста, укажите, кого Вы представляете</b>"
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton("👩‍💻 Физическое лицо",
                                       callback_data=employment_type_callback.new(choice="individual"))
        ],
        [
            types.InlineKeyboardButton("🏢 Компанию",
                                       callback_data=employment_type_callback.new(choice="company"))
        ]
    ])
    await message.answer(message_text, reply_markup=keyboard)
    await state.set_state("partnership__get_user_employment_type")


@dp.callback_query_handler(employment_type_callback.filter(choice="company"),
                           state="partnership__get_user_employment_type")
async def get_user_company_name(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(user_employment_type="company")
    await call.message.edit_reply_markup()
    prefix = "<i>Вы выбрали: 🏢 Компанию</i>\n"
    message_text = prefix + "<b>Пожалуйста, напишите, какую компанию Вы представляете</b>"
    await call.message.answer(message_text)
    await state.set_state("partnership__get_user_company_name")


@dp.message_handler(state="partnership__get_user_company_name")
async def get_company_user_skill_name(message: types.Message, state: FSMContext):
    user_company_name = message.text
    await state.update_data(user_company_name=user_company_name)
    await get_user_skill_name(message, state)


@dp.callback_query_handler(employment_type_callback.filter(choice="individual"),
                           state="partnership__get_user_employment_type")
async def get_individual_user_skill_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.update_data(user_employment_type="individual")
    await get_user_skill_name(call.message, state, prefix="<i>Вы выбрали: 👩‍💻 Физическое лицо</i>\n")


async def get_user_skill_name(message: types.Message, state: FSMContext, prefix=""):
    message_text = prefix + "Отлично!\n<b>Пожалуйста, укажите Ваше основное направление</b>"
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton("💻 FrontEnd", callback_data=skill_name_callback.new(name="💻 FrontEnd"))
        ],
        [
            types.InlineKeyboardButton("🔐 BackEnd", callback_data=skill_name_callback.new(name="🔐 BackEnd"))
        ],
        [
            types.InlineKeyboardButton("📱 Мобильная разработка",
                                       callback_data=skill_name_callback.new(name="📱 Мобильная разработка"))
        ],
        [
            types.InlineKeyboardButton("💬 Другое", callback_data=skill_name_callback.new(name="💬 Другое"))
        ]
    ])
    await message.answer(message_text, reply_markup=keyboard)
    await state.set_state("partnership__get_user_skill_name")


@dp.callback_query_handler(skill_name_callback.filter(), state="partnership__get_user_skill_name")
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
    await state.set_state("partnership__get_user_contact_details")


@dp.message_handler(state="partnership__get_user_contact_details")
async def send_concluding_message(message: types.Message, state: FSMContext):
    user_contact_details = message.text
    # TODO: сохранить все данные пользователя в бд
    message_text = "<b>Благодарим Вас за оставленную заявку, обязательно напишем Вам, " \
                   "как только ознакомимся с Вашими данными!</b>"
    await message.answer(message_text, reply_markup=main_keyboard)
    await state.reset_state()
