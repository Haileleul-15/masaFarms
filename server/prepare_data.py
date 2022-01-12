import sqlalchemy
import pymysql
import pandas as pd
import numpy as np
import math
import time
import datetime
from time import strftime

# MySQL DB variables
engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost:3306/masadb')
connection = engine.connect()

# function to prepare timestamp change of reading time from Jan 1st of that collection year[get season]
def getSeasonValue(readingDatetime):
  element = datetime.datetime.strptime(str(readingDatetime), "%Y-%m-%d %H:%M:%S")
  timestampNow = datetime.datetime.timestamp(element)
  today = datetime.date.fromtimestamp(timestampNow)

  basedatetime = datetime.date(today.year, 1, 1)
  timestampBase = time.mktime(basedatetime.timetuple())
  # print(timestampNow - timestampBase)
  return timestampNow - timestampBase

# function to change the array from database to a pandas dataframe, reshape it and reorder the number
def cleanDataFrame(readings_raw):
  readings_raw_df = pd.DataFrame(readings_raw)
  readings_raw_df = readings_raw_df.drop(['reading_id', 'device_id'], axis = 1)
  # readings_raw_df.columns = range(readings_raw_df.shape[1])

  return readings_raw_df

def prepare(readings_raw):
  readings_prepared = cleanDataFrame(readings_raw)

  seasonValue = readings_prepared['collected_at'].apply(getSeasonValue)

  readings_prepared = readings_prepared[['latitude', 'longitude', 'temperature', 'pressure', 'humidity', 'soil_moisture']]
  readings_prepared = pd.concat([seasonValue, readings_prepared], axis=1)
  readings_prepared = readings_prepared.rename(columns={'collected_at': 'seasonValue'})
  # print(readings_prepared)

  return readings_prepared

# function to add the preprocessed data into the database
def preparedDataToDB(readings_prepared):  
  print("Pre-processed data")
  print(readings_prepared)
  readings_prepared.to_sql(name='readings_prepared',con=engine, index=False, if_exists='replace')
  print('Prepared data successfully added to database')

def run():
  print('Starting data preparation...')
  # connect to mysql database

  readings_raw = pd.read_sql_table("readings_raw", engine)

  # check if database has new entires for preprocessing, if so preprocess
  if(not readings_raw.empty):
      readings_prepared = prepare(readings_raw)
      preparedDataToDB(readings_prepared)
      print('Data prepared successfully completed')
  else:
      print('Raw database is empty')

# run()