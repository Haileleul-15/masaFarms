import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import mysql.connector as mysql
import pre_process_readings
import prepare_data_for_validation
import validationCheck

# MySQL DB variables
DB_HOST = "localhost"
DB_NAME = "masadb"
DB_USER = "root"
DB_PASS = "admin"

pre_process_readings.run()

masadb = mysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME
)

dbcursor = masadb.cursor()


# Hypothesis Function
def hypothesis(theta, X):
    return theta*X

# Function to compute to cost
def computeCost(X, y, theta, m):
    y1 = hypothesis(theta, X)
    y1 = np.sum(y1, axis = 1)

    return sum(np.sqrt((y1 - y)**2))/(2*m)

# Gradient Descent Function
def gradientDescent(X, y, theta, alpha, i, m):
    J = []  #cost function in each iterations
    k = 0
    while k < i:
        y1 = hypothesis(theta, X)
        y1 = np.sum(y1, axis=1)
        for c in range(0, len(X.columns)):
            theta[c] = theta[c] - alpha*(sum((y1-y)*X.iloc[:,c])/m)
        j = computeCost(X, y, theta, m)
        J.append(j)
        k += 1
    print('Gradiet descent completed')
    writeToFile(str(theta).replace("[", "").replace("]", ""))
    return J, j, theta

def prepareInputsForRegression(table_rows):
    df = pd.DataFrame(table_rows)
    df.head()
    # print(df)

    # select entries with specific device_id values
    # df = df[df[0] == 'dragino-end-device-001']

    # Concatenate the X0 term to all entries
    df = pd.concat([pd.Series(1, index = df.index, name = '00'), df], axis = 1)
    df.head()

    # Drop database title, time and soil moisture columns from the raw data
    X = df.drop([6], axis = 1)
    # print(X)

    # Remove data type title row
    # X = X.drop([0], axis = 0)

    # Reset row and column indices to start from 0
    X = X.reset_index(drop=True)
    X.columns = range(X.shape[1])

    # Change object data type to float
    X = X.astype(str).astype(float)

    # print(X)

    # Set y to the soil moisture column of the dataframe
    y = df.iloc[:, 7]

    # Drop the title row, reset index and change object data type to float
    # y = y.drop([0], axis = 0)
    y = y.reset_index(drop=True)
    y = y.astype(str).astype(float)

    # print(y)

    # Condition data values to prepare for linear regression
    for i in range(1, len(X.columns)+1):
        X[i-1] = (X[i-1])/np.max(X[i-1])
    X.head()

    # print(X)


    # Length of the data
    m = len(X)

    return X, y, m

def writeToFile(theta):
    f = open("theta.txt", "w")
    f.write(theta)
    f.close()


def run():
    global masadb, dbcursor

    # take input
    # device_selection = input("Enter your value: ")
    # print(device_selection)

    dbcursor.execute('SELECT * FROM readings_prepared')
    table_rows = dbcursor.fetchall()

    forValidation = prepare_data_for_validation.prepareDataForValidation()

    X, y, m = prepareInputsForRegression(table_rows)
    X20, y20,m20 = prepareInputsForRegression(forValidation)
    
    # Initialize a zero vector for theta
    theta = np.array([0]*len(X.columns))

    print('Pre-processed data successfully loaded onto X and y matrices...')

    print('Starting gradient descent...')
    J, j, theta = gradientDescent(X, y, theta, 0.3, 10000, m)
    print('Theta calculated by gradiet descent')
    print(theta)

    # Testing with existing data
    print('Predicted soil moisture values using 20 percent of the collected data')
    y_hat = hypothesis(theta, X20)
    y_hat = np.sum(y_hat, axis=1)
    print(y_hat)

    # Plot cost
    # plt.figure()
    # plt.scatter(x=list(range(0, 10000)), y=J)
    # plt.show()

    print('Difference between predicted and actual soil moisture reading values')
    # validationCheck.percentageDifference(y20, y_hat)
    print(y20 - y_hat)

    plt.figure()
    plt.scatter(x=list(range(0, len(y20))),y= y20, color='blue')         
    plt.scatter(x=list(range(0, len(y_hat))), y=y_hat, color='black')
    plt.show()


    masadb.commit()
    dbcursor.close()
    masadb.close()

run()