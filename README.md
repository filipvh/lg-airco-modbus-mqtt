# lg-airco-modbus-mqtt
Provides an bridge between an LG Airco with PDRYCB500 to Home Assistant using a modbus tcp server and MQTT

On one side I have an LG indoor unit connected to a PDRYCB500 connected to a Modbus TCP server.
On the over side I have a Home Assistant with a MQTT server.
This piece of software is intended to connect those two together.

I will provide auto configuration with MQTT and allow the user to configure it all using a YAML file.
