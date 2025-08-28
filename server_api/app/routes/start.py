import logging

from fastapi.responses import JSONResponse

from app.abstract_app import AbstractApp
from app.defaults import ok
from app.schemas import StartData


def init(source: AbstractApp):
    @source.app.post('/start', tags=['Start'])
    def start(start_data: StartData):
        source.log.log(logging.getLevelName(start_data.log_level), f"Start of {start_data.method} called")
        return JSONResponse({"msg": f"Start of {start_data.method} called"}, status_code=ok)
