import paho.mqtt.client as mqtt
from loguru import logger

from config import MQTTConfig
from event_hook import EventHook
from models.ha_mqtt_discovery_config import HaMqttDiscoveryConfig
from models.mqtt_fan_speed_enums import MqttFanSpeed
from models.mqtt_message import MqttMessage
from models.mqtt_mode_enums import MqttMode
from models.on_connect_event import OnConnectEvent
from models.on_disconnect_event import OnDisconnectEvent
from models.on_message_event import OnMessageEvent


class MqttClient:
    def __init__(self, config: MQTTConfig, ha_discovery_config: HaMqttDiscoveryConfig):
        self._config = config
        self._ha_discovery_config = ha_discovery_config

        self._client = mqtt.Client()
        self._client.username_pw_set(username=self._config.username, password=self._config.password)

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

        self.on_connected = EventHook[OnConnectEvent]()
        self.on_message = EventHook[OnMessageEvent]()
        self.on_disconnect = EventHook[OnDisconnectEvent]()

    def connect(self) -> None:
        host = self._config.host
        port = self._config.port

        logger.info(f"MQTT   | Connecting to {host}:{port}")
        self._client.connect(
            host=host,
            port=port,
            keepalive=self._config.keepalive
        )

    def go_online(self) -> None:
        topics = [
            self._ha_discovery_config.power_command_topic,
            self._ha_discovery_config.mode_command_topic,
            self._ha_discovery_config.temperature_command_topic,
            self._ha_discovery_config.fan_mode_command_topic
        ]

        for topic in topics:
            self._client.subscribe(topic=topic, qos=0)

        self._client.will_set(
            topic=self._ha_discovery_config.availability_topic,
            payload=self._ha_discovery_config.payload_not_available,
            retain=True
        )
        self._client.publish(
            topic=f"homeassistant/climate/lg-{self._ha_discovery_config.unique_id}/config",
            payload=self._ha_discovery_config.model_dump_json(),
            retain=True
        )
        self._client.publish(
            topic=self._ha_discovery_config.availability_topic,
            payload=self._ha_discovery_config.payload_available,
            retain=True
        )

    def go_offline(self) -> None:
        self._client.publish(
            topic=self._ha_discovery_config.availability_topic,
            payload=self._ha_discovery_config.payload_not_available,
            retain=True
        )

    def loop_forever(self, timeout=1.0, max_packets=1, retry_first_connection=False) -> None:
        logger.info("MQTT   | Starting loop")
        self._client.loop_forever(timeout=timeout, max_packets=max_packets,
                                  retry_first_connection=retry_first_connection)
        logger.info("MQTT   | Loop has ended")

    def publish_mode(self, mode: MqttMode) -> None:
        logger.debug(f"MQTT   | Publishing mode {mode} to HA")
        self._client.publish(
            topic=self._ha_discovery_config.mode_state_topic,
            payload=mode.value,
            qos=0,
            retain=True
        )

    def publish_temperature_state(self, set_temperature: float) -> None:
        logger.debug(f"MQTT   | Publishing set temperature {set_temperature} to HA")
        self._client.publish(
            topic=self._ha_discovery_config.temperature_state_topic,
            payload=str(set_temperature),
            qos=0,
            retain=True
        )

    def publish_current_temperature_state(self, current_temperature: float) -> None:
        logger.debug(f"MQTT   | Publishing current temperature {current_temperature} to HA")
        self._client.publish(
            topic=self._ha_discovery_config.current_temperature_topic,
            payload=str(current_temperature),
            qos=0,
            retain=True
        )

    def publish_fan_speed(self, fan_speed: MqttFanSpeed) -> None:
        logger.debug(f"MQTT   | Publishing fan speed {fan_speed} to HA")
        self._client.publish(
            topic=self._ha_discovery_config.fan_mode_state_topic,
            payload=fan_speed.value,
            qos=0,
            retain=True
        )

    def exit(self) -> None:
        logger.info('MQTT   | Stopping loop.')
        self._client.loop_stop(True)
        logger.info('MQTT   | Disconnecting.')
        self._client.disconnect()

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc: int) -> None:
        if rc == 0:
            logger.info("MQTT   | Connected!")
            self.on_connected.fire(OnConnectEvent(flags=flags))
        else:
            logger.error("MQTT   | Could not connect to Server")

    def _on_message(self, client: mqtt.Client, userdata, msg) -> None:
        logger.debug(
            f"MQTT   | Received message | Topic: {msg.topic} | qos: {msg.qos}  | retain: {msg.retain} | Payload: {msg.payload}")
        self.on_message.fire(OnMessageEvent(msg=MqttMessage(
            topic=msg.topic,
            payload=msg.payload,
            qos=msg.qos,
            retain=msg.retain
        )))

    def _on_disconnect(self, client: mqtt.Client, userdata, rc: int) -> None:
        logger.info(f"MQTT   | Disconnected with result code {rc}")
        self.on_disconnect.fire(OnDisconnectEvent(rc=rc))
