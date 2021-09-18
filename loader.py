from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage

from data import config
# from utils.db_api.postgres import Database

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage()
dp = Dispatcher(bot, storage=storage)
# db = Database()
