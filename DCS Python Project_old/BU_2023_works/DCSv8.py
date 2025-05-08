# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 21:54:17 2023

@author: User
"""

import pandas as pd
from openpyxl import load_workbook
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder

# Load the dataset from the Excel file
file_path = r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\data.xlsx"
sheet_name = "data"
df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")

# Check for missing values and handle them accordingly
df.dropna(inplace=True)

# Convert altitude to feet
df["altitude"] = df["altitude"] * 3.28084

# One-hot encode the 'exercise_level' column
onehot_encoder = OneHotEncoder(sparse=False)
exercise_level_encoded = onehot_encoder.fit_transform(df[['exercise_level']])
exercise_level_columns = onehot_encoder.get_feature_names_out(['exercise_level'])
exercise_level_df = pd.DataFrame(exercise_level_encoded, columns=exercise_level_columns, index=df.index)

# Add the encoded columns to the original dataframe and remove the original 'exercise_level' column
df = pd.concat([df.drop('exercise_level', axis=1), exercise_level_df], axis=1)

# Split the data into input features (X) and target variable (y)
X = df.drop("risk_of_decompression_sickness", axis=1)
y = df["risk_of_decompression_sickness"]

# Scale the target variable to a range of 0 to 1
y = y / 100

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions on the test set (probabilities)
y_pred = model.predict(X_test)

# Clip the predictions to a range between 0 and 1
y_pred = y_pred.clip(0, 1)

# Calculate the mean squared error
mse = mean_squared_error(y_test, y_pred)

print("Mean Squared Error:", mse)
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

# Append the calculated risk to the DataFrame and save it to the Excel file
y_pred_all = model.predict(df.drop("risk_of_decompression_sickness", axis=1)).clip(0, 1) * 100
df["calculated"] = y_pred_all
df.to_excel(file_path, sheet_name=sheet_name, engine="openpyxl", index=False)
