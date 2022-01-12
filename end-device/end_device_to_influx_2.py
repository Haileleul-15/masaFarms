import serial
import time
from influxdb import InfluxDBClient
import datetime
import json
from time import gmtime, strftime
import chardet

#InfluxDB Variables
INFLUXDB_ADDRESS = 'localhost'
INFLUXDB_DATABASE = 'test_database'
INFLUXDB_USER = ''
INFLUXDB_PASSWORD = ''

# make sure the 'COM#' is set according the Windows Device Manager
ser = serial.Serial('COM6', 9600, timeout=1)
time.sleep(2)

influx_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, database=INFLUXDB_DATABASE)

def updateDB(temperature, humidity):
    json_body = [
            {
                "measurement": "readings_verification",
                "tags": {
                    "gatewayID": 'asavq23214fsa',
                    "temperature": temperature,
                    "humidity": humidity,
                },
                "time": str(theTime),
                "fields": {
                    "soil_moisture": 0
                }
            }
            ]
    influx_client.write_points(json_body)

while(1):
    theTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    line = ser.readline()   # read a byte
    if line:
        string = line.decode()  # convert the byte string to a unicode string
        # print(string)
        if string[-3] == 'C':
            size = len(string)
            temp_string = string[: size -5]
            temperature = float(temp_string)
            print("Temperature")
            print(temperature)

        # elif string[-3] == 'a':
        #     size = len(string)
        #     pressure_string = string[: size -6]
        #     pressure = float(pressure_string)
        #     print("Pressure")
        #     print(pressure)

        elif string[-3] == '%' and string[-4] == ' ':
            size = len(string)
            humidity_string = string[: size -4]
            humidity = float(humidity_string)
            print("Humidity")
            print(humidity)
            updateDB(temperature, humidity)
        
        # elif string[-3] == '%' and string[-4] == '%':
        #     size = len(string)
        #     soil_moisture_string = string[: size -4]
        #     soilMoisture = float(soil_moisture_string)
        #     print("Soil Moisture")
        #     print(soilMoisture)
        #     updateDB(temperature, pressure, humidity, soilMoisture)

        # num = int(string) # convert the unicode string to an int
        # print(num)
        

ser.close()
