from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

communication_ways_keyboard = ReplyKeyboardMarkup(keyboard=[[
    KeyboardButton("📧 E-mail"), KeyboardButton("📲 Звонок"), KeyboardButton("📱 Написать в мессенджер")
]], resize_keyboard=True)
