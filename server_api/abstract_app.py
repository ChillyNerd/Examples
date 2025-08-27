from abc import ABC, abstractmethod
from fastapi import FastAPI
from src.core.config import AppConfig
from src.core.schedule_utils.schedule_tasks import ScheduleTaskRunner


class AbstractApp(ABC):
    app: FastAPI
    app_config: AppConfig
    schedule_tasks: ScheduleTaskRunner

    @abstractmethod
    def dump_services(self):
        pass

    @abstractmethod
    def dump_configurations(self):
        pass

    @abstractmethod
    def dump_python_services(self):
        pass
