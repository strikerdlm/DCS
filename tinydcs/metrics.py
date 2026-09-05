"""Probability-scale model agreement and separately labelled binary-outcome metrics.

Model-generated probabilities are not observed clinical outcomes. Undefined
summaries use None so strict JSON serializes them as null, never NaN or zero.
"""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from sklearn.metrics import roc_auc_score


def _pairs(*arrays):
    values = [np.asarray(a, dtype=float).ravel() for a in arrays]
    if len({a.size for a in values}) != 1:
        raise ValueError("metric inputs must have equal lengths")
    if any(not np.isfinite(a).all() or np.any((a < 0) | (a > 1)) for a in values):
        raise ValueError("metric inputs must be finite probabilities in [0,1]")
    return values


@dataclass(slots=True)
class ReliabilityBins:
    bin_edges: np.ndarray
    bin_mean_pred: np.ndarray
    bin_mean_true: np.ndarray
    bin_count: np.ndarray


def reliability_bins(y_true, y_pred, n_bins: int = 10) -> ReliabilityBins:
    y_true, y_pred = _pairs(y_true, y_pred)
    if not isinstance(n_bins, int) or n_bins < 1:
        raise ValueError("n_bins must be a positive integer")
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.searchsorted(edges, y_pred, side="right") - 1, 0, n_bins - 1)
    pred, true = np.full(n_bins, None, dtype=object), np.full(n_bins, None, dtype=object)
    counts = np.bincount(idx, minlength=n_bins)
    for b in range(n_bins):
        if counts[b]:
            pred[b], true[b] = float(y_pred[idx == b].mean()), float(y_true[idx == b].mean())
    return ReliabilityBins(edges, pred, true, counts)


def calibration_slope_intercept(y_true, y_pred):
    """Fractional-logistic agreement for soft targets; not clinical calibration.

    A finite optimum is required. Degenerate/fully separated samples have no
    finite slope/intercept and return (None, None).
    """
    y, p = _pairs(y_true, y_pred)
    if len(y) < 3 or np.ptp(y) == 0 or np.ptp(p) == 0:
        return None, None
    p = np.clip(p, 1e-10, 1 - 1e-10)
    x = np.log(p) - np.log1p(-p)
    if np.isin(y, [0, 1]).all():
        positive, negative = x[y == 1], x[y == 0]
        if positive.min() >= negative.max() or negative.min() >= positive.max():
            return None, None  # complete or quasi separation; no finite MLE
    design = np.column_stack([np.ones(len(x)), x])

    def loss(theta):
        z = design @ theta
        return np.mean(np.logaddexp(0, z) - y * z), design.T @ (expit(z) - y) / len(y)

    result = minimize(loss, [0.0, 1.0], jac=True, method="BFGS", options={"gtol": 1e-8})
    if not result.success or not np.isfinite(result.x).all() or np.max(np.abs(result.x)) > 100:
        return None, None
    return float(result.x[1]), float(result.x[0])


def probability_mse(y_true, y_pred):
    y, p = _pairs(y_true, y_pred)
    return float(np.mean((y - p) ** 2)) if len(y) else None


def brier_score(y_true, y_pred):
    """Brier score for observed binary outcomes only."""
    y, p = _pairs(y_true, y_pred)
    if not np.isin(y, [0, 1]).all():
        raise ValueError("Brier score requires observed binary outcomes")
    return probability_mse(y, p)


def binary_roc_auc(y_true, y_pred):
    y, p = _pairs(y_true, y_pred)
    if not np.isin(y, [0, 1]).all():
        raise ValueError("AUROC requires observed binary outcomes")
    return float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None


def binarized_roc_auc(y_true, y_pred, threshold):
    """Diagnostic threshold discrimination of model targets, NOT clinical AUROC."""
    y, p = _pairs(y_true, y_pred)
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0,1]")
    return binary_roc_auc((y > threshold).astype(float), p)


def bland_altman(y_ref, y_pred):
    y, p = _pairs(y_ref, y_pred)
    bias = float((p - y).mean()) if len(y) else None
    sd = float((p - y).std(ddof=1)) if len(y) > 1 else None
    return {
        "n": len(y),
        "unit": "probability",
        "bias": bias,
        "sd": sd,
        "loa_lower": bias - 1.96 * sd if sd is not None else None,
        "loa_upper": bias + 1.96 * sd if sd is not None else None,
    }


def point_errors(y_true, y_pred):
    y, p = _pairs(y_true, y_pred)
    mse = probability_mse(y, p)
    return {
        "n": len(y),
        "unit": "probability",
        "mae": float(np.mean(np.abs(y - p))) if len(y) else None,
        "mse": mse,
        "rmse": float(np.sqrt(mse)) if mse is not None else None,
        "r2": float(1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2))
        if len(y) > 1 and np.ptp(y) > 0
        else None,
    }


def empirical_coverage(y_true, y_lower, y_upper, nominal=0.95):
    y, lo, hi = _pairs(y_true, y_lower, y_upper)
    if np.any(lo > hi) or not 0 < nominal < 1:
        raise ValueError("ordered intervals and nominal coverage in (0,1) required")
    n = len(y)
    hits = int(((y >= lo) & (y <= hi)).sum())
    coverage = hits / n if n else None
    # Wilson 95% descriptive binomial interval; dependent grid rows are not IID.
    if n:
        z = 1.959963984540054
        denominator = 1 + z * z / n
        center = (coverage + z * z / (2 * n)) / denominator
        half = z * np.sqrt(coverage * (1 - coverage) / n + z * z / (4 * n * n)) / denominator
        bounds = [float(center - half), float(center + half)]
    else:
        bounds = [None, None]
    return {
        "n": n,
        "covered_n": hits,
        "coverage": coverage,
        "nominal": float(nominal),
        "avg_width": float((hi - lo).mean()) if n else None,
        "coverage_wilson_95": bounds,
        "unit": "probability",
    }
