from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("help", "Вывести справку"),
            types.BotCommand("menu", "Главное меню"),
            types.BotCommand("feedback", "Оставить отзыв"),
            types.BotCommand("request", "Оставить заявку для обсуждения проекта"),
            types.BotCommand("partnership", "Связаться по поводу сотрудничества"),
            types.BotCommand("work", "Вакансии"),
            types.BotCommand("question", "Задать вопрос")
        ]
    )
