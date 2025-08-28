from pydantic import BaseModel


class StartData(BaseModel):
    method: str
    log_level: str = "DEBUG"
