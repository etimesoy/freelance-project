import datetime
from typing import Union, List
from uuid import uuid4
from pathlib import Path

import firebase_admin
from firebase_admin import db, credentials, storage

from data.config import DATABASE_URL, PATH_TO_SERVICE_ACCOUNT_KEY, PATH_TO_STORAGE_BUCKET
from utils.misc.file_info import FileInfo


class Database:
    def __init__(self):
        cred = credentials.Certificate(PATH_TO_SERVICE_ACCOUNT_KEY)
        firebase_admin.initialize_app(cred, {
            "databaseURL": DATABASE_URL,
            "storageBucket": PATH_TO_STORAGE_BUCKET,
            "apiKey": "AIzaSyDFm7xJ5n_OLM6xHYenLzg2AghEYbI9Ifc",
            "authDomain": "test-freelance-bot.firebaseapp.com",
            "projectId": "test-freelance-bot",
            "messagingSenderId": "90381944667",
            "appId": "1:90381944667:web:1ddd79d8bd7c121d197c7e",
            "measurementId": "G-JQ18VKJK68"
        })
        self.ref = db.reference()
        self.bucket = storage.bucket()

    @staticmethod
    def _get_last_id_in_table(table_name: str) -> int:
        table_data = db.reference(table_name).get(shallow=True)
        count_of_entries = len(table_data) if table_data else 0
        if count_of_entries == 0:
            return 0
        try:
            return max(map(int, table_data.keys()))
        except ValueError:
            raise ValueError("IDs can only be int-like")

    def get_files_count_in_appeal(self, table_name: str, appeal_id: str):
        table_ref = self.ref.child(table_name)
        appeal_table_ref = table_ref.child(str(appeal_id))
        appeal_data = appeal_table_ref.get(shallow=True)
        return len([key for key in appeal_data.keys() if key.startswith("file_")])

    def upload_file(self, file_info: FileInfo, tg_username: str,
                    table_name: str, appeal_id: Union[int, str]) -> bool:
        """
        :param file_info:
        :param tg_username:
        :param table_name:
        :param appeal_id: номер (id) заявки/вопроса/отзыва и т.д. в таблице в бд
        :return: True если файл был успешно загружен и False и противном
        """
        table_ref = self.ref.child(table_name)
        appeal_table_ref = table_ref.child(str(appeal_id))
        new_file_order_number = self.get_files_count_in_appeal(table_name, appeal_id) + 1
        if new_file_order_number > 3:
            return False

        now_timestamp_str = str(int(datetime.datetime.now().timestamp() * 100))
        file_path = tg_username + '/' + now_timestamp_str + Path(file_info.name).suffix
        blob = self.bucket.blob(file_path)
        blob.metadata = {'firebaseStorageDownloadTokens': uuid4()}
        blob.upload_from_string(file_info.content.getvalue(), content_type=file_info.content_type)
        blob.make_public()

        appeal_table_ref.update({
            "file_" + str(new_file_order_number): blob.public_url
        })
        return True

    def _upload_data_beginning(self, table_name: str, **kwargs) -> int:
        """
        Заносит начальную информацию о заявке/вопросе/отзыве и т.д. в firebase

        :param table_name: название таблицы в firebase
        :param kwargs: начальная информация
        :return: номер (id) заявки/вопроса/отзыва и т.д. в firebase
        """
        last_id = self._get_last_id_in_table(table_name)
        table_ref = self.ref.child(table_name)

        update_data = {
            ' '.join(key.split('_')): value for key, value in kwargs.items()
            if key not in ['date']
        }
        update_data.update({
            'is viewed': False,
            'is viewed by admin': False
        })

        table_ref.update({
            last_id + 1: update_data
        })
        return last_id + 1

    def _upload_data_ending(self, table_name: str, appeal_id: Union[int, str], **kwargs):
        """
        Заносит конечную информацию о заявке/вопросе/отзыве и т.д. в firebase

        :param table_name: название таблицы в firebase
        :param appeal_id: номер (id) заявки/вопроса/отзыва и т.д. в таблице в бд
        :param kwargs: конечная информация
        :return:
        """
        table_ref = self.ref.child(table_name)
        appeal_table_ref = table_ref.child(str(appeal_id))

        update_data = {
            ' '.join(key.split('_')): value for key, value in kwargs.items()
            if key not in ['date']
        }
        date: datetime.datetime
        if 'date' in kwargs and kwargs['date'] is not None:
            date = kwargs['date']
        else:
            date = datetime.datetime.now()
        update_data.update(date=date.strftime("%Y-%m-%d %H:%M:%S"))

        appeal_table_ref.update(update_data)

    def add_feedback_beginning(self, tg_username: str, project_name: str, mark: Union[str, int]) -> int:
        return self._upload_data_beginning('feedbacks', telegram_username=tg_username,
                                           project_name=project_name, mark=int(mark))

    def add_feedback_ending(self, appeal_id: Union[int, str], discount_code: str = None,
                            desire: str = None, date: datetime.datetime = None):
        return self._upload_data_ending('feedbacks', appeal_id, discount_code=discount_code,
                                        desire=desire, date=date)

    def add_request_beginning(self, tg_username: str, user_name: str, project_name: str,
                              communication_way: str, contact_details: str) -> int:
        return self._upload_data_beginning('requests', telegram_username=tg_username, user_name=user_name,
                                           project_name=project_name, communication_way=communication_way,
                                           contact_details=contact_details)

    def add_request_ending(self, appeal_id: Union[int, str],
                           project_budget: str, messenger: str = None, call_time: str = None,
                           date: datetime.datetime = None):
        # Пользователь не может выбрать одновременно и мессенджер, и время для звонка
        assert not (messenger and call_time)
        self._upload_data_ending('requests', appeal_id,
                                 project_budget=project_budget, messenger=messenger,
                                 call_time=call_time, date=date)

    def add_partnership_type_1_beginning(self, tg_username: str, user_name: str, project_name: str,
                                         communication_way: str, contact_details: str) -> int:
        return self._upload_data_beginning('partnerships', partnership_type="Отдать проект",
                                           telegram_username=tg_username, user_name=user_name,
                                           project_name=project_name, communication_way=communication_way,
                                           contact_details=contact_details)

    def add_partnership_type_1_ending(self, appeal_id: Union[int, str],
                                      project_budget: str, messenger: str = None, call_time: str = None,
                                      date: datetime.datetime = None):
        self._upload_data_ending('partnerships', appeal_id, project_budget=project_budget,
                                 messenger=messenger, call_time=call_time, date=date)

    def add_partnership_type_2_beginning(self, tg_username: str, user_name: str, employment_type: str,
                                         company_name: str, skill_name: str) -> int:
        """
        :param tg_username:
        :param user_name:
        :param employment_type: Физическое лицо или компания
        :param company_name:
        :param skill_name: FrontEnd, BackEnd, Mobile или Another
        :return:
        """
        return self._upload_data_beginning('partnerships', partnership_type="Получить проект",
                                           telegram_username=tg_username, user_name=user_name,
                                           employment_type=employment_type, company_name=company_name,
                                           skill_name=skill_name)

    def add_partnership_type_2_ending(self, appeal_id: Union[int, str], contact_details: str,
                                      date: datetime.datetime = None):
        self._upload_data_ending('partnerships', appeal_id, contact_details=contact_details, date=date)

    def add_work_beginning(self, tg_username: str, user_name: str, skill_name: str) -> int:
        """
        :param tg_username:
        :param user_name:
        :param skill_name: FrontEnd, BackEnd, Mobile или Another
        :return:
        """
        return self._upload_data_beginning('works', telegram_username=tg_username,
                                           user_name=user_name, skill_name=skill_name)

    def add_work_ending(self, appeal_id: Union[int, str], contact_details: str,
                        date: datetime.datetime = None):
        self._upload_data_ending('works', appeal_id, contact_details=contact_details, date=date)

    def add_question_beginning(self, tg_username: str, user_name: str, project_name: str,
                               communication_way: str, contact_details: str) -> int:
        return self._upload_data_beginning('questions', telegram_username=tg_username,
                                           user_name=user_name, project_name=project_name,
                                           communication_way=communication_way,
                                           contact_details=contact_details)

    def add_question_ending(self, appeal_id: Union[int, str], messenger: str = None,
                            call_time: str = None, date: datetime.datetime = None):
        self._upload_data_ending('questions', appeal_id, messenger=messenger,
                                 call_time=call_time, date=date)
