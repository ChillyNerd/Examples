from abc import ABC, abstractmethod
from logging import Logger

from dash import Dash

from dash_app.src.config import Config


class NotImplementedException(Exception):
    def __init__(self):
        super().__init__("This method is not implemented")


class AbstractApp(ABC):
    app: Dash
    config: Config
    log: Logger

    @abstractmethod
    def upload_file(self, client_address, file_type: str, file: dict):
        raise NotImplementedException()

    @staticmethod
    @abstractmethod
    def save_file(directory_path, filename, content):
        raise NotImplementedException()

    @abstractmethod
    def refresh_or_create_directory(self, client_address, file_type: str):
        raise NotImplementedException()

    @abstractmethod
    def delete_clients_repo(self, client_address):
        raise NotImplementedException()

    @abstractmethod
    def delete_files(self, client_address, file_type):
        raise NotImplementedException()

    @abstractmethod
    def recursive_files_delete(self, filepath):
        raise NotImplementedException()
