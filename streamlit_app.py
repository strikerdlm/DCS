from __future__ import annotations

import math
import os
import glob
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

from dcs_validation import load_adrac_dataset, validate_ml_surrogate_against_adrac


@dataclass(frozen=True, slots=True)
class ModelValidity:
    """Scientific validity metadata shown in the UI.

    This is strictly a *display* structure. Values are taken from files already
    present in this repository. When a metric is not available in the repo, it
    is reported as "Not available" rather than inferred.
    """

    name: str
    sources: Tuple[str, ...]
    notes_md: str
    metrics: Tuple[Tuple[str, str], ...]


# -------------------------------------------------------------
# Streamlit page configuration + styling
# -------------------------------------------------------------
st.set_page_config(
    page_title="DCS Risk Explorer",
    layout="wide",
    page_icon="🩺",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root {
  --card-bg: rgba(255,255,255,0.75);
  --card-border: rgba(0,0,0,0.08);
}

/* Improve readability + spacing */
.block-container { padding-top: 2.0rem; padding-bottom: 3rem; }

/* Sidebar polish */
section[data-testid="stSidebar"] {
  border-right: 1px solid rgba(0,0,0,0.06);
}

/* Make metric cards a bit more modern */
div[data-testid="stMetric"] {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 14px;
  padding: 14px 16px;
}

/* Subheaders */
h2, h3 { letter-spacing: -0.01em; }

/* Small callout card */
.dcs-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 14px;
  padding: 14px 16px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Decompression Sickness (DCS) Risk Explorer")

st.markdown(
    """
<div class="dcs-card">
  <b>Research UI for exploring DCS risk models.</b><br/>
  This app presents multiple model families that differ in assumptions, inputs, and validation.
  <br/><br/>
  <b>Safety & accuracy disclaimer</b>: This software is for academic/research use only.
  It is <b>not</b> validated for clinical, operational, or personal risk decision-making.
  Do not use it to plan flights, dives, EVAs, or medical care.
</div>
""",
    unsafe_allow_html=True,
)


# -------------------------------------------------------------
# Shared helpers
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


def _safe_read_text(path: str, *, max_bytes: int = 200_000) -> str:
    """Read a text file with a hard byte cap."""

    if max_bytes <= 0:
        raise ValueError("max_bytes must be > 0")
    with open(path, "rb") as f:
        data = f.read(max_bytes + 1)
    if len(data) > max_bytes:
        data = data[:max_bytes]
    return data.decode("utf-8", errors="replace")


def _parse_key_value_metrics(text: str) -> List[Tuple[str, str]]:
    """Parse simple `Key: Value` lines.

    Keeps order and ignores separators.
    """

    out: List[Tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("===") or set(line) <= {"-"}:
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        out.append((k, v))
    return out


def _stable_sigmoid(z: float) -> float:
    """Compute 1/(1+exp(-z)) with overflow safety."""

    if not np.isfinite(z):
        raise ValueError("z must be finite")
    if z >= 0.0:
        ez = math.exp(-z)
        return 1.0 / (1.0 + ez)
    ez = math.exp(z)
    return ez / (1.0 + ez)


@st.cache_data(show_spinner=False, max_entries=4)
def _load_adrac_dataset_cached(*, csv_path: str, max_rows: Optional[int]) -> pd.DataFrame:
    return load_adrac_dataset(csv_path, max_rows=max_rows)


@st.cache_data(show_spinner=True, max_entries=4)
def _run_ml_validation_cached(
    *,
    csv_path: str,
    model_dir: str,
    max_rows: Optional[int],
    expected_features: Tuple[str, ...],
    apply_v11_transforms: bool,
    exercise_filter: Tuple[str, ...],
    altitude_range: Tuple[float, float],
    time_range: Tuple[float, float],
) -> Dict[str, Any]:
    df = _load_adrac_dataset_cached(csv_path=csv_path, max_rows=max_rows).copy()

    if exercise_filter:
        df = df[df["exercise_level"].astype(str).isin(list(exercise_filter))]

    alt_min, alt_max = float(altitude_range[0]), float(altitude_range[1])
    t_min, t_max = float(time_range[0]), float(time_range[1])
    df = df[(df["altitude"] >= alt_min) & (df["altitude"] <= alt_max)]
    df = df[(df["time_at_altitude"] >= t_min) & (df["time_at_altitude"] <= t_max)]

    if df.empty:
        raise ValueError("No rows remain after applying filters")

    scaler_obj, encoder_obj, model_obj, _meta = load_artifacts(model_dir)

    res = validate_ml_surrogate_against_adrac(
        df,
        scaler=scaler_obj,
        encoder=encoder_obj,
        model=model_obj,
        apply_v11_transforms=apply_v11_transforms,
        expected_features=list(expected_features),
    )

    # Keep a compact dataframe for plotting.
    out_df = df.copy()
    out_df["predicted_risk_percent"] = res.y_pred
    out_df["residual_percent"] = res.residual
    out_df["abs_error_percent"] = np.abs(res.residual)

    return {"metrics": res.metrics.as_dict(), "df": out_df}


# -------------------------------------------------------------
# Model validity (from repo artefacts)
# -------------------------------------------------------------

def load_validity_cards() -> Dict[str, ModelValidity]:
    root = os.path.abspath(os.path.dirname(__file__))

    metrics_adrac_path = os.path.join(root, "Model_Rel_Candidate", "Metrics.txt")
    metrics_asem_path = os.path.join(
        root,
        "DCS Python Project_old",
        "BU_2024",
        "model_validation_metrics_20250128_1245.txt",
    )

    adrac_metrics: Tuple[Tuple[str, str], ...] = tuple()
    if os.path.exists(metrics_adrac_path):
        adrac_metrics = tuple(_parse_key_value_metrics(_safe_read_text(metrics_adrac_path)))

    asem_metrics: Tuple[Tuple[str, str], ...] = tuple()
    if os.path.exists(metrics_asem_path):
        asem_metrics = tuple(_parse_key_value_metrics(_safe_read_text(metrics_asem_path)))

    return {
        "ml_surrogate": ModelValidity(
            name="ML surrogate (ADRAC-derived dataset)",
            sources=(
                "Model_Rel_Candidate/README.md",
                "Model_Rel_Candidate/Metrics.txt",
            ),
            notes_md=(
                "- **Model family**: supervised ML regression surrogate trained to reproduce ADRAC outputs (risk %).\n"
                "- **Applicable metrics**: regression metrics (MAE/RMSE/R²).\n"
                "- **Not applicable / not provided**: sensitivity/specificity/PPV/NPV/ROC unless a binary case definition and labeled outcomes are supplied.\n"
                "- **Important**: the surrogate is only valid within the data envelope used to generate `DCS_Risk_DB_2025.csv`/`.xlsx` (avoid extrapolation)."
            ),
            metrics=adrac_metrics
            if adrac_metrics
            else (("Metrics", "Not available in repo artefacts"),),
        ),
        "mechanistic_3rut": ModelValidity(
            name="Mechanistic 3RUT‑MBe1 (time-dependent covariate survival model)",
            sources=(
                "BU_3RUT/3RUT_MBe1/3RUT_Theory.md",
                "rut_mbe1_model.py",
            ),
            notes_md=(
                "- **Model family**: mechanistic bubble-evolution + survival/hazard recursion (NEDU TR 18‑01 Appendix C/D).\n"
                "- **Covariates supported in theory**: pressure, inspired O₂ fraction, inspired inert gas fraction(s), and exercise intensity varying over time.\n"
                "- **Repo includes**: chi-square goodness-of-fit discussions and comparisons vs other models in `3RUT_Theory.md` (e.g., ADRAC/NASA models).\n"
                "- **Not provided as a single table in repo**: sensitivity/specificity/ROC/PPV/NPV; these require curated labeled datasets + decision thresholds."
            ),
            metrics=(
                ("Training data referenced", "2598 man-exposures (as described in theory doc)"),
                ("Fit assessment referenced", "Chi-square goodness-of-fit across groups (see theory doc)"),
                ("Sensitivity/Specificity/ROC", "Not provided in repo"),
            ),
        ),
        "nasa_rm_nm": ModelValidity(
            name="NASA logistic model (ETR-based; RM with age / NM with sex)",
            sources=(
                "NASA_model/conkin-dcs-exercise_2004.md",
                "NASA_model/DCS_NASA.py",
                "NASA_model/Evidence_2024.md",
            ),
            notes_md=(
                "- **Model family**: logistic regression of **P(DCS)** from **ETR** (Exercise Tissue Ratio), with either **age** (RM) or **sex** (NM).\n"
                "- **This UI implements the published equations** from `conkin-dcs-exercise_2004.md` (Eq. 14 and Eq. 15).\n"
                "- **Limitations**: the full NASA models account for multi-interval PB protocols; this UI provides a simplified single-interval PB calculator."  # noqa: E501
            ),
            metrics=(
                ("Dataset size (RM)", "n = 229 exposures (as described in report)"),
                ("Dataset size (NM)", "n = 159 exposures (as described in report)"),
                ("Sensitivity/Specificity/ROC", "Not provided in repo"),
                ("CI95%", "Not provided in repo (report notes CI limitations for some fits)"),
            ),
        ),
        "asem": ModelValidity(
            name="ASEM validation snapshot (legacy BU_2024 artefact)",
            sources=(
                "DCS Python Project_old/BU_2024/model_validation_metrics_20250128_1245.txt",
            ),
            notes_md=(
                "- **What this is**: a legacy text report of regression-style validation metrics (MAE/RMSE/R²) for an ASEM-labelled run.\n"
                "- **How we use it**: displayed verbatim; not assumed to correspond to the currently loaded ML artefacts."
            ),
            metrics=asem_metrics
            if asem_metrics
            else (("Metrics", "Not available in repo artefacts"),),
        ),
    }


VALIDITY = load_validity_cards()


def render_validity(validity: ModelValidity) -> None:
    st.subheader("Scientific validity & limitations")
    st.caption("Displayed from repository artefacts; values are not inferred.")

    with st.expander("Show sources, metrics, and limitations", expanded=True):
        st.markdown("**Sources**")
        for src in validity.sources:
            st.write(f"- `{src}`")

        st.markdown("**Notes**")
        st.markdown(validity.notes_md)

        st.markdown("**Metrics available in this repo**")
        st.dataframe(
            [{"Metric": k, "Value": v} for k, v in validity.metrics],
            use_container_width=True,
            hide_index=True,
        )


# -------------------------------------------------------------
# ML surrogate (artefacts) helpers
# -------------------------------------------------------------

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
        model = (
            model_obj.get("base_model")
            or model_obj.get("model")
            or model_obj.get("models")
            or model_obj
        )
    else:
        model = model_obj

    has_params = bool(glob.glob(os.path.join(model_dir, "model_params_*.joblib")))
    meta = {
        "apply_v11_transforms": has_params,
        "scaler_path": scaler_path,
        "encoder_path": encoder_path,
        "model_path": model_path,
    }
    return scaler, encoder, model, meta


def _infer_expected_feature_names(
    *, scaler: Any, encoder: Any
) -> Optional[List[str]]:
    """Attempt to infer expected feature names for ML artefacts.

    - Prefer `scaler.feature_names_in_` when present.
    - Else fall back to a best-effort constructed schema.

    Returns None if a safe inference is not possible.
    """

    names = getattr(scaler, "feature_names_in_", None)
    if names is not None:
        try:
            return [str(x) for x in list(names)]
        except Exception:
            return None

    # Best-effort fallback for the most common schema in this repo.
    if not hasattr(encoder, "categories_"):
        return None

    try:
        onehot = list(encoder.get_feature_names_out(["exercise_level"]))
    except Exception:
        # Older sklearn encoders
        cats = list(getattr(encoder, "categories_", [["Rest", "Mild", "Heavy"]])[0])
        onehot = [f"exercise_level_{c}" for c in cats]

    base = ["altitude", "time_at_altitude", "prebreathing_time"]
    return base + [str(x) for x in onehot]


def _exercise_onehot_from_expected(
    *, expected_features: Sequence[str], selected_exercise: str
) -> Dict[str, float]:
    out: Dict[str, float] = {}
    selected_norm = selected_exercise.strip().lower()

    # Support both "exercise_level_Rest" and potentially other casing.
    for feat in expected_features:
        if not feat.startswith("exercise_level_"):
            continue
        cat = feat[len("exercise_level_") :].strip().lower()
        out[feat] = 1.0 if cat == selected_norm else 0.0
    return out


def prepare_features_dynamic(
    *,
    input_values: Dict[str, float],
    exercise_level: str,
    scaler: Any,
    encoder: Any,
    apply_v11_transforms: bool,
) -> Tuple[np.ndarray, List[str]]:
    """Build feature vector compatible with the loaded artefacts.

    Returns:
    - scaled 2D array
    - ordered feature names used
    """

    expected = _infer_expected_feature_names(scaler=scaler, encoder=encoder)
    if expected is None:
        raise RuntimeError(
            "Unable to infer expected feature schema for the loaded artefacts. "
            "Provide artefacts produced by the project training scripts (with feature_names_in_) "
            "or update the artefacts to include that metadata."
        )

    # Apply training-time transforms when requested.
    vals = dict(input_values)
    if apply_v11_transforms:
        if "prebreathing_time" in vals:
            vals["prebreathing_time"] = float(np.log1p(vals["prebreathing_time"]))
        if "time_at_altitude" in vals:
            vals["time_at_altitude"] = float(np.power(vals["time_at_altitude"], 1.5))

    # Inject one-hot exercise columns when expected.
    onehot = _exercise_onehot_from_expected(expected_features=expected, selected_exercise=exercise_level)
    vals.update(onehot)

    # Validate and order.
    row: List[float] = []
    for feat in expected:
        if feat not in vals:
            raise ValueError(
                f"Missing required feature '{feat}' for the loaded artefacts. "
                "Use the sidebar inputs to fill all required model variables."
            )
        v = float(vals[feat])
        if not np.isfinite(v):
            raise ValueError(f"Feature '{feat}' must be finite")
        row.append(v)

    X = np.array([row], dtype=float)
    return scaler.transform(X), list(expected)


def predict_risk_percent(model: Any, features: np.ndarray) -> float:
    """Predict risk as a percentage in [0, 100]."""

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(features)
        if isinstance(proba, np.ndarray) and proba.ndim == 2 and proba.shape[1] >= 2:
            return float(np.clip(proba[0, 1] * 100.0, 0.0, 100.0))

    pred = float(model.predict(features)[0])
    if 0.0 <= pred <= 1.0:
        pred *= 100.0
    return float(np.clip(pred, 0.0, 100.0))


# -------------------------------------------------------------
# Mechanistic 3RUT‑MBe1 helpers
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
    prebreathing_exercise_level: str,
    altitude_exercise_level: str,
    dt_min: float,
    breathe_o2_at_altitude: bool,
    prebreath_fio2: float,
    ascent_duration_min: float,
) -> List[Any]:
    """Build a simplified profile for mechanistic mode.

    Implements a common structure discussed in the repo literature:
    - Ground-level O2 prebreathe (FiO2 configurable; default 1.0)
    - Linear decompression ramp from sea level to target altitude pressure
    - Constant altitude exposure

    Notes:
    - The full theory supports arbitrary profile complexity (multiple nodes/stages).
      This UI builder is intentionally constrained and should be treated as a
      convenience input method.
    """

    from rut_mbe1_model import ProfileSegment

    if dt_min <= 0.0:
        raise ValueError("dt_min must be > 0")
    if ascent_duration_min < 0.0:
        raise ValueError("ascent_duration_min must be >= 0")
    if not (0.0 <= prebreath_fio2 <= 1.0):
        raise ValueError("prebreath_fio2 must be in [0, 1]")

    if altitude_ft < 0.0 or time_at_altitude_min < 0.0 or prebreathing_time_min < 0.0:
        raise ValueError("inputs must be >= 0")

    p_final = _altitude_ft_to_p_amb_atm(altitude_ft)
    if p_final <= 0.0:
        raise ValueError("Altitude results in non-positive ambient pressure")

    fio2_alt = 1.0 if breathe_o2_at_altitude else 0.21
    fin2_alt = 0.0 if breathe_o2_at_altitude else 0.79

    i_ex_pre = _exercise_level_to_i_ex_l_min_wb(prebreathing_exercise_level)
    i_ex_alt = _exercise_level_to_i_ex_l_min_wb(altitude_exercise_level)

    segments: List[Any] = []

    if prebreathing_time_min > 0.0:
        segments.append(
            ProfileSegment(
                duration_min=float(prebreathing_time_min),
                p_amb_atm=1.0,
                fio2=float(prebreath_fio2),
                fin2=float(max(0.0, 1.0 - prebreath_fio2)),
                i_ex_l_min_wb=float(i_ex_pre),
            )
        )

    if ascent_duration_min > 0.0:
        n_steps = max(1, int(math.ceil(ascent_duration_min / dt_min)))
        step_dt = ascent_duration_min / n_steps
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
                i_ex_l_min_wb=float(i_ex_alt),
            )
        )

    return segments


# -------------------------------------------------------------
# NASA ETR logistic model helpers (Eq. 14 / Eq. 15)
# -------------------------------------------------------------

LN2 = float(np.log(2.0))
DEFAULT_T_HALF_MIN = 360.0


def nasa_k_from_vo2(*, vo2_ml_kg_min: float, lambda_2: float) -> float:
    """Nitrogen elimination rate constant k (Conkin et al. 2004 style).

    Implements the functional form in `NASA_model/DCS_NASA.py` and discussed in
    `NASA_model/conkin-dcs-exercise_2004.md`.

    Units:
    - vo2_ml_kg_min: mL/kg/min
    - returns: 1/min
    """

    if not np.isfinite(vo2_ml_kg_min) or vo2_ml_kg_min < 0.0:
        raise ValueError("vo2_ml_kg_min must be finite and >= 0")
    if not np.isfinite(lambda_2) or lambda_2 <= 0.0:
        raise ValueError("lambda_2 must be finite and > 0")

    return float((1.0 - math.exp(-lambda_2 * vo2_ml_kg_min)) / 51.937 + (LN2 / DEFAULT_T_HALF_MIN))


def nasa_p1n2_after_pb(
    *, p0_psia: float, pa_psia: float, vo2_ml_kg_min: float, pb_time_min: float, lambda_2: float
) -> float:
    """Compute tissue nitrogen pressure P1N2 after a single PB interval."""

    for name, val in (
        ("p0_psia", p0_psia),
        ("pa_psia", pa_psia),
        ("pb_time_min", pb_time_min),
    ):
        if not np.isfinite(val):
            raise ValueError(f"{name} must be finite")
    if pb_time_min < 0.0:
        raise ValueError("pb_time_min must be >= 0")

    k = nasa_k_from_vo2(vo2_ml_kg_min=vo2_ml_kg_min, lambda_2=lambda_2)
    return float(p0_psia + (pa_psia - p0_psia) * (1.0 - math.exp(-k * pb_time_min)))


def nasa_etr(*, p1n2_psia: float, p2_psia: float) -> float:
    if not np.isfinite(p1n2_psia) or not np.isfinite(p2_psia):
        raise ValueError("pressures must be finite")
    if p2_psia <= 0.0:
        raise ValueError("p2_psia must be > 0")
    return float(p1n2_psia / p2_psia)


def nasa_p_dcs_nm(*, etr_val: float, sex: str) -> float:
    """NASA Model (NM): Eq. 14.

    Eq. 14 in `NASA_model/conkin-dcs-exercise_2004.md`:
      P(DCS) = exp(-25.56 + 12.83*ETR - 1.037*SEX) / (1 + exp(...))

    SEX coding in the report example:
    - male = 1
    - female = 0
    """

    if not np.isfinite(etr_val) or etr_val <= 0.0:
        raise ValueError("etr_val must be finite and > 0")

    s = sex.strip().lower()
    if s not in {"male", "female"}:
        raise ValueError("sex must be 'Male' or 'Female'")
    sex_code = 1.0 if s == "male" else 0.0

    z = -25.56 + 12.83 * float(etr_val) - 1.037 * sex_code
    return float(_stable_sigmoid(z))


def nasa_p_dcs_rm(*, etr_val: float, age_years: float) -> float:
    """Research Model (RM): Eq. 15."""

    if not np.isfinite(etr_val) or etr_val <= 0.0:
        raise ValueError("etr_val must be finite and > 0")
    if not np.isfinite(age_years) or age_years <= 0.0:
        raise ValueError("age_years must be finite and > 0")

    z = -31.71 + 14.55 * float(etr_val) + 0.053 * float(age_years)
    return float(_stable_sigmoid(z))


# -------------------------------------------------------------
# Sidebar: model selection + input controls
# -------------------------------------------------------------

MODEL_OPTIONS = (
    "ML surrogate (loaded artefacts)",
    "Mechanistic 3RUT‑MBe1",
    "NASA ETR logistic (RM/NM)",
)

with st.sidebar:
    st.header("Model")
    model_choice = st.radio(
        "Select model",
        options=list(MODEL_OPTIONS),
        index=0,
        help="Each model supports a different set of inputs. The UI only shows variables that the chosen model uses.",
    )

    st.divider()
    st.header("Inputs")

    # -------------------------
    # ML artefact model inputs
    # -------------------------
    if model_choice == "ML surrogate (loaded artefacts)":
        st.caption("Loads joblib artefacts (scaler + encoder + estimator).")
        model_dir = st.text_input("Artefact directory", value="output")

        if st.button("Load ML artefacts", type="primary"):
            try:
                scaler_obj, encoder_obj, model_obj, meta = load_artifacts(model_dir)
                st.session_state["ml_artefacts"] = {
                    "scaler": scaler_obj,
                    "encoder": encoder_obj,
                    "model": model_obj,
                    "apply_v11_transforms": bool(meta.get("apply_v11_transforms", False)),
                    "meta": meta,
                }
                st.success("Loaded")
            except Exception as ex:
                st.error(f"Failed to load artefacts: {ex}")

        st.subheader("Exposure parameters")
        altitude_ft = st.number_input(
            "Altitude (ft)",
            min_value=0.0,
            max_value=63_000.0,
            value=18_000.0,
            step=500.0,
        )
        time_at_altitude_min = st.number_input(
            "Time at altitude (min)",
            min_value=0.0,
            max_value=600.0,
            value=30.0,
            step=5.0,
        )
        prebreathing_time_min = st.number_input(
            "Pre-breathe time (min)",
            min_value=0.0,
            max_value=240.0,
            value=30.0,
            step=5.0,
            help="Assumed 100% O₂ prebreathe in the training data described in repo docs.",
        )

        if "ml_artefacts" in st.session_state:
            enc = st.session_state["ml_artefacts"]["encoder"]
            try:
                exercise_options = list(enc.categories_[0])
            except Exception:
                exercise_options = ["Rest", "Mild", "Heavy"]
        else:
            exercise_options = ["Rest", "Mild", "Heavy"]

        exercise_level = st.selectbox("Exercise level", options=exercise_options, index=0)

        # Additional variables: only when artefacts explicitly request them.
        extra_numeric: Dict[str, float] = {}
        if "ml_artefacts" in st.session_state:
            scaler_obj = st.session_state["ml_artefacts"]["scaler"]
            encoder_obj = st.session_state["ml_artefacts"]["encoder"]
            expected = _infer_expected_feature_names(scaler=scaler_obj, encoder=encoder_obj)

            known = {
                "altitude",
                "time_at_altitude",
                "prebreathing_time",
            }
            if expected is not None:
                additional = [
                    f
                    for f in expected
                    if (f not in known) and (not f.startswith("exercise_level_"))
                ]

                if additional:
                    with st.expander("Additional model variables (auto-detected)", expanded=False):
                        st.caption(
                            "These inputs appear only when the loaded artefacts declare extra expected features. "
                            "If your model was trained with age/sex/etc., they will show here."
                        )
                        for feat in additional:
                            default_val = 0.0
                            if feat.lower() in {"age", "age_years"}:
                                default_val = 35.0
                            extra_numeric[feat] = float(
                                st.number_input(
                                    f"{feat}",
                                    value=float(default_val),
                                    step=1.0 if default_val != 0.0 else 0.1,
                                )
                            )

        st.session_state["ml_inputs"] = {
            "altitude": float(altitude_ft),
            "time_at_altitude": float(time_at_altitude_min),
            "prebreathing_time": float(prebreathing_time_min),
            "exercise_level": str(exercise_level),
            "extra": extra_numeric,
        }

    # -------------------------
    # Mechanistic 3RUT‑MBe1
    # -------------------------
    elif model_choice == "Mechanistic 3RUT‑MBe1":
        st.caption("Published recursion (Appendix C/D) with time-varying covariates.")

        altitude_ft = st.number_input(
            "Altitude (ft)",
            min_value=0.0,
            max_value=63_000.0,
            value=30_000.0,
            step=500.0,
        )
        time_at_altitude_min = st.number_input(
            "Time at altitude (min)",
            min_value=0.0,
            max_value=600.0,
            value=240.0,
            step=10.0,
        )
        prebreathing_time_min = st.number_input(
            "Pre-breathe time (min)",
            min_value=0.0,
            max_value=240.0,
            value=75.0,
            step=5.0,
        )

        altitude_exercise_level = st.selectbox(
            "Exercise level at altitude",
            options=["Rest", "Mild", "Heavy"],
            index=0,
        )

        with st.expander("Advanced profile options", expanded=False):
            prebreathing_exercise_level = st.selectbox(
                "Exercise level during prebreathe",
                options=["Rest", "Mild", "Heavy"],
                index=0,
                help="The 3RUT theory supports exercise during prebreathe; ADRAC does not.",
            )
            prebreath_fio2 = st.slider(
                "Prebreathe FiO₂",
                min_value=0.21,
                max_value=1.00,
                value=1.00,
                step=0.01,
                help="Default 1.00 (100% O₂).",
            )
            breathe_o2_at_altitude = st.toggle(
                "Breathe O₂ during altitude exposure",
                value=False,
                help="If enabled, uses FiO₂=1.0 during ascent and altitude segments.",
            )
            ascent_duration_min = st.number_input(
                "Ascent/decompression duration (min)",
                min_value=0.0,
                max_value=60.0,
                value=30.0,
                step=1.0,
                help="Used to discretize a linear pressure ramp.",
            )
            dt_min = st.select_slider(
                "Simulation time step dt (min)",
                options=[0.5, 0.25, 0.1, 0.05, 0.02, 0.01],
                value=0.05,
            )

        st.session_state["mech_inputs"] = {
            "altitude_ft": float(altitude_ft),
            "time_at_altitude_min": float(time_at_altitude_min),
            "prebreathing_time_min": float(prebreathing_time_min),
            "prebreathing_exercise_level": str(prebreathing_exercise_level),
            "altitude_exercise_level": str(altitude_exercise_level),
            "prebreath_fio2": float(prebreath_fio2),
            "breathe_o2_at_altitude": bool(breathe_o2_at_altitude),
            "ascent_duration_min": float(ascent_duration_min),
            "dt_min": float(dt_min),
        }

    # -------------------------
    # NASA ETR logistic
    # -------------------------
    else:
        st.caption("Implements Eq. 14 (NM) and Eq. 15 (RM) from the NASA report.")

        nasa_variant = st.radio(
            "Variant",
            options=["NM (ETR + sex)", "RM (ETR + age)"],
            index=0,
        )

        # Single-interval PB inputs
        st.subheader("Prebreathe (single-interval simplified)")
        p0_psia = st.number_input(
            "Initial tissue ppN₂ P0 (psia)",
            min_value=0.0,
            max_value=20.0,
            value=8.0,
            step=0.1,
            help="Report example uses 8.0 psia.",
        )
        pa_psia = st.number_input(
            "Ambient ppN₂ during PB Pa (psia)",
            min_value=0.0,
            max_value=20.0,
            value=0.0,
            step=0.1,
            help="100% O₂ PB implies Pa≈0 psia for N₂.",
        )
        pb_time_min = st.number_input(
            "PB duration (min)",
            min_value=0.0,
            max_value=240.0,
            value=90.0,
            step=5.0,
        )
        vo2_ml_kg_min = st.number_input(
            "VO₂ during PB (mL/kg/min)",
            min_value=0.0,
            max_value=120.0,
            value=25.0,
            step=0.5,
            help="For RM/NM, the report models exercise/rest intervals via VO₂. This UI uses one interval.",
        )

        st.subheader("Exposure")
        p2_psia = st.number_input(
            "Ambient pressure after depressurization P2 (psia)",
            min_value=1.0,
            max_value=14.7,
            value=4.3,
            step=0.1,
            help="Report focuses on depressurization to 4.3 psia.",
        )

        with st.expander("Model parameters", expanded=False):
            default_lambda = 0.030 if nasa_variant.startswith("NM") else 0.025
            lambda_2 = st.number_input(
                "λ₂ (lambda)",
                min_value=0.0001,
                max_value=0.2000,
                value=float(default_lambda),
                step=0.0005,
                help="Report examples: NM λ₂=0.030, RM λ₂=0.025.",
                format="%.4f",
            )

        sex = st.selectbox("Sex", options=["Male", "Female"], index=0)
        age_years = st.number_input(
            "Age (years)",
            min_value=1.0,
            max_value=100.0,
            value=35.0,
            step=1.0,
        )

        st.session_state["nasa_inputs"] = {
            "variant": str(nasa_variant),
            "p0_psia": float(p0_psia),
            "pa_psia": float(pa_psia),
            "pb_time_min": float(pb_time_min),
            "vo2_ml_kg_min": float(vo2_ml_kg_min),
            "lambda_2": float(lambda_2),
            "p2_psia": float(p2_psia),
            "sex": str(sex),
            "age_years": float(age_years),
        }


# -------------------------------------------------------------
# Main panel: model execution
# -------------------------------------------------------------

predicted_risk_percent: Optional[float] = None

if model_choice == "ML surrogate (loaded artefacts)":
    st.header("ML surrogate prediction")

    if "ml_artefacts" not in st.session_state:
        st.info("Load ML artefacts from the sidebar to begin.")
        render_validity(VALIDITY["ml_surrogate"])
        st.stop()

    art = st.session_state["ml_artefacts"]
    ml_in = st.session_state.get("ml_inputs", {})

    meta = art.get("meta", {})
    if bool(art.get("apply_v11_transforms", False)):
        st.caption("Detected v11 preprocessing: time_at_altitude^1.5 and log1p(pre-breathing time).")

    input_values = {
        "altitude": float(ml_in.get("altitude", 0.0)),
        "time_at_altitude": float(ml_in.get("time_at_altitude", 0.0)),
        "prebreathing_time": float(ml_in.get("prebreathing_time", 0.0)),
    }
    extra = ml_in.get("extra", {})
    if isinstance(extra, dict):
        for k, v in extra.items():
            input_values[str(k)] = float(v)

    try:
        X_scaled, used_features = prepare_features_dynamic(
            input_values=input_values,
            exercise_level=str(ml_in.get("exercise_level", "Rest")),
            scaler=art["scaler"],
            encoder=art["encoder"],
            apply_v11_transforms=bool(art.get("apply_v11_transforms", False)),
        )
        predicted_risk_percent = predict_risk_percent(art["model"], X_scaled)
    except Exception as ex:
        st.error(f"Unable to run prediction: {ex}")
        render_validity(VALIDITY["ml_surrogate"])
        st.stop()

    st.metric("Predicted DCS risk (%)", f"{predicted_risk_percent:.2f}")

    with st.expander("Show input vector used", expanded=False):
        st.write("**Artefacts**")
        st.write(f"- scaler: `{meta.get('scaler_path', '')}`")
        st.write(f"- encoder: `{meta.get('encoder_path', '')}`")
        st.write(f"- model: `{meta.get('model_path', '')}`")

        st.write("**Features (ordered)**")
        st.dataframe(
            [{"feature": f, "value": float(input_values.get(f, float('nan')))} for f in used_features],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Validation against ADRAC-derived reference dataset")
    st.caption(
        "Validates the loaded ML artefacts by comparing predictions against "
        "`Model_Rel_Candidate/DCS_Risk_DB_2025.csv` (ADRAC-derived risk %)."
    )

    # Validation is only meaningful when the artefacts match the ADRAC schema.
    adrac_ok_features = {"altitude", "time_at_altitude", "prebreathing_time"}
    extra_non_onehot = [
        f for f in used_features if (f not in adrac_ok_features) and (not f.startswith("exercise_level_"))
    ]

    if extra_non_onehot:
        st.info(
            "Validation is disabled for these artefacts because they require additional features "
            f"not present in the ADRAC dataset: {extra_non_onehot}"
        )
    else:
        with st.expander("Run validation (interactive plots)", expanded=False):
            col_v1, col_v2, col_v3 = st.columns(3)
            with col_v1:
                max_rows = st.selectbox(
                    "Rows to load (performance)",
                    options=[None, 2000, 5000, 12000],
                    index=0,
                    help="Use a smaller value for faster plotting; None loads the full CSV.",
                )
            with col_v2:
                exercise_filter = st.multiselect(
                    "Exercise filter",
                    options=["Rest", "Mild", "Heavy"],
                    default=["Rest", "Mild", "Heavy"],
                )
            with col_v3:
                top_n = st.selectbox("Show worst cases", options=[10, 25, 50], index=0)

            alt_min, alt_max = st.slider(
                "Altitude filter (ft)",
                min_value=0.0,
                max_value=63_000.0,
                value=(0.0, 63_000.0),
                step=500.0,
            )
            t_min, t_max = st.slider(
                "Time-at-altitude filter (min)",
                min_value=0.0,
                max_value=600.0,
                value=(0.0, 600.0),
                step=10.0,
            )

            run_val = st.button("Run ADRAC validation", type="primary")
            if run_val:
                try:
                    expected_tuple = tuple(str(x) for x in used_features)
                    out = _run_ml_validation_cached(
                        csv_path=os.path.join(
                            os.path.abspath(os.path.dirname(__file__)),
                            "Model_Rel_Candidate",
                            "DCS_Risk_DB_2025.csv",
                        ),
                        model_dir=str(model_dir),
                        max_rows=max_rows if isinstance(max_rows, int) else None,
                        expected_features=expected_tuple,
                        apply_v11_transforms=bool(art.get("apply_v11_transforms", False)),
                        exercise_filter=tuple(str(x) for x in exercise_filter),
                        altitude_range=(float(alt_min), float(alt_max)),
                        time_range=(float(t_min), float(t_max)),
                    )
                except Exception as ex:
                    st.error(f"Validation failed: {ex}")
                else:
                    dfv = out["df"]
                    m = out["metrics"]

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("R²", f"{float(m['r2']):.4f}")
                    c2.metric("MAE (pp)", f"{float(m['mae']):.3f}")
                    c3.metric("RMSE (pp)", f"{float(m['rmse']):.3f}")
                    c4.metric("Rows", f"{int(dfv.shape[0])}")

                    tab1, tab2, tab3, tab4 = st.tabs(
                        ["Predicted vs reference", "Residuals", "Error heatmap", "Worst cases"]
                    )

                    with tab1:
                        fig_sc = px.scatter(
                            dfv,
                            x="risk_of_decompression_sickness",
                            y="predicted_risk_percent",
                            color="exercise_level",
                            hover_data=["altitude", "time_at_altitude", "prebreathing_time", "abs_error_percent"],
                            render_mode="webgl",
                            opacity=0.65,
                            labels={
                                "risk_of_decompression_sickness": "ADRAC reference risk (%)",
                                "predicted_risk_percent": "ML predicted risk (%)",
                            },
                        )
                        lo = float(np.nanmin(dfv[["risk_of_decompression_sickness", "predicted_risk_percent"]].to_numpy()))
                        hi = float(np.nanmax(dfv[["risk_of_decompression_sickness", "predicted_risk_percent"]].to_numpy()))
                        fig_sc.add_trace(
                            go.Scatter(
                                x=[lo, hi],
                                y=[lo, hi],
                                mode="lines",
                                name="y=x",
                                line=dict(color="black", width=2, dash="dash"),
                            )
                        )
                        fig_sc.update_layout(template="plotly_white", height=650, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig_sc, use_container_width=True)

                    with tab2:
                        fig_hist = px.histogram(
                            dfv,
                            x="residual_percent",
                            nbins=60,
                            color="exercise_level",
                            opacity=0.7,
                            barmode="overlay",
                            labels={"residual_percent": "Residual (pred - reference) percentage-points"},
                        )
                        fig_hist.update_layout(template="plotly_white", height=420, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig_hist, use_container_width=True)

                        fig_res = px.scatter(
                            dfv,
                            x="time_at_altitude",
                            y="residual_percent",
                            color="exercise_level",
                            render_mode="webgl",
                            opacity=0.6,
                            hover_data=["altitude", "prebreathing_time", "risk_of_decompression_sickness", "predicted_risk_percent"],
                            labels={
                                "time_at_altitude": "Time at altitude (min)",
                                "residual_percent": "Residual (pp)",
                            },
                        )
                        fig_res.update_layout(template="plotly_white", height=520, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig_res, use_container_width=True)

                    with tab3:
                        # Bin to fixed grids (bounded, deterministic).
                        alt_min = float(dfv["altitude"].min())
                        alt_max = float(dfv["altitude"].max())
                        time_min = float(dfv["time_at_altitude"].min())
                        time_max = float(dfv["time_at_altitude"].max())

                        # Handle uniform values: ensure bins are monotonically increasing.
                        # Add small epsilon if range is zero to avoid pd.cut ValueError.
                        if alt_max <= alt_min:
                            alt_max = alt_min + 1e-6
                        if time_max <= time_min:
                            time_max = time_min + 1e-6

                        alt_bins = np.linspace(alt_min, alt_max, 13)
                        time_bins = np.linspace(time_min, time_max, 13)

                        binned = dfv.copy()
                        binned["alt_bin"] = pd.cut(binned["altitude"], bins=alt_bins, include_lowest=True)
                        binned["time_bin"] = pd.cut(binned["time_at_altitude"], bins=time_bins, include_lowest=True)
                        pivot = (
                            binned.groupby(["alt_bin", "time_bin"], observed=True)["abs_error_percent"]
                            .mean()
                            .reset_index()
                            .pivot(index="alt_bin", columns="time_bin", values="abs_error_percent")
                        )
                        # Convert Interval labels to short strings for nice axes.
                        y_labels = [str(i) for i in list(pivot.index)]
                        x_labels = [str(i) for i in list(pivot.columns)]
                        z = pivot.to_numpy(dtype=float)

                        fig_hm = go.Figure(
                            data=go.Heatmap(
                                z=z,
                                x=x_labels,
                                y=y_labels,
                                colorscale="Viridis",
                                colorbar=dict(title="Mean |error| (pp)"),
                                zmin=float(np.nanmin(z)),
                                zmax=float(np.nanmax(z)),
                            )
                        )
                        fig_hm.update_layout(
                            template="plotly_white",
                            height=650,
                            margin=dict(l=20, r=20, t=40, b=20),
                            xaxis_title="Time-at-altitude bin (min)",
                            yaxis_title="Altitude bin (ft)",
                        )
                        st.plotly_chart(fig_hm, use_container_width=True)

                    with tab4:
                        worst = (
                            dfv.sort_values("abs_error_percent", ascending=False)
                            .head(int(top_n))
                            .loc[
                                :,
                                [
                                    "altitude",
                                    "time_at_altitude",
                                    "prebreathing_time",
                                    "exercise_level",
                                    "risk_of_decompression_sickness",
                                    "predicted_risk_percent",
                                    "residual_percent",
                                    "abs_error_percent",
                                ],
                            ]
                        )
                        st.dataframe(worst, use_container_width=True, hide_index=True)

    render_validity(VALIDITY["ml_surrogate"])


elif model_choice == "Mechanistic 3RUT‑MBe1":
    st.header("Mechanistic 3RUT‑MBe1 simulation")

    mech = st.session_state.get("mech_inputs", {})
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Altitude (ft)", f"{float(mech.get('altitude_ft', 0.0)):.0f}")
    with col_b:
        st.metric("Time @ altitude (min)", f"{float(mech.get('time_at_altitude_min', 0.0)):.0f}")
    with col_c:
        try:
            p_amb = _altitude_ft_to_p_amb_atm(float(mech.get("altitude_ft", 0.0)))
            st.metric("Target ambient pressure (atm)", f"{p_amb:.4f}")
        except Exception:
            st.metric("Target ambient pressure (atm)", "—")

    run_mech = st.button("Run simulation", type="primary")

    if run_mech:
        from rut_mbe1_model import RutMbe1Model

        try:
            segments = _build_mechanistic_profile(
                altitude_ft=float(mech.get("altitude_ft", 0.0)),
                time_at_altitude_min=float(mech.get("time_at_altitude_min", 0.0)),
                prebreathing_time_min=float(mech.get("prebreathing_time_min", 0.0)),
                prebreathing_exercise_level=str(mech.get("prebreathing_exercise_level", "Rest")),
                altitude_exercise_level=str(mech.get("altitude_exercise_level", "Rest")),
                dt_min=float(mech.get("dt_min", 0.05)),
                breathe_o2_at_altitude=bool(mech.get("breathe_o2_at_altitude", False)),
                prebreath_fio2=float(mech.get("prebreath_fio2", 1.0)),
                ascent_duration_min=float(mech.get("ascent_duration_min", 30.0)),
            )

            model_mech = RutMbe1Model()
            model_mech.initialize_state(p_amb_atm=1.0, fio2=0.21, fin2=0.79, i_ex_l_min_wb=0.0)
            hist = model_mech.run_profile(segments, dt_min=float(mech.get("dt_min", 0.05)))

            st.session_state["mech_history"] = hist

            final_p = (hist[-1].p_dcs * 100.0) if hist else float("nan")
            st.metric("Mechanistic P(DCS) at end (%)", f"{final_p:.3f}")

            # Plot
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
                label="Download results (CSV)",
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
        except Exception as ex:
            st.error(f"Mechanistic simulation failed: {ex}")

    render_validity(VALIDITY["mechanistic_3rut"])


else:
    st.header("NASA ETR logistic calculator")

    nasa_in = st.session_state.get("nasa_inputs", {})

    try:
        p1n2 = nasa_p1n2_after_pb(
            p0_psia=float(nasa_in.get("p0_psia", 8.0)),
            pa_psia=float(nasa_in.get("pa_psia", 0.0)),
            vo2_ml_kg_min=float(nasa_in.get("vo2_ml_kg_min", 25.0)),
            pb_time_min=float(nasa_in.get("pb_time_min", 90.0)),
            lambda_2=float(nasa_in.get("lambda_2", 0.030)),
        )
        etr_val = nasa_etr(p1n2_psia=p1n2, p2_psia=float(nasa_in.get("p2_psia", 4.3)))

        variant = str(nasa_in.get("variant", "NM (ETR + sex)"))
        if variant.startswith("NM"):
            p = nasa_p_dcs_nm(etr_val=etr_val, sex=str(nasa_in.get("sex", "Male")))
            predicted_risk_percent = p * 100.0
        else:
            p = nasa_p_dcs_rm(etr_val=etr_val, age_years=float(nasa_in.get("age_years", 35.0)))
            predicted_risk_percent = p * 100.0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("P1N2 after PB (psia)", f"{p1n2:.3f}")
        with col2:
            st.metric("ETR = P1N2 / P2", f"{etr_val:.3f}")
        with col3:
            st.metric("Predicted P(DCS) (%)", f"{predicted_risk_percent:.2f}")

        with st.expander("Show equation used", expanded=False):
            if variant.startswith("NM"):
                st.markdown(
                    r"""
**NM (Eq. 14)** from `NASA_model/conkin-dcs-exercise_2004.md`:

\(P(DCS)=\frac{\exp(-25.56 + 12.83\cdot ETR - 1.037\cdot SEX)}{1+\exp(-25.56 + 12.83\cdot ETR - 1.037\cdot SEX)}\)

Where the report uses **SEX = 1 for male, 0 for female**.
"""
                )
            else:
                st.markdown(
                    r"""
**RM (Eq. 15)** from `NASA_model/conkin-dcs-exercise_2004.md`:

\(P(DCS)=\frac{\exp(-31.71 + 14.55\cdot ETR + 0.053\cdot AGE)}{1+\exp(-31.71 + 14.55\cdot ETR + 0.053\cdot AGE)}\)
"""
                )

    except Exception as ex:
        st.error(f"NASA calculator failed: {ex}")

    render_validity(VALIDITY["nasa_rm_nm"])

    with st.expander("Legacy validation snapshot (ASEM)", expanded=False):
        render_validity(VALIDITY["asem"])