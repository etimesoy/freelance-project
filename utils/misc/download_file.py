from io import BytesIO

from loader import bot


async def download_file_by_file_id(file_id: str) -> (BytesIO, str):
    """
    Скачивает из телеграма файл по его file_id

    :param file_id:
    :return: кортеж из бинарного контента файла и полного названия файла
    """
    info_about_file = await bot.get_file(file_id)
    file = await bot.download_file_by_id(file_id)
    return file, info_about_file.file_path
