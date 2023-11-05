from enum import Enum

from loguru import logger


class MqttFanSpeed(Enum):
    AUTO = "auto"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "Unknown"

    @staticmethod
    def from_value(value: str):
        for member in MqttFanSpeed:
            if member.value == value:
                return member
        # Handle the case where the value is not found
        logger.error(f"Could not map str {value} to a {MqttFanSpeed.__name__} value.")
        return None
