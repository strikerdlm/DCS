import streamlit as st
import joblib
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def load_model_artifacts(model_dir):
    """Load saved model artifacts from directory"""
    try:
        scaler = joblib.load(os.path.join(model_dir, "scaler_20250129_1034.joblib"))
        encoder = joblib.load(os.path.join(model_dir, "onehot_encoder_20250129_1034.joblib"))
        model_dict = joblib.load(os.path.join(model_dir, "simple_model_20250129_1034.joblib"))
        return scaler, encoder, model_dict
    except Exception as e:
        raise RuntimeError(f"Error loading model artifacts: {str(e)}")

def calculate_dcs_risk(altitude, time_at_altitude, prebreathing_time, exercise_level, model_dir):
    """Calculate DCS risk using the trained model"""
    scaler, encoder, model_dict = load_model_artifacts(model_dir)
    actual_model = model_dict['base_model']
    
    available_levels = encoder.categories_[0].tolist()
    matched_level = next((lvl for lvl in available_levels if lvl.lower() == exercise_level.lower()), None)
    
    if not matched_level:
        raise RuntimeError(f"Invalid exercise level: '{exercise_level}'. Valid options: {available_levels}")

    exercise_encoded = encoder.transform([[matched_level]]).ravel()
    numerical_features = [altitude, time_at_altitude, prebreathing_time]
    full_features = np.array([numerical_features + exercise_encoded.tolist()])
    
    scaled_features = scaler.transform(full_features)
    prediction = actual_model.predict(scaled_features)[0]
    return max(0, min(100, prediction))

# Streamlit UI
st.title("DCS Risk Prediction Calculator")
st.markdown("""
Predict decompression sickness risk using altitude and dive parameters.
""")

# Input controls
col1, col2 = st.columns(2)
with col1:
    altitude = st.number_input("Altitude (feet)", min_value=0.0, max_value=63000.0, value=18000.0)
    time_at_altitude = st.number_input("Time at altitude (minutes)", min_value=0.0, value=30.0)
with col2:
    prebreathing_time = st.number_input("Prebreathing time (minutes)", min_value=0.0, value=30.0)
    exercise_level = st.selectbox("Exercise level", ["Heavy", "Mild", "Rest"])

model_dir = st.text_input("Model directory", value="output")

if st.button("Calculate DCS Risk"):
    try:
        risk = calculate_dcs_risk(
            altitude=altitude,
            time_at_altitude=time_at_altitude,
            prebreathing_time=prebreathing_time,
            exercise_level=exercise_level,
            model_dir=model_dir
        )
        st.success(f"Predicted DCS risk: **{risk:.2f}%**")
    except Exception as e:
        st.error(f"Error calculating risk: {str(e)}") 