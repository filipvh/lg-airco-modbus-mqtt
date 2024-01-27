# lg-airco-modbus-mqtt
Provides an bridge between an LG Airco with PDRYCB500 to Home Assistant using a modbus tcp server and MQTT

On one side I have an LG indoor unit connected to a PDRYCB500 connected to a Modbus TCP server.
On the other side I have a Home Assistant with a MQTT server.
This piece of software is intended to connect those two together.


## Running using Docker

Example run:

`
docker run -it -v $(pwd)/config.yaml:/usr/src/app/config/config.yaml filipvanham/lg-airco-modbus-mqtt
`

You can find an example config file at [config/config.example.yaml](config/config.example.yaml)
