import signal
import sys
from time import sleep

from loguru import logger

from config import load_config, load_version
from modbus_client import ModbusClient
from models.fan_speed_enums import FanSpeed
from models.ha_device_config import HaDeviceConfig
from models.ha_mqtt_discovery_config import HaMqttDiscoveryConfig
from models.mode_enums import Mode
from models.mqtt_fan_speed_enums import MqttFanSpeed
from models.mqtt_mode_enums import MqttMode
from models.mqtt_topcis import MqttTopics
from models.on_message_event import OnMessageEvent
from models.state import State
from mqtt_client import MqttClient
from state_service import StateService


class Server:
    def __init__(self):
        logger.info("Server | Setup server")
        self._config = load_config()
        self._version = load_version()
        self._topics = self._get_mqtt_topics()
        self._ha_discovery_config = self._get_ha_discovery_config()

        self._state_service = StateService()
        self._mqtt_client = MqttClient(
            config=self._config.mqtt,
            ha_discovery_config=self._ha_discovery_config
        )
        self._modbus_client = ModbusClient(config=self._config.modbus, state_service=self._state_service)

        self._mqtt_client.on_message.add_handler(self._on_mqtt_message)

        self._state_service.state_changed.add_handler(self._on_state_changed)

    def start(self) -> None:
        logger.info("Server | Startup server")
        try:
            self._modbus_client.connect()
        except Exception as e:
            logger.error(e)
            self.stop()
        self._mqtt_client.connect()
        self._mqtt_client.go_online()
        self._mqtt_client.loop_forever()

    def stop(self, signum=None, frame=None) -> None:
        logger.info(f"Server | Shutting down")
        self._mqtt_client.exit()
        self._modbus_client.disconnect()

        logger.info(f"Server | Done. Bye!")
        sys.exit(0)

    def _on_state_changed(self, changes: State) -> None:
        if changes.running is False:
            self._mqtt_client.publish_mode(MqttMode.OFF)
        if changes.running is True:
            current_state = self._state_service.get_state()
            mode = current_state.mode
            self._publish_mode_state(mode)

        if changes.running is None and changes.mode:
            self._publish_mode_state(changes.mode)

        if changes.set_temperature:
            self._mqtt_client.publish_temperature_state(changes.set_temperature)

        if changes.current_temperature:
            self._mqtt_client.publish_current_temperature_state(changes.current_temperature)

        if changes.fan_speed:
            self._publish_fan_speed_state(changes.fan_speed)

    def _publish_mode_state(self, mode) -> None:
        if mode == Mode.AUTO:
            self._mqtt_client.publish_mode(MqttMode.AUTO)
        if mode == Mode.COOL:
            self._mqtt_client.publish_mode(MqttMode.COOL)
        if mode == Mode.DRY:
            self._mqtt_client.publish_mode(MqttMode.DRY)
        if mode == Mode.FAN_ONLY:
            self._mqtt_client.publish_mode(MqttMode.FAN_ONLY)
        if mode == Mode.HEATING:
            self._mqtt_client.publish_mode(MqttMode.HEAT)

    def _publish_fan_speed_state(self, fan_speed: FanSpeed) -> None:
        if fan_speed == FanSpeed.AUTO:
            self._mqtt_client.publish_fan_speed(MqttFanSpeed.AUTO)
        if fan_speed == FanSpeed.LOW:
            self._mqtt_client.publish_fan_speed(MqttFanSpeed.LOW)
        if fan_speed == FanSpeed.MIDDLE:
            self._mqtt_client.publish_fan_speed(MqttFanSpeed.MEDIUM)
        if fan_speed == FanSpeed.HIGH:
            self._mqtt_client.publish_fan_speed(MqttFanSpeed.HIGH)
        if fan_speed == FanSpeed.UNKNOWN:
            self._mqtt_client.publish_fan_speed(MqttFanSpeed.UNKNOWN)

    def _on_mqtt_message(self, event: OnMessageEvent) -> None:
        topic = event.msg.topic
        payload = event.msg.payload

        if topic == self._ha_discovery_config.power_command_topic:
            command = str(payload)
            if command == "ON":
                self._modbus_client.write_operate(value=True)
            elif command == "OFF":
                self._modbus_client.write_operate(value=False)
                self._mqtt_client.publish_mode(mode=MqttMode.OFF)

        elif topic == self._ha_discovery_config.temperature_command_topic:
            command = float(payload)
            self._modbus_client.set_temperature(value=command)
            self._mqtt_client.publish_temperature_state(set_temperature=command)

        elif topic == self._ha_discovery_config.mode_command_topic:
            command = MqttMode.from_value(str(payload))
            if command == MqttMode.OFF:
                self._modbus_client.write_operate(value=False)
                self._mqtt_client.publish_mode(mode=command)
            else:
                self._modbus_client.write_operate(value=True)
                self._mqtt_client.publish_mode(mode=command)
                # If you set mode too quick, the mode the unit was in previously might prevail.
                sleep(3)
                self._modbus_set_mode(command)

        elif topic == self._ha_discovery_config.fan_mode_command_topic:
            logger.debug("Processing fan speed change from HA")
            command = MqttFanSpeed.from_value(str(payload))
            if command == MqttFanSpeed.AUTO:
                self._modbus_client.set_fan_speed(value=FanSpeed.AUTO)
            elif command == MqttFanSpeed.LOW:
                self._modbus_client.set_fan_speed(value=FanSpeed.LOW)
            elif command == MqttFanSpeed.MEDIUM:
                self._modbus_client.set_fan_speed(value=FanSpeed.MIDDLE)
            elif command == MqttFanSpeed.HIGH:
                self._modbus_client.set_fan_speed(value=FanSpeed.HIGH)
            elif command == MqttFanSpeed.UNKNOWN:
                self._modbus_client.set_fan_speed(value=FanSpeed.UNKNOWN)
            self._mqtt_client.publish_fan_speed(fan_speed=command)

    def _modbus_set_mode(self, command) -> None:
        if command == MqttMode.AUTO:
            self._modbus_client.set_mode(value=Mode.AUTO)
        elif command == MqttMode.COOL:
            self._modbus_client.set_mode(value=Mode.COOL)
        elif command == MqttMode.HEAT:
            self._modbus_client.set_mode(value=Mode.HEATING)
        elif command == MqttMode.DRY:
            self._modbus_client.set_mode(value=Mode.DRY)
        elif command == MqttMode.FAN_ONLY:
            self._modbus_client.set_mode(value=Mode.FAN_ONLY)

    def _get_mqtt_topics(self) -> MqttTopics:
        unique_id = self._config.id
        return MqttTopics(
            availability=f"{unique_id}/availability",
            power_command=f"{unique_id}/command/power",
            mode_command=f"{unique_id}/command/mode",
            temperature_command=f"{unique_id}/command/temperature",
            fan_mode_command=f"{unique_id}/command/fan-mode",
            mode_state=f"{unique_id}/state/mode",
            temperature_state=f"{unique_id}/state/temperature",
            fan_mode_state=f"{unique_id}/state/fan-mode",
            current_temperature=f"{unique_id}/current-temperature"
        )

    def _get_ha_discovery_config(self) -> HaMqttDiscoveryConfig:
        topics = self._topics
        config = self._config
        return HaMqttDiscoveryConfig(
            name=config.name,
            availability_topic=topics.availability,
            power_command_topic=topics.power_command,
            mode_command_topic=topics.mode_command,
            temperature_command_topic=topics.temperature_command,
            fan_mode_command_topic=topics.fan_mode_command,
            mode_state_topic=topics.mode_state,
            temperature_state_topic=topics.temperature_state,
            fan_mode_state_topic=topics.fan_mode_state,
            current_temperature_topic=topics.current_temperature,
            unique_id=config.id,
            device=HaDeviceConfig(
                identifiers=[f"lg-{config.id}"],
                model=config.model,
                name=f"LG",
                sw_version=self._version
            )
        )


logger.configure(handlers=[{"sink": sys.stdout, "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                                                          "<level>{level: <8}</level> | "
                                                          "<level>{message}</level>"}])

logger.info("Welcome to lg-airco-modbus-mqtt!")
server = Server()
try:
    server.start()
except KeyboardInterrupt:
    logger.warning("Server | Interrupt received, stopping server...")
    server.stop()

signal.signal(signal.SIGINT, server.stop)
signal.signal(signal.SIGTERM, server.stop)
