import asyncio
from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def throttle(self, target: Union[types.Message, types.CallbackQuery], data: dict):
        handler = current_handler.get()
        dp = Dispatcher.get_current()
        key = f"{self.prefix}_message"
        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
        else:
            limit = self.rate_limit
        try:
            await dp.throttle(key, rate=limit)
        except Throttled as t:
            await self.target_throttled(target, t, dp, key)

    @staticmethod
    async def target_throttled(target: Union[types.Message, types.CallbackQuery],
                               throttled: Throttled, dispatcher: Dispatcher, key: str):
        msg = target.message if isinstance(target, types.CallbackQuery) else target
        if throttled.exceeded_count == 6:
            reply_message = "Упс! К сожалению, Вы обращались к боту слишком часто 😞\n" \
                            "Во избежании спама, мы были вынуждены заблокировать Вас на 8 часов.\n" \
                            "Если это произошло случайно, пожалуйста, оповести нас об этом по окончании блокировки 😌"
            await msg.answer(reply_message)
            await asyncio.sleep(60*60)  # TODO: *8 еще
            raise CancelHandler()
        elif throttled.exceeded_count > 6:
            raise CancelHandler()

    async def on_process_message(self, message, data):
        await self.throttle(message, data)

    async def on_process_callback_query(self, call, data):
        await self.throttle(call, data)
