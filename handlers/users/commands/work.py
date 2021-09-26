from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from keyboards.inline import skills_names_keyboard
from loader import dp


@dp.message_handler(Command("work"))
@dp.message_handler(text="Вакансии")
async def send_welcome_message(message: types.Message, state: FSMContext):
    message_text = "<b>Доброго времени суток!</b>\n" \
                   "Очень рады, что Вы решили воспользоваться возможностями нашего бота 🙂\n\n" \
                   "Количество проектов растет и мы всецело заинтересованы в новых людях! " \
                   "Старайтесь описать Ваши навыки и умения как можно подробнее 😉\n\n" \
                   "________________________\n" \
                   "<b>Пожалуйста, напишите, как Вас зовут</b>"
    await message.answer(message_text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state("work__get_user_name")


@dp.message_handler(state="work__get_user_name")
async def get_user_skill_name(message: types.Message, state: FSMContext):
    user_name = message.text
    await state.update_data(user_name=user_name)
    message_text = f"Приятно познакомиться, {user_name} 🤩\n\n" \
                   "<b>Пожалуйста, укажите Ваше основное направление</b>"
    await message.answer(message_text, reply_markup=skills_names_keyboard)
    await state.set_state("work__get_user_skill_name")
