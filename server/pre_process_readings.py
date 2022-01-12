import time
import datetime
from time import strftime
import pandas as pd
import numpy as np
import math
import sqlalchemy
import pymysql

# MySQL DB variables
engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost:3306/masadb')
connection = engine.connect()

readings_pre_processes = pd.DataFrame()
readings_seasonValue = pd.DataFrame()
readings_gps = pd.DataFrame()

# function to prepare timestamp change of reading time from Jan 1st of that collection year[get season]
def getSeasonValue(readingDatetime):

    element = datetime.datetime.strptime(str(readingDatetime), "%Y-%m-%d %H:%M:%S")
    timestampNow = datetime.datetime.timestamp(element)
    today = datetime.date.fromtimestamp(timestampNow)

    basedatetime = datetime.date(today.year, 1, 1)
    timestampBase = time.mktime(basedatetime.timetuple())
    # print(timestampNow - timestampBase)
    return timestampNow - timestampBase

# function to check if the reading entries being compared prior to being averaged are collected by the same device. i.e from the same site
def checkReadingSite(readings_raw_current_device, reading_raw_temp_device):
    return readings_raw_current_device == reading_raw_temp_device

# function to change the array from database to a pandas dataframe, reshape it and reorder the number
def prepareDataFrame(readings_raw):
    readings_raw_df = pd.DataFrame(readings_raw)
    readings_raw_df = readings_raw_df.drop(['reading_id'], axis = 1)
    readings_raw_df.columns = range(readings_raw_df.shape[1])

    return readings_raw_df

# function to add the preprocessed data into the database
def preProcessedDataToDB():
    i = 0
    global readings_pre_processes
    global readings_seasonValue
    global readings_gps

    readings_pre_processes = pd.concat([readings_seasonValue, readings_pre_processes, readings_gps], axis=1)
    readings_pre_processes = readings_pre_processes.rename(columns={6: 'latitude', 7: 'longitude'}, inplace=False)
    
    print("Pre-processed data")
    print(readings_pre_processes)
    readings_pre_processes.to_sql(name='readings_pre_processed',con=engine, index=False, if_exists='append')
    print('Pre-processed data successfully added to database')

# function to calculate mean of reading entries which are collected at the same site within an hour duration
def preProcess(readings_raw):
    # how to access the global dataframe
    global readings_pre_processes
    global readings_seasonValue
    global readings_gps
    global dbcursor
    # the index that hold the new distant reading value
    current_index = 0

    # temporary dataframe to hold the readings and timestamp in loop
    readings_pre_processes_temp = pd.DataFrame()
    readings_seasonValue_temp = pd.DataFrame(columns=['season_value'])
    readings_raw_df = prepareDataFrame(readings_raw)

    # iterate through distant reading values to average them with following values(in less than 60min range)
    while(current_index < len(readings_raw_df)):
        temp_index = current_index + 1
        seasonValue = [{'season_value': getSeasonValue(readings_raw_df[0][current_index])}]

        # add the first distant reading and reading season value to the temporary dataframes
        readings_pre_processes_temp = readings_pre_processes_temp.append(readings_raw_df.loc[[current_index]], ignore_index=True)
        readings_seasonValue_temp = readings_seasonValue_temp.append(seasonValue, ignore_index=True)
        readings_gps = readings_gps.append(readings_pre_processes_temp[[6, 7]], ignore_index=True)
        # print(readings_gps)

        # iterate through the entire data to check the time difference and add entires to temporary dataframe
        while(temp_index < len(readings_raw_df)):
            # var to hold time of the first distant reading value
            index_time = readings_raw_df[0][current_index]
            # print(index_time)
            # geatSeasonValue(index_time)

            # var to hold time of the current entry being checked
            reading_time = readings_raw_df[0][temp_index]
            seasonValue = [{'season_value': getSeasonValue(readings_raw_df[0][temp_index])}]

            if checkReadingSite(readings_raw_df[1][current_index], readings_raw_df[1][temp_index]):
                device_id = readings_raw_df[1][current_index]
                # find the difference between current entry and current distant reading entry
                time_difference = (reading_time - index_time).total_seconds() / 60
                
                # if the time difference is 0, then it is checking the current reading entry iteself so jump this entry
                if(time_difference == 0):
                    continue
                # if the time difference is less than 60 mins, then add it to the temporary dataframe
                if(time_difference < 60):
                    readings_pre_processes_temp = readings_pre_processes_temp.append(readings_raw_df.loc[[temp_index]], ignore_index=True)
                    readings_seasonValue_temp = readings_seasonValue_temp.append(seasonValue, ignore_index=True)
                # else move out of for loop ???
                else:
                    break
            else:
                break
            # update index to the current entry being checked to make sure to end for loop with index of next distant reading entry
            temp_index = temp_index + 1
            
        # calculate mean of the reading values collected within the same hour
        mean = readings_pre_processes_temp.mean(axis=0)
        meanSeasonValue = readings_seasonValue_temp.mean(axis=0)

        # add averaged row to the global preprocessed readings dataframe
        data = [{'temperature': mean[2], 'pressure': mean[3], 'humidity': mean[4], 'soil_moisture': mean[5]}]
        readings_pre_processes = readings_pre_processes.append(data, ignore_index=True)
        readings_seasonValue = readings_seasonValue.append([meanSeasonValue], ignore_index=True)
        
        # clear temporary readings and season value dataframe
        readings_pre_processes_temp = readings_pre_processes_temp.iloc[0:0]
        readings_seasonValue_temp = readings_seasonValue_temp.iloc[0:0]

        # change current index index to index of the next distant value
        current_index = temp_index

    # clear the already pre processed data from the database
    sql_query = sqlalchemy.text('DELETE FROM readings_for_pre_process')
    connection.execute(sql_query)
    print("Pre-processed entries removed from raw database")

def run():
    print('Starting data pre-processing...')
    # connect to mysql database

    readings_raw = pd.read_sql_table("readings_for_pre_process", engine)
    # Uncomment following lines to only preprocess 80% of data
    # sizeOfDataSet = len(readings_raw)
    # find 80% of the dataset
    # eightyPercentOfDataset = math.ceil(0.8 * sizeOfDataSet)
    # print(eightyPercentOfDataset)

    # readings_raw = readings_raw.iloc[:eightyPercentOfDataset]
    # print(readings_raw)

    # check if database has new entires for preprocessing, if so preprocess
    if(not readings_raw.empty):
        preProcess(readings_raw)
        preProcessedDataToDB()
        print('Data pre-processed successfully completed')
    else:
        print('Raw database is empty')

# run()