import logging
import asyncio

from flask import Request

from aiogram import executor, Bot, Dispatcher, types

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


def gcloud_function_main(request: Request):
    """Google cloud functions handler."""

    request_json = request.get_json()
    print(f"{request_json=}")

    if request.method == 'POST':
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        loop.run_until_complete(process_event(request_json))
        return {'statusCode': 200, 'body': 'ok'}

    return {'statusCode': 405}


async def process_event(request_json):
    """
    Converting an Google cloud functions event to an update and
    handling it
    """
    Bot.set_current(bot)
    Dispatcher.set_current(dp)
    update = types.Update.to_object(request_json)
    await dp.process_update(update)
