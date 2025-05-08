# -*- coding: utf-8 -*-
"""
Created on Jan 28 - 2025
v0.0.10
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
from scipy import stats

def engineer_features(df):
    """
    Preprocess and engineer features from the input dataframe
    """
    # Check for missing values and handle them accordingly
    df.dropna(inplace=True)
    
    # One-hot encode the 'exercise_level' column
    onehot_encoder = OneHotEncoder(sparse_output=False)
    exercise_level_encoded = onehot_encoder.fit_transform(df[['exercise_level']])
    exercise_level_columns = onehot_encoder.get_feature_names_out(['exercise_level'])
    exercise_level_df = pd.DataFrame(exercise_level_encoded, columns=exercise_level_columns, index=df.index)
    
    # Add the encoded columns to the original dataframe and remove the original 'exercise_level' column
    df = pd.concat([df.drop('exercise_level', axis=1), exercise_level_df], axis=1)
    return df, onehot_encoder

def train_ensemble_models(X_train_scaled, y_train, best_params, n_models=100):
    """
    Train ensemble of gradient boosting models
    """
    models = []
    print("\nTraining Ensemble Models...")
    for i in range(n_models):
        model = GradientBoostingRegressor(**best_params, random_state=i)
        model.fit(X_train_scaled, y_train)
        models.append(model)
    return models

def make_predictions(models, X_scaled):
    """
    Make predictions using the ensemble of models
    """
    n_models = len(models)
    y_preds = np.zeros((len(X_scaled), n_models))
    
    for i, model in enumerate(models):
        y_preds[:, i] = model.predict(X_scaled)
    
    y_pred_mean = y_preds.mean(axis=1)
    y_pred_std = y_preds.std(axis=1)
    return y_pred_mean.clip(min=0, max=100), y_pred_std, y_preds

def calculate_metrics(y_true, y_pred):
    """
    Calculate and return model performance metrics
    """
    mse = mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    return mse, r2, mae, rmse

def print_metrics(mse, r2, mae, rmse):
    """
    Print model performance metrics
    """
    print("\nModel Performance Metrics:")
    print("-" * 30)
    print(f"R-squared (Ensemble): {r2:.4f}")
    print(f"Mean Squared Error: {mse:.4f}")
    print(f"Root Mean Squared Error: {rmse:.4f}")
    print(f"Mean Absolute Error: {mae:.4f}")

def calculate_feature_importance(models, feature_names):
    """
    Calculate and return feature importance from ensemble
    """
    feature_importance = np.zeros(len(feature_names))
    for model in models:
        feature_importance += model.feature_importances_
    
    feature_importance /= len(models)
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': feature_importance
    })
    return importance_df.sort_values('Importance', ascending=False)

def save_results(results_df, models, scaler, onehot_encoder, X_columns, output_dir, timestamp):
    """
    Save all model artifacts and results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results DataFrame
    output_file_path = os.path.join(output_dir, f"DCS_predictions_{timestamp}.xlsx")
    results_df.to_excel(output_file_path, sheet_name="data", engine="openpyxl", index=False)
    
    # Save model artifacts
    dump(models[0], os.path.join(output_dir, f"trained_model_{timestamp}.joblib"))
    dump(scaler, os.path.join(output_dir, f"scaler_{timestamp}.joblib"))
    dump(onehot_encoder, os.path.join(output_dir, f"onehot_encoder_{timestamp}.joblib"))
    dump(X_columns, os.path.join(output_dir, f"column_names_{timestamp}.joblib"))
    
    print(f"\nResults saved to {output_file_path}")

def main():
    # Load the dataset from the Excel file
    file_path = r"C:\Users\neodl\OneDrive\FAC\Research\Python Scripts\DCS\DCS_Risk_DB_2025.xlsx"
    df = pd.read_excel(file_path, sheet_name="data", engine="openpyxl")
    
    # Preprocess data
    df, onehot_encoder = engineer_features(df)
    
    # Split the data into input features (X) and target variable (y)
    X = df.drop("risk_of_decompression_sickness", axis=1)
    y = df["risk_of_decompression_sickness"]
    
    # Split and scale data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_scaled = scaler.transform(X)
    
    # Perform Grid Search
    param_grid = {
        'n_estimators': [100, 200],
        'learning_rate': [0.01, 0.1],
        'max_depth': [3, 4, 5],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2],
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
    
    print("Performing Grid Search...")
    grid_search.fit(X_train_scaled, y_train)
    print("\nBest parameters found:")
    print(grid_search.best_params_)
    print(f"\nBest cross-validation score: {grid_search.best_score_:.4f}")
    
    # Train ensemble models
    models = train_ensemble_models(X_train_scaled, y_train, grid_search.best_params_)
    
    # Make predictions
    y_pred_mean, y_pred_std, y_preds_all = make_predictions(models, X_scaled)
    y_pred_test_mean, _, y_preds_test = make_predictions(models, X_test_scaled)
    
    # Calculate metrics
    mse, r2, mae, rmse = calculate_metrics(y_test, y_pred_test_mean)
    print_metrics(mse, r2, mae, rmse)
    
    # Calculate feature importance
    importance_df = calculate_feature_importance(models, X.columns)
    print("\nFeature Importances:")
    print("-" * 30)
    for idx, row in importance_df.iterrows():
        print(f"{row['Feature']}: {row['Importance']:.4f}")
    
    # Calculate prediction intervals
    prediction_interval_95 = 1.96 * y_pred_std
    lower_bound = (y_pred_mean - prediction_interval_95).clip(min=0)
    upper_bound = (y_pred_mean + prediction_interval_95).clip(max=100)
    
    # Create results DataFrame
    results_df = df.copy()
    results_df["calculated_risk"] = y_pred_mean
    results_df["confidence_interval_lower"] = lower_bound
    results_df["confidence_interval_upper"] = upper_bound
    results_df["prediction_uncertainty"] = y_pred_std
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = r"C:\Users\neodl\OneDrive\FAC\Research\Python Scripts\DCS"
    save_results(results_df, models, scaler, onehot_encoder, X.columns, output_dir, timestamp)

if __name__ == "__main__":
    main()