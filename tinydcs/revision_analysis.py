"""Deterministic validation utilities for the KJAsEM-26-0013 revision.

The source data are a structured ADRAC-derived grid, not independent human
exposures.  This module therefore keeps split construction, interval
efficiency, and cluster-bootstrap uncertainty explicit and auditable.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

try:
    import lightgbm as lgb
except ImportError as exc:  # pragma: no cover
    raise ImportError("lightgbm is required for revision analysis") from exc

from tinydcs.features import extract_features
from tinydcs.simulator import ExposureProfile, ornstein_uhlenbeck_vo2
from tinydcs.surrogate import (
    TinyDcsSurrogate,
    TrainConfig,
    _logit,
    _smithson_verkuilen,
    fit_conformal,
    fit_cqr,
    fit_mondrian_conformal,
    fit_ood,
    fit_zero_inflated,
)


@dataclass(frozen=True, slots=True)
class HoldoutFold:
    """One prespecified, contiguous holdout region of the source grid."""

    family: str
    label: str
    test_indices: np.ndarray


_ALTITUDE_BANDS = (
    (18000, 23000, "18-<23 kft"),
    (23000, 28000, "23-<28 kft"),
    (28000, 33000, "28-<33 kft"),
    (33000, 38000, "33-<38 kft"),
    (38000, 40001, "38-40 kft"),
)

_DURATION_BANDS = (
    (10, 60, "10-60 min"),
    (70, 120, "70-120 min"),
    (130, 180, "130-180 min"),
    (190, 240, "190-240 min"),
)

_EXERCISE_VO2_LOOKUP = {
    "Rest": {"mean": 0.10, "sd": 0.05},
    "Mild": {"mean": 0.45, "sd": 0.10},
    "Heavy": {"mean": 1.10, "sd": 0.15},
}


def augment_adrac_grid(df: pd.DataFrame, *, seed: int = 42) -> pd.DataFrame:
    """Create the submitted 13-feature representation of each ADRAC grid cell.

    The categorical exercise level is converted to a deterministic synthetic
    workload trajectory using the same assumptions as the submitted training
    script.  Original cell keys are retained for leakage audits and stratified
    reporting; the target is converted from percent to probability.
    """
    required = {
        "altitude",
        "prebreathing_time",
        "exercise_level",
        "time_at_altitude",
        "risk_of_decompression_sickness",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"ADRAC augmentation columns missing: {missing}")
    rng = np.random.default_rng(seed)
    records: list[dict[str, object]] = []
    source = df.reset_index(drop=True)
    for source_cell_id, row in source.iterrows():
        exercise = str(row["exercise_level"])
        if exercise not in _EXERCISE_VO2_LOOKUP:
            raise ValueError(f"unsupported exercise level: {exercise}")
        parameters = _EXERCISE_VO2_LOOKUP[exercise]
        mean_i_ex = max(0.0, rng.normal(parameters["mean"], parameters["sd"]))
        duration = float(row["time_at_altitude"])
        trajectory = ornstein_uhlenbeck_vo2(
            duration_min=duration,
            dt_min=5.0,
            mean_i_ex=mean_i_ex,
            rng=rng,
        )
        profile = ExposureProfile(
            target_altitude_ft=float(row["altitude"]),
            prebreathe_duration_min=float(row["prebreathing_time"]),
            prebreathe_fio2=1.0,
            prebreathe_fin2=0.0,
            prebreathe_i_ex_trajectory=0.0,
            ascent_rate_fpm=5000.0,
            altitude_duration_min=duration,
            altitude_fio2=0.21,
            altitude_fin2=0.79,
            altitude_i_ex_trajectory=trajectory,
            vo2_dt_min=5.0,
        )
        record: dict[str, object] = asdict(extract_features(profile))
        target = float(row["risk_of_decompression_sickness"]) / 100.0
        record.update(
            source_cell_id=int(source_cell_id),
            altitude=int(row["altitude"]),
            prebreathing_time=int(row["prebreathing_time"]),
            exercise_level=exercise,
            time_at_altitude=int(row["time_at_altitude"]),
            pdcs_adrac_target=target,
            pdcs_3rut_mbe1=target,
        )
        records.append(record)
    return pd.DataFrame.from_records(records)


def _indices_where(df: pd.DataFrame, mask: pd.Series | np.ndarray) -> np.ndarray:
    return df.index[np.asarray(mask, dtype=bool)].to_numpy(dtype=int)


def build_structured_holdouts(df: pd.DataFrame) -> list[HoldoutFold]:
    """Build the locked reviewer holdouts over altitude, prebreathe, duration,
    exercise, and altitude-by-duration regions.

    Within each family, folds partition the full grid exactly once.
    """
    required = {
        "altitude",
        "prebreathing_time",
        "exercise_level",
        "time_at_altitude",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"structured-holdout columns missing: {missing}")

    folds: list[HoldoutFold] = []
    altitude_masks: list[tuple[str, np.ndarray]] = []
    for lower, upper, label in _ALTITUDE_BANDS:
        mask = (df["altitude"] >= lower) & (df["altitude"] < upper)
        indices = _indices_where(df, mask)
        altitude_masks.append((label, indices))
        folds.append(HoldoutFold("altitude_band", label, indices))

    for value in (0, 15, 30, 45, 60):
        indices = _indices_where(df, df["prebreathing_time"] == value)
        folds.append(HoldoutFold("prebreathe_level", f"{value} min", indices))

    duration_masks: list[tuple[str, np.ndarray]] = []
    for lower, upper, label in _DURATION_BANDS:
        mask = (df["time_at_altitude"] >= lower) & (df["time_at_altitude"] <= upper)
        indices = _indices_where(df, mask)
        duration_masks.append((label, indices))
        folds.append(HoldoutFold("duration_band", label, indices))

    for value in ("Rest", "Mild", "Heavy"):
        indices = _indices_where(df, df["exercise_level"] == value)
        folds.append(HoldoutFold("exercise_level", value, indices))

    for altitude_label, altitude_indices in altitude_masks:
        altitude_set = set(altitude_indices.tolist())
        for duration_label, duration_indices in duration_masks:
            region = np.asarray(
                sorted(altitude_set.intersection(duration_indices.tolist())), dtype=int
            )
            folds.append(
                HoldoutFold(
                    "altitude_x_duration",
                    f"{altitude_label} × {duration_label}",
                    region,
                )
            )

    empty = [f"{fold.family}: {fold.label}" for fold in folds if fold.test_indices.size == 0]
    if empty:
        raise ValueError(f"empty structured holdouts: {empty}")
    return folds


def split_train_calibration(
    all_indices: Iterable[int],
    test_indices: Iterable[int],
    *,
    seed: int,
    calibration_fraction: float = 0.20,
) -> tuple[np.ndarray, np.ndarray]:
    """Split all non-test cells 80/20 into training and calibration sets."""
    if not 0.0 < calibration_fraction < 1.0:
        raise ValueError("calibration_fraction must be in (0, 1)")
    all_idx = np.asarray(list(all_indices), dtype=int)
    test_idx = np.asarray(list(test_indices), dtype=int)
    if np.unique(all_idx).size != all_idx.size:
        raise ValueError("all_indices contains duplicates")
    if not set(test_idx).issubset(set(all_idx)):
        raise ValueError("test_indices must be a subset of all_indices")
    remaining = np.asarray(sorted(set(all_idx).difference(test_idx)), dtype=int)
    if remaining.size < 25:
        raise ValueError("at least 25 non-test rows are required")
    rng = np.random.default_rng(seed)
    shuffled = rng.permutation(remaining)
    n_cal = round(shuffled.size * calibration_fraction)
    n_cal = max(20, min(n_cal, shuffled.size - 1))
    calibration = shuffled[:n_cal]
    train = shuffled[n_cal:]
    return train, calibration


def random_train_cal_test_split(
    all_indices: Iterable[int],
    *,
    seed: int,
    calibration_fraction: float = 0.15,
    test_fraction: float = 0.15,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return the locked random 70/15/15 development split."""
    if not 0.0 < calibration_fraction < 1.0:
        raise ValueError("calibration_fraction must be in (0, 1)")
    if not 0.0 < test_fraction < 1.0:
        raise ValueError("test_fraction must be in (0, 1)")
    if calibration_fraction + test_fraction >= 1.0:
        raise ValueError("calibration and test fractions must leave training rows")
    all_idx = np.asarray(list(all_indices), dtype=int)
    if np.unique(all_idx).size != all_idx.size:
        raise ValueError("all_indices contains duplicates")
    shuffled = np.random.default_rng(seed).permutation(all_idx)
    n_test = round(all_idx.size * test_fraction)
    n_calibration = round(all_idx.size * calibration_fraction)
    n_train = all_idx.size - n_test - n_calibration
    train = shuffled[:n_train]
    calibration = shuffled[n_train : n_train + n_calibration]
    test = shuffled[n_train + n_calibration :]
    return train, calibration, test


def _validate_fixed_split(
    df: pd.DataFrame,
    train_indices: Iterable[int],
    calibration_indices: Iterable[int],
) -> tuple[np.ndarray, np.ndarray]:
    train = np.asarray(list(train_indices), dtype=int)
    calibration = np.asarray(list(calibration_indices), dtype=int)
    if train.size == 0 or calibration.size < 20:
        raise ValueError("fixed split requires training rows and at least 20 calibration rows")
    if set(train).intersection(calibration):
        raise ValueError("training and calibration indices overlap")
    available = set(df.index.to_numpy(dtype=int))
    if not set(train).union(calibration).issubset(available):
        raise ValueError("fixed split contains indices outside the dataframe")
    return train, calibration


def fit_variant_on_split(
    df: pd.DataFrame,
    *,
    feature_names: list[str],
    target_col: str,
    train_indices: Iterable[int],
    calibration_indices: Iterable[int],
    variant: str,
    config: TrainConfig | None = None,
    confidence: float = 0.95,
    altitude_band_feature: str = "altitude_ft",
    altitude_band_width: float = 5000.0,
    altitude_band_origin: float = 18000.0,
    zi_gate_threshold: float = 0.5,
    zi_zero_upper_bound: float = 0.02,
) -> TinyDcsSurrogate:
    """Fit one interval variant on caller-supplied train/calibration cells.

    Unlike :func:`tinydcs.surrogate.train_surrogate`, this function never
    repartitions rows.  It is therefore suitable for prespecified contiguous
    holdouts where any hidden random test split would waste data or leak cells.
    """
    allowed = {
        "global_conformal",
        "mondrian_conformal",
        "global_cqr",
        "mondrian_cqr",
        "zero_inflated",
    }
    if variant not in allowed:
        raise ValueError(f"unknown variant '{variant}'; expected one of {sorted(allowed)}")
    missing = [name for name in [*feature_names, target_col] if name not in df]
    if missing:
        raise ValueError(f"model columns missing: {missing}")
    train, calibration = _validate_fixed_split(df, train_indices, calibration_indices)
    cfg = config or TrainConfig()

    train_df = df.loc[train]
    calibration_df = df.loc[calibration]
    X_train = train_df[feature_names].to_numpy(dtype=float)
    X_calibration = calibration_df[feature_names].to_numpy(dtype=float)
    y_train = train_df[target_col].to_numpy(dtype=float)
    y_calibration = calibration_df[target_col].to_numpy(dtype=float)

    common = {
        "n_estimators": cfg.n_estimators,
        "learning_rate": cfg.learning_rate,
        "num_leaves": cfg.num_leaves,
        "max_depth": cfg.max_depth,
        "min_data_in_leaf": cfg.min_data_in_leaf,
        "subsample": cfg.subsample,
        "subsample_freq": cfg.subsample_freq,
        "colsample_bytree": cfg.colsample_bytree,
        "reg_alpha": cfg.reg_alpha,
        "reg_lambda": cfg.reg_lambda,
        "random_state": cfg.random_state,
        "verbosity": -1,
    }
    monotone = [int(cfg.monotonic_constraints.get(name, 0)) for name in feature_names]
    y_all_shrunk = _smithson_verkuilen(df[target_col].to_numpy(dtype=float), n=len(df))
    y_all_logit = _logit(y_all_shrunk)
    y_logit = pd.Series(y_all_logit, index=df.index)

    if variant == "zero_inflated":
        conformal = fit_zero_inflated(
            X_train=X_train,
            y_train=y_train,
            X_cal=X_calibration,
            y_cal=y_calibration,
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
        # The zero-inflated predict path uses the two-stage calibration models
        # for its point and interval.  Reusing the continuous model here avoids
        # fitting an otherwise unused third model.
        model = conformal.continuous_model
    else:
        model = lgb.LGBMRegressor(
            **common,
            monotone_constraints=monotone,
            monotone_constraints_method="advanced",
        )
        model.fit(pd.DataFrame(X_train, columns=feature_names), y_logit.loc[train])
        calibration_prediction = np.asarray(
            model.predict(pd.DataFrame(X_calibration, columns=feature_names)), dtype=float
        )
        calibration_residual = y_logit.loc[calibration].to_numpy() - calibration_prediction

        if variant == "global_conformal":
            conformal = fit_conformal(calibration_residual, confidence=confidence)
        elif variant == "mondrian_conformal":
            if altitude_band_feature not in feature_names:
                raise ValueError(f"'{altitude_band_feature}' is required for Mondrian conformal")
            band_col = feature_names.index(altitude_band_feature)
            conformal = fit_mondrian_conformal(
                calibration_residual,
                X_calibration[:, band_col],
                group_feature=altitude_band_feature,
                band_width=altitude_band_width,
                band_origin=altitude_band_origin,
                confidence=confidence,
            )
        else:
            use_mondrian = variant == "mondrian_cqr"
            conformal = fit_cqr(
                X_train=X_train,
                y_logit_train=y_logit.loc[train].to_numpy(),
                X_cal=X_calibration,
                y_logit_cal=y_logit.loc[calibration].to_numpy(),
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
                band_feature=altitude_band_feature if use_mondrian else None,
                band_width=altitude_band_width if use_mondrian else None,
                band_origin=altitude_band_origin,
            )

    return TinyDcsSurrogate(
        feature_names=list(feature_names),
        model=model,
        ood=fit_ood(X_train),
        conformal=conformal,
    )


def interval_efficiency(
    y_true: np.ndarray,
    y_lower: np.ndarray,
    y_upper: np.ndarray,
    *,
    nominal: float = 0.95,
) -> dict[str, float | int]:
    """Coverage plus probability-scale interval-width distribution."""
    y = np.asarray(y_true, dtype=float).ravel()
    lower = np.asarray(y_lower, dtype=float).ravel()
    upper = np.asarray(y_upper, dtype=float).ravel()
    if not (y.size == lower.size == upper.size):
        raise ValueError("y_true, y_lower, and y_upper must have equal lengths")
    if y.size == 0:
        raise ValueError("interval efficiency requires at least one row")
    if np.any(upper < lower):
        raise ValueError("interval upper bounds must be >= lower bounds")
    covered = (y >= lower) & (y <= upper)
    width = upper - lower
    return {
        "n": int(y.size),
        "n_covered": int(covered.sum()),
        "coverage": float(covered.mean()),
        "nominal": float(nominal),
        "mean_width": float(np.mean(width)),
        "median_width": float(np.median(width)),
        "p90_width": float(np.quantile(width, 0.90)),
        "max_width": float(np.max(width)),
    }


def cluster_bootstrap_coverage_ci(
    covered: np.ndarray,
    cluster_ids: np.ndarray,
    *,
    n_boot: int = 10_000,
    seed: int = 2026,
    confidence: float = 0.95,
) -> dict[str, float | int]:
    """Percentile CI after resampling source-grid clusters with replacement."""
    values = np.asarray(covered, dtype=bool).ravel()
    clusters = np.asarray(cluster_ids, dtype=object).ravel()
    if values.size != clusters.size or values.size == 0:
        raise ValueError("covered and cluster_ids must have the same non-zero length")
    if n_boot < 100:
        raise ValueError("n_boot must be at least 100")
    codes, uniques = pd.factorize(clusters, sort=True)
    n_clusters = len(uniques)
    if n_clusters < 2:
        return {
            "lower": float(values.mean()),
            "upper": float(values.mean()),
            "confidence": float(confidence),
            "n_clusters": n_clusters,
            "n_boot": int(n_boot),
        }

    cluster_n = np.bincount(codes, minlength=n_clusters).astype(float)
    cluster_covered = np.bincount(codes, weights=values.astype(float), minlength=n_clusters)
    rng = np.random.default_rng(seed)
    sampled = rng.integers(0, n_clusters, size=(int(n_boot), n_clusters))
    rates = cluster_covered[sampled].sum(axis=1) / cluster_n[sampled].sum(axis=1)
    alpha = 1.0 - float(confidence)
    lower, upper = np.quantile(rates, [alpha / 2.0, 1.0 - alpha / 2.0])
    return {
        "lower": float(lower),
        "upper": float(upper),
        "confidence": float(confidence),
        "n_clusters": n_clusters,
        "n_boot": int(n_boot),
    }


def assign_source_risk_strata(risk: np.ndarray) -> tuple[np.ndarray, list[float]]:
    """Assign exact zero plus quartiles of the non-zero source-model risk."""
    values = np.asarray(risk, dtype=float).ravel()
    if values.size == 0 or not np.isfinite(values).all():
        raise ValueError("risk must be a non-empty finite vector")
    positive = values[values > 0.0]
    if positive.size < 4:
        raise ValueError("at least four non-zero risks are required")
    cutpoints = np.quantile(positive, [0.25, 0.50, 0.75]).astype(float)
    labels = np.full(values.size, "exact zero", dtype=object)
    q_labels = np.asarray(["nonzero Q1", "nonzero Q2", "nonzero Q3", "nonzero Q4"])
    nonzero = values > 0.0
    labels[nonzero] = q_labels[np.searchsorted(cutpoints, values[nonzero], side="right")]
    return labels.astype(str), cutpoints.tolist()


def boundary_shell_mask(df: pd.DataFrame) -> pd.Series:
    """Mark cells on any continuous edge of the supported source envelope."""
    columns = ("altitude", "prebreathing_time", "time_at_altitude")
    missing = [column for column in columns if column not in df]
    if missing:
        raise ValueError(f"boundary-shell columns missing: {missing}")
    mask = pd.Series(False, index=df.index)
    for column in columns:
        mask |= df[column].eq(df[column].min()) | df[column].eq(df[column].max())
    return mask
