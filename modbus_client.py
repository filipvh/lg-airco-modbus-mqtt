from threading import Event, Timer

from loguru import logger
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

from config import ModbusConfig
from models.fan_speed_enums import FanSpeed
from models.mode_enums import Mode
from models.state import State
from state_service import StateService


class ModbusClient:
    def __init__(self, config: ModbusConfig, state_service: StateService):
        self._config = config
        self._state_service = state_service
        self._client = ModbusTcpClient(host=config.host, port=config.port)
        self._poll_interval = config.poll_interval
        self._shutdown_event = Event()
        self._loops_to_skip = 0

    def start_polling(self) -> None:
        logger.info("Modbus | Starting the modbus polling...")
        self._shutdown_event.clear()
        self._schedule_next_poll()

    def stop_polling(self) -> None:
        logger.info("Modbus | Stopping the modbus polling...")
        self._shutdown_event.set()
        if self._poll_timer:
            self._poll_timer.cancel()

    def _schedule_next_poll(self):
        if not self._shutdown_event.is_set():
            self._poll_timer = Timer(interval=self._poll_interval, function=self._poll_modbus_server)
            self._poll_timer.start()

    def _poll_modbus_server(self):
        slave = self._config.slave
        if self._loops_to_skip>0:
            logger.debug("Skipping poll")
            self._loops_to_skip -= 1
            self._schedule_next_poll()
            return

        if self._shutdown_event.is_set():
            # Stop polling since the shutdown flag is set
            return

        try:
            if not self._client.is_socket_open():
                self._client.connect()

            """
            Read in operation
            """
            in_operation = None
            rr = self._client.read_coils(address=0, slave=slave, unit=1)
            if rr.isError():
                logger.error("Modbus | Could not read set temperature")
                pass
            else:
                in_operation = rr.bits[0] == 1

            """
            Read current temperature
            """
            current_temperature = None
            rr = self._client.read_input_registers(address=2, slave=slave, unit=1)
            if rr.isError():
                logger.error("Modbus | Could not read current temperature")
                pass
            else:
                current_temperature = rr.registers[0] / 10

            """
            Read set temperature
            """
            set_temperature = None
            rr = self._client.read_holding_registers(address=1, slave=slave, unit=1)
            if rr.isError():
                logger.error("Modbus | Could not read set temperature")
                pass
            else:
                set_temperature = rr.registers[0] / 10

            """
            Read run mode
            """
            run_mode = None
            rr = self._client.read_holding_registers(address=0, slave=slave, unit=1)
            if rr.isError():
                logger.error("Modbus | Could not read run mode")
                pass
            else:
                run_mode = rr.registers[0]

            """
            Read fan speed
            """
            fan_speed = None
            rr = self._client.read_holding_registers(address=14, slave=slave, unit=1)
            if rr.isError():
                logger.error("Modbus | Could not read fan speed")
                pass
            else:
                fan_speed = rr.registers[0]

            """
            Send off the state
            """
            self._state_service.merge_in_state(State(
                running=in_operation,
                current_temperature=current_temperature,
                set_temperature=set_temperature,
                mode=Mode.from_value(run_mode),
                fan_speed=FanSpeed.from_value(fan_speed)
            ))
        except ConnectionException as e:
            logger.error(f"Modbus | Connection exception: {e}")
        except Exception as e:
            logger.error(f"Modbus | Polling exception: {e}")
        finally:
            self._schedule_next_poll()

    def write_operate(self, value: bool):
        logger.info(f"Modbus | Writing {value} to operate coil.")
        self._loops_to_skip = 3
        response = self._client.write_coil(address=0, value=value, slave=self._config.slave)
        if response.isError():
            logger.error(f"Modbus | Could not set operate to {value}")
        else:
            logger.info(f"Modbus | {response}")

    def set_temperature(self, value: float):
        temp = int(value*10)
        logger.info(f"Modbus | Writing {value} to register 1.")
        self._loops_to_skip = 3
        response = self._client.write_register(address=1, value=temp, slave=self._config.slave)
        if response.isError():
            logger.error(f"Modbus | Could not set temperature to {temp}")
        else:
            logger.info(f"Modbus | {response}")

    def set_mode(self, value: Mode):
        mode = value.value
        logger.info(f"Modbus | Writing {value} to register 0.")
        self._loops_to_skip = 3
        response = self._client.write_register(address=0, value=mode, slave=self._config.slave)
        if response.isError():
            logger.error(f"Modbus | Could not set mode to {mode}")
        else:
            logger.info(f"Modbus | {response}")

    def set_fan_speed(self, value):
        fan_speed = value.value
        logger.info(f"Modbus | Writing {value} to register 0.")
        self._loops_to_skip = 3
        response = self._client.write_register(address=14, value=fan_speed, slave=self._config.slave)
        if response.isError():
            logger.error(f"Modbus | Could not set fan speed to {fan_speed}")
        else:
            logger.info(f"Modbus | {response}")
