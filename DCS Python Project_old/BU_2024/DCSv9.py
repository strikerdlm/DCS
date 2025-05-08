# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 22:04:20 2023

@author: DiegoMalpica
Modified to be platform-independent
"""
import pandas as pd
from openpyxl import load_workbook
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from joblib import dump
import os
import sys
from pathlib import Path

def train_dcs_model(input_file):
    """
    Train the DCS model using the input Excel file.
    
    Args:
        input_file: String or Path object pointing to the input Excel file
    """
    # Convert input path to Path object and resolve to absolute path
    input_path = Path(input_file).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Get the directory of the input file to save outputs in the same location
    output_dir = input_path.parent
    
    # Load the dataset from the Excel file
    sheet_name = "data"
    try:
        df = pd.read_excel(input_path, sheet_name=sheet_name, engine="openpyxl")
    except Exception as e:
        raise Exception(f"Error reading Excel file: {e}")

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

    # Train a Gradient Boosting Regressor
    model = GradientBoostingRegressor(n_estimators=100, random_state=42, learning_rate=0.1, max_depth=3)
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Ensure predictions are within a valid range (0 to 100)
    y_pred = y_pred.clip(min=0, max=100)

    # Calculate the mean squared error
    mse = mean_squared_error(y_test, y_pred)

    print("Mean Squared Error:", mse)

    # Print feature importances and intercept
    print("Feature Importances:\n", model.feature_importances_)
    print("Intercept:", model.init_.constant_[0][0])

    # Add calculated risk to the original DataFrame
    df["calculated"] = model.predict(df.drop("risk_of_decompression_sickness", axis=1)).clip(min=0, max=100)

    # Define output paths using Path objects
    output_paths = {
        'data': output_dir / "output_data_set.xlsx",
        'model': output_dir / "trained_model.joblib",
        'encoder': output_dir / "onehot_encoder.joblib",
        'columns': output_dir / "column_names.joblib"
    }
    
    # Save the DataFrame to a new Excel file
    try:
        df.to_excel(output_paths['data'], sheet_name=sheet_name, engine="openpyxl", index=False)
        dump(model, output_paths['model'])
        dump(onehot_encoder, output_paths['encoder'])
        dump(X.columns, output_paths['columns'])
    except Exception as e:
        raise Exception(f"Error saving output files: {e}")
    
    print(f"Files saved successfully in: {output_dir}")
    return model, onehot_encoder, X.columns

def main():
    """Main function to handle command line arguments and execute the model training."""
    if len(sys.argv) != 2:
        print("Usage: python DCSv9.py <path_to_input_excel>")
        sys.exit(1)
    
    try:
        model, encoder, columns = train_dcs_model(sys.argv[1])
        print("Model training completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()