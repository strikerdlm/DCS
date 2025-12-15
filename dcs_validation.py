from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


@dataclass(frozen=True, slots=True)
class RegressionMetrics:
    """Regression metrics for risk (%) predictions."""

    r2: float
    mae: float
    rmse: float
    mse: float

    def as_dict(self) -> Dict[str, float]:
        return {"r2": self.r2, "mae": self.mae, "rmse": self.rmse, "mse": self.mse}


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Validation outputs for UI consumption."""

    y_true: np.ndarray
    y_pred: np.ndarray
    residual: np.ndarray
    metrics: RegressionMetrics


ADRAC_DATASET_COLUMNS: Tuple[str, ...] = (
    "altitude",
    "prebreathing_time",
    "exercise_level",
    "time_at_altitude",
    "risk_of_decompression_sickness",
)


def load_adrac_dataset(
    csv_path: str,
    *,
    max_rows: Optional[int] = None,
    required_columns: Sequence[str] = ADRAC_DATASET_COLUMNS,
) -> pd.DataFrame:
    """Load the ADRAC-derived dataset CSV with basic schema validation.

    Args:
        csv_path: Path to `DCS_Risk_DB_2025.csv`.
        max_rows: Optional maximum number of rows to load (for fast UI preview).
        required_columns: Columns that must exist in the file.

    Returns:
        A DataFrame with at least the required columns.

    Raises:
        ValueError: If schema is missing required columns or max_rows is invalid.
    """
    if max_rows is not None and max_rows <= 0:
        raise ValueError("max_rows must be > 0 when provided")

    df = pd.read_csv(csv_path, nrows=max_rows)
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"ADRAC dataset missing required columns: {missing}")

    # Basic type coercion (fail closed for non-finite numeric values).
    for col in ("altitude", "prebreathing_time", "time_at_altitude", "risk_of_decompression_sickness"):
        df[col] = pd.to_numeric(df[col], errors="raise")

    if not np.isfinite(df["risk_of_decompression_sickness"].to_numpy(dtype=float)).all():
        raise ValueError("risk_of_decompression_sickness contains non-finite values")

    if (df["risk_of_decompression_sickness"] < 0).any() or (df["risk_of_decompression_sickness"] > 100).any():
        raise ValueError("risk_of_decompression_sickness must be in [0, 100]")

    return df


def compute_regression_metrics(*, y_true: np.ndarray, y_pred: np.ndarray) -> RegressionMetrics:
    """Compute common regression metrics for risk (%) predictions."""
    if y_true.ndim != 1 or y_pred.ndim != 1:
        raise ValueError("y_true and y_pred must be 1D arrays")
    if y_true.shape[0] != y_pred.shape[0]:
        raise ValueError("y_true and y_pred must have same length")
    if y_true.size == 0:
        raise ValueError("y_true/y_pred must be non-empty")
    if not np.isfinite(y_true).all() or not np.isfinite(y_pred).all():
        raise ValueError("y_true/y_pred must be finite")

    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    return RegressionMetrics(r2=r2, mae=mae, rmse=rmse, mse=mse)


def _apply_v11_transforms_inplace(df: pd.DataFrame) -> None:
    """Apply v11 training-time transforms in-place."""
    df["prebreathing_time"] = np.log1p(df["prebreathing_time"].astype(float))
    df["time_at_altitude"] = np.power(df["time_at_altitude"].astype(float), 1.5)


def build_feature_frame_for_adrac(
    df: pd.DataFrame,
    *,
    encoder: Any,
    apply_v11_transforms: bool,
    expected_features: Sequence[str],
) -> pd.DataFrame:
    """Build a feature DataFrame that matches the trained artefact feature order.

    This assumes the ADRAC CSV schema (altitude, time_at_altitude, prebreathing_time, exercise_level)
    and creates one-hot columns to match `expected_features`.
    """
    if not expected_features:
        raise ValueError("expected_features must be non-empty")

    for col in ("altitude", "time_at_altitude", "prebreathing_time", "exercise_level"):
        if col not in df.columns:
            raise ValueError(f"Missing required column {col!r} in input df")

    work = df[["altitude", "time_at_altitude", "prebreathing_time", "exercise_level"]].copy()
    if apply_v11_transforms:
        _apply_v11_transforms_inplace(work)

    # Exercise encoding: prefer the encoder's learned categories.
    if not hasattr(encoder, "categories_"):
        raise ValueError("encoder must provide categories_ for exercise_level one-hot")

    categories = [str(x) for x in list(encoder.categories_[0])]
    if not categories:
        raise ValueError("encoder.categories_[0] is empty")

    # One-hot in a deterministic order aligned with encoder categories.
    for cat in categories:
        col = f"exercise_level_{cat}"
        work[col] = (work["exercise_level"].astype(str) == cat).astype(float)

    # Assemble to expected order, fail if missing.
    missing = [c for c in expected_features if c not in work.columns]
    if missing:
        raise ValueError(
            "Unable to build full feature frame for loaded artefacts; "
            f"missing expected feature(s): {missing}"
        )

    X = work.reindex(columns=list(expected_features)).astype(float)
    if not np.isfinite(X.to_numpy(dtype=float)).all():
        raise ValueError("Non-finite values produced in feature frame")
    return X


def predict_ml_risk_percent_vectorized(*, model: Any, X_scaled: np.ndarray) -> np.ndarray:
    """Vectorized prediction for risk (%) in [0, 100]."""
    if X_scaled.ndim != 2:
        raise ValueError("X_scaled must be a 2D array")
    if X_scaled.shape[0] == 0:
        raise ValueError("X_scaled must have at least 1 row")

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_scaled)
        if isinstance(proba, np.ndarray) and proba.ndim == 2 and proba.shape[1] >= 2:
            out = np.clip(proba[:, 1].astype(float) * 100.0, 0.0, 100.0)
            return out

    pred = np.asarray(model.predict(X_scaled), dtype=float).reshape(-1)
    # If model returns [0,1], interpret as probability and map to percent.
    if float(np.nanmin(pred)) >= 0.0 and float(np.nanmax(pred)) <= 1.0:
        pred = pred * 100.0
    return np.clip(pred, 0.0, 100.0)


def validate_ml_surrogate_against_adrac(
    df: pd.DataFrame,
    *,
    scaler: Any,
    encoder: Any,
    model: Any,
    apply_v11_transforms: bool,
    expected_features: Sequence[str],
) -> ValidationResult:
    """Validate an ML surrogate against ADRAC-derived reference risk (%)."""
    if "risk_of_decompression_sickness" not in df.columns:
        raise ValueError("df must include 'risk_of_decompression_sickness'")

    y_true = df["risk_of_decompression_sickness"].to_numpy(dtype=float)
    if y_true.ndim != 1 or y_true.size == 0:
        raise ValueError("y_true must be non-empty 1D")

    X = build_feature_frame_for_adrac(
        df,
        encoder=encoder,
        apply_v11_transforms=apply_v11_transforms,
        expected_features=expected_features,
    )
    X_scaled = scaler.transform(X.to_numpy(dtype=float))
    y_pred = predict_ml_risk_percent_vectorized(model=model, X_scaled=X_scaled)

    residual = y_pred - y_true
    metrics = compute_regression_metrics(y_true=y_true, y_pred=y_pred)
    return ValidationResult(y_true=y_true, y_pred=y_pred, residual=residual, metrics=metrics)

