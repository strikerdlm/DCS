# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 09:38:00 2023

@author: DiegoMalpica
"""

# Import necessary libraries
import pandas as pd  # For data manipulation and analysis
import numpy as np   # For numerical operations, especially for array handling
# from openpyxl import load_workbook # No longer needed as we are using CSV
from sklearn.model_selection import train_test_split, cross_val_score, KFold, GridSearchCV  # For splitting data, cross-validation, and hyperparameter tuning
from sklearn.ensemble import GradientBoostingRegressor  # The machine learning model
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error  # For evaluating model performance
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # For preparing categorical and numerical features
from joblib import dump  # For saving the trained model and preprocessing objects
import os  # For interacting with the operating system, e.g., creating directories
from datetime import datetime  # For generating timestamps for output files

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "DCS_Risk_DB_2025.csv")
# sheet_name = "data" # Not needed for CSV files

# Load the dataset from the CSV file
df = pd.read_csv(file_path)

# Data Preprocessing
# Check for missing values and handle them by dropping rows with any missing values.
# This is a simple approach; for other scenarios, imputation might be considered.
df.dropna(inplace=True)

# Feature Engineering: One-hot encode the 'exercise_level' column
# 'exercise_level' is a categorical feature. Machine learning models typically require numerical input.
# OneHotEncoder converts categorical variables into a format that can be provided to ML algorithms.
# sparse_output=False ensures the output is a dense array.
onehot_encoder = OneHotEncoder(sparse_output=False)
# Fit the encoder on the 'exercise_level' column and transform it.
exercise_level_encoded = onehot_encoder.fit_transform(df[['exercise_level']])
# Get the new column names for the encoded features.
exercise_level_columns = onehot_encoder.get_feature_names_out(['exercise_level'])
# Create a DataFrame with the encoded columns and original index.
exercise_level_df = pd.DataFrame(exercise_level_encoded, columns=exercise_level_columns, index=df.index)

# Add the encoded columns to the original dataframe and remove the original 'exercise_level' column.
df = pd.concat([df.drop('exercise_level', axis=1), exercise_level_df], axis=1)

# Split the data into input features (X) and target variable (y)
# "risk_of_decompression_sickness" is the target variable we want to predict.
# All other columns are used as input features.
X = df.drop("risk_of_decompression_sickness", axis=1)
y = df["risk_of_decompression_sickness"]

# Split data into training and testing sets
# X_train, y_train are used to train the model.
# X_test, y_test are used to evaluate the trained model's performance on unseen data.
# test_size=0.2 means 20% of the data is used for testing, 80% for training.
# random_state=42 ensures reproducibility of the split.
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the numerical features
# StandardScaler standardizes features by removing the mean and scaling to unit variance.
# This is important for Gradient Boosting and other algorithms sensitive to feature magnitudes.
# Fit the scaler on the training data only, then transform both training and test data to prevent data leakage.
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
# Also scale the entire X dataset for cross-validation scoring on the whole dataset later.
X_scaled = scaler.transform(X) # Note: Ideally, for CV, scaling should be done within each fold.
                               # However, scaling X based on X_train's fit is a common simplification.

# Model Training: Gradient Boosting Regressor with Hyperparameter Tuning

# Perform Grid Search for best parameters
# Define the parameter grid to search through. These are hyperparameters for GradientBoostingRegressor.
param_grid = {
    'n_estimators': [100, 200],          # Number of boosting stages to perform.
    'learning_rate': [0.01, 0.05, 0.1],  # Shrinks the contribution of each tree.
    'max_depth': [3, 4, 5],              # Maximum depth of the individual regression estimators.
    'min_samples_split': [2, 5],       # Minimum number of samples required to split an internal node.
    'min_samples_leaf': [1, 3],        # Minimum number of samples required to be at a leaf node.
    'subsample': [0.8, 0.9, 1.0],        # Fraction of samples to be used for fitting the individual base learners.
    'max_features': ['sqrt', 'log2']     # Number of features to consider when looking for the best split.
}

# Initialize the base model. random_state for reproducibility.
base_model = GradientBoostingRegressor(random_state=42)

# Initialize GridSearchCV.
# This will try all combinations of parameters in param_grid using 5-fold cross-validation.
# 'n_jobs=-1' uses all available CPU cores.
# 'scoring='r2'' uses R-squared as the metric to evaluate parameter combinations.
# 'verbose=1' prints progress messages.
grid_search = GridSearchCV(
    estimator=base_model,
    param_grid=param_grid,
    cv=5,
    n_jobs=-1,
    scoring='r2',
    verbose=1
)

# Fit grid search to the scaled training data to find the best hyperparameters.
print("Performing Grid Search...")
grid_search.fit(X_train_scaled, y_train)

# Print best parameters found by GridSearchCV and the corresponding cross-validation score.
print("\nBest parameters found:")
print(grid_search.best_params_)
print(f"\nBest cross-validation score: {grid_search.best_score_:.4f}")

# Ensemble Modeling: Use best parameters to train an ensemble of models
# This approach involves training multiple models (here, 100) with the same best hyperparameters
# but different random initializations (random_state=i). The ensemble's prediction is an average,
# which can lead to better generalization and more robust predictions.
best_params = grid_search.best_params_
n_models = 100  # Number of models in the ensemble
models = []     # List to store the trained models

# Perform k-fold cross-validation setup for evaluating one of the ensemble models
# KFold provides train/test indices to split data in train/test sets.
# shuffle=True shuffles the data before splitting. random_state for reproducibility.
kf = KFold(n_splits=5, shuffle=True, random_state=42)

print("\nTraining Ensemble Models...")
for i in range(n_models):
    # Initialize a new model with the best parameters and a unique random_state for diversity.
    model = GradientBoostingRegressor(**best_params, random_state=i)
    # Fit the model on the scaled training data.
    model.fit(X_train_scaled, y_train)
    models.append(model)
    
    # Perform cross-validation for the first model in the ensemble as an example.
    # This uses the entire scaled dataset (X_scaled, y) for a more robust estimate of performance.
    if i == 0:
        # cross_val_score evaluates a score by cross-validation.
        cv_scores = cross_val_score(model, X_scaled, y, cv=kf, scoring='r2')
        print(f"\nCross-validation R² scores for the first ensemble model: {cv_scores}")
        print(f"Mean CV R² score for the first ensemble model: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

# Make predictions using the trained ensemble
print("\nMaking predictions...")
# Initialize arrays to store predictions from each model in the ensemble.
# y_preds is for the test set, y_preds_all is for the entire dataset.
y_preds_test_all_models = np.zeros((len(X_test_scaled), n_models)) # Renamed for clarity
y_preds_full_data_all_models = np.zeros((len(X_scaled), n_models)) # Renamed for clarity

for i, model in enumerate(models):
    # Predict on the scaled test set.
    y_preds_test_all_models[:, i] = model.predict(X_test_scaled)
    # Predict on the entire scaled dataset.
    y_preds_full_data_all_models[:, i] = model.predict(X_scaled)

# Calculate the ensemble prediction by averaging predictions from all models in the ensemble (for the test set).
y_pred_ensemble_test = y_preds_test_all_models.mean(axis=1)
# Clip predictions to be within a realistic range (0 to 100 for DCS risk percentage).
y_pred_ensemble_test = y_pred_ensemble_test.clip(min=0, max=100)

# Evaluate Model Performance on the Test Set
# Calculate and print detailed metrics for the ensemble predictions on the test set.
mse = mean_squared_error(y_test, y_pred_ensemble_test)
r2 = r2_score(y_test, y_pred_ensemble_test)
mae = mean_absolute_error(y_test, y_pred_ensemble_test)
rmse = np.sqrt(mse) # Root Mean Squared Error

print("\nModel Performance Metrics (Ensemble on Test Set):")
print("-" * 30)
print(f"R-squared (Ensemble): {r2:.4f}")          # Proportion of variance in the dependent variable predictable from the independent variables.
print(f"Mean Squared Error: {mse:.4f}")            # Average squared difference between estimated values and actual value.
print(f"Root Mean Squared Error: {rmse:.4f}")      # Square root of MSE, in the same units as the target variable.
print(f"Mean Absolute Error: {mae:.4f}")           # Average absolute difference between predicted and actual values.

# Feature Importance Analysis
# Calculate average feature importance across all models in the ensemble.
feature_importance = np.zeros(len(X.columns))
for model in models:
    feature_importance += model.feature_importances_

feature_importance /= len(models) # Average importance

# Create a DataFrame to display feature importances, sorted by importance.
importance_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': feature_importance
})
importance_df = importance_df.sort_values('Importance', ascending=False)

print("\nFeature Importances (Averaged over Ensemble):")
print("-" * 30)
for idx, row in importance_df.iterrows():
    print(f"{row['Feature']}: {row['Importance']:.4f}")

# Prediction Intervals and Uncertainty
# Calculate predictions and uncertainty for the entire dataset using the ensemble.
# Standard deviation of predictions from different models in the ensemble serves as a measure of uncertainty.
y_pred_ensemble_full_data_std = y_preds_full_data_all_models.std(axis=1)
# Mean prediction of the ensemble for the full dataset.
y_pred_ensemble_full_data_mean = y_preds_full_data_all_models.mean(axis=1)

# Calculate 95% prediction interval.
# This interval provides an estimate of the range where the true value might lie.
# Assumes predictions are somewhat normally distributed around the mean.
prediction_interval_95 = 1.96 * y_pred_ensemble_full_data_std # 1.96 is the z-score for 95% confidence
# Calculate lower and upper bounds, clipping to realistic 0-100 range.
lower_bound = (y_pred_ensemble_full_data_mean - prediction_interval_95).clip(min=0, max=100)
upper_bound = (y_pred_ensemble_full_data_mean + prediction_interval_95).clip(min=0, max=100)

# Prepare Results DataFrame
# Create a copy of the original DataFrame to store results.
results_df = df.copy()
# Add calculated risk (mean ensemble prediction for the full dataset), clipped to 0-100.
results_df["calculated_risk"] = y_pred_ensemble_full_data_mean.clip(min=0, max=100)
# Add confidence interval bounds and prediction uncertainty.
results_df["confidence_interval_lower"] = lower_bound
results_df["confidence_interval_upper"] = upper_bound
results_df["prediction_uncertainty"] = y_pred_ensemble_full_data_std

# Save Results and Model Artifacts

# Define the output directory relative to the script's location.
output_dir = os.path.join(script_dir, "output")
# Create the output directory if it doesn't exist.
os.makedirs(output_dir, exist_ok=True)

# Add timestamp to file names for versioning.
timestamp = datetime.now().strftime("%Y%m%d_%H%M")

# Save the DataFrame with predictions and uncertainties to a new Excel file.
output_file_path = os.path.join(output_dir, f"DCS_predictions_{timestamp}.xlsx")
# We will save to CSV to align with input format and avoid openpyxl dependency for this output
output_csv_path = os.path.join(output_dir, f"DCS_predictions_{timestamp}.csv")
results_df.to_csv(output_csv_path, index=False)


# Save the first model of the ensemble, scaler, OneHotEncoder, and column names.
# Saving the first model as representative; for full reproducibility, all models or a method to recreate them would be needed.
# Alternatively, a single, retrained model on all data could be saved.
dump(models[0], os.path.join(output_dir, f"trained_model_{timestamp}.joblib"))
dump(scaler, os.path.join(output_dir, f"scaler_{timestamp}.joblib"))
dump(onehot_encoder, os.path.join(output_dir, f"onehot_encoder_{timestamp}.joblib"))
dump(X.columns, os.path.join(output_dir, f"column_names_{timestamp}.joblib"))

print(f"\nResults and model artifacts saved to ./{output_dir}/ with timestamp {timestamp}")
print(f"Predictions saved to {output_csv_path}")