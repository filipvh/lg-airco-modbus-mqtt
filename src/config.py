import yaml

from pydantic import BaseModel, IPvAnyAddress, Field


class ModbusConfig(BaseModel):
    host: str = Field(..., example="192.168.1.10")
    port: int = Field(..., gt=0, lt=65535)
    slave: int = Field(..., gt=0)
    poll_interval: int = Field(..., gt=0)


class MQTTConfig(BaseModel):
    host: str = Field(..., example="mqtt.example.com")
    port: int = Field(..., gt=0, lt=65535)
    keepalive: int = Field(..., gt=0)
    username: str = Field(...)
    password: str = Field(...)


class Config(BaseModel):
    modbus: ModbusConfig
    mqtt: MQTTConfig
    name: str = Field(...)
    id: str = Field(...)
    model: str = Field(...)


def load_config():
    with open('config.yaml', 'r') as f:
        raw_config = yaml.safe_load(f)
        config = Config(**raw_config)
        return config


def load_version():
    with open('version.info', 'r') as f:
        # Read the first line and strip any leading/trailing whitespace
        version = f.readline().strip()
        return version
