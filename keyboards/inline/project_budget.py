from aiogram.types import InlineKeyboardMarkup, inline_keyboard, InlineKeyboardButton

from keyboards.inline.callback_data import project_budget_callback

project_budget_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("100.000₽ - 300.000₽",
                             callback_data=project_budget_callback.new(amount="100.000₽ - 300.000₽")),
        InlineKeyboardButton("300.000₽ - 500.000₽",
                             callback_data=project_budget_callback.new(amount="300.000₽ - 500.000₽"))
    ],
    [
        InlineKeyboardButton("500.000₽ - 1.000.000₽",
                             callback_data=project_budget_callback.new(amount="500.000₽ - 1.000.000₽")),
        InlineKeyboardButton("1.000.000₽ - 3.000.000₽",
                             callback_data=project_budget_callback.new(amount="1.000.000₽ - 3.000.000₽"))
    ],
    [
        InlineKeyboardButton("3.000.000₽ - ... ₽",
                             callback_data=project_budget_callback.new(amount="3.000.000₽ - ... ₽"))
    ]
])
