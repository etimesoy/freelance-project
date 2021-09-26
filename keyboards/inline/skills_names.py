from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import skill_name_callback

skills_names_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("💻 FrontEnd", callback_data=skill_name_callback.new(name="💻 FrontEnd"))
    ],
    [
        InlineKeyboardButton("🔐 BackEnd", callback_data=skill_name_callback.new(name="🔐 BackEnd"))
    ],
    [
        InlineKeyboardButton("📱 Мобильная разработка",
                             callback_data=skill_name_callback.new(name="📱 Мобильная разработка"))
    ],
    [
        InlineKeyboardButton("💬 Другое", callback_data=skill_name_callback.new(name="💬 Другое"))
    ]
])
