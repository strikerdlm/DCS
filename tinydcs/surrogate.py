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

from dataclasses import asdict, dataclass, field
from typing import Iterable

import joblib
import numpy as np
import pandas as pd

try:
    import lightgbm as lgb
except ImportError as exc:  # pragma: no cover
    raise ImportError("lightgbm is required for tinydcs.surrogate") from exc


_EPS = 1e-6


def _smithson_verkuilen(p: np.ndarray, n: int) -> np.ndarray:
    """Smithson–Verkuilen (2006) transform that shrinks exact 0 and 1 values
    away from the boundary so ``logit`` is finite.

        y' = (y * (n - 1) + 0.5) / n

    Essential when the target has mass at exact 0 (a large fraction of the
    low-altitude ADRAC grid).
    """
    p = np.asarray(p, dtype=float)
    nn = float(max(n, 2))
    return (p * (nn - 1.0) + 0.5) / nn


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
class MondrianConformalCalibration:
    """Group-stratified ("Mondrian") conformal calibration.

    Residuals are partitioned into groups by discretizing one feature. A
    separate quantile is computed per group; at inference each sample is
    routed to its group's quantile. This restores per-group marginal
    coverage when residuals are heteroscedastic along the grouping feature
    (e.g. larger at high altitudes).

    Parameters
    ----------
    group_feature
        Name of the feature to stratify on (must be in the surrogate's
        ``feature_names``).
    band_width
        Width of each group in the units of ``group_feature``. For altitude
        in feet, 5000 gives 5 altitude bands across 18,000–40,000 ft.
    band_origin
        Zero-point for the band index. A sample's band is
        ``int((value - band_origin) // band_width)``.
    group_quantiles
        Mapping band-index → residual quantile on the logit scale.
    global_q
        Fallback quantile for samples whose band is unseen at calibration
        (e.g. an out-of-envelope altitude). Defaults to the overall 95%
        quantile across all calibration residuals so callers still get
        sensible intervals.
    confidence
        Nominal coverage level (e.g. 0.95).
    """

    group_feature: str
    band_width: float
    band_origin: float
    group_quantiles: dict[int, float] = field(default_factory=dict)
    global_q: float = 0.0
    confidence: float = 0.95

    def band_of(self, values: np.ndarray) -> np.ndarray:
        v = np.asarray(values, dtype=float).ravel()
        return np.floor((v - float(self.band_origin)) / float(self.band_width)).astype(int)

    def q_for(self, values: np.ndarray) -> np.ndarray:
        """Return the per-sample conformal quantile, routing to the sample's band."""
        bands = self.band_of(values)
        out = np.full(bands.shape, float(self.global_q), dtype=float)
        for b, q in self.group_quantiles.items():
            out[bands == int(b)] = float(q)
        return out


@dataclass(slots=True)
class ZeroInflatedCalibration:
    """Two-stage zero-inflated calibration (Lambert 1992 style).

    Handles target distributions with a point mass at zero — here, the
    low-altitude band of the ADRAC grid where ~40% of rows have exact-zero
    P(DCS). The stack is:

      stage 1: binary classifier P(y = 0 | x) over the whole training fold;
      stage 2: continuous regressor of logit(y) conditional on y > 0,
               trained only on non-zero rows.

    Inference gates on a configurable probability threshold:

      * If P(y = 0 | x) >= ``gate_threshold`` → output point = 0 with a
        narrow zero-anchored interval ``[0, zero_upper_bound]``. The upper
        end reflects residual classifier uncertainty.
      * Otherwise → the continuous regressor's prediction is the point
        estimate, and the existing split-conformal logic gives the
        interval.
    """

    zero_classifier: object
    continuous_model: object
    continuous_q: float
    confidence: float
    gate_threshold: float = 0.5
    zero_upper_bound: float = 0.02


def fit_zero_inflated(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_cal: np.ndarray,
    y_cal: np.ndarray,
    *,
    feature_names: list[str],
    monotonic_constraints: dict[str, int] | None = None,
    n_estimators: int = 400,
    learning_rate: float = 0.05,
    num_leaves: int = 31,
    min_data_in_leaf: int = 20,
    subsample: float = 0.9,
    subsample_freq: int = 1,
    colsample_bytree: float = 0.9,
    random_state: int = 42,
    confidence: float = 0.95,
    zero_tol: float = 1e-6,
    gate_threshold: float = 0.5,
    zero_upper_bound: float = 0.02,
) -> ZeroInflatedCalibration:
    """Fit a two-stage zero-inflated surrogate.

    Stage 1: binary classifier on is_zero = (y <= zero_tol).
    Stage 2: continuous LightGBM regressor on logit(y) over non-zero rows only.
    Conformal quantile is fit on the calibration fold's non-zero rows.
    """
    X_train_df = pd.DataFrame(X_train, columns=feature_names)
    X_cal_df = pd.DataFrame(X_cal, columns=feature_names)

    is_zero_train = (y_train <= zero_tol).astype(int)

    # Stage 1 classifier.
    zero_clf = lgb.LGBMClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        num_leaves=num_leaves,
        min_data_in_leaf=min_data_in_leaf,
        subsample=subsample,
        subsample_freq=subsample_freq,
        colsample_bytree=colsample_bytree,
        random_state=random_state,
        verbosity=-1,
    )
    zero_clf.fit(X_train_df, is_zero_train)

    # Stage 2 regressor on non-zero rows only.
    non_zero_train = ~is_zero_train.astype(bool)
    if int(non_zero_train.sum()) < 100:
        raise ValueError("Too few non-zero rows to fit the continuous stage.")
    y_nonzero = np.clip(y_train[non_zero_train], _EPS, 1.0 - _EPS)
    y_logit_nonzero = np.log(y_nonzero / (1.0 - y_nonzero))

    mono_vec = [int((monotonic_constraints or {}).get(name, 0)) for name in feature_names]
    cont_model = lgb.LGBMRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        num_leaves=num_leaves,
        min_data_in_leaf=min_data_in_leaf,
        subsample=subsample,
        subsample_freq=subsample_freq,
        colsample_bytree=colsample_bytree,
        random_state=random_state,
        monotone_constraints=mono_vec,
        monotone_constraints_method="advanced",
        verbosity=-1,
    )
    cont_model.fit(X_train_df.loc[non_zero_train], y_logit_nonzero)

    # Conformal quantile on the calibration fold's non-zero rows.
    is_zero_cal = (y_cal <= zero_tol)
    non_zero_cal = ~is_zero_cal
    if int(non_zero_cal.sum()) < 20:
        raise ValueError("Too few non-zero calibration rows for conformal calibration.")
    y_cal_nonzero = np.clip(y_cal[non_zero_cal], _EPS, 1.0 - _EPS)
    y_cal_logit = np.log(y_cal_nonzero / (1.0 - y_cal_nonzero))
    cont_logit_pred = cont_model.predict(X_cal_df.loc[non_zero_cal])
    resid = np.abs(y_cal_logit - cont_logit_pred)
    n = int(resid.size)
    alpha = 1.0 - float(confidence)
    k = int(np.ceil((n + 1) * (1.0 - alpha)))
    k = max(1, min(k, n))
    q = float(np.partition(resid, k - 1)[k - 1])

    return ZeroInflatedCalibration(
        zero_classifier=zero_clf,
        continuous_model=cont_model,
        continuous_q=q,
        confidence=float(confidence),
        gate_threshold=float(gate_threshold),
        zero_upper_bound=float(zero_upper_bound),
    )


@dataclass(slots=True)
class CQRCalibration:
    """Conformalized Quantile Regression calibration (Romano, Patterson & Candès 2019).

    Attaches a lower- and an upper-quantile regressor to the base surrogate
    and computes a conformal correction on the nonconformity score
    ``E_i = max(q_lo(x_i) - eta_i, eta_i - q_hi(x_i))`` over a held-out
    calibration fold. The correction can be:

    * **Global** (``band_width is None``) — a single scalar ``q`` applied to
      every test point.
    * **Mondrian CQR** (``band_width`` and ``band_feature`` set) — a separate
      ``q_g`` per altitude band, with a global fallback. This is the right
      tool when quantile-regression spread is itself biased in a specific
      region (e.g. the zero-target low-altitude band of the ADRAC grid).

    Final predictive interval on the logit scale is ``[q_lo(x) - q(x),
    q_hi(x) + q(x)]``; in probability space both ends pass through a
    sigmoid so the interval stays in ``[0, 1]``.
    """

    lower_model: object
    upper_model: object
    q: float
    confidence: float
    band_feature: str | None = None
    band_width: float | None = None
    band_origin: float = 0.0
    group_q: dict[int, float] = field(default_factory=dict)

    def correction_for(self, X_df: pd.DataFrame) -> np.ndarray:
        """Per-sample conformal correction on the logit scale."""
        n = len(X_df)
        if self.band_feature is None or self.band_width is None:
            return np.full(n, float(self.q), dtype=float)
        if self.band_feature not in X_df.columns:
            raise ValueError(
                f"CQR band feature '{self.band_feature}' missing at predict time"
            )
        v = X_df[self.band_feature].to_numpy(dtype=float)
        bands = np.floor((v - float(self.band_origin)) / float(self.band_width)).astype(int)
        out = np.full(n, float(self.q), dtype=float)
        for b, q_b in self.group_q.items():
            out[bands == int(b)] = float(q_b)
        return out


def fit_cqr(
    X_train: np.ndarray,
    y_logit_train: np.ndarray,
    X_cal: np.ndarray,
    y_logit_cal: np.ndarray,
    *,
    feature_names: list[str],
    monotonic_constraints: dict[str, int] | None = None,
    n_estimators: int = 400,
    learning_rate: float = 0.05,
    num_leaves: int = 31,
    min_data_in_leaf: int = 20,
    subsample: float = 0.9,
    subsample_freq: int = 1,
    colsample_bytree: float = 0.9,
    random_state: int = 42,
    confidence: float = 0.95,
    band_feature: str | None = None,
    band_width: float | None = None,
    band_origin: float = 0.0,
    min_group_size: int = 20,
) -> CQRCalibration:
    """Fit CQR calibration on the logit scale.

    Two LightGBM quantile regressors are trained on ``(X_train, y_logit_train)``
    at quantile levels ``alpha/2`` and ``1 - alpha/2``. Nonconformity scores
    are computed on ``(X_cal, y_logit_cal)`` and the ``ceil((n+1)(1-alpha))``
    quantile is taken as the conformal correction.
    """
    alpha = 1.0 - float(confidence)
    # LightGBM refuses monotone constraints with the quantile objective, so
    # CQR's two quantile regressors cannot be monotonicity-constrained. The
    # base model (mean regression on logit) keeps them; the conformal
    # correction then absorbs any residual non-monotone behaviour of the
    # quantile outputs within the validated envelope.
    _ = monotonic_constraints  # kept in the signature for consistency; not used
    common = dict(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        num_leaves=num_leaves,
        min_data_in_leaf=min_data_in_leaf,
        subsample=subsample,
        subsample_freq=subsample_freq,
        colsample_bytree=colsample_bytree,
        random_state=random_state,
        verbosity=-1,
    )
    lower_model = lgb.LGBMRegressor(objective="quantile", alpha=alpha / 2.0, **common)
    upper_model = lgb.LGBMRegressor(objective="quantile", alpha=1.0 - alpha / 2.0, **common)

    X_train_df = pd.DataFrame(X_train, columns=feature_names)
    X_cal_df = pd.DataFrame(X_cal, columns=feature_names)
    lower_model.fit(X_train_df, y_logit_train)
    upper_model.fit(X_train_df, y_logit_train)

    q_lo = np.asarray(lower_model.predict(X_cal_df), dtype=float).ravel()
    q_hi = np.asarray(upper_model.predict(X_cal_df), dtype=float).ravel()
    nonconformity = np.maximum(q_lo - y_logit_cal, y_logit_cal - q_hi)
    n = int(nonconformity.size)
    if n < 20:
        raise ValueError("at least 20 calibration residuals are required for CQR")

    def _conformal_q(r: np.ndarray) -> float:
        nn = int(r.size)
        k = int(np.ceil((nn + 1) * (1.0 - alpha)))
        k = max(1, min(k, nn))
        return float(np.partition(r, k - 1)[k - 1])

    q_global = _conformal_q(nonconformity)

    group_q: dict[int, float] = {}
    if band_feature is not None and band_width is not None and band_width > 0:
        if band_feature not in feature_names:
            raise ValueError(
                f"CQR band_feature '{band_feature}' is not in feature_names"
            )
        col = feature_names.index(band_feature)
        cal_vals = X_cal[:, col]
        bands = np.floor((cal_vals - float(band_origin)) / float(band_width)).astype(int)
        for b in np.unique(bands):
            mask = bands == b
            if int(mask.sum()) >= min_group_size:
                group_q[int(b)] = _conformal_q(nonconformity[mask])

    return CQRCalibration(
        lower_model=lower_model,
        upper_model=upper_model,
        q=q_global,
        confidence=float(confidence),
        band_feature=band_feature,
        band_width=band_width,
        band_origin=float(band_origin),
        group_q=group_q,
    )


def fit_mondrian_conformal(
    logit_residuals: np.ndarray,
    group_values: np.ndarray,
    *,
    group_feature: str,
    band_width: float,
    band_origin: float = 0.0,
    confidence: float = 0.95,
    min_group_size: int = 20,
) -> MondrianConformalCalibration:
    """Fit per-band conformal quantiles with a global fallback.

    Bands containing fewer than ``min_group_size`` residuals fall back to
    the global quantile.
    """
    resid = np.abs(np.asarray(logit_residuals, dtype=float).ravel())
    values = np.asarray(group_values, dtype=float).ravel()
    if resid.size != values.size:
        raise ValueError("logit_residuals and group_values must be the same length")
    if resid.size < 20:
        raise ValueError("at least 20 calibration residuals are required")

    alpha = 1.0 - float(confidence)

    def _conformal_q(r: np.ndarray) -> float:
        n = int(r.size)
        k = int(np.ceil((n + 1) * (1.0 - alpha)))
        k = max(1, min(k, n))
        return float(np.partition(r, k - 1)[k - 1])

    bands = np.floor((values - float(band_origin)) / float(band_width)).astype(int)
    group_quantiles: dict[int, float] = {}
    for b in np.unique(bands):
        mask = bands == b
        if int(mask.sum()) >= min_group_size:
            group_quantiles[int(b)] = _conformal_q(resid[mask])

    global_q = _conformal_q(resid)

    return MondrianConformalCalibration(
        group_feature=str(group_feature),
        band_width=float(band_width),
        band_origin=float(band_origin),
        group_quantiles=group_quantiles,
        global_q=global_q,
        confidence=float(confidence),
    )


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
    # Per-feature monotonicity constraints: +1 = non-decreasing, -1 =
    # non-increasing, 0 = unconstrained. Keyed by feature name. Only
    # applied if the feature is present in ``feature_names`` at training.
    # Physiological defaults: altitude/time/tissue-ratio up ⇒ risk up;
    # prebreathe up ⇒ risk down.
    monotonic_constraints: dict[str, int] = field(default_factory=lambda: {
        "altitude_ft": 1,
        "ambient_pressure_atm": -1,
        "altitude_time_min": 1,
        "prebreathe_time_min": -1,
        "tissue_n2_ratio_360min": 1,
    })


@dataclass(slots=True)
class TinyDcsSurrogate:
    """Self-contained surrogate bundle: model + calibration + OOD + feature list.

    Conformal calibration can be either a global ``ConformalCalibration`` or a
    group-stratified ``MondrianConformalCalibration``. The ``predict`` method
    dispatches on the type.
    """

    feature_names: list[str]
    model: object
    ood: OODDetector
    conformal: (
        ConformalCalibration | MondrianConformalCalibration | CQRCalibration | ZeroInflatedCalibration
    )
    target_min: float = 0.0
    target_max: float = 1.0

    def _conformal_q_for(self, X_df: pd.DataFrame) -> np.ndarray:
        """Return a per-sample conformal half-width on the logit scale (for
        non-CQR calibrations). CQR uses a different interval construction;
        callers should check :meth:`_is_cqr` and use ``predict()`` directly."""
        if isinstance(self.conformal, MondrianConformalCalibration):
            if self.conformal.group_feature not in X_df.columns:
                raise ValueError(
                    f"Mondrian grouping feature '{self.conformal.group_feature}' missing at predict time"
                )
            return self.conformal.q_for(X_df[self.conformal.group_feature].to_numpy(dtype=float))
        if isinstance(self.conformal, CQRCalibration):
            # CQR does not expose a single half-width; return NaN to signal
            # that ``predict`` will compute intervals directly.
            return np.full(len(X_df), np.nan, dtype=float)
        # Global conformal: constant half-width for all samples.
        return np.full(len(X_df), float(self.conformal.q), dtype=float)

    def predict(self, X: pd.DataFrame | np.ndarray) -> dict[str, np.ndarray]:
        X_arr = _as_array(X, self.feature_names)
        X_df = pd.DataFrame(X_arr, columns=self.feature_names)
        logit_pred = np.asarray(self.model.predict(X_df), dtype=float).ravel()
        distance = self.ood.distance(X_arr)
        in_env = distance <= self.ood.threshold
        point = _sigmoid(logit_pred)

        if isinstance(self.conformal, ZeroInflatedCalibration):
            zi = self.conformal
            p_zero = zi.zero_classifier.predict_proba(X_df)[:, 1]
            is_gated_zero = p_zero >= zi.gate_threshold
            cont_logit = np.asarray(zi.continuous_model.predict(X_df), dtype=float).ravel()
            cont_point = _sigmoid(cont_logit)
            cont_lower = _sigmoid(cont_logit - zi.continuous_q)
            cont_upper = _sigmoid(cont_logit + zi.continuous_q)
            # Mixture point estimate: E[y] = (1 - p_zero) * E[y | y>0]
            point_mix = (1.0 - p_zero) * cont_point
            # Intervals: when gated to zero, [0, zero_upper_bound]; otherwise
            # use the continuous-conditional conformal interval scaled to the
            # mixture so ground-truth zeros remain inside.
            lower = np.where(is_gated_zero, 0.0, (1.0 - p_zero) * cont_lower)
            upper = np.where(is_gated_zero, zi.zero_upper_bound, np.maximum(zi.zero_upper_bound, (1.0 - p_zero) * cont_upper + p_zero * zi.zero_upper_bound))
            half_width = (_logit(np.clip(upper, _EPS, 1 - _EPS)) - _logit(np.clip(lower + _EPS, _EPS, 1 - _EPS))) / 2.0
            return {
                "point": point_mix,
                "lower": lower,
                "upper": upper,
                "logit": logit_pred,
                "p_zero": p_zero,
                "is_gated_zero": is_gated_zero,
                "continuous_point": cont_point,
                "conformal_half_width_logit": half_width,
                "ood_distance": distance,
                "in_envelope": in_env,
            }

        if isinstance(self.conformal, CQRCalibration):
            q_lo_logit = np.asarray(self.conformal.lower_model.predict(X_df), dtype=float).ravel()
            q_hi_logit = np.asarray(self.conformal.upper_model.predict(X_df), dtype=float).ravel()
            q_correction = self.conformal.correction_for(X_df)
            lower_logit = q_lo_logit - q_correction
            upper_logit = q_hi_logit + q_correction
            lower = _sigmoid(lower_logit)
            upper = _sigmoid(upper_logit)
            half_width = (upper_logit - lower_logit) / 2.0
            return {
                "point": point,
                "lower": lower,
                "upper": upper,
                "logit": logit_pred,
                "logit_lower": lower_logit,
                "logit_upper": upper_logit,
                "conformal_half_width_logit": half_width,
                "cqr_correction_logit": q_correction,
                "ood_distance": distance,
                "in_envelope": in_env,
            }

        half_width = self._conformal_q_for(X_df)
        lower = _sigmoid(logit_pred - half_width)
        upper = _sigmoid(logit_pred + half_width)
        return {
            "point": point,
            "lower": lower,
            "upper": upper,
            "logit": logit_pred,
            "conformal_half_width_logit": half_width,
            "ood_distance": distance,
            "in_envelope": in_env,
        }

    def save(self, path: str) -> None:
        blob: dict = {
            "feature_names": list(self.feature_names),
            "model": self.model,
            "ood_mean": self.ood.mean,
            "ood_inv_cov": self.ood.inv_cov,
            "ood_threshold": self.ood.threshold,
            "target_min": self.target_min,
            "target_max": self.target_max,
            "version": "0.2.2",
        }
        if isinstance(self.conformal, MondrianConformalCalibration):
            blob.update(
                conformal_kind="mondrian",
                mondrian_feature=self.conformal.group_feature,
                mondrian_band_width=self.conformal.band_width,
                mondrian_band_origin=self.conformal.band_origin,
                mondrian_group_quantiles=dict(self.conformal.group_quantiles),
                mondrian_global_q=self.conformal.global_q,
                mondrian_confidence=self.conformal.confidence,
            )
        elif isinstance(self.conformal, CQRCalibration):
            blob.update(
                conformal_kind="cqr",
                cqr_lower_model=self.conformal.lower_model,
                cqr_upper_model=self.conformal.upper_model,
                cqr_q=self.conformal.q,
                cqr_confidence=self.conformal.confidence,
                cqr_band_feature=self.conformal.band_feature,
                cqr_band_width=self.conformal.band_width,
                cqr_band_origin=self.conformal.band_origin,
                cqr_group_q=dict(self.conformal.group_q),
            )
        elif isinstance(self.conformal, ZeroInflatedCalibration):
            blob.update(
                conformal_kind="zero_inflated",
                zi_zero_classifier=self.conformal.zero_classifier,
                zi_continuous_model=self.conformal.continuous_model,
                zi_continuous_q=self.conformal.continuous_q,
                zi_confidence=self.conformal.confidence,
                zi_gate_threshold=self.conformal.gate_threshold,
                zi_zero_upper_bound=self.conformal.zero_upper_bound,
            )
        else:
            blob.update(
                conformal_kind="global",
                conformal_q=self.conformal.q,
                conformal_confidence=self.conformal.confidence,
            )
        joblib.dump(blob, path)

    @classmethod
    def load(cls, path: str) -> "TinyDcsSurrogate":
        blob = joblib.load(path)
        ood = OODDetector(
            mean=blob["ood_mean"],
            inv_cov=blob["ood_inv_cov"],
            threshold=float(blob["ood_threshold"]),
        )
        kind = blob.get("conformal_kind", "global")
        conformal: ConformalCalibration | MondrianConformalCalibration | CQRCalibration
        if kind == "mondrian":
            conformal = MondrianConformalCalibration(
                group_feature=str(blob["mondrian_feature"]),
                band_width=float(blob["mondrian_band_width"]),
                band_origin=float(blob["mondrian_band_origin"]),
                group_quantiles={int(k): float(v) for k, v in blob["mondrian_group_quantiles"].items()},
                global_q=float(blob["mondrian_global_q"]),
                confidence=float(blob["mondrian_confidence"]),
            )
        elif kind == "cqr":
            group_q_raw = blob.get("cqr_group_q", {}) or {}
            conformal = CQRCalibration(
                lower_model=blob["cqr_lower_model"],
                upper_model=blob["cqr_upper_model"],
                q=float(blob["cqr_q"]),
                confidence=float(blob["cqr_confidence"]),
                band_feature=blob.get("cqr_band_feature"),
                band_width=blob.get("cqr_band_width"),
                band_origin=float(blob.get("cqr_band_origin", 0.0)),
                group_q={int(k): float(v) for k, v in group_q_raw.items()},
            )
        elif kind == "zero_inflated":
            conformal = ZeroInflatedCalibration(
                zero_classifier=blob["zi_zero_classifier"],
                continuous_model=blob["zi_continuous_model"],
                continuous_q=float(blob["zi_continuous_q"]),
                confidence=float(blob["zi_confidence"]),
                gate_threshold=float(blob["zi_gate_threshold"]),
                zero_upper_bound=float(blob["zi_zero_upper_bound"]),
            )
        else:
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
    mondrian_feature: str | None = None,
    mondrian_band_width: float | None = None,
    mondrian_band_origin: float = 0.0,
    use_cqr: bool = False,
    cqr_band_feature: str | None = None,
    cqr_band_width: float | None = None,
    cqr_band_origin: float = 0.0,
    use_zero_inflated: bool = False,
    zi_gate_threshold: float = 0.5,
    zi_zero_upper_bound: float = 0.02,
) -> tuple[TinyDcsSurrogate, dict[str, pd.DataFrame]]:
    """Train the full TinyDCS surrogate with calibration and OOD detection.

    Parameters
    ----------
    mondrian_feature, mondrian_band_width, mondrian_band_origin
        If all provided, Mondrian (group-stratified) conformal calibration is
        used instead of the global one. Common choice for altitude-DCS data
        is ``mondrian_feature="altitude_ft"``, ``band_width=5000.0``,
        ``band_origin=18000.0``.
    use_cqr
        If True, use Conformalized Quantile Regression (Romano et al. 2019)
        — two additional LightGBM quantile regressors + a single conformal
        correction on their nonconformity score. Handles bias-driven
        coverage shortfalls that Mondrian alone cannot fix. Supersedes the
        Mondrian/global options when enabled.

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

    # Smithson–Verkuilen transform, then logit. This handles exact 0/1 target
    # mass cleanly (e.g. the ~40% exact-zero rows at low altitude in the
    # ADRAC grid) without introducing pathological logit pile-up.
    y_shrunk = _smithson_verkuilen(y, n=len(y))
    y_logit = _logit(y_shrunk)

    monotone_vec = [int(cfg.monotonic_constraints.get(name, 0)) for name in feature_names]
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
        monotone_constraints=monotone_vec,
        monotone_constraints_method="advanced",
        verbosity=-1,
    )
    model.fit(X[train_idx], y_logit[train_idx])

    # Conformal residuals on calibration fold (in logit space).
    cal_logit_pred = model.predict(X[cal_idx])
    cal_residuals = y_logit[cal_idx] - cal_logit_pred

    use_mondrian = (
        mondrian_feature is not None and mondrian_band_width is not None and mondrian_band_width > 0
    )
    conformal: ConformalCalibration | MondrianConformalCalibration | CQRCalibration
    if use_zero_inflated:
        # Two-stage zero-inflated surrogate: binary classifier for P(y=0|x)
        # + continuous regressor for E[logit(y) | y>0, x]. Handles the
        # exact-zero target mass directly, which CQR/Mondrian cannot reach.
        conformal = fit_zero_inflated(
            X_train=X[train_idx],
            y_train=y[train_idx],
            X_cal=X[cal_idx],
            y_cal=y[cal_idx],
            feature_names=feature_names,
            monotonic_constraints=dict(cfg.monotonic_constraints),
            n_estimators=cfg.n_estimators,
            learning_rate=cfg.learning_rate,
            num_leaves=cfg.num_leaves,
            min_data_in_leaf=cfg.min_data_in_leaf,
            subsample=cfg.subsample,
            subsample_freq=cfg.subsample_freq,
            colsample_bytree=cfg.colsample_bytree,
            random_state=cfg.random_state,
            confidence=confidence,
            gate_threshold=zi_gate_threshold,
            zero_upper_bound=zi_zero_upper_bound,
        )
    elif use_cqr:
        # CQR trains two extra quantile regressors plus a conformal
        # correction. If cqr_band_feature is also set, the correction is
        # stratified per altitude band (Mondrian-CQR), which repairs the
        # remaining bias-driven shortfall that global CQR alone cannot fix
        # when the quantile regressors themselves under-estimate spread in
        # a zero-target region.
        conformal = fit_cqr(
            X_train=X[train_idx],
            y_logit_train=y_logit[train_idx],
            X_cal=X[cal_idx],
            y_logit_cal=y_logit[cal_idx],
            feature_names=feature_names,
            monotonic_constraints=dict(cfg.monotonic_constraints),
            n_estimators=cfg.n_estimators,
            learning_rate=cfg.learning_rate,
            num_leaves=cfg.num_leaves,
            min_data_in_leaf=cfg.min_data_in_leaf,
            subsample=cfg.subsample,
            subsample_freq=cfg.subsample_freq,
            colsample_bytree=cfg.colsample_bytree,
            random_state=cfg.random_state,
            confidence=confidence,
            band_feature=cqr_band_feature,
            band_width=cqr_band_width,
            band_origin=cqr_band_origin,
        )
    elif use_mondrian:
        if mondrian_feature not in feature_names:
            raise ValueError(
                f"mondrian_feature '{mondrian_feature}' is not in feature_names {feature_names}"
            )
        col_idx = feature_names.index(mondrian_feature)
        conformal = fit_mondrian_conformal(
            logit_residuals=cal_residuals,
            group_values=X[cal_idx, col_idx],
            group_feature=mondrian_feature,
            band_width=float(mondrian_band_width),
            band_origin=float(mondrian_band_origin),
            confidence=confidence,
        )
    else:
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
