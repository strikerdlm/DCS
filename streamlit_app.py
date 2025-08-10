import streamlit as st
import joblib
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import glob
from typing import Tuple, Optional, Any, Dict

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


def load_artifacts(model_dir: str) -> Tuple[Any, Any, Any, Dict[str, Any]]:
    """Load scaler, encoder, and model objects plus preprocessing metadata."""
    scaler_path, encoder_path, model_path = discover_artifacts(model_dir)
    scaler = joblib.load(scaler_path)
    encoder = joblib.load(encoder_path)
    model_obj = joblib.load(model_path)

    # Some artefacts wrap the actual estimator in a dict → extract if needed
    if isinstance(model_obj, dict):
        model = model_obj.get("base_model") or model_obj.get("model") or model_obj.get("models") or model_obj
    else:
        model = model_obj

    # Heuristic: presence of model_params_*.joblib indicates v11 training with non-linear preprocessing
    has_params = bool(glob.glob(os.path.join(model_dir, "model_params_*.joblib")))
    meta = {
        "apply_v11_transforms": has_params
    }
    return scaler, encoder, model, meta


def prepare_features(
    altitude: float,
    time_at_altitude: float,
    prebreathing_time: float,
    exercise_level: str,
    scaler: Any,
    encoder: Any,
    apply_v11_transforms: bool = False,
) -> np.ndarray:
    """Return a 2-D numpy array ready to feed into *model.predict(..)*

    When ``apply_v11_transforms`` is True, applies the v11 non-linear preprocessing used during training:
    - prebreathing_time := log1p(prebreathing_time)
    - time_at_altitude := (time_at_altitude) ** 1.5
    """
    # Apply v11 non-linear transforms if requested (to match training distribution)
    if apply_v11_transforms:
        prebreathing_time = float(np.log1p(prebreathing_time))
        time_at_altitude = float(np.power(time_at_altitude, 1.5))

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
            scaler_obj, encoder_obj, model_obj, meta = load_artifacts(model_dir)
            st.success("Model artefacts loaded successfully! 🎉")
            st.session_state["artefacts"] = {
                "scaler": scaler_obj,
                "encoder": encoder_obj,
                "model": model_obj,
                "apply_v11_transforms": bool(meta.get("apply_v11_transforms", False)),
            }
        except Exception as ex:
            st.error(f"Failed to load artefacts: {ex}")

    # Parameter inputs (sticky even if artefacts not loaded yet)
    st.header("Exposure parameters")
    altitude = st.number_input("Altitude (feet)", 0.0, 63000.0, 18000.0, step=500.0, help="Cabin altitude in feet.")
    time_at_altitude = st.number_input("Time at altitude (minutes)", 0.0, 600.0, 30.0, step=5.0, help="Duration of exposure at altitude.")
    prebreathing_time = st.number_input("Pre-breathing time (minutes)", 0.0, 180.0, 30.0, step=5.0, help="Pre-breathe oxygen time prior to exposure.")

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
apply_v11_transforms = bool(st.session_state["artefacts"].get("apply_v11_transforms", False))

# Preprocessing indicator for user clarity
if apply_v11_transforms:
    st.caption("Using model with non-linear preprocessing: time_at_altitude^1.5 and log1p(pre-breathing time).")

features = prepare_features(
    altitude,
    time_at_altitude,
    prebreathing_time,
    exercise_level,
    scaler,
    encoder,
    apply_v11_transforms,
)

predicted_risk = predict_risk(model, features)

st.metric(label="Predicted DCS Risk (%)", value=f"{predicted_risk:.2f}")

# Create tabbed interface for more exploration

prediction_tab, sweep_tab, importance_tab, three_d_tab, math_tab = st.tabs([
    "📈 Single Prediction",
    "🧮 Parameter Sweep",
    "📊 Feature Importance",
    "🌐 3D Surface",
    "📐 Model Math",
])

with prediction_tab:
    st.subheader("Input Summary")
    st.json({
        "Altitude (ft)": altitude,
        "Time @ Altitude (min)": time_at_altitude,
        "Pre-breathing (min)": prebreathing_time,
        "Exercise level": exercise_level,
        "Preprocessing": "v11 non-linear" if apply_v11_transforms else "standard",
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
        step=(sweep_max - sweep_min) / 50,
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
            f_vec = prepare_features(_alt, _time, _pre, exercise_level, scaler, encoder, apply_v11_transforms)
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

with three_d_tab:
    st.subheader("3D risk surface")
    st.caption("Explore predicted risk as a surface varying two inputs while holding the others fixed.")

    var_options = ["Altitude", "Time at altitude", "Pre-breathing time"]
    col_x, col_y = st.columns(2)
    with col_x:
        param_x = st.selectbox("X-axis", var_options, index=0)
    with col_y:
        param_y = st.selectbox("Y-axis", var_options, index=1)

    if param_x == param_y:
        st.warning("Select two different parameters for X and Y.")
    else:
        ranges = {
            "Altitude": (0.0, 63000.0),
            "Time at altitude": (0.0, 600.0),
            "Pre-breathing time": (0.0, 180.0),
        }
        x_min, x_max = ranges[param_x]
        y_min, y_max = ranges[param_y]

        grid_res = st.select_slider("Grid resolution", options=[20, 30, 40, 60, 80, 100], value=40)
        if st.button("Generate 3D surface"):
            x_vals = np.linspace(x_min, x_max, grid_res)
            y_vals = np.linspace(y_min, y_max, grid_res)
            z_matrix = np.zeros((grid_res, grid_res), dtype=float)

            def assign_vars(x_value, y_value):
                _alt, _time, _pre = altitude, time_at_altitude, prebreathing_time
                if param_x == "Altitude":
                    _alt = x_value
                elif param_x == "Time at altitude":
                    _time = x_value
                elif param_x == "Pre-breathing time":
                    _pre = x_value

                if param_y == "Altitude":
                    _alt = y_value
                elif param_y == "Time at altitude":
                    _time = y_value
                elif param_y == "Pre-breathing time":
                    _pre = y_value
                return _alt, _time, _pre

            for i, xv in enumerate(x_vals):
                for j, yv in enumerate(y_vals):
                    _alt, _time, _pre = assign_vars(xv, yv)
                    f_vec = prepare_features(_alt, _time, _pre, exercise_level, scaler, encoder, apply_v11_transforms)
                    z_matrix[j, i] = predict_risk(model, f_vec)

            surface_fig = go.Figure(
                data=[
                    go.Surface(
                        x=x_vals, y=y_vals, z=z_matrix,
                        colorscale="Turbo",
                        colorbar=dict(title="Risk (%)"),
                        contours={"z": {"show": True, "usecolormap": True, "project_z": True}}
                    )
                ]
            )
            surface_fig.update_layout(
                scene=dict(
                    xaxis_title=param_x,
                    yaxis_title=param_y,
                    zaxis_title="Predicted DCS Risk (%)",
                ),
                height=650,
                template="plotly_dark",
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(surface_fig, use_container_width=True)

            st.markdown("—")
            st.subheader("2D contour heatmap")
            contour_fig = go.Figure(
                data=[
                    go.Contour(
                        x=x_vals,
                        y=y_vals,
                        z=z_matrix,
                        colorscale="Turbo",
                        contours_coloring="heatmap",
                        colorbar=dict(title="Risk (%)")
                    )
                ]
            )
            contour_fig.update_layout(
                xaxis_title=param_x,
                yaxis_title=param_y,
                height=550,
                template="plotly_dark",
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(contour_fig, use_container_width=True)

with math_tab:
    st.subheader("Model math and transformations")
    st.markdown(
        """
        - Training v11 preprocessing transforms:
          - time_at_altitude' = time_at_altitude^{1.5}
          - prebreathing_time' = log(1 + prebreathing_time)
        - Streamlit applies these transforms when v11 artefacts are detected so inputs match training.
        """
    )
    st.latex(r"p1n2 = p_0 + (p_a - p_0)\,\left(1 - e^{-k\,t}\right)")
    st.latex(r"k = \frac{1 - e^{-\lambda\,VO_2}}{51.937} + \frac{\ln 2}{360}")
    st.latex(r"ETR = \frac{P1N2}{P2}")
    st.latex(r"Pr(\text{DCS}) = \sigma\!\left(B_0 + B_{etr}\,ETR + B_{age}\,age + B_{gender}\,gender\right)")