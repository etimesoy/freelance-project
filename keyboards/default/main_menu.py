from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton("Оставить заявку для обсуждения проекта")
    ],
    [
        KeyboardButton("Оставить отзыв"),
        KeyboardButton("Связаться по поводу сотрудничества")
    ],
    [
        KeyboardButton("Вакансии"), KeyboardButton("Задать вопрос")
    ]
], resize_keyboard=True)
