"""Evaluation metrics for TinyDCS.

Everything here operates on probability-scale predictions y_pred ∈ [0, 1] and
references y_true ∈ [0, 1] (either the 3RUT-MBe1 surrogate target or observed
binary outcomes). Metrics split cleanly into:

* point accuracy (MAE, RMSE, R²),
* discrimination (Brier score; AUROC if ``binarize`` is provided),
* calibration (slope/intercept of a logistic recalibration, reliability bins),
* conformal coverage at a nominal level.

All functions are deterministic and side-effect-free. They are designed to be
called from the training script to produce a JSON metrics blob.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, roc_auc_score
except ImportError as exc:  # pragma: no cover
    raise ImportError("scikit-learn is required for tinydcs.metrics") from exc


_EPS = 1e-6


def _clip(x: np.ndarray) -> np.ndarray:
    return np.clip(x.astype(float), _EPS, 1.0 - _EPS)


@dataclass(slots=True)
class ReliabilityBins:
    bin_edges: np.ndarray
    bin_mean_pred: np.ndarray
    bin_mean_true: np.ndarray
    bin_count: np.ndarray


def reliability_bins(y_true: np.ndarray, y_pred: np.ndarray, n_bins: int = 10) -> ReliabilityBins:
    """Binning for a reliability diagram.

    Bins are equally spaced on [0, 1]. Empty bins are returned with NaN means.
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(y_pred, edges, right=True) - 1, 0, n_bins - 1)
    mean_pred = np.full(n_bins, np.nan)
    mean_true = np.full(n_bins, np.nan)
    count = np.zeros(n_bins, dtype=int)
    for b in range(n_bins):
        mask = idx == b
        count[b] = int(mask.sum())
        if mask.any():
            mean_pred[b] = float(y_pred[mask].mean())
            mean_true[b] = float(y_true[mask].mean())
    return ReliabilityBins(bin_edges=edges, bin_mean_pred=mean_pred, bin_mean_true=mean_true, bin_count=count)


def calibration_slope_intercept(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[float, float]:
    """Logistic recalibration slope/intercept (Van Calster et al. 2019).

    Fits `logit(y_true) ~ a + b * logit(y_pred)` as a 1-feature logistic
    regression where the response is the Bernoulli draw from y_true. For
    continuous y_true in (0, 1) we use the probabilistic-target trick: weight
    each sample by y_true (positive) and 1-y_true (negative).
    """
    y_true = _clip(np.asarray(y_true, dtype=float).ravel())
    y_pred = _clip(np.asarray(y_pred, dtype=float).ravel())
    logit_pred = np.log(y_pred / (1.0 - y_pred)).reshape(-1, 1)

    # Duplicate each sample with (pos, 1-pos) weighting.
    X = np.concatenate([logit_pred, logit_pred], axis=0)
    y = np.concatenate([np.ones_like(y_true, dtype=int), np.zeros_like(y_true, dtype=int)])
    w = np.concatenate([y_true, 1.0 - y_true])
    if w.sum() < 1e-9:
        return (float("nan"), float("nan"))
    lr = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
    lr.fit(X, y, sample_weight=w)
    return float(lr.coef_[0, 0]), float(lr.intercept_[0])


def brier_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean squared error between probabilistic targets and predictions."""
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    return float(np.mean((y_true - y_pred) ** 2))


def binarized_roc_auc(y_true: np.ndarray, y_pred: np.ndarray, threshold: float) -> Optional[float]:
    """ROC-AUC with a binary positive label defined as ``y_true > threshold``.

    Returns ``None`` if the label is degenerate.
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    y_bin = (y_true > threshold).astype(int)
    if y_bin.sum() == 0 or y_bin.sum() == y_bin.size:
        return None
    return float(roc_auc_score(y_bin, y_pred))


def bland_altman(y_ref: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Bland–Altman summary: bias + 95% limits of agreement."""
    y_ref = np.asarray(y_ref, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    diff = y_pred - y_ref
    bias = float(diff.mean())
    sd = float(diff.std(ddof=1)) if diff.size > 1 else 0.0
    return {"bias": bias, "sd": sd, "loa_lower": bias - 1.96 * sd, "loa_upper": bias + 1.96 * sd}


def point_errors(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)) if y_true.var() > 0 else float("nan"),
    }


def empirical_coverage(
    y_true: np.ndarray, y_lower: np.ndarray, y_upper: np.ndarray, nominal: float = 0.95
) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_lower = np.asarray(y_lower, dtype=float).ravel()
    y_upper = np.asarray(y_upper, dtype=float).ravel()
    inside = (y_true >= y_lower) & (y_true <= y_upper)
    coverage = float(inside.mean())
    avg_width = float(np.mean(y_upper - y_lower))
    return {"coverage": coverage, "nominal": float(nominal), "avg_width": avg_width}
