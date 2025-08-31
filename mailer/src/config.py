import datetime
import logging
import logging.handlers
import os
from typing import Optional

import yaml


class Config:
    mailer_host: Optional[str] = None
    mailer_port: Optional[int] = None
    mailer_user: Optional[str] = None
    mailer_password: Optional[str] = None
    mailer_from: Optional[str] = None
    logging_level: str = logging.INFO
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_name: Optional[str] = None

    def __init__(self, config_path: str = os.path.join(os.getcwd(), 'config.yaml')):
        with open(config_path, encoding='utf-8') as file:
            config_file = yaml.load(file, Loader=yaml.FullLoader)
            self.set_config_parameter('mailer_host', config_file, str, 'mail', 'host')
            self.set_config_parameter('mailer_port', config_file, str, 'mail', 'port')
            self.set_config_parameter('mailer_user', config_file, str, 'mail', 'user')
            self.set_config_parameter('mailer_password', config_file, str, 'mail', 'password')
            self.set_config_parameter('mailer_from', config_file, str, 'mail', 'from')
            self.set_config_parameter('logging_level', config_file, str, 'log', 'level')
            self.set_config_parameter('db_host', config_file, str, 'db', 'host')
            self.set_config_parameter('db_port', config_file, int, 'db', 'port')
            self.set_config_parameter('db_user', config_file, str, 'db', 'user')
            self.set_config_parameter('db_password', config_file, str, 'db', 'password')
            self.set_config_parameter('db_name', config_file, str, 'db', 'name')
        self.config_logging()

    def config_logging(self):
        current_date = str(datetime.datetime.now().date())
        logs_path = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(logs_path):
            os.mkdir(logs_path)
        handler = logging.handlers.RotatingFileHandler(os.path.join(logs_path, f'{current_date}.log'), mode='a',
                                                       maxBytes=5_000_000, backupCount=1000)
        logger_handlers = [handler, logging.StreamHandler()]
        logging.basicConfig(format='%(asctime)s - %(name)21s %(levelname)-7s %(threadName)12s: %(message)s',
                            handlers=logger_handlers, level=logging.getLevelName(self.logging_level))
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

    def set_config_parameter(self, config_parameter, config_file: dict, parameter_type: type, *parameter_names):
        if len(parameter_names) == 0:
            return
        inner_config = config_file
        for parameter_name in parameter_names:
            if not isinstance(inner_config, dict) or parameter_name not in inner_config.keys():
                return
            inner_config = inner_config[parameter_name]
        if not isinstance(inner_config, dict):
            self.__setattr__(config_parameter, parameter_type(inner_config))
