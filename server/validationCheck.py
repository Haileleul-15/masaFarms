import pandas as pd
import numpy as np

def percentageDifference(originalValue, predictedValue):
    percentageDifference = pd.DataFrame()
    difference = originalValue.sub(predictedValue)

    percentageDifference = difference.div(originalValue)
    percentageDifference = percentageDifference.mul(100)

    print(percentageDifference)