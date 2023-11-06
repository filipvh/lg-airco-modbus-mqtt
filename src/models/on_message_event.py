from pydantic import BaseModel

from models.mqtt_message import MqttMessage


class OnMessageEvent(BaseModel):
    msg: MqttMessage
