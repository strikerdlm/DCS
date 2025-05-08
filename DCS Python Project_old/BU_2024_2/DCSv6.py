# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 20:59:15 2023

@author: neodl
"""


import pandas as pd
from openpyxl import load_workbook
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
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

# Scale the target variable to a range of 0 to 1
y = y / 100

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Gradient Boosting Regressor and optimize its hyperparameters using GridSearchCV
params = {
    'n_estimators': [100, 200],
    'learning_rate': [0.01, 0.1],
    'max_depth': [3, 4, 5]
}
model = GradientBoostingRegressor(random_state=42)
grid_search = GridSearchCV(model, params, scoring='neg_mean_squared_error', cv=5)
grid_search.fit(X_train, y_train)

# Select the best estimator found by GridSearchCV
best_model = grid_search.best_estimator_

# Make predictions on the test set (probabilities)
y_pred = best_model.predict(X_test)

# Calculate the mean squared error
mse = mean_squared_error(y_test, y_pred)

print("Best Model Parameters:", grid_search.best_params_)
print("Mean Squared Error:", mse)

# Save the model and the one-hot encoder to files
joblib.dump(best_model, 'gradient_boosting_regressor_model.pkl')
joblib.dump(onehot_encoder, 'onehot_encoder.pkl')
