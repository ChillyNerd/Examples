import logging
import logging.handlers
import os
import socket
from datetime import datetime
from typing import Optional

import yaml


class Config:
    host: str = socket.gethostname()
    port: int = 80
    logging_level: str = "DEBUG"

    def __init__(self, config_path: str = os.path.join(os.getcwd(), 'config.yaml')):
        if os.path.exists(config_path):
            with open(config_path, encoding='utf-8') as file:
                config_file = yaml.load(file, Loader=yaml.FullLoader)
                self.set_config_parameter('host', config_file, str, 'app', 'host')
                self.set_config_parameter('port', config_file, int, 'app', 'port')
                self.set_config_parameter('logging_level', config_file, str, 'log', 'level')
        else:
            default_config = {'log': {'level': "INFO"}}
            with open(config_path, mode='w') as file:
                yaml.dump(default_config, file)
        self.config_logging()

    def config_logging(self):
        current_date = str(datetime.now().date())
        logs_path = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(logs_path):
            os.mkdir(logs_path)
        handler = logging.handlers.RotatingFileHandler(os.path.join(logs_path, f'{current_date}.log'), mode='a',
                                                       maxBytes=5_000_000, backupCount=1000)
        logger_handlers = [handler, logging.StreamHandler()]
        logging.basicConfig(format='%(asctime)s - %(name)20s %(levelname)-7s %(threadName)20s: %(message)s',
                            handlers=logger_handlers, level=logging.getLevelName(self.logging_level))

    def set_config_parameter(self, config_parameter, config_file: dict, parameter_type: Optional[type],
                             *parameter_names):
        if len(parameter_names) == 0:
            return
        inner_config = config_file
        for parameter_name in parameter_names:
            if not isinstance(inner_config, dict) or parameter_name not in inner_config.keys():
                return
            inner_config = inner_config[parameter_name]
        if parameter_type is not None:
            self.__setattr__(config_parameter, parameter_type(inner_config))
        else:
            self.__setattr__(config_parameter, inner_config)
