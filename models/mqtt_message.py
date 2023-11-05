from pydantic import BaseModel


class MqttMessage(BaseModel):
    topic: str
    payload: str
    qos: int
    retain: bool
