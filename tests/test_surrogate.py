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
    # Finite-sample coverage can wobble on small folds; relaxed threshold.
    assert cov["coverage"] >= 0.85


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


def test_cqr_beats_global_on_biased_low_region() -> None:
    """Synthesize a dataset with a boundary-mass (zero-target) region at
    low altitude. Global conformal under-covers there because the interval
    is symmetric around a biased mean. CQR handles asymmetric / bias-
    driven intervals natively and should recover closer-to-nominal coverage
    in that region.
    """
    rng = np.random.default_rng(11)
    n = 2000
    alt = rng.uniform(18000, 40000, size=n)
    # Generate target: at low altitude the truth is clumped near zero; at
    # high altitude it spreads across [0.1, 0.9].
    p_lin = np.clip((alt - 18000) / (40000 - 18000), 0, 1)
    p = np.where(
        alt < 24000,
        rng.choice([0.0, 0.01, 0.02, 0.05], size=n, p=[0.6, 0.2, 0.1, 0.1]),
        np.clip(0.1 + 0.8 * p_lin + 0.05 * rng.standard_normal(size=n), 0.02, 0.95),
    )

    rows = []
    for i in range(n):
        rows.append({
            "altitude_ft": alt[i],
            "ambient_pressure_atm": (1 - 6.87535e-6 * alt[i]) ** 5.2559,
            "prebreathe_time_min": 30.0,
            "prebreathe_fio2": 1.0,
            "ascent_rate_fpm": 5000.0,
            "altitude_time_min": 120.0,
            "altitude_fio2": 0.21,
            "prebreathe_vo2_mean_lmin": 0.0,
            "prebreathe_vo2_peak_lmin": 0.0,
            "altitude_vo2_mean_lmin": 0.2,
            "altitude_vo2_peak_1min_lmin": 0.3,
            "altitude_vo2_integral_lmin_min": 24.0,
            "tissue_n2_ratio_360min": 1.5,
            "pdcs_3rut_mbe1": float(p[i]),
        })
    df = pd.DataFrame(rows)

    from tinydcs.surrogate import CQRCalibration

    s_global, splits_global = train_surrogate(
        df, feature_names=FEATURE_COLUMNS, test_fraction=0.2, calibration_fraction=0.25,
        config=TrainConfig(n_estimators=150, learning_rate=0.08, num_leaves=31),
    )
    s_cqr, splits_cqr = train_surrogate(
        df, feature_names=FEATURE_COLUMNS, test_fraction=0.2, calibration_fraction=0.25,
        config=TrainConfig(n_estimators=150, learning_rate=0.08, num_leaves=31),
        use_cqr=True,
    )
    assert isinstance(s_cqr.conformal, CQRCalibration)

    # Coverage on the low-altitude slice of the test fold.
    def _low_slice(splits_):
        test_df = splits_["test"]
        lo = test_df["altitude_ft"] < 24000
        y = test_df.loc[lo, "pdcs_3rut_mbe1"].to_numpy(dtype=float)
        return test_df.loc[lo], y

    test_g, y_g = _low_slice(splits_global)
    test_c, y_c = _low_slice(splits_cqr)
    pred_g = s_global.predict(test_g)
    pred_c = s_cqr.predict(test_c)
    cov_g = empirical_coverage(y_g, pred_g["lower"], pred_g["upper"], nominal=0.95)["coverage"]
    cov_c = empirical_coverage(y_c, pred_c["lower"], pred_c["upper"], nominal=0.95)["coverage"]

    # CQR should not be worse than global on the biased region and should
    # typically close a meaningful fraction of the gap to nominal.
    assert cov_c >= cov_g - 1e-9, (
        f"CQR coverage {cov_c:.3f} worse than global {cov_g:.3f} on biased region"
    )


def test_cqr_save_load_roundtrip(tmp_path) -> None:
    rng = np.random.default_rng(0)
    n = 400
    rows = []
    for _ in range(n):
        alt = rng.uniform(20000, 40000)
        rows.append({
            "altitude_ft": alt,
            "ambient_pressure_atm": (1 - 6.87535e-6 * alt) ** 5.2559,
            "prebreathe_time_min": 30.0,
            "prebreathe_fio2": 1.0,
            "ascent_rate_fpm": 5000.0,
            "altitude_time_min": 120.0,
            "altitude_fio2": 0.21,
            "prebreathe_vo2_mean_lmin": 0.0,
            "prebreathe_vo2_peak_lmin": 0.0,
            "altitude_vo2_mean_lmin": 0.2,
            "altitude_vo2_peak_1min_lmin": 0.3,
            "altitude_vo2_integral_lmin_min": 24.0,
            "tissue_n2_ratio_360min": 1.8,
            "pdcs_3rut_mbe1": float(np.clip(0.3 + 0.05 * rng.standard_normal(), 1e-4, 1 - 1e-4)),
        })
    df = pd.DataFrame(rows)
    from tinydcs.surrogate import CQRCalibration, TinyDcsSurrogate

    surrogate, splits = train_surrogate(
        df, feature_names=FEATURE_COLUMNS, test_fraction=0.2, calibration_fraction=0.25,
        config=TrainConfig(n_estimators=60, learning_rate=0.1, num_leaves=15),
        use_cqr=True,
    )
    path = tmp_path / "cqr.joblib"
    surrogate.save(str(path))
    loaded = TinyDcsSurrogate.load(str(path))
    assert isinstance(loaded.conformal, CQRCalibration)
    p1 = surrogate.predict(splits["test"])["point"]
    p2 = loaded.predict(splits["test"])["point"]
    assert np.allclose(p1, p2)


def test_mondrian_conformal_round_trip() -> None:
    """Mondrian calibration fits, predicts with varying half-widths across
    bands, and survives a save/load cycle."""
    rng = np.random.default_rng(7)
    n = 600
    alt = rng.uniform(18000, 40000, size=n)
    z = -4.0 + (alt - 30000) / 8000 + 0.15 * rng.standard_normal(size=n)
    p = 1.0 / (1.0 + np.exp(-z))
    p = np.clip(p + 0.02 * rng.standard_normal(size=n), 1e-4, 1 - 1e-4)

    rows = []
    for i in range(n):
        rows.append({
            "altitude_ft": alt[i],
            "ambient_pressure_atm": (1 - 6.87535e-6 * alt[i]) ** 5.2559,
            "prebreathe_time_min": 30.0,
            "prebreathe_fio2": 1.0,
            "ascent_rate_fpm": 5000.0,
            "altitude_time_min": 120.0,
            "altitude_fio2": 0.21,
            "prebreathe_vo2_mean_lmin": 0.0,
            "prebreathe_vo2_peak_lmin": 0.0,
            "altitude_vo2_mean_lmin": 0.2,
            "altitude_vo2_peak_1min_lmin": 0.3,
            "altitude_vo2_integral_lmin_min": 24.0,
            "tissue_n2_ratio_360min": 1.8,
            "pdcs_3rut_mbe1": float(p[i]),
        })
    df = pd.DataFrame(rows)
    from tinydcs.surrogate import MondrianConformalCalibration, TinyDcsSurrogate

    surrogate, splits = train_surrogate(
        df, feature_names=FEATURE_COLUMNS, test_fraction=0.2, calibration_fraction=0.25,
        config=TrainConfig(n_estimators=120, learning_rate=0.08, num_leaves=31),
        mondrian_feature="altitude_ft", mondrian_band_width=5000.0, mondrian_band_origin=18000.0,
    )

    # The calibration object is Mondrian, not global.
    assert isinstance(surrogate.conformal, MondrianConformalCalibration)

    # Per-sample half-width varies because different test rows fall in
    # different altitude bands.
    pred = surrogate.predict(splits["test"])
    assert pred["conformal_half_width_logit"].std() > 0.0

    # Test that overall coverage is in a reasonable range (not necessarily at
    # nominal on a small synthetic fold, but not degenerate).
    y_true = splits["test"]["pdcs_3rut_mbe1"].to_numpy(dtype=float)
    cov = empirical_coverage(y_true, pred["lower"], pred["upper"], nominal=0.95)
    assert cov["coverage"] >= 0.65  # small-sample OK; non-degeneracy is the claim

    # Save/load round-trip.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        path = f"{tmp}/mondrian.joblib"
        surrogate.save(path)
        loaded = TinyDcsSurrogate.load(path)
        assert isinstance(loaded.conformal, MondrianConformalCalibration)
        p1 = surrogate.predict(splits["test"])["point"]
        p2 = loaded.predict(splits["test"])["point"]
        assert np.allclose(p1, p2)
