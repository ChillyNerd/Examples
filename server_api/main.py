import logging

import uvicorn

from app.app import ApplicationServer
from utils.config import Config

config = Config()
application = ApplicationServer(config)
log = logging.getLogger('Main')
log.info('Application Server Initialized')
uvicorn.run(application.app, host=config.host, port=config.port)
log.info('Application Server Stopped')
