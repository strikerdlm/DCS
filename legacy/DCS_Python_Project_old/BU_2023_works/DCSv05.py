# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 12:03:02 2023

@author: User
"""

import pandas as pd
from openpyxl import load_workbook
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder
import joblib

# Load the dataset from the Excel file
file_path = r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\data.xlsx"
sheet_name = "data"
df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")

# Check for missing values and handle them accordingly
df.dropna(inplace=True)

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

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#Train a linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

#Make predictions on the test set
y_pred = model.predict(X_test)

#Ensure that the predicted values are within the range of 0 to 100
y_pred_clipped = y_pred.clip(0, 100)

#Calculate the mean squared error
mse = mean_squared_error(y_test, y_pred_clipped)
print("Mean Squared Error:", mse)

#Print the coefficients and intercept
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)

#Append the calculated risk to the original DataFrame
df_all = pd.concat([X, y], axis=1)
df_all['calculated'] = model.predict(X)
df_all['calculated'] = df_all['calculated'].clip(0, 100)

#Save the updated DataFrame to the Excel file
with pd.ExcelWriter(file_path, engine="openpyxl", mode='a') as writer:
    df_all.to_excel(writer, sheet_name='Sheet4', index=False)
    
# Save the trained model as a pickle file
model_path = r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\model.pkl"
joblib.dump(model, model_path)

# Save the one-hot encoder as a pickle file
encoder_path = r"C:\Users\User\OneDrive\FAC\Research\DCS FAC\encoder.pkl"
joblib.dump(onehot_encoder, encoder_path)