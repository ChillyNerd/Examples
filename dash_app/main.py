import logging

from dash_app.app import ApplicationServer
from dash_app.utils.config import Config

if __name__ == '__main__':
    config = Config()
    log = logging.getLogger(config.main)
    try:
        server = ApplicationServer(config)
        log.debug("Application initialized")
        log.debug(f"Config host {config.host} and port {config.port}")
        server.app.run_server(host=config.host, port=config.port, ssl_context=config.ssl_context)
        log.debug("Application stopped")
    except Exception as e:
        log.error("Failed to initialize application")
        log.exception(e)
