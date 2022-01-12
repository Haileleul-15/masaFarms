# masaFarms
### Project Description
masaFarms is an AIoT solution for data-driven agriculture. It employs LoRaWAN communication architecture and powerful machine learning algorithms to make soil moisture predictions for up-to 5 days in advance.

#### Hardware
The LoRaWAN architecture generally has three components.

 1. LoRaWAN end-device
The end-device is an arduino-uno based system which houses temperature, pressure, humidity and soil moisture sensors. It also has a LoRaWAN packet transmitter which sends the collected sensor readings to the LoRaWAN gateway.
![alt text](https://github.com/haile-leul/masaFarms/blob/main/img/IMG_20210816_210706.jpg)
 2. LoRaWAN gateway
The gateway is a central hub which collects the LoRa traffic coming from different end-devices deployed within a certain range. The gateway decodes the received message and forwards the packet to the LoRaWAN network server.
 3. LoRaWAN network server
The network server enables connectivity, management, and monitoring of devices, gateways and end-user applications. Here the received packet is unpacked and the data used for further processing.
