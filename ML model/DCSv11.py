# -*- coding: utf-8 -*-
"""
Created on Jan 28 - 2025
v0.0.11
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
from tqdm import tqdm
from sklearn.inspection import PartialDependenceDisplay

def engineer_features(df):
    """
    Preprocess and engineer features from the input dataframe
    """
    # Check for missing values and handle them accordingly
    df.dropna(inplace=True)
    
    # Add physical constraints
    df['prebreathing_time'] = np.clip(df['prebreathing_time'], 0, 120)  # Max 2 hours
    df['time_at_altitude'] = np.clip(df['time_at_altitude'], 0, 480)  # Max 8 hours
    df['altitude'] = np.clip(df['altitude'], 5000, 45000)  # 5k-45k feet
    
    # Ensure correct ordering of exercise levels
    df['exercise_level'] = pd.Categorical(
        df['exercise_level'], 
        categories=['Rest', 'Mild', 'Heavy'],  # Explicit order for ordinal relationship
        ordered=True
    )
    
    # One-hot encode the 'exercise_level' column with specified order
    onehot_encoder = OneHotEncoder(categories=[['Rest', 'Mild', 'Heavy']], sparse_output=False)
    exercise_level_encoded = onehot_encoder.fit_transform(df[['exercise_level']])
    exercise_level_columns = onehot_encoder.get_feature_names_out(['exercise_level'])
    exercise_level_df = pd.DataFrame(exercise_level_encoded, columns=exercise_level_columns, index=df.index)
    
    # Add the encoded columns to the original dataframe and remove the original 'exercise_level' column
    df = pd.concat([df.drop('exercise_level', axis=1), exercise_level_df], axis=1)
    
    # Apply non-linear transformations for time-based features
    df['prebreathing_time'] = np.log1p(df['prebreathing_time'])  # Logarithmic transformation
    df['time_at_altitude'] = df['time_at_altitude'] ** 1.5  # Power transformation
    
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
        # Clip individual model predictions
        y_preds[:, i] = np.clip(model.predict(X_scaled), 0, 100)
    
    y_pred_mean = y_preds.mean(axis=1)
    y_pred_mean = np.clip(y_pred_mean, 0, 100)  # Add explicit clip for mean
    y_pred_std = y_preds.std(axis=1)
    # No need to clip mean as it's already based on clipped predictions
    return y_pred_mean, y_pred_std, y_preds

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

def calculate_feature_importance(models, feature_names, X_train, scaler, original_data):
    """
    Calculate and return feature importance from ensemble
    Parameters:
        models: List of trained models in the ensemble
        feature_names: List of feature names
        X_train: Training data used for the models
        scaler: Fitted StandardScaler object
        original_data: Original dataframe with untransformed features
    """
    feature_importance = np.zeros(len(feature_names))
    partial_dependence = {}
    
    # Calculate partial dependence for verification
    for feature in ['altitude', 'time_at_altitude', 'prebreathing_time']:
        # Sample values for partial dependence analysis
        grid = np.linspace(original_data[feature].min(), original_data[feature].max(), 50)
        pdp = np.zeros_like(grid)
        
        for i, value in enumerate(grid):
            temp_df = X_train.copy()
            temp_df[feature] = value
            temp_df_scaled = scaler.transform(temp_df)
            pdp[i] = np.mean([model.predict(temp_df_scaled).mean() for model in models])
        
        partial_dependence[feature] = (grid, pdp)

    for model in models:
        feature_importance += model.feature_importances_
    
    feature_importance /= len(models)
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': feature_importance
    }).sort_values('Importance', ascending=False)
    
    # Verify directionality of relationships
    print("\nRelationship Verification:")
    print("-" * 30)
    print(f"Altitude vs Risk: {np.polyfit(partial_dependence['altitude'][0], partial_dependence['altitude'][1], 1)[0]:.4f} (should be positive)")
    print(f"Time at Altitude vs Risk: {np.polyfit(partial_dependence['time_at_altitude'][0], partial_dependence['time_at_altitude'][1], 1)[0]:.4f} (should be positive)")
    print(f"Prebreathing Time vs Risk: {np.polyfit(partial_dependence['prebreathing_time'][0], partial_dependence['prebreathing_time'][1], 1)[0]:.4f} (should be negative)")
    
    return importance_df

def save_results(results_df, models, scaler, onehot_encoder, X_columns, output_dir, timestamp):
    """
    Save all model artifacts and results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results DataFrame
    output_file_path = os.path.join(output_dir, f"DCS_predictions_{timestamp}.xlsx")
    results_df.to_excel(output_file_path, sheet_name="data", engine="openpyxl", index=False)
    
    # Get feature names in the correct order
    numeric_features = ['altitude', 'time_at_altitude', 'prebreathing_time']
    exercise_cols = onehot_encoder.get_feature_names_out(['exercise_level'])
    feature_names = numeric_features + list(exercise_cols)
    
    # Save model parameters instead of the full model
    model_params = {
        'params': models[0].get_params(),
        'n_estimators': models[0].n_estimators_,
        'feature_importances': models[0].feature_importances_.tolist(),
        'train_score': models[0].train_score_.tolist(),
        'feature_names': feature_names
    }
    
    # Save artifacts with protocol=4 for better compatibility
    dump(model_params, os.path.join(output_dir, f"model_params_{timestamp}.joblib"), protocol=4)
    dump(scaler, os.path.join(output_dir, f"scaler_{timestamp}.joblib"), protocol=4)
    dump(onehot_encoder, os.path.join(output_dir, f"onehot_encoder_{timestamp}.joblib"), protocol=4)
    
    # Also save a simple version of the model for direct predictions
    simple_model = {
        'feature_names': feature_names,
        'scaler': scaler,
        'onehot_encoder': onehot_encoder,
        'base_model': models[0]
    }
    dump(simple_model, os.path.join(output_dir, f"simple_model_{timestamp}.joblib"), protocol=4)
    
    print(f"\nResults saved to {output_file_path}")
    print("\nFeature names in order:", feature_names)

def bootstrap_sample(X, y, n_samples=1000):
    """
    Create bootstrap samples for Monte Carlo simulation
    Returns generator of bootstrapped samples
    """
    n_instances = len(X)
    # Convert y to numpy array if it's a pandas Series
    if isinstance(y, pd.Series):
        y = y.to_numpy()
    
    for _ in range(n_samples):
        indices = np.random.choice(n_instances, size=n_instances, replace=True)
        # Use numpy indexing for both X and y
        yield X[indices], y[indices]

def monte_carlo_parameter_sampling(best_params, n_samples=100):
    """
    Sample model parameters for uncertainty estimation with safe parameter handling
    """
    param_samples = []
    
    # Ensure subsample is properly set with a default if not present
    default_subsample = 0.8
    current_subsample = best_params.get('subsample', default_subsample)
    
    # Set safe bounds for parameter sampling
    min_learning_rate = 0.001
    max_learning_rate = 0.5
    min_subsample = 0.5
    max_subsample = 1.0
    
    for _ in range(n_samples):
        sample = best_params.copy()
        
        # Learning rate: log-normal distribution
        if 'learning_rate' in best_params:
            current_lr = best_params['learning_rate']
            sample['learning_rate'] = np.clip(
                np.random.lognormal(
                    np.log(current_lr), 
                    0.1
                ), 
                min_learning_rate, 
                max_learning_rate
            )
        
        # Subsample: beta distribution with safe parameters
        alpha = 20 * current_subsample + 1  # Adding 1 ensures alpha > 0
        beta = 20 * (1 - current_subsample) + 1  # Adding 1 ensures beta > 0
        
        sample['subsample'] = np.clip(
            np.random.beta(alpha, beta),
            min_subsample,
            max_subsample
        )
        
        # Keep discrete parameters unchanged
        for param in ['n_estimators', 'max_depth', 'min_samples_split', 
                     'min_samples_leaf', 'max_features']:
            if param in best_params:
                sample[param] = best_params[param]
        
        param_samples.append(sample)
    
    return param_samples

def monte_carlo_prediction(models, X, n_samples=1000, uncertainty=0.05):
    """
    Propagate input uncertainty through the model using Monte Carlo simulation
    """
    predictions = []
    print("\nPerforming Monte Carlo predictions...")
    n_instances = len(X)
    
    # Add constrained random noise to inputs
    X_noisy = X.copy()
    for i in range(X.shape[1]):
        # Get original feature min/max from training data
        feat_min = np.min(X[:, i])
        feat_max = np.max(X[:, i])
        
        # Apply bounded noise
        noise = np.random.normal(0, uncertainty * np.std(X[:, i]), X.shape[0])
        X_noisy[:, i] = np.clip(X[:, i] + noise, feat_min, feat_max)
    
    for _ in tqdm(range(n_samples)):
        # Add random noise to inputs based on their scale
        X_noisy = X + np.random.normal(0, uncertainty * np.std(X, axis=0), X.shape)
        
        # Get predictions from all models
        model_preds = np.zeros((n_instances, len(models)))
        for i, model in enumerate(models):
            # Clip predictions between 0 and 100
            model_preds[:, i] = np.clip(model.predict(X_noisy), 0, 100)
        
        # Take mean prediction for this Monte Carlo iteration
        predictions.append(model_preds.mean(axis=1))
    
    predictions = np.array(predictions)  # Shape: (n_samples, n_instances)
    
    # Add Bayesian smoothing
    predictions = np.where(
        predictions < 0,
        predictions * 0.25,  # Dampen negative excursions
        predictions
    )
    predictions = np.where(
        predictions > 100,
        100 + (predictions - 100) * 0.25,  # Dampen positive excursions
        predictions
    )
    
    # Calculate statistics across Monte Carlo samples
    mean_pred = np.clip(np.mean(predictions, axis=0), 0, 100)  # Add clip here
    std_pred = np.std(predictions, axis=0)
    lower_ci = np.clip(np.percentile(predictions, 2.5, axis=0), 0, 100)
    upper_ci = np.clip(np.percentile(predictions, 97.5, axis=0), 0, 100)
    
    return mean_pred, std_pred, lower_ci, upper_ci

def evaluate_monte_carlo_performance(y_true, mc_predictions, mc_std):
    """
    Evaluate the performance of Monte Carlo predictions
    """
    # Ensure inputs are numpy arrays
    y_true = np.asarray(y_true)
    mc_predictions = np.asarray(mc_predictions)
    mc_std = np.asarray(mc_std)
    
    # Calculate basic metrics
    mse = mean_squared_error(y_true, mc_predictions)
    r2 = r2_score(y_true, mc_predictions)
    mae = mean_absolute_error(y_true, mc_predictions)
    rmse = np.sqrt(mse)
    
    # Calculate coverage probability of 95% confidence intervals
    ci_lower = mc_predictions - 1.96 * mc_std
    ci_upper = mc_predictions + 1.96 * mc_std
    coverage = np.mean((y_true >= ci_lower) & (y_true <= ci_upper))
    
    # Calculate mean prediction interval width
    interval_width = np.mean(ci_upper - ci_lower)
    
    return {
        'mse': mse,
        'r2': r2,
        'mae': mae,
        'rmse': rmse,
        'coverage_probability': coverage,
        'mean_interval_width': interval_width
    }

def print_monte_carlo_metrics(metrics):
    """
    Print comprehensive Monte Carlo simulation metrics
    """
    print("\nMonte Carlo Simulation Metrics:")
    print("-" * 40)
    print(f"R-squared (MC): {metrics['r2']:.4f}")
    print(f"Mean Squared Error: {metrics['mse']:.4f}")
    print(f"Root Mean Squared Error: {metrics['rmse']:.4f}")
    print(f"Mean Absolute Error: {metrics['mae']:.4f}")
    print(f"95% CI Coverage Probability: {metrics['coverage_probability']:.4f}")
    print(f"Mean Prediction Interval Width: {metrics['mean_interval_width']:.4f}")

def main():
    # Load the dataset from the Excel file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "DCS_Risk_DB_2025.xlsx")
    
    # Create an 'output' directory in the same folder as the script
    output_dir = os.path.join(base_dir, "output")
    
    try:
        df = pd.read_excel(file_path, sheet_name="data", engine="openpyxl")
    except FileNotFoundError:
        print(f"Error: Could not find the data file at {file_path}")
        print("Please ensure 'DCS_Risk_DB_2025.xlsx' is in the same directory as this script.")
        return
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return
    
    # Store original data before transformations
    original_data = df.copy()
    
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
    
    # Calculate feature importance with correct parameters
    importance_df = calculate_feature_importance(models, X.columns, X_train, scaler, original_data)
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
    
    # Monte Carlo Simulation
    print("\nPerforming Monte Carlo Simulations...")
    
    # Convert training data to numpy arrays for bootstrapping
    X_train_scaled_np = X_train_scaled
    y_train_np = y_train.to_numpy() if isinstance(y_train, pd.Series) else y_train
    
    # 1. Parameter uncertainty through Monte Carlo sampling
    mc_params = monte_carlo_parameter_sampling(grid_search.best_params_)
    param_models = []
    for params in tqdm(mc_params, desc="Training MC parameter models"):
        model = GradientBoostingRegressor(**params, random_state=42)
        model.fit(X_train_scaled_np, y_train_np)
        param_models.append(model)
    
    # 2. Bootstrap sampling for model uncertainty
    bootstrap_models = []
    for X_boot, y_boot in tqdm(list(bootstrap_sample(X_train_scaled_np, y_train_np, n_samples=50)), 
                              desc="Training bootstrap models"):
        model = GradientBoostingRegressor(**grid_search.best_params_, random_state=42)
        model.fit(X_boot, y_boot)
        bootstrap_models.append(model)
    
    # 3. Monte Carlo predictions with input uncertainty
    all_models = models + param_models + bootstrap_models
    mc_mean, mc_std, mc_lower, mc_upper = monte_carlo_prediction(
        all_models,
        X_test_scaled,
        n_samples=100,
        uncertainty=0.05
    )
    
    # Evaluate Monte Carlo performance
    mc_metrics = evaluate_monte_carlo_performance(y_test, mc_mean, mc_std)
    print_monte_carlo_metrics(mc_metrics)
    
    # Add Monte Carlo results to the results DataFrame
    # Ensure predictions are for all data points
    mc_mean_all, mc_std_all, mc_lower_all, mc_upper_all = monte_carlo_prediction(
        all_models,
        X_scaled,
        n_samples=100,
        uncertainty=0.05
    )
    
    results_df["mc_predicted_risk"] = mc_mean_all
    results_df["mc_uncertainty"] = mc_std_all
    results_df["mc_ci_lower"] = mc_lower_all
    results_df["mc_ci_upper"] = mc_upper_all
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    save_results(results_df, models, scaler, onehot_encoder, X.columns, output_dir, timestamp)

if __name__ == "__main__":
    main()