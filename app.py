import logging
from asyncio import get_event_loop

from flask import Request

from aiogram import executor, Bot, Dispatcher
from aiogram import types

from loader import dp, bot
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляем про запуск
    logging.info("Уведомляем админов о том, что бот запустился")
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)


def gcloud_function_main(request: Request):
    request_json = request.get_json()
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    update = types.Update(update_id=request_json["update_id"],
                          message=request_json["message"])

    loop = get_event_loop()
    loop.run_until_complete(dp.process_update(update))
