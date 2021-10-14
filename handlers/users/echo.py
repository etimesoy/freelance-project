from aiogram import types

from data.constants import choose_menu_item_prompt
from loader import dp


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(choose_menu_item_prompt)


@dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def bot_echo_all(message: types.Message):
    await message.answer(choose_menu_item_prompt)
