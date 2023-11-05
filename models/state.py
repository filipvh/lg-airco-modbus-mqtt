from typing import Optional

from pydantic import BaseModel

from models.fan_speed_enums import FanSpeed
from models.mode_enums import Mode


class State(BaseModel):
    running: Optional[bool] = None
    current_temperature: Optional[float] = None
    set_temperature: Optional[float] = None
    mode: Optional[Mode] = None
    fan_speed: Optional[FanSpeed] = None
