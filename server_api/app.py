from fastapi import FastAPI

from src.core.application_server.abstract_app import AbstractApp
from src.core.application_server.routes import *
from src.core.config import AppConfig
from src.core.implementations.utils import dump_services, dump_configurations, dump_python_services
from src.core.schedule_utils.schedule_tasks import ScheduleTaskRunner


class ApplicationServer(AbstractApp):

    def __init__(self, app_config: AppConfig, schedule_tasks: ScheduleTaskRunner):
        self.app = FastAPI()
        self.app_config = app_config
        self.schedule_tasks = schedule_tasks
        self.init_routes()
        self.dump_services()
        self.dump_configurations()
        self.dump_python_services()

    def init_routes(self):
        init_utils_routes(self)
        init_configure_routes(self)
        init_start_routes(self)
        init_stop_routes(self)
        init_restart_routes(self)
        init_deploy_routes(self)
        init_set_routes(self)
        init_drop_routes(self)
        init_list_routes(self)
        init_schedule_routes(self)
        init_update_routes(self)
        init_backup_routes(self)

    def dump_services(self):
        dump_services(self.app_config)

    def dump_configurations(self):
        dump_configurations(self.app_config)

    def dump_python_services(self):
        dump_python_services(self.app_config)
