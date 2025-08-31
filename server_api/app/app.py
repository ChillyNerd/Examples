import logging

from fastapi import FastAPI

from app.abstract_app import AbstractApp
from app.routes import *
from utils.config import Config


class ApplicationServer(AbstractApp):

    def __init__(self, config: Config):
        self.app = FastAPI()
        self.config = config
        self.log = logging.getLogger('ApplicationServer')
        self.init_routes()
        self.reset_services()

    def init_routes(self):
        init_utils_routes(self)
        init_start_routes(self)
        init_stop_routes(self)

    def reset_services(self):
        self.log.info("Services reset")
