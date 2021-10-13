from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.commands.feedback import send_gratitude_response as feedback__send_gratitude_response
from handlers.users.commands.request import get_user_project_budget
from handlers.users.user_info import get_user_contact_details, \
    send_gratitude_response as question__send_gratitude_response
from loader import dp, db
from states.answers import DetailedAnswer


@dp.message_handler(text="Готово", state=DetailedAnswer.gather_files_and_messages)
async def stop_receiving_files(message: types.Message, state: FSMContext):
    state_data = await state.get_data()

    if state_data.get("files_count"):
        attention_message = await message.answer("<b>Пожалуйста, подождите, Ваши файлы загружаются на сервер</b>")
        await db.convert_file_ids_to_file_links(state_data["table_name"], state_data["appeal_id"], state_data["user_tg_username"])
    if state_data.get("files_count") is None and state_data.get("text_messages_count") is None:
        await message.answer("Пожалуйста, пришлите хотя бы одно сообщение или файл")
        return

    if state_data.get("files_count"):
        await attention_message.edit_text("<b>Ваши файлы были успешно загружены на сервер</b>")
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
        if message.photo:
            file_name = (await message.photo[-1].get_file()).file_path
        else:
            file_name = document.file_name
        message_text = "Файл <b>" + file_name + "</b> принимается...\n" \
                       "<i>Пожалуйста, подождите несколько секунд. Мы оповестим вас, когда файл примется.</i>"
        answered_message = await message.answer(message_text)

        user_files_in_database_count = db.get_files_count_in_appeal(state_data["table_name"], state_data["appeal_id"])
        files_count = user_files_in_database_count + 1
        error_message_text = "К сожалению, нельзя прикрепить больше файлов 😞\n" \
                             "Вы можете перенести их в облако и продублировать ссылку в сообщении\n" \
                             "Также Вы можете прикрепить архив с вашими файлами (Максимальный вес: 50 МБ)"
        if files_count > 3:
            await answered_message.edit_text(error_message_text)
            return

        await state.update_data(files_count=files_count)
        if message.photo:
            file_id = message.photo[-1].file_id
            file_name = (await message.photo[-1].get_file()).file_path
            mime_type = "image/jpeg"
        else:
            file_id = message.document.file_id
            file_name = document.file_name
            mime_type = document.mime_type
        is_file_uploaded = db.upload_file(file_id, mime_type, state_data["table_name"], state_data["appeal_id"])
        if is_file_uploaded:
            await answered_message.edit_text("Файл <b>" + file_name + "</b> принят")
        else:
            await answered_message.edit_text(error_message_text)

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
