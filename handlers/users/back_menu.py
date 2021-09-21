from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram import types

from keyboards.default.main_menu import main_keyboard
from loader import dp


@dp.message_handler(Command("menu"), state="*")
@dp.message_handler(text="Главное меню", state="*")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await state.reset_state()
    # await state.update_data(user_tg_id=message.from_user.id)

    await message.delete()
    await message.answer("<b>Главное меню</b>", reply_markup=main_keyboard)
