"""Bernoulli log-odds susceptibility with deterministic 1D quadrature.

y_ij ~ Bernoulli(expit(logit(base_point(x_ij)) + delta_i)),
delta_i ~ Normal(mu, variance). All observations are retained; batching has no
statistical effect. Intervals are posterior credible intervals for probability
conditional on this assumed model, NOT conformal coverage or clinical validation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping
import numpy as np
import pandas as pd
from scipy.integrate import quad, quad_vec
from scipy.optimize import minimize_scalar, brentq
from scipy.special import expit
from .surrogate import TinyDcsSurrogate


def _logit(p):
    # A modelling floor keeps even an exact-zero emulator open to observed events.
    q = np.clip(np.asarray(p, dtype=float), 1e-10, 1 - 1e-10)
    return np.log(q) - np.log1p(-q)


@dataclass(slots=True)
class SubjectPosterior:
    mean: float = 0.0
    variance: float = 1.0
    n_observations: int = 0
    lower: float | None = None
    upper: float | None = None

    def update(self, residual, sigma_lik_sq, prior_mean, prior_var):
        """Legacy continuous-Gaussian residual helper; NEVER used for binary y."""
        if (
            not np.isfinite([residual, sigma_lik_sq, self.mean, self.variance]).all()
            or sigma_lik_sq <= 0
            or self.variance <= 0
        ):
            raise ValueError("finite residual and positive Gaussian variances required")
        variance = 1 / (1 / self.variance + 1 / sigma_lik_sq)
        return SubjectPosterior(
            variance * (self.mean / self.variance + residual / sigma_lik_sq),
            variance,
            self.n_observations + 1,
        )


@dataclass(slots=True)
class PopulationPrior:
    mu_lambda: float = 0.0
    sigma_lambda_sq: float = 0.5
    sigma_lik_sq: float = 1.0  # retained for continuous-residual EB only

    def __post_init__(self):
        if (
            not np.isfinite([self.mu_lambda, self.sigma_lambda_sq, self.sigma_lik_sq]).all()
            or self.sigma_lambda_sq <= 0
            or self.sigma_lik_sq <= 0
        ):
            raise ValueError("prior mean must be finite and variances positive")


def fit_population_prior(subject_residuals: Mapping[object, np.ndarray], *, min_observations=3):
    """Moment estimate from CONTINUOUS logit residuals, not shrunk binary y.

    The between-subject correction averages within-subject variance/n_i,
    respecting unequal sample sizes; excluded subjects contribute nothing.
    """
    eligible = [
        np.asarray(r, dtype=float).ravel()
        for r in subject_residuals.values()
        if len(r) >= min_observations
    ]
    if any(not np.isfinite(r).all() for r in eligible) or min_observations < 2:
        raise ValueError("finite residuals and min_observations >=2 required")
    if len(eligible) < 2:
        return PopulationPrior()
    means = np.array([r.mean() for r in eligible])
    variances = np.array([r.var(ddof=1) for r in eligible])
    sizes = np.array([len(r) for r in eligible])
    return PopulationPrior(
        float(means.mean()),
        float(max(means.var(ddof=1) - np.mean(variances / sizes), 1e-3)),
        float(max(np.sum((sizes - 1) * variances) / np.sum(sizes - 1), 1e-3)),
    )


def _distribution(offsets, outcomes, prior):
    """Mode-centered adaptive integration; stable even after repeated outcomes."""
    eta, y = np.asarray(offsets), np.asarray(outcomes)

    def log_density(delta):
        z = eta + delta
        return -((delta - prior.mu_lambda) ** 2) / (2 * prior.sigma_lambda_sq) + np.sum(
            y * z - np.logaddexp(0, z)
        )

    mode = float(
        minimize_scalar(
            lambda d: -log_density(d), bracket=(prior.mu_lambda - 1, prior.mu_lambda + 1)
        ).x
    )
    p = expit(eta + mode)
    scale = float(1 / np.sqrt(1 / prior.sigma_lambda_sq + np.sum(p * (1 - p))))
    peak = log_density(mode)

    def density(z):
        return float(np.exp(log_density(mode + scale * z) - peak))

    moments, _ = quad_vec(
        lambda z: density(z) * np.array([1.0, z, z * z]),
        -np.inf,
        np.inf,
        epsabs=1e-10,
        epsrel=1e-10,
    )
    norm = float(moments[0])
    mean = float(mode + scale * moments[1] / norm)
    variance = float(max(0, scale**2 * (moments[2] / norm - (moments[1] / norm) ** 2)))
    radius = (abs(mode - prior.mu_lambda) + 12 * np.sqrt(prior.sigma_lambda_sq)) / scale

    def quantile(q):
        z = brentq(
            lambda z: quad(density, -np.inf, z, epsabs=1e-10)[0] / norm - q,
            -radius,
            radius,
            xtol=1e-10,
        )
        return float(mode + scale * z)

    summary = SubjectPosterior(mean, variance, len(y), quantile(0.025), quantile(0.975))
    return summary, density, norm, mode, scale


@dataclass
class PersonalizedSurrogate:
    base: TinyDcsSurrogate
    prior: PopulationPrior = field(default_factory=PopulationPrior)
    subjects: dict[object, SubjectPosterior] = field(default_factory=dict)
    observations: dict[object, tuple[list[float], list[float]]] = field(default_factory=dict)

    def observe(self, subject_id, X, y):
        y = np.atleast_1d(np.asarray(y, dtype=float)).ravel()
        if not np.isin(y, [0, 1]).all() or len(y) != len(X) or not len(y):
            raise ValueError("one observed binary outcome per exposure is required")
        eta = _logit(self.base.predict(X)["point"])
        offsets, outcomes = self.observations.get(subject_id, ([], []))
        offsets, outcomes = offsets + eta.tolist(), outcomes + y.tolist()
        posterior, *_ = _distribution(offsets, outcomes, self.prior)
        self.observations[subject_id] = (offsets, outcomes)
        self.subjects[subject_id] = posterior
        return posterior

    def predict(self, subject_id, X, *, inflate_interval_with_posterior_sd=True):
        """Posterior mean probability and equal-tailed 95% credible interval.

        The old inflation flag is accepted for call compatibility; no conformal
        bound is combined with posterior variance.
        """
        offsets, outcomes = self.observations.get(subject_id, ([], []))
        posterior, density, norm, mode, scale = _distribution(offsets, outcomes, self.prior)
        self.subjects[subject_id] = posterior
        base = self.base.predict(X)
        eta = _logit(base["point"])
        expected, _ = quad_vec(
            lambda z: density(z) * expit(eta + mode + scale * z),
            -np.inf,
            np.inf,
            epsabs=1e-10,
            epsrel=1e-10,
        )
        point = expected / norm
        return {
            "point": point,
            "lower": expit(eta + posterior.lower),
            "upper": expit(eta + posterior.upper),
            "base_logit": eta,
            "personal_logit": _logit(point),
            "subject_mean_log_lambda": posterior.mean,
            "subject_sd_log_lambda": float(np.sqrt(posterior.variance)),
            "subject_n_observations": posterior.n_observations,
            "ood_distance": base["ood_distance"],
            "in_envelope": base["in_envelope"],
            "interval_kind": "posterior_credible",
            "credible_mass": 0.95,
            "nominal_coverage": None,
            "base_probability_floor": 1e-10,
        }


def generate_synthetic_cohort(
    base_surrogate: TinyDcsSurrogate,
    exposure_template: pd.DataFrame,
    *,
    n_subjects: int,
    exposures_per_subject: int,
    sigma_lambda: float = 0.8,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate a synthetic cohort of subjects with known ``log lambda_i``.

    Each subject samples ``exposures_per_subject`` rows at random (with
    replacement) from ``exposure_template``. Outcomes are drawn from
    ``Bernoulli(sigmoid(eta_base + log lambda_i))`` where
    ``log lambda_i ~ N(0, sigma_lambda^2)``.

    Returns a long-format dataframe with columns
    ``[subject_id, log_lambda_true, y, y_prob_true, <base features...>]``.
    """
    if len(exposure_template) < 2:
        raise ValueError("exposure_template must have at least 2 rows")
    if n_subjects <= 0 or exposures_per_subject <= 0:
        raise ValueError("n_subjects and exposures_per_subject must be > 0")
    if sigma_lambda <= 0:
        raise ValueError("sigma_lambda must be > 0")

    rng = np.random.default_rng(seed)
    log_lambdas = rng.normal(0.0, sigma_lambda, size=n_subjects)

    all_rows = []
    for subject_id in range(n_subjects):
        idx = rng.integers(0, len(exposure_template), size=exposures_per_subject)
        template = exposure_template.iloc[idx].reset_index(drop=True)
        base_pred = base_surrogate.predict(template)
        eta_base = _logit(base_pred["point"])
        log_lam = float(log_lambdas[subject_id])
        eta_personal = eta_base + log_lam
        p_personal = expit(eta_personal)
        y = rng.binomial(1, np.clip(p_personal, 0.0, 1.0))

        rows = template.copy()
        rows["subject_id"] = int(subject_id)
        rows["log_lambda_true"] = log_lam
        rows["y_prob_true"] = p_personal
        rows["y"] = y.astype(int)
        all_rows.append(rows)

    cohort = pd.concat(all_rows, ignore_index=True)
    cols = ["subject_id", "log_lambda_true", "y_prob_true", "y"] + [
        c for c in cohort.columns if c not in ("subject_id", "log_lambda_true", "y_prob_true", "y")
    ]
    return cohort[cols]
