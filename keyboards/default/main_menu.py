from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton("Оставить отзыв")
    ],
    [
        KeyboardButton("Оставить заявку для обсуждения проекта")
    ],
    [
        KeyboardButton("Связаться по поводу сотрудничества")
    ],
    [
        KeyboardButton("Вакансии"), KeyboardButton("Задать вопрос")
    ]
], resize_keyboard=True)
