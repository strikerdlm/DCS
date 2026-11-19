"""Serve the two fixed, aggregate-only research model exports from the companion project."""

from __future__ import annotations

import hashlib
import json
import math
from functools import lru_cache
from importlib.resources import files

from scipy.special import expit

GROUP = "nasa-chamber-dcs-v1"
BUBBLES = "grade-iv-vge-v1"
# These digests identify reviewed JSON data; loading does not execute model code.
DIGESTS = {
    GROUP: "27ed89287df63a8069282fd0528597136e95a6c98d642093af2916c669398ef3",
    BUBBLES: "311861bb1c66211e432940db6b52b4ace9ca75d5260df6e3bfac22f3fe8c5ca2",
}
GROUP_SOURCE = "https://www.nasa.gov/wp-content/uploads/2023/03/abercromby-suited-chamber-testing-tp220343-2019.pdf"
VGE_SOURCE = "https://raw.githubusercontent.com/cran/thregI/11919e13da5be6412dde3184c814ffd3fb4f1873/man/hdsd.Rd"


@lru_cache(maxsize=2)
def read_study(name: str) -> dict:
    if name not in DIGESTS:
        raise ValueError("Unknown outcome study")
    payload = files("tinydcs").joinpath("studies").joinpath(name + ".json").read_bytes()
    if hashlib.sha256(payload).hexdigest() != DIGESTS[name]:
        raise ValueError("Research study digest mismatch")
    return json.loads(payload)


def group_estimate(study, pressure, hours, tr, ambulatory):
    """Accept the exact published joint configuration after caller-declared precision."""
    if not study["release"]["exploratory_group_incidence_enabled"]:
        return None, None
    match = next(
        (
            row
            for row in study["support"]
            if row["ambulatory"] == ambulatory
            and math.isclose(row["pressure_psia"], pressure, rel_tol=0, abs_tol=1e-7)
            and math.isclose(row["duration_hours"], hours, rel_tol=0, abs_tol=1e-8)
            and math.isclose(row["mean_tr360"], tr, rel_tol=0, abs_tol=1e-8)
        ),
        None,
    )
    if match is None:
        return None, None
    model = study["model"]
    if study["features"] != [
        "mean_tr360",
        "pressure_psia",
        "duration_hours",
        "ambulatory",
    ]:
        raise ValueError("Unexpected protocol group feature order")
    values = [
        match["mean_tr360"],
        match["pressure_psia"],
        match["duration_hours"],
        int(ambulatory),
    ]
    logit = model["intercept"] + sum(
        b * (x - c) / s
        for x, b, c, s in zip(
            values, model["coefficients"], model["center"], model["scale"], strict=True
        )
    )
    return float(expit(logit)), match


def vge_estimate(study, hours, age, sex, tr, ambulatory):
    """Predict Grade IV detection from the four covariates in the public extract."""
    features = study["splits"]["training"]["features"]
    reasons = []
    for x, key in [(age, "age_years"), (tr, "arrival_tr360")]:
        if x is None or not features[key]["min"] <= x <= features[key]["max"]:
            reasons.append("STUDY_" + key.upper() + "_OUTSIDE_TRAINING_RANGE")
    if sex not in {"male", "female"}:
        reasons.append("STUDY_SOURCE_SEX_REQUIRED")
    if not 2 <= hours <= 4:
        reasons.append("STUDY_HORIZON_OUTSIDE_SUPPORT")
    if reasons:
        return None, reasons
    model = study["models"]["predictor"]
    if model["feature_order"] != [
        "intercept",
        "age_per_10_centered_35",
        "source_male",
        "tr360_centered_1_5",
        "ambulatory",
    ]:
        raise ValueError("Unexpected Grade IV study feature order")
    fields = [1, (age - 35) / 10, int(sex == "male"), tr - 1.5, int(ambulatory)]
    location = sum(x * b for x, b in zip(fields, model["coefficients"], strict=True))
    return float(expit((math.log(hours) - location) / model["scale"])), []


def study_comparisons(inputs, physiology, published):
    """Express the entered plan as a hypothetical cohort and, separately, a VGE study covariate vector."""
    pressure, tr = (
        physiology["plateau_pressure_psia"],
        physiology["arrival_tissue_ratio"],
    )
    hours = inputs.time_at_altitude_min / 60
    ambulatory = inputs.activity == "ambulatory"
    # The protocol group fit has no BMI or sex term. The specific DCS source
    # coefficient domain is independent of this study's exact joint grid.
    reference = {r["id"]: r for r in published}
    common_vetoes = [
        r
        for r in reference["symptomatic_dcs"]["applicability"]["reasons"]
        if r
        not in {
            "BMI_OUTSIDE_SOURCE",
            "SOURCE_POPULATION_MISMATCH",
            "TISSUE_RATIO_OUTSIDE_SOURCE",
            "PRESSURE_BRANCH_MISMATCH",
        }
    ]
    if tr is None:
        common_vetoes.append("STUDY_ARRIVAL_DOSE_UNAVAILABLE")
    group_reasons = list(dict.fromkeys(common_vetoes))
    matched_group = None
    group_point = None
    try:
        group_study = read_study(GROUP)
        if not group_reasons:
            # Table F1 prints mean TR360 to two decimal places. Match the
            # published bin, without nearest-neighbour interpolation.
            group_point, matched_group = group_estimate(
                group_study, pressure, hours, round(tr, 2), ambulatory
            )
            if group_point is None:
                group_reasons.append("OUTSIDE_OBSERVED_PROTOCOL_GROUP_SETTINGS")
    except (ValueError, OSError):
        group_reasons.append("STUDY_ARTIFACT_UNAVAILABLE")

    vge_reasons = list(reference["grade_iv_vge"]["applicability"]["reasons"])
    # Original pressure, gas and session linkage are absent from the public
    # extract. Only offer a dose-based sensitivity comparison near 4.3 psia.
    if abs(pressure - 4.3) > 0.005:
        vge_reasons.append("STUDY_PRESSURE_TRANSPORT_UNVERIFIED")
    bubble_point = None
    try:
        bubbles = read_study(BUBBLES)
        if not vge_reasons:
            bubble_point, vge_reasons = vge_estimate(
                bubbles, hours, inputs.age_years, inputs.source_sex, tr, ambulatory
            )
    except (ValueError, OSError):
        vge_reasons.append("STUDY_ARTIFACT_UNAVAILABLE")

    def row(
        name, label, model_id, point, reasons, endpoint, population, source, cls, detail
    ):
        return dict(
            id=name,
            label=label,
            model_id=model_id,
            model_digest=DIGESTS.get(name),
            probability_fraction=point,
            applicability=dict(
                status="supported" if point is not None else "unsupported",
                reasons=list(dict.fromkeys(reasons)),
            ),
            endpoint=endpoint,
            window=f"Through {inputs.time_at_altitude_min:g} minutes at plateau pressure",
            population=population,
            source_url=source,
            evidence_class=cls,
            uncertainty=dict(status="unavailable", detail=detail),
        )

    group = row(
        GROUP,
        "DCS in a matched protocol group",
        "nasa-chamber-dcs-group-v1",
        group_point,
        group_reasons,
        "Group proportion with signs or symptoms classified as Type I or II DCS by an independent medical officer.",
        "Hypothetical NASA chamber group sharing the supplied dose as its mean, at the precision of Table F1.",
        GROUP_SOURCE,
        "protocol_group_benchmark",
        "Internal evaluation held out protocol families. Repeated participants cannot be linked. No calibrated probability interval for a new group.",
    )
    group["group_dose_at_published_precision"] = (
        round(tr, 2) if tr is not None else None
    )
    group["matched_test_ids"] = matched_group["test_ids"] if matched_group else []
    group["observed_cases"] = matched_group["observed_cases"] if matched_group else None
    group["dcs_denominator"] = (
        matched_group["dcs_denominator"] if matched_group else None
    )
    group["window"] = (
        f"Historical tests with {inputs.time_at_altitude_min:g} planned plateau minutes. "
        "Cases were usually identified at altitude, with some first reported after the test. "
        "The table gives no uniform post-return surveillance horizon."
    )
    bubble = row(
        BUBBLES,
        "Grade IV VGE in the public monitoring study",
        "hdsd_grade_iv_aft_v1",
        bubble_point,
        vge_reasons,
        "First Grade IV VGE detection, with interval- and right-censored monitoring.",
        "Released NASA study covariates: age, source sex, ambulation and arrival TR360. Individual pressure and gas histories are unavailable.",
        VGE_SOURCE,
        "interval_censored_benchmark",
        "60 held-out study IDs. The four-hour event fraction was bounded by incomplete follow-up. No calibrated individual interval or external validation.",
    )
    return [group, bubble]
