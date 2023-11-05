from enum import Enum

from loguru import logger


class FanSpeed(Enum):
    LOW = 1
    MIDDLE = 2
    HIGH = 3
    AUTO = 4
    UNKNOWN = 5

    @staticmethod
    def from_value(value: int):
        for member in FanSpeed:
            if member.value == value:
                return member
        # Handle the case where the value is not found
        logger.error(f"Could not map integer {value} to a {FanSpeed.__name__} value.")
        return None
