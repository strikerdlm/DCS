# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 11:57:39 2023

@author: User
"""

import pandas as pd
from openpyxl import load_workbook
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Load the dataset from the Excel file
file_path = r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\data.xlsx"
sheet_name = "data"
df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")

# Check for missing values and handle them accordingly
df.dropna(inplace=True)

# One-hot encode the 'exercise_level' column
exercise_level_dummies = pd.get_dummies(df['exercise_level'], prefix='exercise_level')
df = pd.concat([df.drop('exercise_level', axis=1), exercise_level_dummies], axis=1)

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

# Calculate the mean squared error
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)

# Print the coefficients and intercept
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

# Calculate the risk for the entire dataset and append it to the original DataFrame
y_all_pred = model.predict(X) * 100
df['calculated'] = y_all_pred

# Save the updated DataFrame with the calculated risk to a new Excel file
output_file_path = r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\updated_data_set.xlsx"
df.to_excel(output_file_path, index=False, engine="openpyxl")