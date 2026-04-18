"""TinyDCS surrogate: LightGBM regressor on logit(P(DCS)) with split-conformal
prediction intervals and a simple Mahalanobis OOD detector.

Design
------
- Target transform: the mechanistic 3RUT-MBe1 output is a probability. We
  model it on the **logit scale** so predictions can't fall outside [0, 1] after
  the sigmoid, and residuals are roughly homoscedastic across the 0–1 range.
- Split conformal on the logit scale: residuals in logit space → fixed-width
  intervals that translate back to heteroscedastic intervals in probability
  space via the sigmoid. This is finite-sample distribution-free.
- OOD: Mahalanobis distance to the training-feature mean. Threshold is set to
  the empirical 99th percentile on the training set.

The surrogate object is a single self-contained joblib — no external files —
so it round-trips to disk without accessory artifacts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import joblib
import numpy as np
import pandas as pd

try:
    import lightgbm as lgb
except ImportError as exc:  # pragma: no cover
    raise ImportError("lightgbm is required for tinydcs.surrogate") from exc


_EPS = 1e-6


def _logit(p: np.ndarray) -> np.ndarray:
    q = np.clip(p.astype(float), _EPS, 1.0 - _EPS)
    return np.log(q / (1.0 - q))


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


@dataclass(slots=True)
class OODDetector:
    """Mahalanobis distance in feature space; abstain above ``threshold``."""

    mean: np.ndarray
    inv_cov: np.ndarray
    threshold: float

    def distance(self, X: np.ndarray) -> np.ndarray:
        d = X - self.mean
        return np.sqrt(np.einsum("ij,jk,ik->i", d, self.inv_cov, d))

    def is_in_envelope(self, X: np.ndarray) -> np.ndarray:
        return self.distance(X) <= self.threshold


def fit_ood(X: np.ndarray, q: float = 0.99) -> OODDetector:
    """Fit an OOD detector that abstains on the top-(1-q) training fraction.

    Uses a Ledoit–Wolf-style 1e-3 shrinkage for numerical stability when
    features are collinear.
    """
    mean = X.mean(axis=0)
    cov = np.cov(X, rowvar=False)
    cov = cov + 1e-3 * np.trace(cov) / max(cov.shape[0], 1) * np.eye(cov.shape[0])
    inv_cov = np.linalg.pinv(cov)
    # Training distances
    d = np.sqrt(np.einsum("ij,jk,ik->i", X - mean, inv_cov, X - mean))
    threshold = float(np.quantile(d, q))
    return OODDetector(mean=mean, inv_cov=inv_cov, threshold=threshold)


@dataclass(slots=True)
class ConformalCalibration:
    """Split-conformal residual quantile on the logit scale."""

    q: float
    confidence: float


def fit_conformal(logit_residuals: np.ndarray, confidence: float = 0.95) -> ConformalCalibration:
    resid = np.abs(np.asarray(logit_residuals, dtype=float).ravel())
    n = int(resid.size)
    if n < 20:
        raise ValueError("at least 20 calibration residuals are required")
    alpha = 1.0 - float(confidence)
    k = int(np.ceil((n + 1) * (1.0 - alpha)))
    k = max(1, min(k, n))
    q = float(np.partition(resid, k - 1)[k - 1])
    return ConformalCalibration(q=q, confidence=float(confidence))


@dataclass(slots=True)
class TrainConfig:
    n_estimators: int = 400
    learning_rate: float = 0.05
    num_leaves: int = 31
    max_depth: int = -1
    min_data_in_leaf: int = 20
    subsample: float = 0.9
    subsample_freq: int = 1
    colsample_bytree: float = 0.9
    reg_alpha: float = 0.0
    reg_lambda: float = 0.0
    random_state: int = 42


@dataclass(slots=True)
class TinyDcsSurrogate:
    """Self-contained surrogate bundle: model + calibration + OOD + feature list."""

    feature_names: list[str]
    model: object
    ood: OODDetector
    conformal: ConformalCalibration
    target_min: float = 0.0
    target_max: float = 1.0

    def predict(self, X: pd.DataFrame | np.ndarray) -> dict[str, np.ndarray]:
        X_arr = _as_array(X, self.feature_names)
        # Wrap in a DataFrame with the trained feature names so LightGBM does
        # not warn about missing names.
        X_df = pd.DataFrame(X_arr, columns=self.feature_names)
        logit_pred = np.asarray(self.model.predict(X_df), dtype=float).ravel()
        point = _sigmoid(logit_pred)
        lower = _sigmoid(logit_pred - self.conformal.q)
        upper = _sigmoid(logit_pred + self.conformal.q)
        distance = self.ood.distance(X_arr)
        in_env = distance <= self.ood.threshold
        return {
            "point": point,
            "lower": lower,
            "upper": upper,
            "logit": logit_pred,
            "ood_distance": distance,
            "in_envelope": in_env,
        }

    def save(self, path: str) -> None:
        joblib.dump(
            {
                "feature_names": list(self.feature_names),
                "model": self.model,
                "ood_mean": self.ood.mean,
                "ood_inv_cov": self.ood.inv_cov,
                "ood_threshold": self.ood.threshold,
                "conformal_q": self.conformal.q,
                "conformal_confidence": self.conformal.confidence,
                "target_min": self.target_min,
                "target_max": self.target_max,
                "version": "0.1.0",
            },
            path,
        )

    @classmethod
    def load(cls, path: str) -> "TinyDcsSurrogate":
        blob = joblib.load(path)
        ood = OODDetector(
            mean=blob["ood_mean"],
            inv_cov=blob["ood_inv_cov"],
            threshold=float(blob["ood_threshold"]),
        )
        conformal = ConformalCalibration(
            q=float(blob["conformal_q"]),
            confidence=float(blob["conformal_confidence"]),
        )
        return cls(
            feature_names=list(blob["feature_names"]),
            model=blob["model"],
            ood=ood,
            conformal=conformal,
            target_min=float(blob.get("target_min", 0.0)),
            target_max=float(blob.get("target_max", 1.0)),
        )


def _as_array(X: pd.DataFrame | np.ndarray, feature_names: list[str]) -> np.ndarray:
    if isinstance(X, pd.DataFrame):
        return X[feature_names].to_numpy(dtype=float)
    arr = np.asarray(X, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if arr.shape[1] != len(feature_names):
        raise ValueError(f"expected {len(feature_names)} features, got {arr.shape[1]}")
    return arr


def train_surrogate(
    df: pd.DataFrame,
    feature_names: Iterable[str],
    target_col: str = "pdcs_3rut_mbe1",
    *,
    test_fraction: float = 0.15,
    calibration_fraction: float = 0.15,
    config: TrainConfig | None = None,
    confidence: float = 0.95,
) -> tuple[TinyDcsSurrogate, dict[str, pd.DataFrame]]:
    """Train the full TinyDCS surrogate with calibration and OOD detection.

    Returns
    -------
    surrogate
        Self-contained :class:`TinyDcsSurrogate` ready to predict.
    splits
        Dict of ``train``, ``cal``, ``test`` dataframes (useful for downstream
        evaluation by the caller).
    """
    cfg = config or TrainConfig()
    feature_names = list(feature_names)
    if target_col not in df.columns:
        raise ValueError(f"target column '{target_col}' not in dataframe")
    if not (0.0 < test_fraction < 1.0):
        raise ValueError("test_fraction must be in (0, 1)")
    if not (0.0 < calibration_fraction < 1.0):
        raise ValueError("calibration_fraction must be in (0, 1)")
    if test_fraction + calibration_fraction >= 0.9:
        raise ValueError("test + calibration fraction must leave room for training")

    rng = np.random.default_rng(cfg.random_state)
    idx = rng.permutation(len(df))
    n = len(df)
    n_test = int(round(n * test_fraction))
    n_cal = int(round(n * calibration_fraction))
    n_train = n - n_test - n_cal
    train_idx = idx[:n_train]
    cal_idx = idx[n_train:n_train + n_cal]
    test_idx = idx[n_train + n_cal:]

    X = df[feature_names].to_numpy(dtype=float)
    y = df[target_col].to_numpy(dtype=float)

    # Target on the logit scale, clipped to avoid infinities.
    y_logit = _logit(y)

    model = lgb.LGBMRegressor(
        n_estimators=cfg.n_estimators,
        learning_rate=cfg.learning_rate,
        num_leaves=cfg.num_leaves,
        max_depth=cfg.max_depth,
        min_data_in_leaf=cfg.min_data_in_leaf,
        subsample=cfg.subsample,
        subsample_freq=cfg.subsample_freq,
        colsample_bytree=cfg.colsample_bytree,
        reg_alpha=cfg.reg_alpha,
        reg_lambda=cfg.reg_lambda,
        random_state=cfg.random_state,
        verbosity=-1,
    )
    model.fit(X[train_idx], y_logit[train_idx])

    # Conformal residuals on calibration fold (in logit space).
    cal_logit_pred = model.predict(X[cal_idx])
    cal_residuals = y_logit[cal_idx] - cal_logit_pred
    conformal = fit_conformal(cal_residuals, confidence=confidence)

    # OOD on training features.
    ood = fit_ood(X[train_idx])

    surrogate = TinyDcsSurrogate(
        feature_names=feature_names,
        model=model,
        ood=ood,
        conformal=conformal,
    )
    splits = {
        "train": df.iloc[train_idx].reset_index(drop=True),
        "cal": df.iloc[cal_idx].reset_index(drop=True),
        "test": df.iloc[test_idx].reset_index(drop=True),
    }
    return surrogate, splits
