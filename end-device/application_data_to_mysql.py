import paho.mqtt.client as mqtt
# from influxdb import InfluxDBClient
import datetime
import json
from time import gmtime, strftime
import chardet
import mysql.connector as mysql

# MQTT Settings
# The topic selects only application ID 3 (chaire_cisco_weather_station)
MQTT_Broker = "localhost"
MQTT_Port = 1883
Keep_Alive_Interval = 45
MQTT_Topic = "application/3/+/+/rx"    #2/device/afe79ec0c3ed5b27/rx

# # InfluxDB Settings
# INFLUXDB_ADDRESS = 'localhost'
# INFLUXDB_DATABASE = 'lorax_hz'
# INFLUXDB_USER = 'test_user'
# INFLUXDB_PASSWORD = 'akcF59G1kfa'

# MySQL DB variables
DB_HOST = "localhost"
DB_NAME = "masadb"
DB_USER = "root"
DB_PASS = "admin"

# Function to input new data to mysql db
def updateDB(collectedAt, deviceId, temperature, pressure, humidity, soilMoisture):
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

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_Topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    collectedAt = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    resp_dict = json.loads(msg.payload.decode(chardet.detect(msg.payload)["encoding"]))
    obj = resp_dict["object"]
    deviceId = resp_dict["deviceName"]
    soilMoisture = obj["analogInput"]["5"]
    pressure = obj["barometer"]["10"]
    temperature = obj["temperatureSensor"]["3"]
    humidity = obj["humiditySensor"]["4"]
    print(obj)
    print(deviceId)
    print(soilMoisture)
    print(temperature)
    print(pressure)
    print(humidity)

    updateDB(collectedAt, deviceId, temperature, pressure, humidity, soilMoisture)    

    # rxinfo = resp_dict["rxInfo"]
    # location = rxinfo[0]["location"]
    # latitude = location["latitude"]
    # longitude = location["longitude"]

    # length = len(obj)
    # print(length)

    # appname = resp_dict["applicationName"]
    # deveui = resp_dict["devEUI"]
    # devname = resp_dict["deviceName"]

    # for i in obj: #for humsensor and tempsensor

    #     print(i)
    #     newobj = obj[i]
    #     print(newobj)

    #     if i == "temperatureSensor":
    #         unit = "C"
    #     if i == "humiditySensor":
    #         unit = "%"
    #     if i == "barometer":
    #         unit = "hPa"
    #     if i == "analogInput":
    #         unit = "hPa"

    #     for j in newobj:

    #         #print(j.values())
    #         value = newobj[j]
    #         print(value)
    #         print(i)
    #         print(j)
    #         # Create a database named appDataTest1
    #         json_body = [
    #         {
    #             "measurement": "appDataTest1", #i,#"temperature",
    #             "tags": {
    #                 "applicationName": appname,
    #                 "deviceEUI": deveui,
    #                 "deviceName": devname,
    #                 "gps": str(round(latitude,2)) + " N " + str(round(longitude,2)) + $
    #                 "location": "Cisco Lab",
    #                 "measurementType": i
    #             },
    #             "time": str(theTime),
    #             "fields": {
    #                 "value": value, #str(msg.payload)
    #                 "unit" : unit
    #             }
    #         }
    #         ]
    #     influx_client.write_points(json_body)
    # print(msg.topic+" "+str(msg.payload))

# influx_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWOR$
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
