from fastapi.responses import JSONResponse

from app.abstract_app import AbstractApp
from app.defaults import ok


def init(source: AbstractApp):
    @source.app.get('/health', tags=['Utils'])
    def health():
        return JSONResponse({'msg': "Not dead"}, status_code=ok)

    @source.app.post('/reset', tags=['Utils'])
    def reset():
        source.reset_services()
        return JSONResponse({'msg': "Resetting now"}, status_code=ok)
