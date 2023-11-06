from typing import List

from pydantic import BaseModel

from models.ha_device_config import HaDeviceConfig
from models.mqtt_fan_speed_enums import MqttFanSpeed


class HaMqttDiscoveryConfig(BaseModel):
    name: str
    availability_topic: str
    fan_modes: List[str] = [
        MqttFanSpeed.AUTO.value,
        MqttFanSpeed.LOW.value,
        MqttFanSpeed.MEDIUM.value,
        MqttFanSpeed.HIGH.value,
        MqttFanSpeed.UNKNOWN.value
    ]
    modes: List[str] = ["auto", "off", "cool", "heat", "dry", "fan_only"]
    max_temp: int = 30
    min_temp: int = 18
    power_command_topic: str
    mode_command_topic: str
    temperature_command_topic: str
    fan_mode_command_topic: str
    mode_state_topic: str
    temperature_state_topic: str
    fan_mode_state_topic: str
    current_temperature_topic: str
    payload_available: str = "Online"
    payload_not_available: str = "Offline"
    unique_id: str
    device: HaDeviceConfig
