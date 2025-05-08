import argparse
import joblib
import numpy as np
import os
import warnings
import pandas as pd
from glob import glob
from datetime import datetime

warnings.filterwarnings("ignore", category=UserWarning)

def get_latest_model_files(model_dir):
    """Find the most recent model artifacts based on timestamp in filename"""
    try:
        # Get all joblib files in the directory
        model_files = glob(os.path.join(model_dir, "*_*.joblib"))
        if not model_files:
            raise FileNotFoundError("No model files found in directory")
        
        # Extract timestamps and find the latest one
        timestamps = []
        for f in model_files:
            try:
                # Extract timestamp from filename (format: *_YYYYMMDD_HHMM.joblib)
                filename = os.path.basename(f)
                if '_' in filename:
                    # Get the last two parts of the timestamp (YYYYMMDD_HHMM)
                    parts = filename.split('_')
                    if len(parts) >= 3:  # Ensure we have enough parts
                        date_part = parts[-2]  # YYYYMMDD
                        time_part = parts[-1].replace('.joblib', '')  # HHMM
                        if len(date_part) == 8 and len(time_part) == 4:
                            timestamps.append(f"{date_part}_{time_part}")
            except:
                continue
        
        if not timestamps:
            raise ValueError("No valid timestamps found in model files")
            
        latest_timestamp = max(timestamps)
        print(f"Using model timestamp: {latest_timestamp}")
        
        # Return paths with the latest timestamp
        return {
            'scaler': os.path.join(model_dir, f"scaler_{latest_timestamp}.joblib"),
            'model': os.path.join(model_dir, f"simple_model_{latest_timestamp}.joblib"),
            'onehot': os.path.join(model_dir, f"onehot_encoder_{latest_timestamp}.joblib")
        }
    except Exception as e:
        raise RuntimeError(f"Error finding model files: {str(e)}")

def load_model_artifacts(model_dir):
    """Load saved model artifacts from directory"""
    try:
        # Get latest model file paths
        model_files = get_latest_model_files(model_dir)
        
        # Load artifacts
        scaler = joblib.load(model_files['scaler'])
        model_dict = joblib.load(model_files['model'])
        onehot_encoder = joblib.load(model_files['onehot'])
        
        return scaler, model_dict, onehot_encoder
    except Exception as e:
        raise RuntimeError(f"Error loading model artifacts: {str(e)}")

def preprocess_features(features_dict, onehot_encoder, expected_features=None):
    """Apply the same preprocessing as the training pipeline"""
    # Apply non-linear transformations
    features_dict = features_dict.copy()  # Create a copy to avoid modifying the original
    features_dict['prebreathing_time'] = np.log1p(features_dict['prebreathing_time'])
    features_dict['time_at_altitude'] = features_dict['time_at_altitude'] ** 1.5
    
    # Handle exercise level encoding
    exercise_encoded = onehot_encoder.transform([[features_dict['exercise_level']]])
    exercise_columns = onehot_encoder.get_feature_names_out(['exercise_level'])
    
    # Create DataFrame with all features
    processed_dict = {
        'altitude': features_dict['altitude'],
        'time_at_altitude': features_dict['time_at_altitude'],
        'prebreathing_time': features_dict['prebreathing_time']
    }
    
    # Add encoded exercise levels
    for col, val in zip(exercise_columns, exercise_encoded[0]):
        processed_dict[col] = val
    
    # Create DataFrame
    features_df = pd.DataFrame([processed_dict])
    
    if expected_features is not None:
        # Verify all expected features are present
        missing_features = set(expected_features) - set(features_df.columns)
        if missing_features:
            raise ValueError(f"Missing features: {missing_features}")
        
        # Print feature orders for debugging
        print("\nCurrent feature order:", list(features_df.columns))
        print("Expected feature order:", expected_features)
        
        # Reorder columns to match expected order
        features_df = features_df.reindex(columns=expected_features)
    
    return features_df

def calculate_dcs_risk(altitude=None, time_at_altitude=None, prebreathing_time=None, 
                      exercise_level=None, model_dir='output', features_df=None):
    """Calculate DCS risk using the trained ensemble model with uncertainty quantification"""
    try:
        # Load model artifacts
        scaler, model_dict, onehot_encoder = load_model_artifacts(model_dir)
        models = model_dict.get('ensemble_models', [model_dict['base_model']])
        expected_features = model_dict.get('feature_names')
        
        if expected_features is None:
            raise ValueError("Model is missing feature_names. Please retrain the model.")
            
        print(f"\nModel expects features in this order: {expected_features}")
        
        # If features_df is provided, use it directly
        if features_df is not None:
            if not all(col in features_df.columns for col in expected_features):
                raise ValueError(f"Missing expected features. Required: {expected_features}")
            features_df = features_df[expected_features]
        else:
            # Create and preprocess features
            features_dict = {
                'altitude': float(altitude),
                'time_at_altitude': float(time_at_altitude),
                'prebreathing_time': float(prebreathing_time),
                'exercise_level': exercise_level.capitalize()
            }
            
            # Apply preprocessing transformations with expected feature order
            features_df = preprocess_features(features_dict, onehot_encoder, expected_features)
        
        # Verify feature order before scaling
        if not list(features_df.columns) == list(expected_features):
            raise ValueError(f"Feature order mismatch. Got: {list(features_df.columns)}, Expected: {expected_features}")
        
        # Debugging output to verify feature names and order
        print("\nFeatures before scaling:")
        print(features_df.head())
        
        # Check scaler's feature names
        if hasattr(scaler, 'feature_names_in_'):
            print("Scaler's feature names:", scaler.feature_names_in_)
            # Reorder DataFrame columns to match scaler's feature names
            features_df = features_df.reindex(columns=scaler.feature_names_in_)
        else:
            print("Scaler does not have feature_names_in_ attribute")
        
        # Scale features
        scaled_features = scaler.transform(features_df)
        
        # Make predictions with all models in ensemble
        predictions = np.array([model.predict(scaled_features) for model in models])
        
        # Calculate mean and uncertainty
        mean_prediction = predictions.mean(axis=0)[0]
        std_prediction = predictions.std(axis=0)[0]
        
        # Calculate 95% confidence interval
        ci_lower = max(0, mean_prediction - 1.96 * std_prediction)
        ci_upper = min(100, mean_prediction + 1.96 * std_prediction)
        
        return {
            'risk': mean_prediction,
            'uncertainty': std_prediction,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper
        }
        
    except Exception as e:
        raise RuntimeError(f"Error in calculate_dcs_risk: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Calculate DCS risk using trained ensemble model')
    parser.add_argument('--altitude', type=float, required=True, help='Altitude in feet')
    parser.add_argument('--time', type=float, required=True, help='Time at altitude in minutes')
    parser.add_argument('--prebreathing', type=float, required=True, 
                       help='Prebreathing time in minutes')
    parser.add_argument('--exercise', required=True, 
                       choices=['Heavy', 'Mild', 'Rest', 'heavy', 'mild', 'rest'],
                       help='Exercise level (case-insensitive)')
    parser.add_argument('--model_dir', default='output', 
                       help='Directory containing saved model artifacts')
    
    args = parser.parse_args()
    
    try:
        result = calculate_dcs_risk(
            args.altitude,
            args.time,
            args.prebreathing,
            args.exercise,
            args.model_dir
        )
        
        print("\nDCS Risk Prediction Results:")
        print("-" * 30)
        print(f"Predicted Risk: {result['risk']:.2f}%")
        print(f"Uncertainty: ±{result['uncertainty']:.2f}%")
        print(f"95% Confidence Interval: [{result['ci_lower']:.2f}%, {result['ci_upper']:.2f}%]")
        
    except Exception as e:
        print(f"Error calculating risk: {str(e)}")

if __name__ == '__main__':
    main() 