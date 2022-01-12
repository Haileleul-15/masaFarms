import requests
import json
import pandas as pd
import numpy as np
import datetime
import sqlalchemy
import pymysql

def run():
    weather_forecast_dataframe = pd.DataFrame()
    engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost:3306/masadb')

    gps = pd.read_sql_table("sites", engine)
    gps.head()
    gps = gps[['latitude', 'longitude']]
    gps = np.array(gps)
    # print(df.shape)
    # df = df[0][0]

    for i in range(0, gps.shape[0]):
        print(gps[i][0])
        print(gps[i][1])
        payload = {'lat': gps[i][0], 'lon': gps[i][1]}
        response = requests.get('http://api.openweathermap.org/data/2.5/forecast?appid=03efc2df61c98e93c47db949e9671ea4&units=metric', params=payload)
        
        data = response.json()
        
        dataframe = pd.DataFrame(data['list'])
        mainframe = pd.DataFrame(dataframe['main'])
        timeframe = pd.DataFrame(dataframe['dt_txt'])
        timeframe = pd.DataFrame(dataframe['dt_txt'])
        data = mainframe["main"]

        datalist = data.values.tolist()
        df = pd.DataFrame(datalist)
        # df = pd.concat([timeframe, df], axis = 1)
        df = pd.concat([timeframe, pd.Series(gps[i][0], index = df.index, name = 'latitude'), pd.Series(gps[i][1], index = df.index, name = 'longitude'), df], axis = 1)
        # print(df)
        weather_forecast_dataframe = weather_forecast_dataframe.append(df)
        # print(weather_forecast_dataframe)

    weather_forecast_dataframe.to_sql(name='weather_forecast',con=engine, index=False, if_exists='replace')
    print('Weather Collected Successfully')