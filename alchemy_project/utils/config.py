from datetime import datetime
import warnings as warnings
import logging
import logging.handlers
import os
import yaml
from typing import Optional


class Config:
    db_user: str
    db_pass: str
    db_host: str
    db_port: int
    db_name: str
    use_external_oracle: bool
    external_oracle_path: str
    logging_level: str = "DEBUG"

    def __init__(self, config_path: str = os.path.join(os.getcwd(), 'config.yaml')):
        self.path = config_path
        with open(self.path, encoding='utf-8') as file:
            config_file = yaml.load(file, Loader=yaml.FullLoader)
            self.set_config_parameter('db_user', config_file, str, 'db', 'user')
            self.set_config_parameter('db_pass', config_file, str, 'db', 'pass')
            self.set_config_parameter('db_host', config_file, str, 'db', 'host')
            self.set_config_parameter('db_port', config_file, int, 'db', 'port')
            self.set_config_parameter('db_name', config_file, str, 'db', 'name')
            self.set_config_parameter('use_external_oracle', config_file, bool, 'db', 'dll', 'use_external')
            self.set_config_parameter('external_oracle_path', config_file, str, 'db', 'dll', 'path')
            self.set_config_parameter('logging_level', config_file, str, 'log', 'level')
            warnings.simplefilter('ignore')
        self.config_logging()

    def config_logging(self):
        current_date = str(datetime.now().date())
        logs_path = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(logs_path):
            os.mkdir(logs_path)
        handler = logging.handlers.RotatingFileHandler(os.path.join(logs_path, f'{current_date}.log'), mode='a',
                                                       maxBytes=5_000_000, backupCount=1000)
        logger_handlers = [handler, logging.StreamHandler()]
        logging.basicConfig(format='%(asctime)s - %(name)12s %(levelname)-7s %(threadName)12s: %(message)s',
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
