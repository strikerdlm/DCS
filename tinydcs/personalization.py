"""Per-subject hierarchical Bayesian personalization on top of TinyDCS.

This module implements Paper 2's "Implementation A" — a conjugate Gaussian
per-subject susceptibility update that adds a personalized log-odds shift
above the base :class:`tinydcs.surrogate.TinyDcsSurrogate` prediction.

Model
-----

For subject ``i`` with exposures ``j = 1..n_i``:

    logit( P(DCS_{ij} | x_{ij}, lambda_i) ) = eta_base(x_{ij}) + log lambda_i

with the hierarchical prior

    log lambda_i ~ N(mu_lambda, sigma_lambda^2)

and the likelihood approximated as Gaussian around the base logit prediction:

    observed logit residual r_{ij} = logit(y_{ij}) - eta_base(x_{ij}) | log lambda_i
        ~ N(log lambda_i, sigma_lik^2)

Under this Gaussian-Gaussian conjugate setup, the posterior over
``log lambda_i`` is

    mu_post = (sigma_lik^2 * mu_lambda + sigma_lambda^2 * n_i * mean_residual)
              / (sigma_lik^2 + n_i * sigma_lambda^2)
    sigma_post^2 = (sigma_lik^2 * sigma_lambda^2)
                   / (sigma_lik^2 + n_i * sigma_lambda^2)

which is closed-form, O(1) per new observation, no MCMC. Suitable for
on-device personalization with memory footprint ~16 bytes per subject
(posterior mean + variance).

Caveats
-------

* The Gaussian likelihood approximation is valid when base predictions are
  not pinned near 0 or 1; in that regime the full Bayesian hierarchical
  model (Paper 2 Implementation B, PyMC-based, not in this module) should
  be preferred for methodological reporting. The conjugate update is the
  practical deployment path.

* Binary outcomes ``y in {0, 1}`` are Smithson-Verkuilen-shrunk before the
  logit, consistent with the base surrogate's training pipeline.

* The ``sigma_lik^2`` hyper-parameter controls how quickly subject posteriors
  move away from the population prior in response to new observations.
  Reasonable defaults are derived from Paper 1's held-out residuals; users
  with their own calibration cohorts should override.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

import numpy as np
import pandas as pd

from .surrogate import TinyDcsSurrogate


_EPS = 1e-6


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def _smithson_verkuilen(p: np.ndarray, n: int) -> np.ndarray:
    nn = float(max(n, 2))
    p = np.asarray(p, dtype=float)
    return (p * (nn - 1.0) + 0.5) / nn


def _logit(p: np.ndarray) -> np.ndarray:
    q = np.clip(np.asarray(p, dtype=float), _EPS, 1.0 - _EPS)
    return np.log(q / (1.0 - q))


@dataclass(slots=True)
class SubjectPosterior:
    """Gaussian posterior over a subject's ``log lambda``.

    Attributes
    ----------
    mean
        Posterior mean of ``log lambda_i``.
    variance
        Posterior variance.
    n_observations
        Number of exposures incorporated.
    """

    mean: float = 0.0
    variance: float = 1.0
    n_observations: int = 0

    def update(self, residual: float, sigma_lik_sq: float, prior_mean: float, prior_var: float) -> "SubjectPosterior":
        """Return a new posterior after one observation (conjugate Gaussian).

        ``residual`` is the observed logit residual
        ``logit(y) - eta_base(x)`` for a new exposure.
        """
        # Combine the current posterior with the new data point as if the
        # current posterior were the prior.
        new_var = (self.variance * sigma_lik_sq) / (self.variance + sigma_lik_sq)
        new_mean = new_var * (self.mean / self.variance + residual / sigma_lik_sq)
        return SubjectPosterior(
            mean=float(new_mean),
            variance=float(new_var),
            n_observations=int(self.n_observations) + 1,
        )


@dataclass(slots=True)
class PopulationPrior:
    """Hyperparameters for the hierarchical prior on ``log lambda_i``."""

    mu_lambda: float = 0.0
    sigma_lambda_sq: float = 0.5
    sigma_lik_sq: float = 1.0  # likelihood noise on the logit scale


def _logit_binary_target(y: np.ndarray) -> np.ndarray:
    """Smithson-Verkuilen-shrink binary or probabilistic y and take logit."""
    y_arr = np.asarray(y, dtype=float).ravel()
    return _logit(_smithson_verkuilen(y_arr, n=len(y_arr)))


def fit_population_prior(
    subject_residuals: Mapping[object, np.ndarray],
    *,
    min_observations: int = 3,
) -> PopulationPrior:
    """Empirical-Bayes estimate of ``(mu_lambda, sigma_lambda^2, sigma_lik^2)``.

    Parameters
    ----------
    subject_residuals
        Mapping of ``subject_id -> array of logit residuals from the base surrogate``.
    min_observations
        Subjects with fewer residuals than this are skipped for the prior
        estimate (but can still be personalized later with the full prior).
    """
    means = []
    variances = []
    all_resid = []
    for sid, resid in subject_residuals.items():
        arr = np.asarray(resid, dtype=float).ravel()
        all_resid.append(arr)
        if arr.size < min_observations:
            continue
        means.append(float(arr.mean()))
        variances.append(float(arr.var(ddof=1))) if arr.size > 1 else None

    if not means:
        # Fall back to a weak default prior if nobody has enough data.
        return PopulationPrior(mu_lambda=0.0, sigma_lambda_sq=1.0, sigma_lik_sq=1.0)

    # Method-of-moments decomposition: Var(subject_mean) = sigma_lambda^2 + sigma_lik^2 / n_avg
    # With residual variance within-subject ~ sigma_lik^2.
    mu_hat = float(np.mean(means))
    within = float(np.mean(variances)) if variances else 1.0
    total_between = float(np.var(means, ddof=1)) if len(means) > 1 else 0.5
    sigma_lambda_sq = max(total_between - within / max(1, int(np.mean([len(v) for v in subject_residuals.values()]))), 1e-3)
    sigma_lik_sq = max(within, 1e-3)
    return PopulationPrior(
        mu_lambda=mu_hat,
        sigma_lambda_sq=sigma_lambda_sq,
        sigma_lik_sq=sigma_lik_sq,
    )


@dataclass
class PersonalizedSurrogate:
    """TinyDCS base surrogate + per-subject hierarchical Bayesian adjustment.

    Keeps a :class:`SubjectPosterior` per subject; predictions apply the
    subject's posterior mean as a log-odds shift and optionally inflate the
    interval by the posterior standard deviation.
    """

    base: TinyDcsSurrogate
    prior: PopulationPrior = field(default_factory=PopulationPrior)
    subjects: dict[object, SubjectPosterior] = field(default_factory=dict)

    def _ensure_subject(self, subject_id: object) -> SubjectPosterior:
        if subject_id not in self.subjects:
            self.subjects[subject_id] = SubjectPosterior(
                mean=float(self.prior.mu_lambda),
                variance=float(self.prior.sigma_lambda_sq),
                n_observations=0,
            )
        return self.subjects[subject_id]

    def observe(self, subject_id: object, X: pd.DataFrame, y: np.ndarray | float) -> SubjectPosterior:
        """Incorporate new (X, y) observations for a subject into their posterior.

        ``y`` may be binary {0, 1} or a probability in [0, 1]. Residuals are
        computed on the logit scale against the base surrogate.
        """
        y_arr = np.atleast_1d(np.asarray(y, dtype=float)).ravel()
        X_df = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        base_pred = self.base.predict(X_df)
        base_logit = base_pred["logit"]  # logit on the mean surrogate
        y_logit = _logit_binary_target(y_arr)
        residuals = y_logit - base_logit

        posterior = self._ensure_subject(subject_id)
        for r in residuals:
            posterior = posterior.update(
                residual=float(r),
                sigma_lik_sq=float(self.prior.sigma_lik_sq),
                prior_mean=float(self.prior.mu_lambda),
                prior_var=float(self.prior.sigma_lambda_sq),
            )
        self.subjects[subject_id] = posterior
        return posterior

    def predict(
        self,
        subject_id: object,
        X: pd.DataFrame,
        *,
        inflate_interval_with_posterior_sd: bool = True,
    ) -> dict[str, np.ndarray]:
        """Personalized prediction.

        Shifts the base logit by the subject's posterior mean ``log lambda_i``
        and optionally widens the conformal interval by the posterior
        standard deviation to reflect personalization uncertainty.
        """
        posterior = self._ensure_subject(subject_id)
        X_df = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        base_pred = self.base.predict(X_df)
        shift = float(posterior.mean)
        personalized_logit = base_pred["logit"] + shift
        point = _sigmoid(personalized_logit)

        # Interval: start from base conformal interval (already on probability
        # scale), shift both ends by the same log-odds amount, and optionally
        # add the posterior SD in quadrature with the conformal half-width on
        # the logit scale.
        half_width_logit = base_pred.get("conformal_half_width_logit")
        if half_width_logit is None or not np.isfinite(np.asarray(half_width_logit, dtype=float)).all():
            # ZI mode returns NaN half-width because it composes sub-intervals
            # directly. Fall back to propagating the base [lower, upper].
            lower_logit = _logit(np.clip(base_pred["lower"], _EPS, 1 - _EPS)) + shift
            upper_logit = _logit(np.clip(base_pred["upper"], _EPS, 1 - _EPS)) + shift
        else:
            hw = np.asarray(half_width_logit, dtype=float)
            if inflate_interval_with_posterior_sd:
                hw = np.sqrt(hw**2 + float(posterior.variance))
            lower_logit = personalized_logit - hw
            upper_logit = personalized_logit + hw
        lower = _sigmoid(lower_logit)
        upper = _sigmoid(upper_logit)

        return {
            "point": point,
            "lower": lower,
            "upper": upper,
            "base_logit": base_pred["logit"],
            "personal_logit": personalized_logit,
            "subject_mean_log_lambda": shift,
            "subject_sd_log_lambda": float(np.sqrt(posterior.variance)),
            "subject_n_observations": posterior.n_observations,
            "ood_distance": base_pred["ood_distance"],
            "in_envelope": base_pred["in_envelope"],
        }


# ---------------------------------------------------------------------------
# Synthetic-cohort generator for Paper 2 validation
# ---------------------------------------------------------------------------


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
        eta_base = base_pred["logit"]
        log_lam = float(log_lambdas[subject_id])
        eta_personal = eta_base + log_lam
        p_personal = 1.0 / (1.0 + np.exp(-eta_personal))
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
