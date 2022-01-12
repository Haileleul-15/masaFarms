//libraries for esp32 wifi lora 32 and cayennelpp
#include <ESP32_LoRaWAN.h>
#include "Arduino.h"
#include <CayenneLPP.h>

//Libraries for bme280 sensor
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

//sea level pressure in hectopascal
#define SEALEVELPRESSURE_HPA (1013.25)

#define led 23


/*license for Heltec ESP32 LoRaWan, quary your ChipID relevant license: http://resource.heltec.cn/search */
uint32_t  license[4] = { 0x2B649173,0x5BEA175E,0x3661C3C8,0xBF698289 };

/* OTAA para*/
uint8_t DevEui[] = { 0x86, 0x0d, 0xbf, 0x99, 0xa3, 0x3d, 0xdf, 0x56 };
uint8_t AppEui[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
uint8_t AppKey[] = { 0x21, 0x16, 0x5c, 0xd6, 0x98, 0xec, 0xbe, 0xa7, 0xdd, 0x0b, 0xc9, 0x9e, 0x7d, 0x56, 0x19, 0xd9 };

/* ABP para*/
uint8_t NwkSKey[] = { 0xe5, 0xa6, 0x62, 0xce, 0xaf, 0x44, 0x59, 0xf7, 0xea, 0x74, 0xe8, 0x8f, 0x23, 0xf4, 0x0c, 0x9d };
uint8_t AppSKey[] = { 0xb7, 0xe5, 0x20, 0x0a, 0xeb, 0x7d, 0x74, 0xc8, 0x49, 0x9f, 0x61, 0x87, 0xfd, 0x36, 0x1a, 0x99 };
uint32_t DevAddr =  ( uint32_t )0x01cefd6d;

/*LoraWan channelsmask, default channels 0-7*/ 
uint16_t userChannelsMask[6]={ 0x00FF,0x0000,0x0000,0x0000,0x0000,0x0000 };

/*LoraWan Class, Class A and Class C are supported*/
DeviceClass_t  loraWanClass = CLASS_A;

/*the application data transmission duty cycle.  value in [ms].*/
uint32_t appTxDutyCycle = 15000;

/*OTAA or ABP*/
bool overTheAirActivation = false;

/*ADR enable*/
bool loraWanAdr = false;

/* Indicates if the node is sending confirmed or unconfirmed messages */
bool isTxConfirmed = true;

/* Application port */
uint8_t appPort = 2;

/*!
* Number of trials to transmit the frame, if the LoRaMAC layer did not
* receive an acknowledgment. The MAC performs a datarate adaptation,
* according to the LoRaWAN Specification V1.0.2, chapter 18.4, according
* to the following table:
*
* Transmission nb | Data Rate
* ----------------|-----------
* 1 (first)       | DR
* 2               | DR
* 3               | max(DR-1,0)
* 4               | max(DR-1,0)
* 5               | max(DR-2,0)
* 6               | max(DR-2,0)
* 7               | max(DR-3,0)
* 8               | max(DR-3,0)
*
* Note, that if NbTrials is set to 1 or 2, the MAC will not decrease
* the datarate, in case the LoRaMAC layer did not receive an acknowledgment
*/
uint8_t confirmedNbTrials = 8;

/*LoraWan debug level, select in arduino IDE tools.
* None : print basic info.
* Freq : print Tx and Rx freq, DR info.
* Freq && DIO : print Tx and Rx freq, DR, DIO0 interrupt and DIO1 interrupt info.
* Freq && DIO && PW: print Tx and Rx freq, DR, DIO0 interrupt, DIO1 interrupt and MCU deepsleep info.
*/
uint8_t debugLevel = LoRaWAN_DEBUG_LEVEL;


/*LoraWan region, select in arduino IDE tools*/
LoRaMacRegion_t loraWanRegion = ACTIVE_REGION;

Adafruit_BME280 bme; // I2C

void  downLinkDataHandle(McpsIndication_t *mcpsIndication)
{
  message(mcpsIndication->BufferSize, mcpsIndication->Buffer, mcpsIndication->Port);
}

static void prepareTxFrame( uint8_t port )
{
    CayenneLPP lpp(160);
    lpp.reset();

//    uint32_t temperature = bme.readTemperature();
//    uint32_t humidity = bme.readHumidity();
//    uint32_t barometricPressure = bme.readPressure() / 100.0F;

    uint32_t temperature = 22.5;
    uint32_t humidity = 57;
    uint32_t barometricPressure = 765;

    lpp.addTemperature(3, temperature);
    lpp.addRelativeHumidity(4, humidity);
    lpp.addBarometricPressure(10, barometricPressure);
    
    appDataSize = 11;//AppDataSize max value is 64

    for(int i = 0; i < appDataSize; i++){
      appData[i] = lpp.getBuffer()[i];
    }
}

// Add your initialization code here
void setup()
{
  Serial.begin(115200);
  while (!Serial);
  pinMode(led, OUTPUT);
  //start the sensor
  bme.begin(0x76);
  SPI.begin(SCK,MISO,MOSI,SS);
  Mcu.init(SS,RST_LoRa,DIO0,DIO1,license);
  deviceState = DEVICE_STATE_INIT;
}

// The loop function is called in an endless loop
void loop()
{
  switch( deviceState )
  {
    case DEVICE_STATE_INIT:
    {
      LoRaWAN.init(loraWanClass,loraWanRegion);
      break;
    }
    case DEVICE_STATE_JOIN:
    {
      LoRaWAN.join();
      break;
    }
    case DEVICE_STATE_SEND:
    {
      prepareTxFrame( appPort );
      LoRaWAN.send(loraWanClass);
      deviceState = DEVICE_STATE_CYCLE;
      break;
    }
    case DEVICE_STATE_CYCLE:
    {
      // Schedule next packet transmission
      txDutyCycleTime = appTxDutyCycle + randr( -APP_TX_DUTYCYCLE_RND, APP_TX_DUTYCYCLE_RND );
      LoRaWAN.cycle(txDutyCycleTime);
      deviceState = DEVICE_STATE_SLEEP;
      break;
    }
    case DEVICE_STATE_SLEEP:
    {
      LoRaWAN.sleep(loraWanClass,debugLevel);
      break;
    }
    default:
    {
      deviceState = DEVICE_STATE_INIT;
      break;
    }
  }
}

void message(uint8_t BufferSize, uint8_t* Buffer, uint8_t Port){
  int timer;
  timer = Buffer[4]*1000;
  for(int i = 0; i < BufferSize; i++){
    Serial.println(Buffer[i]);
  }
  if(Buffer[1] == 2){
    digitalWrite(led, HIGH);
    delay(timer);
  }
}
