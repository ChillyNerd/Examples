import base64
import logging
import os

from dash import Dash

from app.abstract_app import AbstractApp
from app.components import Layout
from utils.config import Config


class ApplicationServer(AbstractApp):
    def __init__(self, config: Config):
        self.config = config
        self.log = logging.getLogger(config.application_server)
        self.app = Dash(
            __name__,
            update_title=None,
            title='Забавное название',
            suppress_callback_exceptions=True
        )
        self.app.layout = Layout(self).get_layout()
        self.hidden = 'component-hidden'

    def upload_file(self, client_address, file_type: str, file: dict):
        directory_path = self.refresh_or_create_directory(client_address, file_type)
        return self.save_file(directory_path, file['filename'], file['content'])

    def refresh_or_create_directory(self, client_address, file_type: str):
        clients_path = os.path.join(self.config.files_path, client_address)
        if not os.path.exists(clients_path):
            os.mkdir(clients_path)
        file_path = os.path.join(clients_path, file_type)
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        content = os.listdir(file_path)
        for file in content:
            self.recursive_files_delete(os.path.join(file_path, file))
        return file_path

    @staticmethod
    def save_file(path, name, content):
        data = content.encode("utf8").split(b";base64,")[1]
        file_path = os.path.join(path, name)
        with open(file_path, "wb") as fp:
            fp.write(base64.decodebytes(data))
        return file_path

    def delete_clients_repo(self, client_address):
        client_path = os.path.join(self.config.files_path, client_address)
        if os.path.exists(client_path):
            self.recursive_files_delete(client_path)
            self.log.info(f'Removed {client_address} directory')

    def delete_files(self, client_address, file_type):
        client_path = os.path.join(self.config.files_path, client_address)
        if not os.path.exists(client_path):
            return
        self.recursive_files_delete(os.path.join(client_path, file_type))
        self.log.info(f'Removed {client_address} {file_type} directory')

    def recursive_files_delete(self, filepath):
        if not os.path.exists(filepath):
            return
        if os.path.isdir(filepath):
            content = os.listdir(filepath)
            for file in content:
                self.recursive_files_delete(os.path.join(filepath, file))
            os.rmdir(filepath)
        else:
            os.remove(filepath)
