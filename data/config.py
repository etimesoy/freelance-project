from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
IP = env.str("IP")  # Тоже str, но для айпи адреса хоста

DATABASE_URL = env.str("DATABASE_URL")
PATH_TO_SERVICE_ACCOUNT_KEY = env.str("PATH_TO_SERVICE_ACCOUNT_KEY")
PATH_TO_STORAGE_BUCKET = env.str("PATH_TO_STORAGE_BUCKET")
DATABASE_API_KEY = env.str("DATABASE_API_KEY")
