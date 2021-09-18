import logging

from aiogram import executor

from loader import dp, bot
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Создаем подключение к базе данных
    # logging.info("Создаем подключение к базе данных")
    # await db.create_pool()

    # Создаем стандартные таблицы, если такие еще не были созданы
    # logging.info("Создаем таблицы: для ..., ...")
    # await db.create_standard_tables()

    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляем про запуск
    logging.info("Уведомляем админов о том, что бот запустился")
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
