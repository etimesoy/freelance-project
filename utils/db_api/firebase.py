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

    def upload_file(self, file_info: FileInfo, tg_username: str) -> str:
        file_name = tg_username + '/' + str(int(datetime.datetime.now().timestamp())) + Path(file_info.name).suffix
        blob = self.bucket.blob(file_name)
        blob.metadata = {'firebaseStorageDownloadTokens': uuid4()}
        blob.upload_from_string(file_info.content.getvalue(), content_type=file_info.content_type)
        blob.make_public()
        return blob.public_url

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

    def _upload_data(self, table_name: str, **kwargs):
        last_id = self._get_last_id_in_table(table_name)
        table_ref = self.ref.child(table_name)

        update_data = {
            ' '.join(key.split('_')): value for key, value in kwargs.items()
            if key not in ['date', 'attached_files_links']
        }
        update_data.update({
            'is viewed': False,
            'is viewed by admin': False
        })
        if 'date' in kwargs and kwargs['date'] is not None:
            date = kwargs['date']
        else:
            date = datetime.datetime.now()
        update_data.update(date=date.strftime("%Y-%m-%d %H:%M:%S"))
        if 'attached_files_links' in kwargs:
            attached_files_links = kwargs['attached_files_links']
            for number, file_link in enumerate(attached_files_links, start=1):
                update_data.update({
                    "file_" + str(number): file_link
                })

        table_ref.update({
            last_id + 1: update_data
        })

    def add_feedback(self, tg_username: str, project_name: str, mark: Union[str, int],
                     message: str, attached_files_links: List[str],
                     discount_code: str = None, desire: str = None,
                     date: datetime.datetime = None):
        self._upload_data(table_name='feedbacks', telegram_username=tg_username,
                          project_name=project_name,
                          attached_files_links=attached_files_links,
                          message=message, date=date,
                          mark=int(mark), discount_code=discount_code, desire=desire)

    def add_request(self, tg_username: str, user_name: str, project_name: str,
                    communication_way: str, contact_details: str,
                    project_description: str, attached_files_links: List[str],
                    project_budget: str, messenger: str = None, call_time: str = None,
                    date: datetime.datetime = None):
        # Пользователь не может выбрать одновременно и мессенджер, и время для звонка
        assert not (messenger and call_time)
        self._upload_data(table_name='requests', telegram_username=tg_username,
                          user_name=user_name, project_name=project_name,
                          communication_way=communication_way, contact_details=contact_details,
                          project_description=project_description,
                          attached_files_links=attached_files_links, project_budget=project_budget,
                          messenger=messenger, call_time=call_time, date=date)

    def add_partnership_type_1(self, tg_username: str, user_name: str, project_name: str,
                               communication_way: str, contact_details: str,
                               project_description: str, attached_files_links: List[str],
                               project_budget: str, messenger: str = None, call_time: str = None,
                               date: datetime.datetime = None):
        self._upload_data(table_name='partnerships', partnership_type="Отдать проект",
                          telegram_username=tg_username, user_name=user_name, project_name=project_name,
                          communication_way=communication_way, contact_details=contact_details,
                          project_description=project_description,
                          attached_files_links=attached_files_links, project_budget=project_budget,
                          messenger=messenger, call_time=call_time, date=date)

    def add_partnership_type_2(self, tg_username: str, user_name: str, employment_type: str,
                               company_name: str, skill_name: str, description: str,
                               attached_files_links: List[str], contact_details: str,
                               date: datetime.datetime = None):
        """
        :param tg_username:
        :param user_name:
        :param employment_type: Физическое лицо или компания
        :param company_name:
        :param skill_name: FrontEnd, BackEnd, Mobile или Another
        :param description:
        :param attached_files_links:
        :param contact_details:
        :param date:
        """
        self._upload_data(table_name='partnerships', partnership_type="Получить проект",
                          telegram_username=tg_username, user_name=user_name,
                          employment_type=employment_type, company_name=company_name,
                          skill_name=skill_name, description=description,
                          attached_files_links=attached_files_links,
                          contact_details=contact_details, date=date)

    def add_work(self, tg_username: str, user_name: str, skill_name: str, description: str,
                 attached_files_links: List[str], contact_details: str, date: datetime.datetime = None):
        """
        :param tg_username:
        :param user_name:
        :param skill_name: FrontEnd, BackEnd, Mobile или Another
        :param description: Описание навыков и компетенций пользователя
        :param attached_files_links:
        :param contact_details:
        :param date:
        """
        self._upload_data(table_name='works', telegram_username=tg_username, user_name=user_name,
                          skill_name=skill_name, description=description,
                          attached_files_links=attached_files_links,
                          contact_details=contact_details, date=date)

    def add_question(self, tg_username: str, user_name: str, communication_way: str,
                     contact_details: str, question: str, attached_files_links: List[str],
                     messenger: str = None, call_time: str = None, date: datetime.datetime = None):
        self._upload_data(table_name='questions', telegram_username=tg_username, user_name=user_name,
                          communication_way=communication_way, contact_details=contact_details,
                          question=question, attached_files_links=attached_files_links,
                          messenger=messenger, call_time=call_time, date=date)
