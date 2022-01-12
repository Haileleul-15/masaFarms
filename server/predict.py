import pandas as pd
import numpy as np
import sqlalchemy
import pymysql
# import mlserver
import prepare_data
import randomforest

engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost:3306/masadb')

def loadForcastData():
    df = pd.read_sql_table("weather_forecast", engine)
    df.head()

    seasonValue = df['dt_txt'].apply(prepare_data.getSeasonValue)

    X = df[['latitude', 'longitude', 'temp', 'grnd_level', 'humidity']]
    Y = df[['dt_txt', 'latitude', 'longitude', 'temp', 'grnd_level', 'humidity']]
    X = pd.concat([seasonValue, X], axis=1)
    # X = pd.concat([pd.Series(1, index = X.index, name = '00'), X], axis = 1)
    # print(X)
    X.columns = range(X.shape[1])
    # Change object data type to float
    X = X.astype(str).astype(float)

    # print(X)
    # Normalization of each column
    # for i in range(1, len(X.columns)+1):
    #     X[i-1] = (X[i-1])/np.max(X[i-1])
    # X.head()
    return X, Y

def predict():
    X, Y = loadForcastData()
    # theta = np.loadtxt("theta.txt", dtype=int)
    # prediction = mlserver.hypothesis(theta, X)
    # prediction = np.sum(prediction, axis=1)
    
    # Predict using random forest algorithm
    predictions = randomforest.predict(X)
    df = pd.DataFrame(data = predictions)
    # print(df)
    forecast = pd.concat([Y, df], axis=1)
    forecast = forecast.rename(columns={0: 'soil_moisture'})
    forecast["dt_txt"] =  pd.to_datetime(forecast.dt_txt)
    forecast["longitude"] =  pd.to_numeric(forecast.longitude)
    forecast["latitude"] =  pd.to_numeric(forecast.latitude)
    print(forecast)
    forecast.to_sql(name='soil_moisture_forecast',con=engine, index=False, if_exists='replace')

    return predictions

# predict()
