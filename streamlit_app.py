import streamlit as st
import joblib
import numpy as np
import plotly.graph_objects as go
import os
import glob
from typing import Tuple, Optional, Any

# -------------------------------------------------------------
# Streamlit page configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="DCS Risk Explorer",
    layout="wide",
    page_icon="🩺",
    initial_sidebar_state="expanded"
)

st.title("🩺 Decompression Sickness (DCS) Risk Explorer")

st.markdown(
    """
    **Interactive application for exploring multiple DCS machine-learning models.**

    1. **Select a trained model directory** – The app will automatically locate the most-recent scaler, encoder, and model artefacts.
    2. **Enter exposure parameters** – Altitude, time at altitude, pre-breathing time, and physical exercise level.
    3. **Visualise predictions** – Instant risk calculation, parameter sweeps, and feature-importance plots – all in one place.

    > *Disclaimer*: These models are provided for **research purposes only**; they are **not** validated for operational or clinical use.
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------

def _locate_latest(pattern: str) -> Optional[str]:
    """Locate the latest artefact matching a pattern (based on timestamp in filename)."""
    files = glob.glob(pattern)
    if not files:
        return None
    # Expect filenames with a YYYYMMDD_HHMM segment before .joblib, e.g. _20250129_1034.joblib
    def _timestamp(f: str) -> str:
        base = os.path.basename(f)
        parts = base.split("_")
        return parts[-2] + parts[-1].split(".")[0] if len(parts) >= 3 else ""

    files.sort(key=_timestamp, reverse=True)
    return files[0]


def discover_artifacts(model_dir: str) -> Tuple[str, str, str]:
    """Return paths to (scaler, encoder, model) artefacts located in *model_dir*.

    The function searches for the most-recent joblib file of each kind using the filename
    prefixes used across the code-base (e.g. ``scaler_YYYYMMDD_HHMM.joblib``).
    """
    scaler = _locate_latest(os.path.join(model_dir, "scaler_*.joblib"))
    encoder = _locate_latest(os.path.join(model_dir, "onehot_encoder_*.joblib"))
    # Models may be saved with different prefixes; we search both
    model = _locate_latest(os.path.join(model_dir, "simple_model_*.joblib")) or \
            _locate_latest(os.path.join(model_dir, "trained_model_*.joblib")) or \
            _locate_latest(os.path.join(model_dir, "model_*.joblib"))

    if not (scaler and encoder and model):
        missing = [n for n, p in zip(["Scaler", "Encoder", "Model"], [scaler, encoder, model]) if p is None]
        raise FileNotFoundError(f"Missing {'/'.join(missing)} artefacts in directory: {model_dir}")
    return scaler, encoder, model


def load_artifacts(model_dir: str) -> Tuple[Any, Any, Any]:
    """Load scaler, encoder, and model objects."""
    scaler_path, encoder_path, model_path = discover_artifacts(model_dir)
    scaler = joblib.load(scaler_path)
    encoder = joblib.load(encoder_path)
    model_obj = joblib.load(model_path)

    # Some artefacts wrap the actual estimator in a dict → extract if needed
    if isinstance(model_obj, dict):
        model = model_obj.get("base_model") or model_obj.get("model") or model_obj.get("models") or model_obj
    else:
        model = model_obj
    return scaler, encoder, model


def prepare_features(
    altitude: float,
    time_at_altitude: float,
    prebreathing_time: float,
    exercise_level: str,
    scaler: Any,
    encoder: Any,
) -> np.ndarray:
    """Return a 2-D numpy array ready to feed into *model.predict(..)*"""
    numerical = [altitude, time_at_altitude, prebreathing_time]
    # Ensure exercise level string matches the encoderʼs categories
    matched = next((lvl for lvl in encoder.categories_[0] if lvl.lower() == exercise_level.lower()), None)
    if matched is None:
        raise ValueError(f"Exercise level '{exercise_level}' not recognised by encoder: {encoder.categories_[0]}")
    categorical = encoder.transform([[matched]]).ravel().tolist()
    full = np.array([numerical + categorical])
    return scaler.transform(full)


def predict_risk(model: Any, features: np.ndarray) -> float:
    """Predict risk (clipped between 0 – 100%)."""
    pred = model.predict(features)[0]
    return float(np.clip(pred, 0, 100))


# -------------------------------------------------------------
# Sidebar – Model selection & parameters
# -------------------------------------------------------------

with st.sidebar:
    st.header("Model artefacts")
    default_dir = "output"  # user-configurable path where artefacts normally live
    model_dir = st.text_input("Artefact directory", value=default_dir)

    if st.button("🔄 Load model"):
        try:
            scaler_obj, encoder_obj, model_obj = load_artifacts(model_dir)
            st.success("Model artefacts loaded successfully! 🎉")
            st.session_state["artefacts"] = {
                "scaler": scaler_obj,
                "encoder": encoder_obj,
                "model": model_obj,
            }
        except Exception as ex:
            st.error(f"Failed to load artefacts: {ex}")

    # Parameter inputs (sticky even if artefacts not loaded yet)
    st.header("Exposure parameters")
    altitude = st.number_input("Altitude (feet)", 0.0, 63000.0, 18000.0, step=500.0)
    time_at_altitude = st.number_input("Time at altitude (minutes)", 0.0, 600.0, 30.0, step=5.0)
    prebreathing_time = st.number_input("Pre-breathing time (minutes)", 0.0, 180.0, 30.0, step=5.0)

    exercise_level = "Rest"
    if "artefacts" in st.session_state:
        exercise_level = st.selectbox(
            "Exercise level",
            options=list(st.session_state["artefacts"]["encoder"].categories_[0]),
            index=0,
        )
    else:
        exercise_level = st.selectbox("Exercise level", ["Rest", "Mild", "Heavy"], index=0)


# -------------------------------------------------------------
# Main tabs
# -------------------------------------------------------------

if "artefacts" not in st.session_state:
    st.info("Load a trained model from the sidebar to begin.")
    st.stop()

scaler = st.session_state["artefacts"]["scaler"]
encoder = st.session_state["artefacts"]["encoder"]
model = st.session_state["artefacts"]["model"]

features = prepare_features(
    altitude,
    time_at_altitude,
    prebreathing_time,
    exercise_level,
    scaler,
    encoder,
)

predicted_risk = predict_risk(model, features)

st.metric(label="Predicted DCS Risk (%)", value=f"{predicted_risk:.2f}")

# Create tabbed interface for more exploration

prediction_tab, sweep_tab, importance_tab = st.tabs([
    "📈 Single Prediction",
    "🧮 Parameter Sweep",
    "📊 Feature Importance",
])

with prediction_tab:
    st.subheader("Input Summary")
    st.json({
        "Altitude (ft)": altitude,
        "Time @ Altitude (min)": time_at_altitude,
        "Pre-breathing (min)": prebreathing_time,
        "Exercise level": exercise_level,
    })

    st.success(f"**Predicted DCS risk**: {predicted_risk:.2f}%")

with sweep_tab:
    st.subheader("Parameter sweep – explore how risk changes when varying a single parameter")

    param_to_vary = st.selectbox(
        "Select parameter to sweep",
        ["Altitude", "Time at altitude", "Pre-breathing time"],
    )

    sweep_min, sweep_max = {
        "Altitude": (0.0, 63000.0),
        "Time at altitude": (0.0, 600.0),
        "Pre-breathing time": (0.0, 180.0),
    }[param_to_vary]

    sweep_range = st.slider(
        f"{param_to_vary} range",
        float(sweep_min),
        float(sweep_max),
        (float(sweep_min), float(sweep_max)),
        step= (sweep_max - sweep_min) / 50,
    )
    num_points = st.selectbox("Resolution (points)", options=[25, 50, 100, 200], index=1)

    if st.button("Run sweep"):
        var_vals = np.linspace(sweep_range[0], sweep_range[1], num_points)
        pred_vals = []
        for v in var_vals:
            _alt = altitude
            _time = time_at_altitude
            _pre = prebreathing_time
            if param_to_vary == "Altitude":
                _alt = v
            elif param_to_vary == "Time at altitude":
                _time = v
            elif param_to_vary == "Pre-breathing time":
                _pre = v
            f_vec = prepare_features(_alt, _time, _pre, exercise_level, scaler, encoder)
            pred_vals.append(predict_risk(model, f_vec))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=var_vals, y=pred_vals, mode="lines", name="Risk (%)"))
        fig.update_layout(
            xaxis_title=param_to_vary,
            yaxis_title="Predicted DCS Risk (%)",
            template="plotly_dark",
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

with importance_tab:
    st.subheader("Model-reported feature importance")

    # Obtain estimator supporting feature_importances_ (e.g., tree-based). If model is an ensemble list, take first.
    estimator = model[0] if isinstance(model, (list, tuple)) else model

    if hasattr(estimator, "feature_importances_"):
        importances = estimator.feature_importances_
        feature_names = list(encoder.get_feature_names_out(["exercise_level"]))
        all_features = ["altitude", "time_at_altitude", "prebreathing_time"] + feature_names
        fig_imp = go.Figure(
            [
                go.Bar(
                    x=importances,
                    y=all_features,
                    orientation="h",
                )
            ]
        )
        fig_imp.update_layout(
            xaxis_title="Importance",
            template="plotly_dark",
            height=450,
        )
        st.plotly_chart(fig_imp, use_container_width=True)
    else:
        st.info("Selected model does not provide native feature-importance information.")