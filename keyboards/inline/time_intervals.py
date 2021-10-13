from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import time_intervals_callback

time_intervals_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("10:00-13:00", callback_data=time_intervals_callback.new(range="10.00-13.00")),
        InlineKeyboardButton("13:00-16:00", callback_data=time_intervals_callback.new(range="13.00-16.00"))
    ],
    [
        InlineKeyboardButton("16:00-20:00", callback_data=time_intervals_callback.new(range="16.00-20.00")),
        InlineKeyboardButton("20:00-22:00", callback_data=time_intervals_callback.new(range="20.00-22.00"))
    ]
])
