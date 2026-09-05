"""Regression tests for previously overstated model-emulation accuracy."""
import numpy as np
import pandas as pd
import pytest

from tinydcs.metrics import brier_score, point_errors, empirical_coverage
from tinydcs.surrogate import (
    fit_conformal, fit_ood, fit_zero_inflated, train_surrogate, TrainConfig,
)


def test_unattainable_finite_sample_conformal_rank_is_unbounded():
    assert np.isinf(fit_conformal(np.arange(20), confidence=0.99).q)


@pytest.mark.parametrize("confidence", [0, 1, float("nan")])
def test_invalid_conformal_confidence_is_rejected(confidence):
    with pytest.raises(ValueError):
        fit_conformal(np.arange(20), confidence)


def test_ood_is_invariant_to_feature_units_and_checks_constant_features():
    rng = np.random.default_rng(123)
    X = np.column_stack([rng.normal(size=200), rng.normal(size=200), np.ones(200)])
    converted = X * [10000, 0.001, 1]
    a, b = fit_ood(X), fit_ood(converted)
    assert a.distance(X) == pytest.approx(b.distance(converted), rel=1e-10)
    assert not a.is_in_envelope(np.array([[0, 0, 2]]))[0]


def test_zero_inflated_calibrates_final_mixture_in_probability_units():
    X = np.zeros((240, 1))
    y = np.tile([0.0, 0.7], 120)
    X_cal = np.zeros((40, 1))
    y_cal = np.tile([0.0, 0.9], 20)
    cal = fit_zero_inflated(X, y, X_cal, y_cal, feature_names=["x"], n_estimators=5)
    frame = pd.DataFrame(X_cal, columns=["x"])
    pzero = cal.zero_classifier.predict_proba(frame)[:, 1]
    continuous = 1 / (1 + np.exp(-cal.continuous_model.predict(frame)))
    expected = fit_conformal(y_cal - (1 - pzero) * continuous).q
    assert cal.probability_q == pytest.approx(expected)


def test_transform_inverse_restores_exact_boundary_targets():
    from tinydcs.surrogate import _smithson_verkuilen, _inverse_smithson_verkuilen
    y = np.array([0, 0.1, 0.5, 0.9, 1])
    assert _inverse_smithson_verkuilen(_smithson_verkuilen(y, 100), 100) == pytest.approx(y)


def test_training_retains_partition_ids_and_training_transform_size():
    df = pd.DataFrame({"x": np.arange(200), "y": np.linspace(0, 1, 200)}, index=np.arange(200)+1000)
    model, splits = train_surrogate(df, ["x"], "y", config=TrainConfig(n_estimators=5))
    assert [len(splits[k]) for k in ["train", "cal", "test"]] == [130, 40, 30]
    assert model.target_transform_n == 130
    ids = [set(s.index) for s in splits.values()]
    assert not ids[0] & ids[1] and not ids[0] & ids[2] and not ids[1] & ids[2]
    assert set.union(*ids) == set(df.index)


def test_empty_or_constant_metrics_are_unavailable_not_perfect():
    empty = point_errors(np.array([]), np.array([]))
    assert empty["n"] == 0 and empty["mae"] is None and empty["r2"] is None
    assert point_errors(np.ones(3), np.zeros(3))["r2"] is None
    assert empirical_coverage(np.array([]), np.array([]), np.array([]))["coverage"] is None


def test_brier_requires_observed_binary_outcomes():
    with pytest.raises(ValueError, match="binary"):
        brier_score(np.array([0.2, 0.7]), np.array([0.2, 0.7]))


def test_separated_binary_calibration_has_no_finite_mle():
    from tinydcs.metrics import calibration_slope_intercept
    assert calibration_slope_intercept([0, 0, 1, 1], [.1, .2, .8, .9]) == (None, None)


def test_invalid_metrics_are_not_silently_dropped_or_clipped():
    with pytest.raises(ValueError):
        point_errors(np.array([0.1, np.nan]), np.array([0.1, 0.2]))
    with pytest.raises(ValueError):
        empirical_coverage(np.array([0.1]), np.array([0.5]), np.array([0.1]))


def test_cumulative_surrogate_excludes_opposing_duration_proxies():
    # Exit tissue ratio decreases as duration grows; it is not an independent
    # predictor of a cumulative endpoint. Integral and peak can also change
    # along a duration sweep independently of a declared constant workload.
    n = 600
    df = pd.DataFrame({"altitude_time_min": np.arange(n)%240+1,
                       "tissue_n2_ratio_360min": np.linspace(2, 1, n),
                       "altitude_vo2_integral_lmin_min": np.linspace(0, 240, n),
                       "y": np.where(np.arange(n)%240 < 50, 0, .5)})
    model, _ = train_surrogate(df, list(df.columns[:-1]), "y", use_zero_inflated=True,
                               config=TrainConfig(n_estimators=30))
    assert "tissue_n2_ratio_360min" not in model.feature_names
    assert "altitude_vo2_integral_lmin_min" not in model.feature_names
    query = pd.DataFrame({"altitude_time_min": np.arange(1,241),
                          "tissue_n2_ratio_360min": np.linspace(2,1,240),
                          "altitude_vo2_integral_lmin_min": np.arange(1,241)})
    assert np.all(np.diff(model.predict(query)["point"]) >= -1e-12)


def test_quantitative_release_requires_evidence_and_input_support():
    df = pd.DataFrame({"x": np.arange(200), "y": np.linspace(0, 1, 200)})
    model, splits = train_surrogate(df, ["x"], "y", config=TrainConfig(n_estimators=5))
    query = pd.concat([splits["test"], pd.DataFrame({"x": [1000]})], ignore_index=True)
    assert not model.predict(query)["quantitative_output_enabled"].any()
    model.metadata["quantitative_enabled"] = True
    released = model.predict(query)
    assert np.array_equal(released["quantitative_output_enabled"], released["in_envelope"])
    assert not released["quantitative_output_enabled"][-1]
    model.metadata["quantitative_enabled"] = False
    withheld = model.predict(query)
    assert not withheld["quantitative_output_enabled"].any()
    # Keep raw diagnostic predictions for evaluations of nonreleased candidates.
    assert withheld["point"] == pytest.approx(released["point"])
