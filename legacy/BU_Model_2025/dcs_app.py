import streamlit as st
import joblib
import numpy as np
import os
import glob
import warnings
from typing import Optional, Tuple, Any, Dict

warnings.filterwarnings("ignore", category=UserWarning)


def _locate_latest(pattern: str) -> Optional[str]:
    files = glob.glob(pattern)
    if not files:
        return None
    def _timestamp(f: str) -> str:
        base = os.path.basename(f)
        parts = base.split("_")
        return parts[-2] + parts[-1].split(".")[0] if len(parts) >= 3 else ""
    files.sort(key=_timestamp, reverse=True)
    return files[0]


def discover_artifacts(model_dir: str) -> Tuple[str, str, str]:
    scaler = _locate_latest(os.path.join(model_dir, "scaler_*.joblib"))
    encoder = _locate_latest(os.path.join(model_dir, "onehot_encoder_*.joblib"))
    model = _locate_latest(os.path.join(model_dir, "simple_model_*.joblib")) or \
            _locate_latest(os.path.join(model_dir, "trained_model_*.joblib")) or \
            _locate_latest(os.path.join(model_dir, "model_*.joblib"))
    if not (scaler and encoder and model):
        missing = [n for n, p in zip(["Scaler", "Encoder", "Model"], [scaler, encoder, model]) if p is None]
        raise FileNotFoundError(f"Missing {'/'.join(missing)} artefacts in directory: {model_dir}")
    return scaler, encoder, model


def load_model_artifacts(model_dir: str) -> Tuple[Any, Any, Any, Dict[str, Any]]:
    """Load saved model artifacts from directory with preprocessing metadata."""
    scaler_path, encoder_path, model_path = discover_artifacts(model_dir)
    scaler = joblib.load(scaler_path)
    encoder = joblib.load(encoder_path)
    model_obj = joblib.load(model_path)
    if isinstance(model_obj, dict):
        model = model_obj.get("base_model") or model_obj.get("model") or model_obj
    else:
        model = model_obj
    has_params = bool(glob.glob(os.path.join(model_dir, "model_params_*.joblib")))
    return scaler, encoder, model, {"apply_v11_transforms": has_params}


def calculate_dcs_risk(altitude: float,
                       time_at_altitude: float,
                       prebreathing_time: float,
                       exercise_level: str,
                       model_dir: str) -> float:
    """Calculate DCS risk using the trained model with correct preprocessing."""
    scaler, encoder, model, meta = load_model_artifacts(model_dir)
    apply_v11_transforms = bool(meta.get("apply_v11_transforms", False))

    available_levels = encoder.categories_[0].tolist()
    matched_level = next((lvl for lvl in available_levels if lvl.lower() == exercise_level.lower()), None)
    if not matched_level:
        raise RuntimeError(f"Invalid exercise level: '{exercise_level}'. Valid options: {available_levels}")

    # Apply v11 non-linear transforms if needed
    if apply_v11_transforms:
        prebreathing_time = float(np.log1p(prebreathing_time))
        time_at_altitude = float(np.power(time_at_altitude, 1.5))

    exercise_encoded = encoder.transform([[matched_level]]).ravel().tolist()
    numerical_features = [altitude, time_at_altitude, prebreathing_time]
    full_features = np.array([numerical_features + exercise_encoded])

    scaled_features = scaler.transform(full_features)
    prediction = float(model.predict(scaled_features)[0])
    return float(np.clip(prediction, 0.0, 100.0))


# Streamlit UI
st.title("DCS Risk Prediction Calculator")
st.markdown("""
Predict decompression sickness risk using altitude and exposure parameters.
""")

# Input controls
col1, col2 = st.columns(2)
with col1:
    altitude = st.number_input("Altitude (feet)", min_value=0.0, max_value=63000.0, value=18000.0)
    time_at_altitude = st.number_input("Time at altitude (minutes)", min_value=0.0, value=30.0)
with col2:
    prebreathing_time = st.number_input("Prebreathing time (minutes)", min_value=0.0, value=30.0)
    exercise_level = st.selectbox("Exercise level", ["Rest", "Mild", "Heavy"])  # default scientific order

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