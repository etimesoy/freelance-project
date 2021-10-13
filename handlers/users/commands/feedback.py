from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from handlers.users.user_info import add_new_feedback_to_db
from keyboards.default import done_keyboard
from keyboards.default.main_menu import main_keyboard
from keyboards.inline.callback_data import stars_callback, feedback_callback
from keyboards.inline import stars_keyboard
from states.answers import DetailedAnswer
from utils.misc import discount_code_generator, rate_limit
from loader import dp, db


@dp.message_handler(Command("feedback"))
@dp.message_handler(text="Оставить отзыв")
async def send_welcome_message(message: types.Message, state: FSMContext):
    await state.update_data(command="feedback")
    await state.update_data(table_name="feedbacks")
    await state.update_data(user_tg_username=message.from_user.username)
    await message.answer("""<b>Доброго времени суток!</b>
Очень рады, что Вы решили воспользоваться возможностями нашего бота и оставить отзыв 🙂
Будем благодарны за развернутый отзыв о нашей работе! 

________________________
<b>Пожалуйста, напишите название вашего проекта</b>""", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("get_project_name")


@dp.message_handler(state="get_project_name")
async def get_project_name(message: types.Message, state: FSMContext):
    project_name = message.text
    await state.update_data(project_name=project_name)
    await message.answer("Отлично!\nПожалуйста, коротко оцените работу наших сотрудников",
                         reply_markup=stars_keyboard)
    await state.set_state("get_assessment_of_work")


@dp.callback_query_handler(stars_callback.filter(), state="get_assessment_of_work")
async def get_assessment_of_work(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    await call.message.edit_reply_markup()
    stars_count = callback_data["count"]
    stars = {"1": "1️⃣⭐️", "2": "2️⃣⭐️", "3": "3️⃣⭐️", "4": "4️⃣⭐️", "5": "5️⃣⭐️️"}
    prefix = f"<i>Вы выбрали: {stars[stars_count]}</i>\n"
    message_text = prefix + """Спасибо за вашу оценку! <b>Пожалуйста, напишите развернутый отзыв о нашей работе 🙂
Вы также можете прикрепить 3 файла к Вашим сообщениям общим весом до 50 Мб.

<i>Вы можете писать несколькими сообщениями. Когда закончите, просто отправьте отдельным сообщением “Готово” 
или выберите соответствующий пункт в меню.</i></b>
"""
    await call.message.answer(message_text, reply_markup=done_keyboard)
    await state.update_data(stars_count=stars_count)
    await state.update_data(action="get_feedback")
    await DetailedAnswer.gather_files_and_messages.set()

    state_data = await state.get_data()
    appeal_id = db.add_feedback_beginning(state_data["user_tg_username"], state_data["project_name"], mark=stars_count)
    await state.update_data(appeal_id=appeal_id)


async def send_gratitude_response(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    stars_count = state_data["stars_count"]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton("Пропустить", callback_data=feedback_callback.new(action="Пропустить")),
        types.InlineKeyboardButton("Предложить улучшение",
                                   callback_data=feedback_callback.new(action="Предложить улучшение"))
    ]])

    if stars_count == "1":
        message_text = "Спасибо за Ваш отзыв! Подскажите, что мы могли бы сделать, чтобы Вы остались довольны?"
    elif stars_count == "2":
        message_text = "Спасибо за Ваш отзыв! Подскажите, что мы могли бы улучшить, чтобы Вы остались довольны?"
    elif stars_count == "3":
        message_text = "Спасибо за Ваш отзыв! Пожалуйста, напишите, что мы можем сделать для дальнейшего сотрудничества с Вами?"
    elif stars_count == "4":
        message_text = "Спасибо за Ваш отзыв! Надеемся на дальнейшее сотрудничество с Вами!"
    else:  # stars_count == "5"
        message_text = "Спасибо за Ваш отзыв! Будем ждать дальнейшее сотрудничество!"

    if stars_count in ["1", "2", "3"]:
        await message.answer(message_text, reply_markup=keyboard)
        await state.set_state("get_gratitude")
    elif stars_count in ["4", "5"]:
        await message.answer(message_text, reply_markup=main_keyboard)
        await state.reset_state()
        add_new_feedback_to_db(state_data)


@dp.callback_query_handler(feedback_callback.filter(action="Предложить улучшение"),
                           state="get_gratitude")
async def send_suggestions_for_improvements_message(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("<b>Пожалуйста, напишите, что мы могли бы улучшить 😔</b>",
                              reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("get_suggestions_for_improvements_message")


@rate_limit(limit=180)
@dp.message_handler(state="get_suggestions_for_improvements_message")
async def get_suggestions_for_improvements_message(message: types.Message, state: FSMContext):
    suggestions_for_improvements = message.text
    # TODO: проверить, не имеет ли уже пользователь скидочный код
    discount_code = discount_code_generator()
    state_data = await state.get_data()
    message_text = "Спасибо, что поделились с нами\!\n" \
                   "Мы дорожим каждым нашим клиентом и обязательно прислушаемся к Вашему предложению\.\n" \
                   "Мы очень сожалеем, что Вы не остались довольны нашей работой\. " \
                   "В качестве извинения мы хотим предоставить Вам скидку на дальнейшее обращение за нашими услугами\. " \
                   "Мы верим, что все заслуживают второй шанс\.\n" \
                   "При следующем обращении, пожалуйста, укажите, что Вы получали скидку, Ваш уникальный идентификатор для получения скидки:\n" \
                   f"`{discount_code}`"
    await message.answer(message_text, reply_markup=main_keyboard, parse_mode=types.ParseMode.MARKDOWN_V2)
    await state.reset_state()
    add_new_feedback_to_db(state_data, discount_code=discount_code, desire=suggestions_for_improvements)


@rate_limit(limit=180)
@dp.callback_query_handler(feedback_callback.filter(action="Пропустить"),
                           state="get_gratitude")
async def go_back_to_main_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    state_data = await state.get_data()
    await call.message.answer("Главное меню", reply_markup=main_keyboard)
    await state.reset_state()
    add_new_feedback_to_db(state_data)
