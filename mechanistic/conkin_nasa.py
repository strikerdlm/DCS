"""Conkin RM/NM reference equations, NASA TP-2004-213158.

Eq. 6 defines k = exp(lambda * VO2) / 519.37 (min^-1). The fitted
lambda is 0.025 for RM and 0.030 for NM. Eq. 4 uses DRY ambient nitrogen,
not humidified inspired nitrogen. Eq. 14/15 are endpoint logistic models
for the reference 4-hour exposure at 4.3 psia; they are not hazard models.
"""
from __future__ import annotations

import math
from collections.abc import Iterable, Mapping

import numpy as np
from scipy.special import expit

LN2 = math.log(2)
P2 = 4.3
DEFAULT_T_HALF = 360
MODEL_VERSION = "conkin-reference-v2"
LAMBDAS = {"RM": 0.025, "NM": 0.030}
SOURCE_URL = "https://www.nasa.gov/wp-content/uploads/2023/03/conkin-dcs-exercise-tp-213158-2004.pdf"


def _nonnegative(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and >= 0")
    return result


def nitrogen_half_time(vo2_ml_kg_min: float, lambda_param: float) -> float:
    """Return the Eq. 6 rate constant k, despite the historical function name."""
    vo2 = _nonnegative(vo2_ml_kg_min, "VO2")
    lam = _nonnegative(lambda_param, "lambda")
    if lam <= 0 or lam * vo2 > 700:
        raise ValueError("lambda must be positive and lambda * VO2 <= 700")
    return math.exp(lam * vo2) / 519.37


def compute_p1n2(p0: float, pa: float, vo2_ml_kg_min: float,
                 pb_time_min: float, lambda_param: float) -> float:
    """Eq. 4: sequential equilibration toward dry ambient ppN2, in psia."""
    initial = _nonnegative(p0, "initial nitrogen")
    target = _nonnegative(pa, "ambient nitrogen")
    duration = _nonnegative(pb_time_min, "prebreathe duration")
    k = nitrogen_half_time(vo2_ml_kg_min, lambda_param)
    return target + (initial - target) * math.exp(-k * duration)


def compute_etr(p1n2: float, p2_val: float = P2) -> float:
    tissue = _nonnegative(p1n2, "tissue nitrogen")
    pressure = _nonnegative(p2_val, "exposure pressure")
    if pressure == 0:
        raise ValueError("exposure pressure must be > 0")
    return tissue / pressure


def logistic_regression_model(etr, age, gender_str, coefficients):
    """Legacy generic coefficient interface; female=1 for this interface only."""
    _nonnegative(etr, "ETR")
    _nonnegative(age, "age")
    if gender_str not in {"Male", "Female"}:
        raise ValueError("sex must be Male or Female")
    beta = np.asarray(coefficients, dtype=float)
    if beta.shape != (4,) or not np.isfinite(beta).all():
        raise ValueError("four finite coefficients are required")
    return float(expit(beta @ [1, etr, age, int(gender_str == "Female")]))


def predict_endpoint(etr: float, *, variant: str = "RM",
                     age_years: float = 40, sex: str = "Male") -> float:
    """Eq. 14/15 endpoint probability, as a fraction; no time interpolation."""
    dose = _nonnegative(etr, "ETR")
    if variant not in LAMBDAS:
        raise ValueError("variant must be RM or NM")
    if variant == "RM":
        age = _nonnegative(age_years, "age")
        if age == 0:
            raise ValueError("age must be positive")
        return float(expit(-31.71 + 14.55 * dose + 0.053 * age))
    if sex not in {"Male", "Female"}:
        raise ValueError("sex must be Male or Female")
    return float(expit(-25.56 + 12.83 * dose - 1.037 * int(sex == "Male")))


def predict_prebreathe(initial_n2_psia: float, segments: Iterable[Mapping[str, float]],
                       *, variant: str = "RM", exposure_pressure_psia: float = P2,
                       age_years: float = 40, sex: str = "Male") -> dict:
    """Evaluate explicit PB intervals and the reference-horizon equation.

    Segments contain durationMin, ambientN2Psia and vo2MlKgMin.
    The computed endpoint is an equation evaluation; applicability must be
    assessed separately before representing it as risk for a mission.
    """
    if variant not in LAMBDAS:
        raise ValueError("variant must be RM or NM")
    tissue = _nonnegative(initial_n2_psia, "initial nitrogen")
    for segment in segments:
        tissue = compute_p1n2(tissue, segment["ambientN2Psia"],
                              segment["vo2MlKgMin"], segment["durationMin"],
                              LAMBDAS[variant])
    etr = compute_etr(tissue, exposure_pressure_psia)
    return {
        "p1n2Psia": tissue, "etr": etr,
        "pDcsPercent": 100 * predict_endpoint(etr, variant=variant, age_years=age_years, sex=sex),
        "variant": variant, "lambda": LAMBDAS[variant], "predictionHorizonMin": 240,
        "referencePressurePsia": 4.3, "modelVersion": MODEL_VERSION, "source": SOURCE_URL,
    }
