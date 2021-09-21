from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import messengers_callback

messengers_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton("🟦 Telegram", callback_data=messengers_callback.new(messenger="Telegram")),
    InlineKeyboardButton("🟩 WhatsApp", callback_data=messengers_callback.new(messenger="WhatsApp")),
    InlineKeyboardButton("🟪 Viber", callback_data=messengers_callback.new(messenger="Viber"))
]])
