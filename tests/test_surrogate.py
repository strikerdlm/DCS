"""Unit tests for tinydcs.surrogate and tinydcs.metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from tinydcs.features import FEATURE_COLUMNS
from tinydcs.metrics import brier_score, point_errors, empirical_coverage
from tinydcs.surrogate import TrainConfig, train_surrogate


@pytest.fixture
def toy_dataset() -> pd.DataFrame:
    """Synthetic dataset with a known monotone target on the logit scale."""
    rng = np.random.default_rng(0)
    n = 800
    rows = []
    for _ in range(n):
        alt = rng.uniform(18000, 40000)
        pt = rng.uniform(0, 180)
        vo2 = rng.uniform(0, 0.8)
        at_t = rng.uniform(10, 240)
        tr_noise = rng.uniform(0.0, 0.5)
        # A monotonic synthetic P(DCS) grows with altitude/time, shrinks with PB.
        z = -4.0 + (alt - 30000) / 5000 + at_t / 120 + vo2 - pt / 90
        p = 1.0 / (1.0 + np.exp(-z))
        rows.append({
            "altitude_ft": alt,
            "ambient_pressure_atm": (1 - 6.87535e-6 * alt) ** 5.2559,
            "prebreathe_time_min": pt,
            "prebreathe_fio2": 1.0,
            "ascent_rate_fpm": 5000.0,
            "altitude_time_min": at_t,
            "altitude_fio2": 0.21,
            "prebreathe_vo2_mean_lmin": 0.0,
            "prebreathe_vo2_peak_lmin": 0.0,
            "altitude_vo2_mean_lmin": vo2,
            "altitude_vo2_peak_1min_lmin": vo2 * 1.3,
            "altitude_vo2_integral_lmin_min": vo2 * at_t,
            "tissue_n2_ratio_360min": 1.5 + tr_noise,
            "pdcs_3rut_mbe1": float(np.clip(p + 0.01 * rng.standard_normal(), 1e-4, 1 - 1e-4)),
        })
    return pd.DataFrame(rows)


def test_surrogate_end_to_end(toy_dataset: pd.DataFrame) -> None:
    surrogate, splits = train_surrogate(
        toy_dataset,
        feature_names=FEATURE_COLUMNS,
        test_fraction=0.2,
        calibration_fraction=0.2,
        config=TrainConfig(n_estimators=200, learning_rate=0.08, num_leaves=31),
    )

    pred = surrogate.predict(splits["test"])
    assert pred["point"].shape == (len(splits["test"]),)
    assert np.all(pred["point"] >= 0.0) and np.all(pred["point"] <= 1.0)
    assert np.all(pred["lower"] <= pred["point"] + 1e-9)
    assert np.all(pred["upper"] >= pred["point"] - 1e-9)

    y_true = splits["test"]["pdcs_3rut_mbe1"].to_numpy(dtype=float)
    metrics = point_errors(y_true, pred["point"])
    assert metrics["r2"] > 0.85
    assert metrics["mae"] < 0.10


def test_conformal_coverage_on_toy(toy_dataset: pd.DataFrame) -> None:
    surrogate, splits = train_surrogate(
        toy_dataset,
        feature_names=FEATURE_COLUMNS,
        test_fraction=0.2,
        calibration_fraction=0.2,
        config=TrainConfig(n_estimators=200, learning_rate=0.08, num_leaves=31),
    )
    pred = surrogate.predict(splits["test"])
    y_true = splits["test"]["pdcs_3rut_mbe1"].to_numpy(dtype=float)
    cov = empirical_coverage(y_true, pred["lower"], pred["upper"], nominal=0.95)
    # Finite-sample coverage can wobble a few points under nominal on small folds.
    assert cov["coverage"] >= 0.88


def test_surrogate_save_load_roundtrip(toy_dataset: pd.DataFrame, tmp_path) -> None:
    surrogate, splits = train_surrogate(
        toy_dataset,
        feature_names=FEATURE_COLUMNS,
        test_fraction=0.2,
        calibration_fraction=0.2,
        config=TrainConfig(n_estimators=100, learning_rate=0.08, num_leaves=31),
    )
    path = tmp_path / "surrogate.joblib"
    surrogate.save(str(path))
    from tinydcs.surrogate import TinyDcsSurrogate

    loaded = TinyDcsSurrogate.load(str(path))
    p_orig = surrogate.predict(splits["test"])
    p_load = loaded.predict(splits["test"])
    assert np.allclose(p_orig["point"], p_load["point"])


def test_brier_score_zero_on_perfect_pred() -> None:
    y = np.array([0.1, 0.5, 0.9, 0.3])
    assert brier_score(y, y) == pytest.approx(0.0)
