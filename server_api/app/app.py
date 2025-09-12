import logging

from fastapi import FastAPI

from app.abstract_app import AbstractApp
import app.routes as routes
from utils.config import Config


class ApplicationServer(AbstractApp):

    def __init__(self, config: Config):
        self.app = FastAPI()
        self.config = config
        self.log = logging.getLogger('ApplicationServer')
        self.init_routes()
        self.reset_services()

    def init_routes(self):
        initable_routes = list(filter(lambda attr: attr.startswith('init'), dir(routes)))
        for route_name in initable_routes:
            init_route = getattr(routes, route_name)
            if init_route is not None:
                init_route(self)

    def reset_services(self):
        self.log.info("Services reset")
