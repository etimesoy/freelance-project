from io import BytesIO

from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.commands.feedback import send_gratitude_response as feedback__send_gratitude_response
from handlers.users.user_info import get_user_contact_details, send_gratitude_response as question__send_gratitude_response
from handlers.users.commands.request import get_user_project_budget
from states.answers import DetailedAnswer
from loader import dp, db
from utils.misc.file_info import FileInfo


@dp.message_handler(text="Готово", state=DetailedAnswer.gather_files_and_messages)
async def stop_receiving_files(message: types.Message, state: FSMContext):

    await message.answer("<b>Пожалуйста, подождите, Ваши данные отправляются</b>")
    # TODO: сделать так чтобы сначала сразу отправилось это сообщение, потом загрузились все файлы
    # и только потом отправилось следующее сообщение
    state_data = await state.get_data()
    if state_data.get("files_count") is None and state_data.get("text_messages_count") is None:
        await message.answer("Пожалуйста, пришлите хотя бы одно сообщение или файл")
        return

    if state_data["command"] == "feedback":
        db._upload_data_ending("feedbacks", state_data["appeal_id"],
                               message=state_data.get("detailed_answer", ""))
    elif state_data["command"] == "request":
        db._upload_data_ending("requests", state_data["appeal_id"],
                               project_description=state_data.get("detailed_answer", ""))
    elif state_data["command"] == "partnership":
        if state_data["partnership_type"] == "Отдать проект":
            db._upload_data_ending("partnerships", state_data["appeal_id"],
                                   project_description=state_data.get("detailed_answer", ""))
        elif state_data["partnership_type"] == "Получить проект":
            db._upload_data_ending("partnerships", state_data["appeal_id"],
                                   description=state_data.get("detailed_answer", ""))
    elif state_data["command"] == "work":
        db._upload_data_ending("works", state_data["appeal_id"],
                               description=state_data.get("detailed_answer", ""))
    elif state_data["command"] == "question":
        db._upload_data_ending("questions", state_data["appeal_id"],
                               question=state_data.get("detailed_answer", ""))

    if state_data["action"] == "get_feedback":
        await feedback__send_gratitude_response(message, state)
    elif state_data["action"] == "get_user_project_info":
        await get_user_project_budget(message, state)
    elif state_data["action"] == "get_user_skill_description":
        await get_user_contact_details(message, state)
    elif state_data["action"] == "get_user_question_info":
        await question__send_gratitude_response(message, state)


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
        user_files_in_database_count = db.get_files_count_in_appeal(state_data["table_name"], state_data["appeal_id"])
        files_count = user_files_in_database_count + 1
        if files_count > 3:
            message_text = "К сожалению, нельзя прикрепить больше файлов 😞\n" \
                           "Вы можете перенести их в облако и продублировать ссылку в сообщении\n" \
                           "Также Вы можете прикрепить архив с вашими файлами (Максимальный вес: 50 МБ)"
            # TODO: получается архив не входит в лимит в 3 сообщения?
            await message.answer(message_text)
            return
        await state.update_data(files_count=files_count)
        file = BytesIO()
        if message.photo:
            await message.photo[-1].download(file)
            file_name = (await message.photo[-1].get_file()).file_path
            file_info = FileInfo(file, file_name, "image/jpeg")
        else:
            await document.download(file)
            file_info = FileInfo(file, document.file_name, document.mime_type)
        is_file_uploaded = db.upload_file(file_info, state_data["user_tg_username"],
                                          state_data["table_name"], state_data["appeal_id"])
        if is_file_uploaded:
            message_text = "Файл <b>" + file_info.name + "</b> сохранен"
        else:
            message_text = "К сожалению, нельзя прикрепить больше файлов 😞\n" \
                           "Вы можете перенести их в облако и продублировать ссылку в сообщении\n" \
                           "Также Вы можете прикрепить архив с вашими файлами (Максимальный вес: 50 МБ)"
        await message.answer(message_text)
    if message.content_type == "text" or message.caption:
        message_text = message.text if message.text else message.caption
        if text_messages_count := state_data.get("text_messages_count"):
            text_messages_count = int(text_messages_count) + 1
            if text_messages_count > 30:
                # TODO: обработать спам текстовыми сообщениями
                return
        else:
            text_messages_count = 1
        await state.update_data(text_messages_count=text_messages_count)
        updated_answer = state_data.get("detailed_answer", "") + message_text + ' \n '
        await state.update_data(detailed_answer=updated_answer)
