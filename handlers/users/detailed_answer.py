from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.commands.feedback import send_gratitude_response
from handlers.users.commands.request import get_user_project_budget
from states.answers import DetailedAnswer
from loader import dp


@dp.message_handler(text="Готово", state=DetailedAnswer.gather_files_and_messages)
async def stop_receiving_files(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    if state_data["action"] == "get_feedback":
        await send_gratitude_response(message, state)
    elif state_data["action"] == "get_user_project_info":
        await get_user_project_budget(message, state)


@dp.message_handler(state=DetailedAnswer.gather_files_and_messages,
                    content_types=types.ContentTypes.TEXT | types.ContentTypes.DOCUMENT |
                                  types.ContentTypes.PHOTO | types.ContentTypes.VIDEO)
async def get_file(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    document = message.document
    if message.content_type == "video" or document and document.mime_type.startswith("video/"):
        message_text = "К сожалению, нельзя прикрепить видео 😞\n" \
                       "Вы можете перенести его в облако и продублировать ссылку в сообщении\n"
        await message.answer(message_text)
        return
    if message.content_type in ["document", "photo"]:
        if files_count := state_data.get("files_count"):
            files_count = int(files_count) + 1
            if files_count > 3:
                message_text = "К сожалению, нельзя прикрепить больше файлов 😞\n" \
                               "Вы можете перенести их в облако и продублировать ссылку в сообщении\n" \
                               "Также Вы можете прикрепить архив с вашими файлами (Максимальный вес: 50 МБ)"
                # TODO: что нужно сделать с уже присланными файлами, если пользователь получил это предупреждение?
                # TODO: получается архив не входит в лимит в 3 сообщения?
                await message.answer(message_text)
                return
        else:
            files_count = 1
        await state.update_data(files_count=files_count)
    elif message.content_type == "text":
        if text_messages_count := state_data.get("text_messages_count"):
            text_messages_count = int(text_messages_count) + 1
            if text_messages_count > 30:
                # TODO: обработать спам текстовыми сообщениями
                return
        else:
            text_messages_count = 1
        await state.update_data(text_messages_count=text_messages_count)
        # TODO: сохранить текст в state???
    # TODO: сохранить сообщение/документ/фото в бд
