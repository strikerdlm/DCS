# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 09:38:00 2023

@author: DiegoMalpica
"""

import pandas as pd
import numpy as np
from openpyxl import load_workbook
from sklearn.model_selection import train_test_split, cross_val_score, KFold, GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from joblib import dump
import os
from datetime import datetime

# Load the dataset from the Excel file
file_path = r"C:\Users\neodl\OneDrive\FAC\Research\Python Scripts\DCS\DCS_Risk_DB_2025.xlsx"
sheet_name = "data"
df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")

# Check for missing values and handle them accordingly
df.dropna(inplace=True)

# One-hot encode the 'exercise_level' column
onehot_encoder = OneHotEncoder(sparse_output=False)
exercise_level_encoded = onehot_encoder.fit_transform(df[['exercise_level']])
exercise_level_columns = onehot_encoder.get_feature_names_out(['exercise_level'])
exercise_level_df = pd.DataFrame(exercise_level_encoded, columns=exercise_level_columns, index=df.index)

# Add the encoded columns to the original dataframe and remove the original 'exercise_level' column
df = pd.concat([df.drop('exercise_level', axis=1), exercise_level_df], axis=1)

# Split the data into input features (X) and target variable (y)
X = df.drop("risk_of_decompression_sickness", axis=1)
y = df["risk_of_decompression_sickness"]

# First split the data, then scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_scaled = scaler.transform(X)

# Perform Grid Search for best parameters
param_grid = {
    'n_estimators': [100, 200],
    'learning_rate': [0.01, 0.05, 0.1],
    'max_depth': [3, 4, 5],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 3],
    'subsample': [0.8, 0.9, 1.0],
    'max_features': ['sqrt', 'log2']
}

base_model = GradientBoostingRegressor(random_state=42)
grid_search = GridSearchCV(
    estimator=base_model,
    param_grid=param_grid,
    cv=5,
    n_jobs=-1,
    scoring='r2',
    verbose=1
)

# Fit grid search
print("Performing Grid Search...")
grid_search.fit(X_train_scaled, y_train)

# Print best parameters
print("\nBest parameters found:")
print(grid_search.best_params_)
print(f"\nBest cross-validation score: {grid_search.best_score_:.4f}")

# Use best parameters for ensemble
best_params = grid_search.best_params_
n_models = 100
models = []

# Perform k-fold cross-validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)

print("\nTraining Ensemble Models...")
for i in range(n_models):
    model = GradientBoostingRegressor(**best_params, random_state=i)
    model.fit(X_train_scaled, y_train)
    models.append(model)
    
    # Perform cross-validation for first model
    if i == 0:
        cv_scores = cross_val_score(model, X_scaled, y, cv=kf, scoring='r2')
        print(f"\nCross-validation R² scores: {cv_scores}")
        print(f"Mean CV R² score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

# Make predictions using scaled data
print("\nMaking predictions...")
y_preds = np.zeros((len(X_test), n_models))
y_preds_all = np.zeros((len(X), n_models))

for i, model in enumerate(models):
    y_preds[:, i] = model.predict(X_test_scaled)
    y_preds_all[:, i] = model.predict(X_scaled)

y_pred_ensemble = y_preds.mean(axis=1)
y_pred_ensemble = y_pred_ensemble.clip(min=0, max=100)

# Calculate and print detailed metrics
mse = mean_squared_error(y_test, y_pred_ensemble)
r2 = r2_score(y_test, y_pred_ensemble)
mae = mean_absolute_error(y_test, y_pred_ensemble)
rmse = np.sqrt(mse)

print("\nModel Performance Metrics:")
print("-" * 30)
print(f"R-squared (Ensemble): {r2:.4f}")
print(f"Mean Squared Error: {mse:.4f}")
print(f"Root Mean Squared Error: {rmse:.4f}")
print(f"Mean Absolute Error: {mae:.4f}")

# Calculate and print feature importance
feature_importance = np.zeros(len(X.columns))
for model in models:
    feature_importance += model.feature_importances_

feature_importance /= len(models)

# Create feature importance DataFrame
importance_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': feature_importance
})
importance_df = importance_df.sort_values('Importance', ascending=False)

print("\nFeature Importances:")
print("-" * 30)
for idx, row in importance_df.iterrows():
    print(f"{row['Feature']}: {row['Importance']:.4f}")

# Add prediction intervals
y_pred_std = y_preds_all.std(axis=1)
prediction_interval_95 = 1.96 * y_pred_std
y_pred_mean = y_preds_all.mean(axis=1)
lower_bound = (y_pred_mean - prediction_interval_95).clip(min=0)
upper_bound = (y_pred_mean + prediction_interval_95).clip(max=100)

# Create results DataFrame
results_df = df.copy()
results_df["calculated_risk"] = y_pred_mean.clip(min=0, max=100)
results_df["confidence_interval_lower"] = lower_bound
results_df["confidence_interval_upper"] = upper_bound
results_df["prediction_uncertainty"] = y_pred_std

# Create output directory if it doesn't exist
output_dir = r"C:\Users\neodl\OneDrive\FAC\Research\Python Scripts\DCS"
os.makedirs(output_dir, exist_ok=True)

# Add timestamp to file names
timestamp = datetime.now().strftime("%Y%m%d_%H%M")

# Save the DataFrame to a new Excel file with timestamp
output_file_path = os.path.join(output_dir, f"DCS_predictions_{timestamp}.xlsx")
results_df.to_excel(output_file_path, sheet_name=sheet_name, engine="openpyxl", index=False)

# Save the best model, scaler, OneHotEncoder, and column names with timestamp
dump(models[0], os.path.join(output_dir, f"trained_model_{timestamp}.joblib"))
dump(scaler, os.path.join(output_dir, f"scaler_{timestamp}.joblib"))
dump(onehot_encoder, os.path.join(output_dir, f"onehot_encoder_{timestamp}.joblib"))
dump(X.columns, os.path.join(output_dir, f"column_names_{timestamp}.joblib"))

print(f"\nResults saved to {output_file_path}")