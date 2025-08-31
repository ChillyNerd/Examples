from abc import ABC, abstractmethod
from logging import Logger

from fastapi import FastAPI

from utils.config import Config


class AbstractApp(ABC):
    app: FastAPI
    config: Config
    log: Logger

    @abstractmethod
    def reset_services(self):
        pass
