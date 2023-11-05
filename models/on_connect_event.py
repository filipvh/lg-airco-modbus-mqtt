from typing import List, Dict

import yaml

from pydantic import BaseModel, IPvAnyAddress, Field


class OnConnectEvent(BaseModel):
    flags: Dict = Field(...)
