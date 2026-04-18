# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 14:38:02 2023

@author: User
"""

import numpy as np
from sklearn.preprocessing import OneHotEncoder

# Provided parameters
mse = 0.01677497115439567
coefficients = np.array([3.59860256e-05, -1.59568206e-03, 2.23643207e-03, 1.03538731e-01, 2.09400437e-02, -1.24478775e-01])
intercept = -0.8893607739537449

# One-hot encoder for the 'exercise_level' column
onehot_encoder = OneHotEncoder(sparse=False, categories=[['Rest', 'Mild', 'Heavy']])

def predict_decompression_sickness(altitude, prebreathing_time, time_at_altitude, exercise_level):
    # Apply one-hot encoding to the 'exercise_level' column
    exercise_level_encoded = onehot_encoder.fit_transform([[exercise_level]])
    
    # Combine input variables into an array
    input_variables = np.array([altitude, prebreathing_time, time_at_altitude])
    input_variables = np.concatenate((input_variables, exercise_level_encoded.ravel()))

    # Compute the probability of decompression sickness using the linear regression model
    probability = np.dot(coefficients, input_variables) + intercept

    # Clip the probability to a range of 0 to 1
    probability = np.clip(probability, 0, 1)

    return probability

# Prompt the user to input variable data
altitude_feet = float(input("Enter the altitude (in feet): "))
altitude_meters = altitude_feet * 0.3048  # Convert feet to meters
prebreathing_time = float(input("Enter the prebreathing time (in minutes): "))
time_at_altitude = float(input("Enter the time at altitude (in minutes): "))
exercise_level = input("Enter the exercise level (Rest, Mild, Heavy): ")

# Estimate the probability of decompression sickness
probability = predict_decompression_sickness(altitude_meters, prebreathing_time, time_at_altitude, exercise_level)

print("The estimated probability of decompression sickness is {:.2f}%".format(probability * 100))
