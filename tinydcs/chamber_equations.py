"""Source predictors for pulmonary Doppler endpoints, NASA/TP-2020-220529 §§3 and 5.1."""

from __future__ import annotations

import math

SIMPLE_OXYGEN = "nasa_2020_simple_oxygen"
NASA_REPORT = "https://ntrs.nasa.gov/citations/20200004317"
VGE_MODELS = {
    "nasa_2020_eq5": {
        "endpoint": "vge",
        "cases": 368,
        "equation": 5,
        "coefficients": dict(
            intercept=-9.559,
            age=0.0298,
            tr=3.66,
            male=0.513,
            ambulation=0.909,
            rep=-0.471,
            scale=0.941,
        ),
    },
    "nasa_2020_eq6": {
        "endpoint": "grade_iv_vge",
        "cases": 166,
        "equation": 6,
        "coefficients": dict(
            intercept=-11.403,
            age=0.0435,
            tr=3.635,
            male=0.537,
            ambulation=1.418,
            rep=-0.477,
            scale=0.845,
        ),
    },
}


def vge_fraction(model_id, *, hours, tissue_ratio, age, male, ambulatory, staged):
    """CDF of time to first detection. Source time is hours at the test pressure."""
    c = VGE_MODELS[model_id]["coefficients"]
    log_odds = (
        math.log(hours)
        + c["intercept"]
        + c["age"] * age
        + c["tr"] * tissue_ratio
        + c["male"] * male
        + c["ambulation"] * ambulatory
        + c["rep"] * staged
    ) / c["scale"]
    return 1.0 / (1.0 + math.exp(-log_odds))
