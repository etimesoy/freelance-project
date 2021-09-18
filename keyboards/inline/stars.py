from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import stars_callback

stars_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton("1️⃣⭐️", callback_data=stars_callback.new(count=1)),
    InlineKeyboardButton("2️⃣⭐️", callback_data=stars_callback.new(count=2)),
    InlineKeyboardButton("3️⃣⭐️", callback_data=stars_callback.new(count=3)),
    InlineKeyboardButton("4️⃣⭐️", callback_data=stars_callback.new(count=4)),
    InlineKeyboardButton("5️⃣⭐️️", callback_data=stars_callback.new(count=5))
]])
