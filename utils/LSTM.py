import os

import numpy as np
from numpy import asarray
from tensorflow import keras

os.chdir("D:\\Programing\\python\\2022121402UK_Restaurants")
model = keras.models.load_model('static\\my_model.h5')


def oneday_predict(data):
    maxdata = max(data)
    npdata = asarray(data)
    npdata = npdata / maxdata

    return model.predict(npdata.reshape((1, 30, 1))) * maxdata

def fivedays_predict(data):
    predicted = []
    for i in range(5):
        predicted.append(round(float(oneday_predict(data[-30:]).reshape(1))))
        data.append(predicted[-1])

    return predicted

