from pydantic import BaseModel


class MqttTopics(BaseModel):
    availability: str
    power_command: str
    mode_command: str
    temperature_command: str
    fan_mode_command: str
    mode_state: str
    temperature_state: str
    fan_mode_state: str
    current_temperature: str
