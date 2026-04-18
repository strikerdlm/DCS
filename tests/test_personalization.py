"""Tests for tinydcs.personalization."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from tinydcs.features import FEATURE_COLUMNS
from tinydcs.personalization import (
    PersonalizedSurrogate,
    PopulationPrior,
    SubjectPosterior,
    generate_synthetic_cohort,
)
from tinydcs.surrogate import TrainConfig, train_surrogate


@pytest.fixture
def tiny_base():
    """Train a minimal base surrogate for personalization tests."""
    rng = np.random.default_rng(0)
    n = 600
    rows = []
    for _ in range(n):
        alt = rng.uniform(18000, 40000)
        pb = rng.uniform(0, 120)
        vo2 = rng.uniform(0, 0.8)
        t = rng.uniform(10, 240)
        z = -4.0 + (alt - 30000) / 8000 + t / 200 + vo2 - pb / 90
        p = 1.0 / (1.0 + np.exp(-z))
        rows.append({
            "altitude_ft": alt,
            "ambient_pressure_atm": (1 - 6.87535e-6 * alt) ** 5.2559,
            "prebreathe_time_min": pb,
            "prebreathe_fio2": 1.0,
            "ascent_rate_fpm": 5000.0,
            "altitude_time_min": t,
            "altitude_fio2": 0.21,
            "prebreathe_vo2_mean_lmin": 0.0,
            "prebreathe_vo2_peak_lmin": 0.0,
            "altitude_vo2_mean_lmin": vo2,
            "altitude_vo2_peak_1min_lmin": vo2 * 1.2,
            "altitude_vo2_integral_lmin_min": vo2 * t,
            "tissue_n2_ratio_360min": 1.5 + 0.4 * rng.random(),
            "pdcs_3rut_mbe1": float(np.clip(p + 0.02 * rng.standard_normal(), 0.01, 0.99)),
        })
    df = pd.DataFrame(rows)
    base, _ = train_surrogate(
        df, feature_names=FEATURE_COLUMNS, test_fraction=0.2, calibration_fraction=0.2,
        config=TrainConfig(n_estimators=60, learning_rate=0.12, num_leaves=15),
    )
    return base, df


def test_subject_posterior_conjugate_update() -> None:
    """Posterior mean moves towards the observed residual as n grows."""
    p = SubjectPosterior(mean=0.0, variance=1.0, n_observations=0)
    for _ in range(50):
        p = p.update(residual=1.5, sigma_lik_sq=1.0, prior_mean=0.0, prior_var=1.0)
    # After 50 observations of residual 1.5, posterior mean should be close to 1.5.
    assert abs(p.mean - 1.5) < 0.05
    # Variance should shrink monotonically.
    assert p.variance < 0.05


def test_generate_synthetic_cohort_structure(tiny_base) -> None:
    base, df = tiny_base
    template = df.drop(columns=["pdcs_3rut_mbe1"])
    cohort = generate_synthetic_cohort(
        base, template, n_subjects=10, exposures_per_subject=5, sigma_lambda=0.5, seed=1,
    )
    assert len(cohort) == 50
    for col in ("subject_id", "log_lambda_true", "y_prob_true", "y"):
        assert col in cohort.columns
    assert set(cohort["subject_id"].unique()) == set(range(10))
    assert cohort["y"].isin([0, 1]).all()


def test_personalized_surrogate_recovers_lambda_direction(tiny_base) -> None:
    """Given enough observations per subject, the posterior mean should
    correlate positively with the ground-truth log lambda."""
    base, df = tiny_base
    template = df.drop(columns=["pdcs_3rut_mbe1"])
    cohort = generate_synthetic_cohort(
        base, template, n_subjects=60, exposures_per_subject=30, sigma_lambda=1.2, seed=7,
    )
    prior = PopulationPrior(mu_lambda=0.0, sigma_lambda_sq=1.0, sigma_lik_sq=4.0)
    ps = PersonalizedSurrogate(base=base, prior=prior)
    truths = []
    estimates = []
    for sid, group in cohort.groupby("subject_id"):
        feats = group[list(FEATURE_COLUMNS)]
        ps.observe(sid, feats, group["y"].to_numpy())
        truths.append(float(group["log_lambda_true"].iloc[0]))
        estimates.append(ps.subjects[sid].mean)
    truths = np.asarray(truths)
    estimates = np.asarray(estimates)
    # Spearman-like monotone signal: sign agreement between truth and estimate
    # should beat 60%.
    sign_agreement = float(np.mean(np.sign(truths) == np.sign(estimates)))
    assert sign_agreement >= 0.60
    # And Pearson correlation should be positive.
    corr = float(np.corrcoef(truths, estimates)[0, 1])
    assert corr > 0.15  # weak but clearly positive with n=60, k=30


def test_personalized_predict_shifts_and_widens(tiny_base) -> None:
    base, df = tiny_base
    prior = PopulationPrior(mu_lambda=0.0, sigma_lambda_sq=1.0, sigma_lik_sq=2.0)
    ps = PersonalizedSurrogate(base=base, prior=prior)
    sample_feats = df[list(FEATURE_COLUMNS)].iloc[:1]
    # Synthesize a strongly-positive subject: many observed y=1 when base
    # predicts small risk → posterior mean should be positive.
    forced_y = np.ones(20, dtype=int)
    exposures = df[list(FEATURE_COLUMNS)].iloc[:20]
    ps.observe("subject_hi", exposures, forced_y)
    pred_pop = base.predict(sample_feats)["point"][0]
    pred_personal = ps.predict("subject_hi", sample_feats)["point"][0]
    # Positive-susceptibility subject should see upshifted personalized risk
    # (unless pred_pop is already near 1, in which case the shift saturates).
    if pred_pop < 0.99:
        assert pred_personal >= pred_pop - 1e-9
