import pandas as pd
import numpy as np
import pre_process_readings
import sqlalchemy
import pymysql
import math

# MySQL DB variables
engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost:3306/masadb')

def prepareDataForValidation():
    readings_raw = pd.read_sql_table("readings_raw", engine)
    sizeOfDataSet = len(readings_raw)
    # find 80% of the dataset
    eightyPercentOfDataset = math.ceil(0.8 * sizeOfDataSet)
    # print(eightyPercentOfDataset)

    readings_raw = readings_raw.iloc[eightyPercentOfDataset:]
    # print(readings_raw)

    seasonValue = readings_raw['collected_at'].apply(pre_process_readings.getSeasonValue)
    readings_raw = readings_raw[['latitude', 'longitude', 'temperature', 'pressure', 'humidity', 'soil_moisture']]
    readings_raw = pd.concat([seasonValue, readings_raw], axis=1)
    readings_raw.columns = range(readings_raw.shape[1])
    # print(readings_raw)
    return readings_raw
# prepareDataForValidation()