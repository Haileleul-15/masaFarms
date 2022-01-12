import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import sqlalchemy


def testAlgorithm():
    # MySQL DB variables
    engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost:3306/masadb')
    connection = engine.connect()

    features = pd.read_sql_table("readings_prepared", engine)
    features.head()

    # print(features)

    # Labels are the values we want to predict
    labels = np.array(features["soil_moisture"])

    # Remove the labels from the features
    # axis 1 refers to the columns
    features= features.drop("soil_moisture", axis = 1)

    # Convert the features to numpy array
    features = np.array(features)

    # print(labels)

    # Split the data into training and testing sets
    train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.25, random_state = 42)

    # print('Training Features Shape:', train_features.shape)
    # print('Training Labels Shape:', train_labels.shape)
    # print('Testing Features Shape:', test_features.shape)
    # print('Testing Labels Shape:', test_labels.shape)

    # Instantiate model with 1000 decision trees
    rf = RandomForestRegressor(n_estimators = 1000, random_state = 42)
    # Train the model on training data
    rf.fit(train_features, train_labels);

    # Use the forest's predict method on the test data
    predictions = rf.predict(test_features)
    # Calculate the absolute errors
    errors = abs(predictions - test_labels)
    # Print out the mean absolute error (mae)
    # print("The actual values: ")
    # print(test_labels)
    # print("The predicted values: ")
    # print(predictions)
    print('Mean Absolute Error:', round(np.mean(errors), 2), 'degrees.')

    # Calculate mean absolute percentage error (MAPE)
    mape = 100 * (errors / test_labels)
    # Calculate and display accuracy
    accuracy = 100 - np.mean(mape)
    print('Accuracy:', round(accuracy, 2), '%.')
    
    # Prepare prediction and actual values as pandas dataframes and rename the columns
    predictionsDF = pd.DataFrame(predictions)
    predictionsDF = predictionsDF.rename(columns={0: 'prediction'})
    actualValDF = pd.DataFrame(test_labels)
    actualValDF = actualValDF.rename(columns={0: 'actual'})

    # Concatenate prediction and actual values and upload to database
    random_forest_test_comparison = pd.concat([predictionsDF, actualValDF], axis=1)
    print(random_forest_test_comparison)
    random_forest_test_comparison.to_sql(name='random_forest_test_comparison',con=engine, index=False, if_exists='replace')

    # plt.figure()
    # plt.scatter(x=list(range(0, len(test_labels))),y= test_labels, color='blue')         
    # plt.scatter(x=list(range(0, len(predictions))), y=predictions, color='black')
    # plt.show()


def predict(forecast_features):
    # MySQL DB variables
    engine = sqlalchemy.create_engine('mysql+pymysql://root:admin@localhost:3306/masadb')
    connection = engine.connect()

    features = pd.read_sql_table("readings_prepared", engine)
    features.head()

    # print(features)

    # Labels are the values we want to predict
    labels = np.array(features["soil_moisture"])

    # Remove the labels from the features
    # axis 1 refers to the columns
    features= features.drop("soil_moisture", axis = 1)

    # Convert the features to numpy array
    features = np.array(features)

    # print(labels)
    
    # Instantiate model with 1000 decision trees
    rf = RandomForestRegressor(n_estimators = 1000, random_state = 42)
    # Train the model on training data
    rf.fit(features, labels);

    # Use the forest's predict method on the test data
    forecast_features = np.array(forecast_features)
    predictions = rf.predict(forecast_features)
    
    return predictions

testAlgorithm()