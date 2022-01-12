import serial
import time
from influxdb import InfluxDBClient
import datetime
import json
from time import gmtime, strftime
import chardet
import mysql.connector as mysql

# MySQL DB variables
DB_HOST = "localhost"
DB_NAME = "masadb"
DB_USER = "root"
DB_PASS = "admin"

# make sure the 'COM#' is set according the Windows Device Manager
ser = serial.Serial('COM5', 115000, timeout=1)
time.sleep(2)


def updateDB(collectedAt, device_id, temperature, pressure, humidity, soilMoisture):
    # connect to mysql database
    masadb = mysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    
    dbcursor = masadb.cursor()
    insertToReadingsQuery = "INSERT INTO readings_raw (collected_at, device_id, temperature, pressure, humidity, soil_moisture, latitude, longitude) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
    insertToReadingsForPPQuery = "INSERT INTO readings_for_pre_process (collected_at, device_id, temperature, pressure, humidity, soil_moisture, latitude, longitude) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
    
    dbcursor.execute("select latitude, longitude from sites where site_id = (select located_at from devices where device_id = '%s')"% (deviceId))
    gps = dbcursor.fetchone()

    val = (collectedAt, deviceId, temperature, pressure, humidity, soilMoisture, gps[0], gps[1])

    dbcursor.execute(insertToReadingsQuery, val)
    dbcursor.execute(insertToReadingsForPPQuery, val)

    masadb.commit()
    dbcursor.close()
    masadb.close()


while(1):
    collectedAt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    deviceId = "dragino-end-device-001"
    # deviceId = "dragino-end-device-002"

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

        elif string[-3] == 'a':
            size = len(string)
            pressure_string = string[: size -6]
            pressure = float(pressure_string)
            print("Pressure")
            print(pressure)

        elif string[-3] == '%' and string[-4] == ' ':
            size = len(string)
            humidity_string = string[: size -4]
            humidity = float(humidity_string)
            print("Humidity")
            print(humidity)
        
        elif string[-3] == '%' and string[-4] == '%':
            size = len(string)
            soil_moisture_string = string[: size -4]
            soilMoisture = float(soil_moisture_string)
            print("Soil Moisture")
            print(soilMoisture)
            updateDB(collectedAt, deviceId, temperature, pressure, humidity, soilMoisture)

ser.close()
