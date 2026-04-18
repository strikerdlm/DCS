"""Closed-form ADRAC log-logistic accelerated-failure-time model.

This module fits and evaluates an ADRAC-style log-logistic survival model of
altitude decompression-sickness risk, following the functional form of
Kannan, Raychaudhuri & Pilmanis (ASEM 1998; 69:965–70) and
Pilmanis, Petropoulos, Kannan & Webb (ASEM 2004; 75:749–59).

Model
-----

.. math::

    P(\\mathrm{DCS}\\ \\mathrm{by\\ time}\\ t) = 1 - S(t)
      = \\frac{1}{1 + \\exp\\!\\big((\\ln t - \\beta_2 - \\boldsymbol{\\beta} \\cdot \\mathbf{x})/\\beta_1\\big)}

where ``t`` is time-at-altitude (min), ``x`` is a covariate vector
(ambient pressure, prebreathing time, exercise indicator), ``beta_1``
is the scale parameter, ``beta_2`` is the AFT intercept, and ``beta``
are the covariate coefficients.

Why this exists
---------------

We fit ADRAC directly to the cleaned 15,908-row grid
(``legacy/Model_Rel_Candidate/DCS_Risk_DB_2025.csv`` after
``tinydcs.data_clean.clean_dcs_risk_db``) so we have a **closed-form
baseline** the TinyDCS surrogate can be benchmarked against. A good
surrogate should do at least as well as this baseline on random splits,
and it should generalize better on leave-one-altitude-out because it
accommodates a richer feature set (continuous VO2 etc.).

Scope
-----

- This is the ADRAC **functional form** fit to the *shipped-grid target*.
  It is not the original ADRAC coefficients (which were fit to raw
  USAFSAM chamber data with individual failure times).
- Exercise enters as a Rest/Mild/Heavy categorical variable, exactly as
  in the shipped grid. Continuous-VO2 extension lives in ``tinydcs``.
- Uses SciPy's ``optimize.minimize`` with L-BFGS-B on the sum of
  squared logit residuals as a pragmatic loss; the original USAFSAM
  work used maximum likelihood on censored failure-time data, which we
  cannot reproduce without the individual-level dataset.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

try:
    from scipy.optimize import minimize
except ImportError as exc:  # pragma: no cover
    raise ImportError("scipy is required for mechanistic.adrac") from exc


_EPS = 1e-6
_SEA_LEVEL_MMHG = 760.0


def altitude_ft_to_mmhg(altitude_ft: np.ndarray) -> np.ndarray:
    """Convert altitude (ft) to ambient pressure (mmHg) via ISA approximation."""
    alt = np.asarray(altitude_ft, dtype=float)
    p_atm = (1.0 - 6.87535e-6 * np.maximum(alt, 0.0)) ** 5.2559
    return p_atm * _SEA_LEVEL_MMHG


def _logit(p: np.ndarray) -> np.ndarray:
    q = np.clip(np.asarray(p, dtype=float), _EPS, 1.0 - _EPS)
    return np.log(q / (1.0 - q))


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


@dataclass(slots=True)
class AdracModel:
    """Fitted ADRAC log-logistic parameters.

    Parameters
    ----------
    beta_1
        AFT scale parameter (controls the dispersion of the survival curve
        on the log-time scale). Positive.
    beta_2
        AFT intercept on the log-time scale.
    beta
        Coefficient vector on the covariates (pressure_mmhg, prebreathe_min,
        mild_ind, heavy_ind). Length 4.
    feature_names
        Covariate names in the same order as ``beta``.
    """

    beta_1: float
    beta_2: float
    beta: np.ndarray
    feature_names: tuple[str, ...] = (
        "pressure_mmhg",
        "prebreathe_min",
        "exercise_mild",
        "exercise_heavy",
    )

    def predict(
        self,
        altitude_ft: np.ndarray | float,
        prebreathe_min: np.ndarray | float,
        exercise_level: str | Sequence[str],
        time_at_altitude_min: np.ndarray | float,
    ) -> np.ndarray:
        """Evaluate ``P(DCS)`` on a probability scale in ``[0, 1]``."""
        alt = np.atleast_1d(np.asarray(altitude_ft, dtype=float))
        pb = np.atleast_1d(np.asarray(prebreathe_min, dtype=float))
        t = np.atleast_1d(np.asarray(time_at_altitude_min, dtype=float))
        ex = np.atleast_1d(np.asarray(exercise_level))

        if not (alt.shape == pb.shape == t.shape == ex.shape):
            raise ValueError("all inputs must share a common shape")

        pressure = altitude_ft_to_mmhg(alt)
        mild = (ex == "Mild").astype(float)
        heavy = (ex == "Heavy").astype(float)
        X = np.stack([pressure, pb, mild, heavy], axis=-1)

        log_t = np.log(np.maximum(t, _EPS))
        covariate_term = X @ self.beta
        omega = (log_t - self.beta_2 - covariate_term) / self.beta_1
        p_dcs_fraction = 1.0 / (1.0 + np.exp(-omega))
        return np.clip(p_dcs_fraction, 0.0, 1.0)


def _pack(beta_1: float, beta_2: float, beta: np.ndarray) -> np.ndarray:
    return np.concatenate([[beta_1, beta_2], beta])


def _unpack(theta: np.ndarray) -> tuple[float, float, np.ndarray]:
    return float(theta[0]), float(theta[1]), np.asarray(theta[2:], dtype=float)


def _negative_log_likelihood_like(
    theta: np.ndarray,
    log_t: np.ndarray,
    X: np.ndarray,
    target_logit: np.ndarray,
) -> float:
    """Pragmatic loss: MSE between predicted logit(P) and target logit(P_grid).

    This is not the strict Kannan-1998 MLE (which requires censored failure
    times), but recovers the same functional form on an ADRAC-output grid.
    """
    beta_1, beta_2, beta = _unpack(theta)
    if beta_1 <= _EPS:
        return 1e12
    omega = (log_t - beta_2 - X @ beta) / beta_1
    resid = omega - target_logit
    return float(np.mean(resid * resid))


def fit_adrac(
    df: pd.DataFrame,
    *,
    altitude_col: str = "altitude",
    prebreathe_col: str = "prebreathing_time",
    exercise_col: str = "exercise_level",
    time_col: str = "time_at_altitude",
    target_col: str = "risk_of_decompression_sickness",
    target_in_percent: bool = True,
) -> AdracModel:
    """Fit the ADRAC log-logistic AFT form to an ADRAC-output grid.

    Parameters
    ----------
    df
        Cleaned grid with the columns listed above.
    target_in_percent
        If True (default), the target is in [0, 100]; it is rescaled
        internally to [0, 1] for the logit transform.
    """
    for col in (altitude_col, prebreathe_col, exercise_col, time_col, target_col):
        if col not in df.columns:
            raise ValueError(f"input is missing column '{col}'")

    pressure = altitude_ft_to_mmhg(df[altitude_col].to_numpy(dtype=float))
    pb = df[prebreathe_col].to_numpy(dtype=float)
    ex = df[exercise_col].to_numpy()
    t = df[time_col].to_numpy(dtype=float)
    t = np.maximum(t, _EPS)
    log_t = np.log(t)

    mild = (ex == "Mild").astype(float)
    heavy = (ex == "Heavy").astype(float)
    X = np.stack([pressure, pb, mild, heavy], axis=-1)

    y = df[target_col].to_numpy(dtype=float)
    if target_in_percent:
        y = y / 100.0
    target_logit = _logit(y)

    # Initial guess: small positive beta_1, large negative beta_2 (so that
    # low t → low P(DCS)), roughly physiological signs on covariates
    # (increasing pressure → lower risk; increasing PB → lower risk;
    # exercise → higher risk).
    theta0 = np.array([1.0, 0.0, -1.0e-3, -1.0e-2, 1.0, 2.0])

    result = minimize(
        _negative_log_likelihood_like,
        theta0,
        args=(log_t, X, target_logit),
        method="L-BFGS-B",
        bounds=[(_EPS, None), (-100.0, 100.0)] + [(-100.0, 100.0)] * X.shape[1],
        options={"maxiter": 5000, "ftol": 1e-10, "gtol": 1e-8},
    )
    if not result.success:
        raise RuntimeError(f"ADRAC fit did not converge: {result.message}")

    beta_1, beta_2, beta = _unpack(result.x)
    return AdracModel(beta_1=beta_1, beta_2=beta_2, beta=beta)
