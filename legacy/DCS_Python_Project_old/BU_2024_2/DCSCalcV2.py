# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 12:33:30 2023

@author: User
"""

import joblib
import numpy as np
import pandas as pd

# Load the saved trained model
model_path = r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\model.pkl"
model = joblib.load(model_path)

# Load the saved one-hot encoder
encoder_path = r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\encoder.pkl"
onehot_encoder = joblib.load(encoder_path)

# Get input values from the user
altitude_ft = float(input("Enter altitude in feet: "))
time_at_altitude_min = float(input("Enter time at altitude in minutes: "))
prebreathing_time = float(input("Enter prebreathing time: "))
exercise_level = input("Enter exercise level (Rest/Mild/Heavy): ")

# Encode the exercise level
exercise_level_encoded = onehot_encoder.transform([[exercise_level]])
exercise_level_columns = onehot_encoder.get_feature_names_out(['exercise_level'])
exercise_level_df = pd.DataFrame(exercise_level_encoded, columns=exercise_level_columns)

# Create a numpy array with the input values and the encoded exercise level
input_values = np.array([[altitude_ft, time_at_altitude_min, prebreathing_time]])
input_values = np.concatenate((input_values, exercise_level_df.values), axis=1)

# Predict the risk of decompression sickness using the trained model
risk = model.predict(input_values)[0]

# Ensure that the predicted value is within the range of 0 to 100
risk_clipped = np.clip(risk, 0, 100)

# Normalize the predicted risk to a value between 0 and 1
risk_normalized = risk_clipped / 100.0

# Print the predicted risk
print("Predicted risk of decompression sickness:", risk_normalized)