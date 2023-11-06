from enum import Enum

from loguru import logger


class MqttMode(Enum):
    AUTO = "auto"
    OFF = "off"
    COOL = "cool"
    HEAT = "heat"
    DRY = "dry"
    FAN_ONLY = "fan_only"

    @staticmethod
    def from_value(value: str):
        for member in MqttMode:
            if member.value == value:
                return member
        # Handle the case where the value is not found
        logger.error(f"Could not map str {value} to a {MqttMode.__name__} value.")
        return None
