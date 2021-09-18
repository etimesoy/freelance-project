from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default import done_keyboard
from keyboards.default.main_menu import main_keyboard
from keyboards.inline.callback_data import stars_callback, feedback_callback
from keyboards.inline.stars import stars_keyboard
from loader import dp
from states.answers import DetailedAnswer
from utils.misc import discount_code_generator


@dp.message_handler(commands="feedback")
@dp.message_handler(text="Оставить отзыв")
async def send_welcome_message(message: types.Message, state: FSMContext):
    await message.answer("""<b>Доброго времени суток!</b>
Очень рады, что Вы решили воспользоваться возможностями нашего бота и оставить отзыв 🙂
Будем благодарны за развернутый отзыв о нашей работе! 

________________________
<b>Пожалуйста, напишите название вашего проекта</b>""")
    await state.set_state("get_project_name")


@dp.message_handler(state="get_project_name")
async def get_project_name(message: types.Message, state: FSMContext):
    await message.answer("Отлично!\nПожалуйста, коротко оцените работу наших сотрудников",
                         reply_markup=stars_keyboard)
    await state.set_state("get_assessment_of_work")


@dp.callback_query_handler(stars_callback.filter(), state="get_assessment_of_work")
async def get_assessment_of_work(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    await call.message.answer("""Спасибо за вашу оценку! Пожалуйста, напишите развернутый отзыв о нашей работе 🙂
Вы также можете прикрепить файлы к Вашим сообщениям.

Вы можете писать несколькими сообщениями. Когда закончите, просто отправьте отдельным сообщением “Готово” или выберите соответствующий пункт в меню.
""", reply_markup=done_keyboard)
    await state.update_data(stars_count=callback_data["count"])
    await state.update_data(action="get_feedback")
    await DetailedAnswer.first_answer.set()


async def send_gratitude_response(message: types.Message, state: FSMContext):
    await state.set_state("get_gratitude")
    stars_count = (await state.get_data())["stars_count"]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton("Пропустить", callback_data=feedback_callback.new(action="Пропустить")),
            types.InlineKeyboardButton("Получить скидку", callback_data=feedback_callback.new(action="Получить скидку"))
        ],
        [
            types.InlineKeyboardButton("Предложить улучшение", callback_data=feedback_callback.new(action="Предложить улучшение"))
        ]
    ])
    if stars_count == "1":
        await message.answer("Спасибо за Ваш отзыв! Подскажите, что мы могли бы сделать, чтобы Вы остались довольны?",
                             reply_markup=keyboard)
    elif stars_count == "2":
        await message.answer("Спасибо за Ваш отзыв! Подскажите, что мы могли бы улучшить, чтобы Вы остались довольны?",
                             reply_markup=keyboard)
    elif stars_count == "3":
        await message.answer("Спасибо за Ваш отзыв! Пожалуйста, напишите, что мы можем сделать для дальнейшего сотрудничества с Вами?",
                             reply_markup=keyboard)
    elif stars_count == "4":
        await message.answer("Спасибо за Ваш отзыв! Надеемся на дальнейшее сотрудничество с Вами!",
                             reply_markup=main_keyboard)
        await state.reset_state()
    elif stars_count == "5":
        await message.answer("Спасибо за Ваш отзыв! Будем ждать дальнейшее сотрудничество!",
                             reply_markup=main_keyboard)
        await state.reset_state()


@dp.callback_query_handler(feedback_callback.filter(action="Получить скидку"),
                           state="get_gratitude")
async def send_discount_code(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    discount_code = discount_code_generator()
    await call.message.answer(f"""Мы очень сожалеем, что Вы не остались довольны нашей работой\. В качестве извинения мы хотим предоставить Вам скидку на дальнейшее обращение за нашими услугами\. Мы верим, что все заслуживают второй шанс\.
При следующем обращении, пожалуйста, укажите, что Вы получали скидку, Ваш уникальный идентификатор для получения скидки:
`{discount_code}`""", reply_markup=main_keyboard, parse_mode=types.ParseMode.MARKDOWN_V2)
    # TODO: сохранить скидочный код пользователя в бд
    await state.reset_state()


@dp.callback_query_handler(feedback_callback.filter(action="Предложить улучшение"),
                           state="get_gratitude")
async def send_suggestions_for_improvements_message(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("<b>Пожалуйста, напишите, что мы могли бы улучшить 😔</b>")
    await state.set_state("get_suggestions_for_improvements_message")


@dp.message_handler(state="get_suggestions_for_improvements_message")
async def get_suggestions_for_improvements_message(message: types.Message, state: FSMContext):
    await message.answer("""Спасибо, что поделились с нами!
Мы дорожим каждым нашим клиентом и обязательно прислушаемся к Вашему предложению.""",
                         reply_markup=main_keyboard)
    await state.reset_state()


@dp.callback_query_handler(feedback_callback.filter(action="Пропустить"),
                           state="get_gratitude")
async def go_back_to_main_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("Главное меню", reply_markup=main_keyboard)
    await state.reset_state()
