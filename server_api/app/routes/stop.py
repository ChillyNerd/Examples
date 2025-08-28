from fastapi.responses import JSONResponse

from app.abstract_app import AbstractApp
from app.defaults import ok


def init(source: AbstractApp):
    @source.app.post('/stop', tags=['Stop'])
    def stop():
        source.log.info("Stop called")
        return JSONResponse({"msg": "Stop called"}, status_code=ok)
