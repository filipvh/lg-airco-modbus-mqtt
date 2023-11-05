from pydantic import BaseModel


class OnDisconnectEvent(BaseModel):
    rc: int
