from typing import List

from pydantic import BaseModel


class HaDeviceConfig(BaseModel):
    identifiers: List[str]
    manufacturer: str = "LG"
    model: str
    name: str
    sw_version: str
