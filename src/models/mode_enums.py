from enum import Enum

from loguru import logger


class Mode(Enum):
    COOL = 0
    DRY = 1
    FAN_ONLY = 2
    AUTO = 3
    HEATING = 4

    @staticmethod
    def from_value(value: int):
        for member in Mode:
            if member.value == value:
                return member
        # Handle the case where the value is not found
        logger.error(f"Could not map integer {value} to a {Mode.__name__} value.")
        return None

