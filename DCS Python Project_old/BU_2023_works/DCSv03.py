# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 11:09:59 2023

@author: User
"""

import pandas as pd
from openpyxl import load_workbook
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error

# Load the dataset from the Excel file
file_path = r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\data.xlsx"
sheet_name = "data"
df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")

# Check for missing values and handle them accordingly
df.dropna(inplace=True)

# Map exercise_level categories to numerical values
exercise_level_mapping = {'Rest': 1, 'Mild': 2, 'Heavy': 3}
df['exercise_level'] = df['exercise_level'].map(exercise_level_mapping)

# Split the data into input features (X) and target variable (y)
X = df[["altitude", "prebreathing_time", "time_at_altitude", "exercise_level"]]
y = df["risk_of_decompression_sickness"]

# Scale the target variable to a range of 0 to 1
y = y / 100

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a pipeline with PolynomialFeatures, StandardScaler, and LinearRegression
model = make_pipeline(
    PolynomialFeatures(degree=2, interaction_only=True, include_bias=False),
    StandardScaler(),
    LinearRegression()
)

# Train the model
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Calculate the mean squared error
mse = mean_squared_error(y_test, y_pred)

print("Mean Squared Error:", mse)

# Append the calculated risk to the original DataFrame
df['calculated'] = model.predict(X) * 100

# Save the updated DataFrame to the Excel file
df.to_excel(file_path, sheet_name=sheet_name, engine="openpyxl", index=False)

# You can also print feature importances to understand the contribution of each feature to the model
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)