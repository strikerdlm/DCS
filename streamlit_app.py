import math
import os
import glob
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


# -------------------------------------------------------------
# Streamlit page configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="DCS Risk Explorer",
    layout="wide",
    page_icon="🩺",
    initial_sidebar_state="expanded",
)

st.title("🩺 Decompression Sickness (DCS) Risk Explorer")

st.markdown(
    """
    **Interactive application for exploring DCS risk models.**

    - **ML artefact model**: load a trained estimator + preprocessing artefacts (`.joblib`).
    - **Mechanistic 3RUT‑MBe1**: published recursion from NEDU TR 18‑01 (Appendix C).

    > *Disclaimer*: research use only; not validated for clinical or operational use.
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------
# ML artefact helpers
# -------------------------------------------------------------

def _locate_latest(pattern: str) -> Optional[str]:
    """Locate the latest artefact matching a glob pattern.

    Selection heuristic:
    - Prefer filenames containing timestamp segment `YYYYMMDD_HHMM`.
    - Fallback to filesystem mtime.
    """

    files = glob.glob(pattern)
    if not files:
        return None

    ts_re = re.compile(r"(?P<date>\d{8})_(?P<hm>\d{4})")

    def _sort_key(path: str) -> Tuple[int, float]:
        base = os.path.basename(path)
        m = ts_re.search(base)
        if m:
            try:
                dt = datetime.strptime(f"{m.group('date')}_{m.group('hm')}", "%Y%m%d_%H%M")
                return (1, dt.timestamp())
            except ValueError:
                pass
        try:
            return (0, os.path.getmtime(path))
        except OSError:
            return (0, 0.0)

    files.sort(key=_sort_key, reverse=True)
    return files[0]


def discover_artifacts(model_dir: str) -> Tuple[str, str, str]:
    """Return paths to (scaler, encoder, model) artefacts located in *model_dir*."""

    scaler = _locate_latest(os.path.join(model_dir, "scaler_*.joblib"))
    encoder = (
        _locate_latest(os.path.join(model_dir, "onehot_encoder_*.joblib"))
        or _locate_latest(os.path.join(model_dir, "encoder_*.joblib"))
    )
    model = (
        _locate_latest(os.path.join(model_dir, "simple_model_*.joblib"))
        or _locate_latest(os.path.join(model_dir, "trained_model_*.joblib"))
        or _locate_latest(os.path.join(model_dir, "model_*.joblib"))
    )

    if not (scaler and encoder and model):
        missing = [
            n
            for n, p in zip(["Scaler", "Encoder", "Model"], [scaler, encoder, model])
            if p is None
        ]
        raise FileNotFoundError(
            f"Missing {'/'.join(missing)} artefacts in directory: {model_dir}"
        )
    return scaler, encoder, model


def load_artifacts(model_dir: str) -> Tuple[Any, Any, Any, Dict[str, Any]]:
    """Load scaler, encoder, and model objects plus preprocessing metadata."""

    scaler_path, encoder_path, model_path = discover_artifacts(model_dir)
    scaler = joblib.load(scaler_path)
    encoder = joblib.load(encoder_path)
    model_obj = joblib.load(model_path)

    if isinstance(model_obj, dict):
        model = model_obj.get("base_model") or model_obj.get("model") or model_obj.get("models") or model_obj
    else:
        model = model_obj

    # Heuristic: presence of model_params_*.joblib indicates v11 training with non-linear preprocessing
    has_params = bool(glob.glob(os.path.join(model_dir, "model_params_*.joblib")))
    meta = {"apply_v11_transforms": has_params}
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
    """Return a 2-D numpy array ready to feed into `model.predict*()`.

    When `apply_v11_transforms` is True:
    - prebreathing_time := log1p(prebreathing_time)
    - time_at_altitude := time_at_altitude ** 1.5
    """

    for name, val in (
        ("altitude", altitude),
        ("time_at_altitude", time_at_altitude),
        ("prebreathing_time", prebreathing_time),
    ):
        if not np.isfinite(val):
            raise ValueError(f"{name} must be finite")
        if val < 0:
            raise ValueError(f"{name} must be >= 0")

    if apply_v11_transforms:
        prebreathing_time = float(np.log1p(prebreathing_time))
        time_at_altitude = float(np.power(time_at_altitude, 1.5))

    numerical = [float(altitude), float(time_at_altitude), float(prebreathing_time)]

    # Ensure exercise level string matches the encoderʼs categories
    matched = next(
        (lvl for lvl in encoder.categories_[0] if lvl.lower() == exercise_level.lower()),
        None,
    )
    if matched is None:
        raise ValueError(
            f"Exercise level '{exercise_level}' not recognised by encoder: {encoder.categories_[0]}"
        )

    categorical = encoder.transform([[matched]]).ravel().tolist()
    full = np.array([numerical + categorical])
    return scaler.transform(full)


def predict_risk_percent(model: Any, features: np.ndarray) -> float:
    """Predict risk as a percentage in [0, 100].

    - Prefer `predict_proba` if available (binary class=1 probability).
    - Else use `predict`. If output appears in [0, 1], scale to percent.
    """

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(features)
        if isinstance(proba, np.ndarray) and proba.ndim == 2 and proba.shape[1] >= 2:
            return float(np.clip(proba[0, 1] * 100.0, 0.0, 100.0))

    pred = float(model.predict(features)[0])
    if 0.0 <= pred <= 1.0:
        pred *= 100.0
    return float(np.clip(pred, 0.0, 100.0))


# -------------------------------------------------------------
# Mechanistic 3RUT-MBe1 helpers
# -------------------------------------------------------------

def _exercise_level_to_i_ex_l_min_wb(exercise_level: str) -> float:
    """Map UI exercise labels to I_ex (L/min whole-body O2 above rest)."""

    key = exercise_level.strip().lower()
    mapping = {"rest": 0.0, "mild": 0.41, "heavy": 0.55}
    if key not in mapping:
        raise ValueError(f"Unsupported exercise level: {exercise_level!r}")
    return float(mapping[key])


def _altitude_ft_to_p_amb_atm(altitude_ft: float) -> float:
    from rut_mbe1_model import altitude_ft_to_p_amb_atm

    return float(altitude_ft_to_p_amb_atm(float(altitude_ft)))


def _build_mechanistic_profile(
    *,
    altitude_ft: float,
    time_at_altitude_min: float,
    prebreathing_time_min: float,
    exercise_level: str,
    dt_min: float,
    breathe_o2_at_altitude: bool,
) -> List[Any]:
    """Build a simple profile for mechanistic mode.

    - Sea-level O2 prebreathe
    - 1-minute decompression ramp discretized into dt-sized segments
    - Constant altitude exposure (exercise applied here)
    """

    from rut_mbe1_model import ProfileSegment

    if dt_min <= 0.0:
        raise ValueError("dt_min must be > 0")
    if altitude_ft < 0.0 or time_at_altitude_min < 0.0 or prebreathing_time_min < 0.0:
        raise ValueError("inputs must be >= 0")

    p_final = _altitude_ft_to_p_amb_atm(altitude_ft)
    if p_final <= 0.0:
        raise ValueError("Altitude results in non-positive ambient pressure")

    i_ex = _exercise_level_to_i_ex_l_min_wb(exercise_level)

    segments: List[Any] = []

    if prebreathing_time_min > 0.0:
        segments.append(
            ProfileSegment(
                duration_min=float(prebreathing_time_min),
                p_amb_atm=1.0,
                fio2=1.0,
                fin2=0.0,
                i_ex_l_min_wb=0.0,
            )
        )

    # Decompression ramp: 1 minute
    ramp_dur = 1.0
    n_steps = max(1, int(math.ceil(ramp_dur / dt_min)))
    step_dt = ramp_dur / n_steps
    fio2_alt = 1.0 if breathe_o2_at_altitude else 0.21
    fin2_alt = 0.0 if breathe_o2_at_altitude else 0.79

    for i in range(n_steps):
        frac = (i + 1) / n_steps
        p_step = 1.0 + (p_final - 1.0) * frac
        segments.append(
            ProfileSegment(
                duration_min=float(step_dt),
                p_amb_atm=float(p_step),
                fio2=float(fio2_alt),
                fin2=float(fin2_alt),
                i_ex_l_min_wb=0.0,
            )
        )

    if time_at_altitude_min > 0.0:
        segments.append(
            ProfileSegment(
                duration_min=float(time_at_altitude_min),
                p_amb_atm=float(p_final),
                fio2=float(fio2_alt),
                fin2=float(fin2_alt),
                i_ex_l_min_wb=float(i_ex),
            )
        )

    return segments


# -------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------
with st.sidebar:
    st.header("Mode")
    mode = st.radio(
        "Select model type",
        options=["ML artefact model", "Mechanistic 3RUT‑MBe1"],
        index=0,
        help="ML artefacts (.joblib) vs mechanistic 3RUT‑MBe1 recursion (NEDU TR 18‑01, Appendix C).",
    )

    if mode == "ML artefact model":
        st.header("Model artefacts")
        model_dir = st.text_input("Artefact directory", value="output")
        if st.button("🔄 Load model"):
            try:
                scaler_obj, encoder_obj, model_obj, meta = load_artifacts(model_dir)
                st.success("Model artefacts loaded successfully")
                st.session_state["artefacts"] = {
                    "scaler": scaler_obj,
                    "encoder": encoder_obj,
                    "model": model_obj,
                    "apply_v11_transforms": bool(meta.get("apply_v11_transforms", False)),
                }
            except Exception as ex:
                st.error(f"Failed to load artefacts: {ex}")

    st.header("Exposure parameters")
    altitude = st.number_input(
        "Altitude (feet)",
        0.0,
        63000.0,
        18000.0,
        step=500.0,
        help="Cabin altitude in feet.",
    )
    time_at_altitude = st.number_input(
        "Time at altitude (minutes)",
        0.0,
        600.0,
        30.0,
        step=5.0,
        help="Duration of exposure at altitude.",
    )
    prebreathing_time = st.number_input(
        "Pre-breathing time (minutes)",
        0.0,
        180.0,
        30.0,
        step=5.0,
        help="O₂ pre-breathe time prior to exposure.",
    )

    if mode == "ML artefact model" and "artefacts" in st.session_state:
        encoder_obj = st.session_state["artefacts"]["encoder"]
        exercise_level = st.selectbox(
            "Exercise level",
            options=list(encoder_obj.categories_[0]),
            index=0,
        )
    else:
        exercise_level = st.selectbox("Exercise level", ["Rest", "Mild", "Heavy"], index=0)

    if mode == "Mechanistic 3RUT‑MBe1":
        st.header("Mechanistic options")
        breathe_o2_at_altitude = st.toggle(
            "Breathe O₂ during altitude exposure",
            value=False,
            help="If enabled, uses FiO₂=1.0 during the altitude segment (and decompression ramp).",
        )
        dt_min = st.select_slider(
            "Simulation time step (minutes)",
            options=[0.5, 0.25, 0.1, 0.05, 0.02, 0.01],
            value=0.05,
            help="Smaller dt improves numerical accuracy at the cost of runtime.",
        )
        st.session_state["mechanistic_opts"] = {
            "breathe_o2_at_altitude": bool(breathe_o2_at_altitude),
            "dt_min": float(dt_min),
        }


# -------------------------------------------------------------
# Main
# -------------------------------------------------------------
if mode == "ML artefact model" and "artefacts" not in st.session_state:
    st.info("Load a trained model from the sidebar to begin.")
    st.stop()

predicted_risk_ml: Optional[float] = None

if mode == "ML artefact model":
    scaler = st.session_state["artefacts"]["scaler"]
    encoder = st.session_state["artefacts"]["encoder"]
    model = st.session_state["artefacts"]["model"]
    apply_v11_transforms = bool(st.session_state["artefacts"].get("apply_v11_transforms", False))

    if apply_v11_transforms:
        st.caption(
            "ML v11 preprocessing enabled: time_at_altitude^1.5 and log1p(pre-breathing time)."
        )

    features = prepare_features(
        altitude,
        time_at_altitude,
        prebreathing_time,
        exercise_level,
        scaler,
        encoder,
        apply_v11_transforms,
    )
    predicted_risk_ml = predict_risk_percent(model, features)
    st.metric("Predicted DCS Risk (%)", f"{predicted_risk_ml:.2f}")
else:
    st.metric("Predicted DCS Risk (%)", "—", help="Run mechanistic simulation in the tabs.")


prediction_tab, sweep_tab, importance_tab, three_d_tab, math_tab = st.tabs(
    [
        "📈 Single Prediction",
        "🧮 Parameter Sweep",
        "📊 Feature Importance",
        "🌐 3D Surface",
        "📐 Model Math",
    ]
)


with prediction_tab:
    st.subheader("Input Summary")
    summary: Dict[str, Any] = {
        "Mode": mode,
        "Altitude (ft)": float(altitude),
        "Time @ Altitude (min)": float(time_at_altitude),
        "Pre-breathing (min)": float(prebreathing_time),
        "Exercise level": str(exercise_level),
    }

    if mode == "ML artefact model":
        summary["Predicted risk (%)"] = float(predicted_risk_ml) if predicted_risk_ml is not None else None
    else:
        opts = st.session_state.get("mechanistic_opts", {})
        summary["dt (min)"] = opts.get("dt_min")
        summary["Breathe O2 at altitude"] = opts.get("breathe_o2_at_altitude")
        try:
            summary["Altitude pressure (atm)"] = _altitude_ft_to_p_amb_atm(float(altitude))
        except Exception:
            summary["Altitude pressure (atm)"] = None

    st.json(summary)

    if mode == "ML artefact model":
        st.success(f"**Predicted DCS risk**: {predicted_risk_ml:.2f}%")
    else:
        st.info("Run the mechanistic model to compute a time-resolved risk curve.")
        col_run, col_note = st.columns([1, 3])
        with col_run:
            run_mech = st.button("Run mechanistic simulation", type="primary")
        with col_note:
            st.caption(
                "Mechanistic mode implements the published 3RUT‑MBe1 recursion (NEDU TR 18‑01, Appendix C)."
            )

        if run_mech:
            from rut_mbe1_model import RutMbe1Model

            opts = st.session_state.get("mechanistic_opts", {})
            dt_used = float(opts.get("dt_min", 0.05))
            breathe_o2 = bool(opts.get("breathe_o2_at_altitude", False))

            mech_segments = _build_mechanistic_profile(
                altitude_ft=float(altitude),
                time_at_altitude_min=float(time_at_altitude),
                prebreathing_time_min=float(prebreathing_time),
                exercise_level=str(exercise_level),
                dt_min=dt_used,
                breathe_o2_at_altitude=breathe_o2,
            )

            model_mech = RutMbe1Model()
            model_mech.initialize_state(p_amb_atm=1.0, fio2=0.21, fin2=0.79, i_ex_l_min_wb=0.0)
            hist = model_mech.run_profile(mech_segments, dt_min=dt_used)
            st.session_state["mech_history"] = hist

            final_p = (hist[-1].p_dcs * 100.0) if hist else float("nan")
            st.metric("Mechanistic P(DCS) at end (%)", f"{final_p:.3f}")

            t = [s.t_min for s in hist]
            p_amb = [s.p_amb_atm for s in hist]
            pt_n2 = [s.pt_n2_atm for s in hist]
            pt_o2 = [s.pt_o2_atm for s in hist]
            n_b = [s.n_b for s in hist]
            hazard = [s.h_per_min for s in hist]
            p_dcs = [s.p_dcs * 100.0 for s in hist]

            fig = make_subplots(
                rows=3,
                cols=2,
                shared_xaxes=True,
                subplot_titles=(
                    "Ambient pressure (atm)",
                    "Cumulative risk P(DCS) (%)",
                    "Tissue N2 tension (atm)",
                    "Tissue O2 tension (atm)",
                    "Bubble number n_b (fractional)",
                    "Instantaneous hazard h(t) (1/min)",
                ),
                vertical_spacing=0.10,
            )
            fig.add_trace(go.Scatter(x=t, y=p_amb, mode="lines", name="P_amb"), row=1, col=1)
            fig.add_trace(go.Scatter(x=t, y=p_dcs, mode="lines", name="P(DCS)%"), row=1, col=2)
            fig.add_trace(go.Scatter(x=t, y=pt_n2, mode="lines", name="p_tN2"), row=2, col=1)
            fig.add_trace(go.Scatter(x=t, y=pt_o2, mode="lines", name="p_tO2"), row=2, col=2)
            fig.add_trace(go.Scatter(x=t, y=n_b, mode="lines", name="n_b"), row=3, col=1)
            fig.add_trace(go.Scatter(x=t, y=hazard, mode="lines", name="h(t)"), row=3, col=2)
            fig.update_layout(
                height=900,
                template="plotly_white",
                legend_orientation="h",
                legend_yanchor="bottom",
                legend_y=1.02,
                legend_x=0,
                margin=dict(l=20, r=20, t=60, b=20),
            )
            fig.update_xaxes(title_text="Time (min)", row=3, col=1)
            fig.update_xaxes(title_text="Time (min)", row=3, col=2)
            st.plotly_chart(fig, use_container_width=True)

            # Export
            csv_lines = [
                "t_min,p_amb_atm,pt_n2_atm,pt_o2_atm,n_b,r_hat,h_per_min,p_dcs_percent"
            ]
            for s in hist:
                csv_lines.append(
                    f"{s.t_min:.6f},{s.p_amb_atm:.9f},{s.pt_n2_atm:.9f},{s.pt_o2_atm:.9f},{s.n_b:.9e},{s.r_hat:.9e},{s.h_per_min:.9e},{(s.p_dcs * 100.0):.9f}"
                )

            st.download_button(
                label="Download mechanistic results (CSV)",
                data="\n".join(csv_lines),
                file_name="mechanistic_3rut_mbe1_results.csv",
                mime="text/csv",
            )
            st.download_button(
                label="Download plot (HTML)",
                data=fig.to_html(include_plotlyjs="cdn"),
                file_name="mechanistic_3rut_mbe1_plot.html",
                mime="text/html",
            )


with sweep_tab:
    st.subheader("Parameter sweep – explore risk sensitivity")

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

    if mode != "ML artefact model" and int(num_points) > 100:
        st.warning("Mechanistic sweeps can be slow; consider ≤100 points.")

    if st.button("Run sweep"):
        var_vals = np.linspace(sweep_range[0], sweep_range[1], int(num_points))
        pred_vals: List[float] = []

        if mode == "ML artefact model":
            for v in var_vals:
                _alt = float(altitude)
                _time = float(time_at_altitude)
                _pre = float(prebreathing_time)
                if param_to_vary == "Altitude":
                    _alt = float(v)
                elif param_to_vary == "Time at altitude":
                    _time = float(v)
                elif param_to_vary == "Pre-breathing time":
                    _pre = float(v)
                f_vec = prepare_features(_alt, _time, _pre, exercise_level, scaler, encoder, apply_v11_transforms)
                pred_vals.append(predict_risk_percent(model, f_vec))
        else:
            from rut_mbe1_model import RutMbe1Model

            opts = st.session_state.get("mechanistic_opts", {})
            dt_used = float(opts.get("dt_min", 0.05))
            breathe_o2 = bool(opts.get("breathe_o2_at_altitude", False))

            for v in var_vals:
                _alt = float(altitude)
                _time = float(time_at_altitude)
                _pre = float(prebreathing_time)
                if param_to_vary == "Altitude":
                    _alt = float(v)
                elif param_to_vary == "Time at altitude":
                    _time = float(v)
                elif param_to_vary == "Pre-breathing time":
                    _pre = float(v)

                mech_segments = _build_mechanistic_profile(
                    altitude_ft=_alt,
                    time_at_altitude_min=_time,
                    prebreathing_time_min=_pre,
                    exercise_level=str(exercise_level),
                    dt_min=dt_used,
                    breathe_o2_at_altitude=breathe_o2,
                )
                model_mech = RutMbe1Model()
                model_mech.initialize_state(p_amb_atm=1.0, fio2=0.21, fin2=0.79, i_ex_l_min_wb=0.0)
                hist_sweep = model_mech.run_profile(mech_segments, dt_min=dt_used)
                pred_vals.append(hist_sweep[-1].p_dcs * 100.0 if hist_sweep else float("nan"))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=var_vals, y=pred_vals, mode="lines", name="Risk (%)"))
        fig.update_layout(
            xaxis_title=param_to_vary,
            yaxis_title="Predicted DCS Risk (%)",
            template="plotly_white",
            height=520,
        )
        st.plotly_chart(fig, use_container_width=True)


with importance_tab:
    st.subheader("Model-reported feature importance")
    if mode != "ML artefact model":
        st.info("Feature importance is only available for ML models in this app.")
    else:
        estimator = model[0] if isinstance(model, (list, tuple)) else model
        if hasattr(estimator, "feature_importances_"):
            importances = estimator.feature_importances_
            feature_names = list(encoder.get_feature_names_out(["exercise_level"]))
            all_features = ["altitude", "time_at_altitude", "prebreathing_time"] + feature_names
            fig_imp = go.Figure([go.Bar(x=importances, y=all_features, orientation="h")])
            fig_imp.update_layout(
                xaxis_title="Importance",
                template="plotly_white",
                height=450,
            )
            st.plotly_chart(fig_imp, use_container_width=True)
        else:
            st.info("Selected model does not provide native feature-importance information.")


with three_d_tab:
    st.subheader("3D risk surface")
    st.caption("Explore predicted risk varying two inputs while holding the others fixed.")

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
        if mode != "ML artefact model" and int(grid_res) > 40:
            st.warning("Mechanistic 3D surfaces can be expensive; consider ≤40 grid resolution.")

        if st.button("Generate 3D surface"):
            gx = int(grid_res)
            x_vals = np.linspace(x_min, x_max, gx)
            y_vals = np.linspace(y_min, y_max, gx)
            z_matrix = np.zeros((gx, gx), dtype=float)

            def assign_vars(x_value: float, y_value: float) -> Tuple[float, float, float]:
                _alt, _time, _pre = float(altitude), float(time_at_altitude), float(prebreathing_time)
                if param_x == "Altitude":
                    _alt = float(x_value)
                elif param_x == "Time at altitude":
                    _time = float(x_value)
                elif param_x == "Pre-breathing time":
                    _pre = float(x_value)

                if param_y == "Altitude":
                    _alt = float(y_value)
                elif param_y == "Time at altitude":
                    _time = float(y_value)
                elif param_y == "Pre-breathing time":
                    _pre = float(y_value)
                return _alt, _time, _pre

            if mode == "ML artefact model":
                for i, xv in enumerate(x_vals):
                    for j, yv in enumerate(y_vals):
                        _alt, _time, _pre = assign_vars(float(xv), float(yv))
                        f_vec = prepare_features(_alt, _time, _pre, exercise_level, scaler, encoder, apply_v11_transforms)
                        z_matrix[j, i] = predict_risk_percent(model, f_vec)
            else:
                from rut_mbe1_model import RutMbe1Model

                opts = st.session_state.get("mechanistic_opts", {})
                dt_used = float(opts.get("dt_min", 0.05))
                breathe_o2 = bool(opts.get("breathe_o2_at_altitude", False))

                for i, xv in enumerate(x_vals):
                    for j, yv in enumerate(y_vals):
                        _alt, _time, _pre = assign_vars(float(xv), float(yv))
                        mech_segments = _build_mechanistic_profile(
                            altitude_ft=_alt,
                            time_at_altitude_min=_time,
                            prebreathing_time_min=_pre,
                            exercise_level=str(exercise_level),
                            dt_min=dt_used,
                            breathe_o2_at_altitude=breathe_o2,
                        )
                        model_mech = RutMbe1Model()
                        model_mech.initialize_state(p_amb_atm=1.0, fio2=0.21, fin2=0.79, i_ex_l_min_wb=0.0)
                        hist_surf = model_mech.run_profile(mech_segments, dt_min=dt_used)
                        z_matrix[j, i] = (hist_surf[-1].p_dcs * 100.0) if hist_surf else float("nan")

            surface_fig = go.Figure(
                data=[
                    go.Surface(
                        x=x_vals,
                        y=y_vals,
                        z=z_matrix,
                        colorscale="Turbo",
                        colorbar=dict(title="Risk (%)"),
                        contours={"z": {"show": True, "usecolormap": True, "project_z": True}},
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
                template="plotly_white",
                margin=dict(l=0, r=0, t=30, b=0),
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
                        colorbar=dict(title="Risk (%)"),
                    )
                ]
            )
            contour_fig.update_layout(
                xaxis_title=param_x,
                yaxis_title=param_y,
                height=550,
                template="plotly_white",
                margin=dict(l=0, r=0, t=30, b=0),
            )
            st.plotly_chart(contour_fig, use_container_width=True)


with math_tab:
    st.subheader("Model math and transformations")
    if mode == "ML artefact model":
        st.markdown(
            """
            **ML mode**

            - Loads a trained estimator and preprocessing artefacts from disk.
            - If v11 artefacts are detected, the app applies the same input transforms used in training:
              - time_at_altitude′ = time_at_altitude^{1.5}
              - prebreathing_time′ = log(1 + prebreathing_time)
            """
        )
    else:
        st.markdown(
            """
            **Mechanistic 3RUT‑MBe1 mode (NEDU TR 18‑01)**

            The mechanistic solver uses the published recursion from Appendix C.
            """
        )
        st.latex(r"P_\infty=P_{H_2O}+p_{tCO_2}\quad (C.1)")
        st.latex(r"P_{ss,n}=\left[\sum_k p_{t_{k,n}}+P_\infty\right]-P_{amb,n}\quad (C.7)")
        st.latex(
            r"h(t)=g\,(V_b-V_{r0})\,(N_b)^{\beta_N}\quad (D.3a)"
        )
