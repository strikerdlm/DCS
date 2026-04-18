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
    conformal: ConformalCalibration | MondrianConformalCalibration
    target_min: float = 0.0
    target_max: float = 1.0

    def _conformal_q_for(self, X_df: pd.DataFrame) -> np.ndarray:
        """Return a per-sample conformal half-width on the logit scale."""
        if isinstance(self.conformal, MondrianConformalCalibration):
            if self.conformal.group_feature not in X_df.columns:
                raise ValueError(
                    f"Mondrian grouping feature '{self.conformal.group_feature}' missing at predict time"
                )
            return self.conformal.q_for(X_df[self.conformal.group_feature].to_numpy(dtype=float))
        # Global conformal: constant half-width for all samples.
        return np.full(len(X_df), float(self.conformal.q), dtype=float)

    def predict(self, X: pd.DataFrame | np.ndarray) -> dict[str, np.ndarray]:
        X_arr = _as_array(X, self.feature_names)
        X_df = pd.DataFrame(X_arr, columns=self.feature_names)
        logit_pred = np.asarray(self.model.predict(X_df), dtype=float).ravel()
        half_width = self._conformal_q_for(X_df)
        point = _sigmoid(logit_pred)
        lower = _sigmoid(logit_pred - half_width)
        upper = _sigmoid(logit_pred + half_width)
        distance = self.ood.distance(X_arr)
        in_env = distance <= self.ood.threshold
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
        conformal: ConformalCalibration | MondrianConformalCalibration
        if kind == "mondrian":
            conformal = MondrianConformalCalibration(
                group_feature=str(blob["mondrian_feature"]),
                band_width=float(blob["mondrian_band_width"]),
                band_origin=float(blob["mondrian_band_origin"]),
                group_quantiles={int(k): float(v) for k, v in blob["mondrian_group_quantiles"].items()},
                global_q=float(blob["mondrian_global_q"]),
                confidence=float(blob["mondrian_confidence"]),
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
) -> tuple[TinyDcsSurrogate, dict[str, pd.DataFrame]]:
    """Train the full TinyDCS surrogate with calibration and OOD detection.

    Parameters
    ----------
    mondrian_feature, mondrian_band_width, mondrian_band_origin
        If all provided, Mondrian (group-stratified) conformal calibration is
        used instead of the global one. Common choice for altitude-DCS data
        is ``mondrian_feature="altitude_ft"``, ``band_width=5000.0``,
        ``band_origin=18000.0``.

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
    conformal: ConformalCalibration | MondrianConformalCalibration
    if use_mondrian:
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
