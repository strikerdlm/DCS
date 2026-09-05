"""Closed-form ADRAC log-logistic accelerated-failure-time model.

This module fits and evaluates an ADRAC-style log-logistic survival model of
altitude decompression-sickness risk, following the functional form of
Kannan, Raychaudhuri & Pilmanis (ASEM 1998; 69:965–70) and
Pilmanis, Petropoulos, Kannan & Webb (ASEM 2004; 75:749–59).

Model
-----

.. math::

    P(\\mathrm{DCS}\\ \\mathrm{by\\ time}\\ t) = 1 - S(t)
      = \\frac{1}{1 + \\exp\\!\\big(-(\\ln t - \\beta_2 - \\boldsymbol{\\beta} \\cdot \\mathbf{x})/\\beta_1\\big)}

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
- Uses a bounded linear least-squares reparameterization on the sum of
  squared logit residuals as a pragmatic loss; the original USAFSAM
  work used maximum likelihood on censored failure-time data, which we
  cannot reproduce without the individual-level dataset.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
from scipy.special import expit
from .atmosphere import altitude_ft_to_atm

try:
    from scipy.optimize import lsq_linear
except ImportError as exc:  # pragma: no cover
    raise ImportError("scipy is required for mechanistic.adrac") from exc


_EPS = 1e-6
_SEA_LEVEL_MMHG = 760.0


def altitude_ft_to_mmhg(altitude_ft: np.ndarray) -> np.ndarray:
    """Convert altitude (ft) to ambient pressure (mmHg) via ISA approximation."""
    return altitude_ft_to_atm(altitude_ft) * _SEA_LEVEL_MMHG


def _logit(p: np.ndarray) -> np.ndarray:
    q = np.clip(np.asarray(p, dtype=float), _EPS, 1.0 - _EPS)
    return np.log(q / (1.0 - q))


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return expit(z)


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

    def __post_init__(self):
        self.beta = np.asarray(self.beta, dtype=float)
        if self.beta.shape != (4,) or not np.isfinite(self.beta).all():
            raise ValueError("beta must contain four finite coefficients")
        if not np.isfinite([self.beta_1, self.beta_2]).all() or self.beta_1 <= 0:
            raise ValueError("AFT scale must be positive and parameters finite")

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

        alt, pb, t, ex = np.broadcast_arrays(alt, pb, t, ex)
        if not np.isfinite(pb).all() or not np.isfinite(t).all() or np.any(pb < 0) or np.any(t < 0):
            raise ValueError("durations must be finite and nonnegative")
        if not np.isin(ex, ["Rest", "Mild", "Heavy"]).all():
            raise ValueError("exercise must be Rest, Mild or Heavy")

        pressure = altitude_ft_to_mmhg(alt)
        mild = (ex == "Mild").astype(float)
        heavy = (ex == "Heavy").astype(float)
        X = np.stack([pressure, pb, mild, heavy], axis=-1)

        log_t = np.log(np.maximum(t, _EPS))
        covariate_term = X @ self.beta
        omega = (log_t - self.beta_2 - covariate_term) / self.beta_1
        return np.where(t == 0, 0.0, expit(omega))


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
    y = df[target_col].to_numpy(dtype=float) / (100.0 if target_in_percent else 1.0)
    if not np.isfinite([*pb, *t, *y]).all() or np.any(pb < 0) or np.any(t < 0) or np.any((y < 0) | (y > 1)):
        raise ValueError("training covariates and probability targets must be finite and in range")
    if not np.isin(ex, ["Rest", "Mild", "Heavy"]).all():
        raise ValueError("exercise must be Rest, Mild or Heavy")
    if np.any((t == 0) & (y != 0)):
        raise ValueError("zero-duration exposure must have zero cumulative risk")
    positive = t > 0
    if positive.sum() < 6:
        raise ValueError("at least six positive-duration training rows required")
    # logit(p) = a*log(t) + b + c.x, a=1/beta_1 >0.
    # Signs in this reparameterization: pressure/PB <=0, exercise >=0.
    design = np.column_stack([np.log(t[positive]), np.ones(positive.sum()),
                              pressure[positive], pb[positive],
                              (ex[positive] == "Mild"), (ex[positive] == "Heavy")])
    scale = np.maximum(np.linalg.norm(design, axis=0), 1.0)
    result = lsq_linear(design/scale, _logit(y[positive]),
                        bounds=([1e-8*scale[0], -np.inf, -np.inf, -np.inf, 0, 0],
                                [np.inf, np.inf, 0, 0, np.inf, np.inf]),
                        tol=1e-12, max_iter=5000)
    if not result.success:
        raise RuntimeError(f"ADRAC fit did not converge: {result.message}")
    coefficients = result.x/scale
    a = coefficients[0]
    return AdracModel(beta_1=1/a, beta_2=-coefficients[1]/a, beta=-coefficients[2:]/a)
