"""Applicability-aware aviation reference equations. No fitting or clinical calibration."""
from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from dataclasses import dataclass, field

from mechanistic.conkin_nasa import ASCERTAINMENT, LAMBDAS, SOURCE_URL, predict_endpoint
from tinydcs.chamber_equations import SIMPLE_OXYGEN, VGE_MODELS, vge_fraction
from tinydcs.aviation_policy import interruption_record
from tinydcs.exposure import CORE_VERSION, PA_PER_PSIA, SCHEMA_VERSION, SECONDS_PER_UNIT, ExposureProfile
from tinydcs.exposure_physics import derive_physiology, is_sea_level, is_source_air
from tinydcs.hypobaric import HypobaricScenario, probability as hypobaric_probability

NASA_2020 = "https://www.nasa.gov/wp-content/uploads/2023/03/conkin-dcs-survival-models-tp220529-2020.pdf"
PDF_HASHES = {
    SOURCE_URL: "d188f13ee425910308154ebf4b7799188e3273dfad4e5da0bff6be40233656b7",
    NASA_2020: "fe7ae77bf6b5c2d2af223e17737920972ea18a175b9f873721f96f5175b594ec",
}
PHASE_I = "nasa_2004_phase_i"
TABLE5 = "nasa_2020_table5"
APPENDIX_A = "nasa_2020_appendix_a_rest"
TABLE5_ROWS = {4.3: 380, 5.3: 245, 6.5: 115, 7.5: 25}

# End minute, start/end psia, inspired O2, Table 3 %VO2peak, activity.
# Duplicate quiet blocks combine only while pressure and gas are unchanged.
# TP-2004-213158 pp. 15, 22, Appendix D, Phase I.
PHASE_I_INTERVALS = (
    (3, 14.7, 14.7, 1, 37.5, "warmup"), (10, 14.7, 14.7, 1, 75, "exercise"),
    (13, 14.7, 14.7, 1, 37.5, "recovery"), (30, 14.7, 14.7, 1, 25, "recovery"),
    (50, 14.7, 14.7, 1, 9.5, "rest"), (70, 14.7, 9.6, 1, 9.5, "rest"),
    (80, 9.6, 10.2, 1, 9.5, "rest"), (110, 10.2, 10.2, 0.265, 9.5, "rest"),
    (115, 10.2, 14.7, 1, 9.5, "rest"), (150, 14.7, 14.7, 1, 9.5, "rest"),
    (180, 14.7, 4.3, 1, 9.5, "rest"),
)


def _specs():
    specs = {
        "physiology": dict(source=NASA_2020, coefficient_version="fixed-half-time-360-min",
            population="Declared exposure", endpoint="nitrogen trajectory", horizon="Submitted timeline",
            gas="Declared-basis nitrogen only", protocols=[], coefficients={"half_time_min": 360},
            ascertainment="No outcome", validation_status="Analytic and numerical verification"),
        "nasa_2020_eq4": dict(source=NASA_2020, coefficient_version="TP-2020-220529-Eq4",
            population="nasa_hypobaric_chamber", endpoint="symptomatic_dcs", horizon="120–360 plateau minutes",
            gas="Dry nitrogen including argon in air; resting or mixed-exercise source kinetics",
            protocols=[TABLE5, PHASE_I, SIMPLE_OXYGEN], coefficients={"intercept": -9.177, "TR": 4.418,
                "AMB": 0.911, "BMI": -0.0647, "REP": -0.593, "scale": 0.750, "lambda": 0.030},
            ascertainment="Medical officer diagnosis during exposure, with a few first reports after testing; noncases censored at plateau exit.",
            validation_status="Published reference equation; selected source protocols reproduced"),
        "conkin_1996_eq7": dict(source=NASA_2020, coefficient_version="TP-2020-220529-Eq7",
            population="male_hypobaric_chamber", endpoint="symptomatic_dcs", horizon="120–240 plateau minutes",
            gas="Dry nitrogen including argon in air; resting oxygen preparation",
            protocols=[TABLE5, APPENDIX_A, SIMPLE_OXYGEN], coefficients={"pressure_offset_psia": 1.563,
                "stress_power": 4.366, "AMB": 1.578, "time_scale_per_h": 0.063, "time_power": 1.521},
            ascertainment="Cumulative symptomatic DCS from arrival at test pressure, as reproduced in the 2020 report.",
            validation_status="1996 equation reproduced from NASA 2020; selected reference scenarios"),
    }
    for model_id, definition in VGE_MODELS.items():
        grade = "Grade IV" if definition["endpoint"] == "grade_iv_vge" else "any grade"
        specs[model_id] = dict(
            source=NASA_2020, coefficient_version=f"TP-2020-220529-Eq{definition['equation']}",
            population="nasa_hypobaric_chamber", endpoint=definition["endpoint"],
            horizon="120–360 plateau minutes", gas="Source dry nitrogen equivalent at plateau arrival",
            protocols=[SIMPLE_OXYGEN, PHASE_I, TABLE5, APPENDIX_A],
            coefficients=dict(definition["coefficients"]),
            ascertainment=f"First precordial Doppler detection of {grade} pulmonary artery VGE during the plateau; approximately 15-minute interval monitoring.",
            validation_status=f"Published chamber reference; {definition['cases']} detections in 903 monitored exposures across 42 tests.",
        )
    for variant, equation, coefficients in [
        ("NM", 14, {"intercept": -25.56, "ETR": 12.83, "male": -1.037}),
        ("RM", 15, {"intercept": -31.71, "ETR": 14.55, "age_years": 0.053}),
    ]:
        specs["nasa_2004_"+variant.lower()] = dict(
            source=SOURCE_URL, coefficient_version=f"TP-2004-213158-Eq{equation}",
            population="nasa_2004_adynamic_chamber", endpoint="symptomatic_dcs",
            horizon="Fixed 240-minute exposure", gas="Dry ambient nitrogen; nominal surface value 11.6 psia",
            protocols=[PHASE_I], coefficients=coefficients | {"lambda": LAMBDAS[variant]},
            ascertainment=ASCERTAINMENT[variant],
            validation_status="Published reference, Phase I only; Table 17 is an extrapolative arithmetic fixture",
        )
    for model_id, spec in specs.items():
        spec.update(model_id=model_id, model_version=CORE_VERSION, core_version=CORE_VERSION,
                    applicability_version="2",
                    evidence_class="physiology_only" if model_id == "physiology" else "published_reference",
                    uncertainty_status="unavailable", source_pdf_sha256=PDF_HASHES[spec["source"]])
        manifest = json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
        spec["artifact_hash"] = hashlib.sha256(manifest).hexdigest()
        spec["artifact_hash_kind"] = "sha256_of_versioned_equation_manifest"
    return specs


_MODELS = _specs()


def model_registry() -> list[dict]:
    """Public source metadata. Each call returns independent JSON-compatible records."""
    return deepcopy(list(_MODELS.values()))


def _close(a, b):
    return math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-7)


def _p(s, end=False):
    pressure = s.end_pressure if end else s.start_pressure
    return pressure.pascals() / PA_PER_PSIA


def _source_gas(s, oxygen):
    return s.breathing_overpressure_pa == 0 and all(
        g is not None and g.basis == "dry" and _close(g.oxygen_fraction, oxygen)
        and _close(g.nitrogen_fraction, 1-oxygen)
        and not (g.argon_fraction or g.other_inert_fraction or g.carbon_dioxide_fraction)
        and not g.delivery_uncertainty and g.delivery_method != "unknown"
        for g in (s.gas, s.end_gas or s.gas))


def _split(profile):
    """Separate all contiguous intervals of the first plateau, preserving subdivisions."""
    segments = profile.segments
    start = next((i for i, s in enumerate(segments) if s.phase == "plateau"), len(segments))
    end = next((i for i in range(start, len(segments)) if segments[i].phase != "plateau"), len(segments))
    return segments[:start], segments[start:end], segments[end:]


def _duration(profile, segments):
    return sum(profile.minutes(s) for s in segments)


def _required_segments(profile, pre, plateau, after):
    """Data on or before the requested endpoint, including the initialization history."""
    r = profile.prediction_request
    if r.window == "source_post_test":
        return profile.history.segments + profile.segments
    origin = 0.
    if r.prediction_origin == "plateau_arrival" and plateau:
        origin = plateau[0].start
    if r.prediction_origin == "return_to_baseline":
        origin = next((s.end for s in profile.segments if s.phase == "return"), 0.)
    cutoff = origin + r.horizon_minutes * 60 / SECONDS_PER_UNIT[profile.time_unit]
    eligible = pre + plateau if r.window == "during_plateau" else pre + plateau + after
    return profile.history.segments + [s for s in eligible if s.start < cutoff]


def _matching_stages(profile, prep, stages, require_workload=False):
    """Confirm every subinterval's pressure, gas and optional Phase I workload.

    A reported segment may subdivide or straddle source intervals only when its
    linear pressure, gas and activity are compatible throughout the overlap.
    """
    if not prep or not _close(_duration(profile, prep), stages[-1][0]):
        return False
    elapsed = 0.0
    idx = 0
    for s in prep:
        duration = profile.minutes(s)
        segment_end = elapsed+duration
        while idx < len(stages):
            t1, p0, p1, gas, percent, kind = stages[idx]
            t0 = stages[idx-1][0] if idx else 0.0
            left, right = max(elapsed, t0), min(segment_end, t1)
            if right-left > 1e-8:
                for t in (left, right):
                    expected = p0 + (p1-p0)*(t-t0)/(t1-t0)
                    observed = _p(s) + (_p(s, True)-_p(s))*(t-elapsed)/duration
                    if abs(expected-observed) > 0.005:  # sea level vs 1 atm rounding only
                        return False
                if not _source_gas(s, gas):
                    return False
                if require_workload:
                    a = s.activity
                    peak = profile.person_covariates.vo2_peak_ml_kg_min
                    if a is None or a.type != kind or a.ambulation is not False or peak is None:
                        return False
                    q = a.workload(profile.person_covariates)
                    if q is None and kind == "rest":
                        q = 0.095*peak
                    if q is None or not _close(q, peak*percent/100):
                        return False
                    if kind in {"exercise", "warmup"} and a.exercise_mode != "dual_cycle":
                        return False
            if segment_end < t1-1e-8:
                break
            idx += 1
            if segment_end <= t1+1e-8:
                break
        elapsed = segment_end
    return idx == len(stages)


def _split_final_ascent(prep):
    i = len(prep)
    while i and prep[i-1].phase == "ascent":
        i -= 1
    return prep[:i], prep[i:]


def _rep(profile, prep, p2):
    """Identify a known staged prebreathe, separately from altitude/diving history."""
    before, ascent = _split_final_ascent(prep)
    if not ascent:
        return None
    if all(is_sea_level(s.start_pressure.pascals()) and is_sea_level(s.end_pressure.pascals())
           for s in before) and all(_p(s, True) < _p(s) for s in ascent):
        return False
    if not _close(p2, 4.3) or not _close(_duration(profile, ascent), 30):
        return None
    if _matching_stages(profile, prep, PHASE_I_INTERVALS):
        return True
    # TP-2020-220529 §2.2: 30 min down to 10.2, 30 there, 5 back to
    # 14.7, balance of PB, then 30 min down to 4.3. Match the submitted gas
    # as well. A staged identification alone never confers protocol eligibility.
    start = next((i for i, s in enumerate(before) if not is_sea_level(s.end_pressure.pascals())), None)
    if start is None:
        return None
    end = len(before)
    while end > start and is_sea_level(before[end-1].start_pressure.pascals()):
        end -= 1
    cycle = before[start:end]
    staged = ((30, 14.7, 10.2, 1, 0, ""), (60, 10.2, 10.2, .265, 0, ""),
              (65, 10.2, 14.7, 1, 0, ""))
    if (end < len(before) and all(_source_gas(s, 1) for s in before[:start]+before[end:]+ascent)
            and _matching_stages(profile, cycle, staged)
            and _matching_stages(profile, ascent, ((30, 14.7, 4.3, 1, 0, ""),))):
        return True
    return None


@dataclass
class Checks:
    reasons: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    def require(self, condition, code, missing=None):
        if condition:
            return
        if code not in self.reasons:
            self.reasons.append(code)
        if missing and missing not in self.missing:
            self.missing.append(missing)


def _choose_model(profile, p2):
    request = profile.prediction_request
    if request.model_id != "auto":
        return request.model_id
    if request.reference_population == "nasa_hypobaric_chamber":
        for model_id, definition in VGE_MODELS.items():
            if request.endpoint == definition["endpoint"]:
                return model_id
    if request.endpoint != "symptomatic_dcs" or request.reference_population == "aviation":
        return "physiology"
    if request.reference_population == "nasa_2004_adynamic_chamber":
        return "nasa_2004_nm" if request.window == "source_post_test" else "nasa_2004_rm"
    return ("conkin_1996_eq7" if p2 is not None and p2 > 5 else "nasa_2020_eq4")


def _reference_checks(profile, model, pre, plateau, after, checks):
    r = profile.prediction_request
    checks.require(r.endpoint == model["endpoint"], "ENDPOINT_MISMATCH")
    checks.require(r.reference_population == model["population"], "SOURCE_POPULATION_MISMATCH")
    checks.require(r.prediction_origin == "plateau_arrival", "PREDICTION_ORIGIN_MISMATCH")
    nm = model["model_id"] == "nasa_2004_nm"
    checks.require(r.window == ("source_post_test" if nm else "during_plateau"),
                   "OUTCOME_WINDOW_MISMATCH")
    checks.require(r.source_protocol in model["protocols"], "SOURCE_PROTOCOL_UNVERIFIED",
                   "prediction_request.source_protocol" if r.source_protocol is None else None)
    checks.require(bool(plateau), "MISSING_PLATEAU", "segments.plateau")
    if r.window == "source_post_test":
        checks.require(not any(s.phase == "plateau" for s in after), "MULTIPLE_PLATEAUS_UNSUPPORTED")
    if not plateau:
        return
    p2 = _p(plateau[0])
    checks.require(all(_close(_p(s), p2) and _close(_p(s, True), p2) for s in plateau),
                   "VARIABLE_PLATEAU_UNSUPPORTED")
    checks.require(r.horizon_minutes <= _duration(profile, plateau)+1e-8, "SOURCE_HORIZON_MISMATCH")
    for field_name in ("recent_diving", "previous_altitude_exposure"):
        value = getattr(profile.history, field_name)
        checks.require(value is not None, "PRESSURE_HISTORY_UNKNOWN",
                       f"history.{field_name}" if value is None else None)
        checks.require(value is not True, "PRIOR_EXPOSURE_OUTSIDE_SOURCE")
    state = profile.initial_state
    checks.require(state.method == "assumed_equilibrium", "INITIAL_STATE_OUTSIDE_SOURCE")
    checks.require(is_sea_level(state.body_pressure.pascals()), "STARTING_RESIDENCE_OUTSIDE_SOURCE")
    checks.require(is_source_air(state.gas), "INITIAL_GAS_OUTSIDE_SOURCE")
    checks.require(state.gas is None or (
        not state.gas.delivery_uncertainty and state.gas.delivery_method != "unknown"),
        "SOURCE_GAS_DELIVERY_MISMATCH")
    conditioning = profile.history.segments + [s for s in pre if s.phase == "residence"]
    first_preparation = next((i for i,s in enumerate(pre) if s.phase != "residence"), len(pre))
    checks.require(not any(s.phase == "residence" for s in pre[first_preparation:]),
                   "RESIDENCE_INTERRUPTS_PREBREATHE")
    checks.require(all(s.phase == "residence" and is_source_air(s.gas) and is_source_air(s.end_gas or s.gas) and
                       is_sea_level(s.start_pressure.pascals()) and is_sea_level(s.end_pressure.pascals())
                       and s.breathing_overpressure_pa == 0 for s in conditioning),
                   "RESIDENCE_HISTORY_OUTSIDE_SOURCE")
    checks.require(all(s.gas is not None for s in pre+plateau), "GAS_HISTORY_INCOMPLETE")
    checks.require(all(
        not s.breathing_overpressure_pa and all(g is None or (
            g.basis == "dry" and not g.delivery_uncertainty and g.delivery_method != "unknown"
        ) for g in (s.gas, s.end_gas)) for s in conditioning+pre+plateau
    ), "SOURCE_GAS_DELIVERY_MISMATCH")
    checks.require(all(s.gas is None or _source_gas(s, 1) for s in plateau), "PLATEAU_GAS_OUTSIDE_SOURCE")
    for s in plateau:
        checks.require(s.activity and s.activity.ambulation is not None, "AMBULATION_UNKNOWN",
                       f"segments.{s.id}.activity.ambulation")


def _exercise_protocol(profile, pre, plateau, plateau_minutes, checks):
    """TP-2004 Phase I, including the differentiated exercise and gas histories."""
    conditioning = profile.history.segments + [s for s in pre if s.phase == "residence"]
    checks.require(_close(_duration(profile, conditioning), 100) and all(
        s.activity and s.activity.ambulation is False and s.activity.posture == "recumbent"
        for s in conditioning), "PRETEST_ADYNAMIA_NOT_MATCHED")
    prep = [s for s in pre if s.phase != "residence"]
    # The calibration test in Appendix A has a seated fixture. Figures 8–9
    # specify semi-recumbent posture for the PB undertaken by chamber subjects.
    for s in prep:
        unknown = s.activity is None or s.activity.posture in {None, "unknown"}
        checks.require(not unknown, "PREBREATHE_POSTURE_UNKNOWN", f"segments.{s.id}.activity.posture")
        checks.require(unknown or s.activity.posture == "semi_recumbent", "PREBREATHE_POSTURE_OUTSIDE_SOURCE")
    checks.require(all(s.phase in {"prebreathe", "recovery", "ascent"} for s in prep),
                   "SOURCE_PRESSURE_SEQUENCE_MISMATCH")
    checks.require(_matching_stages(profile, prep, PHASE_I_INTERVALS, require_workload=True),
                   "SOURCE_WORKLOAD_OR_PRESSURE_SEQUENCE_MISMATCH")
    checks.require(all(s.activity and s.activity.type == "simulated_eva"
                       and s.activity.exercise_mode == "crank_and_yank" and s.activity.ambulation is False
                       and s.activity.posture == "semi_recumbent" for s in plateau),
                   "ALTITUDE_ACTIVITY_OUTSIDE_SOURCE")
    checks.require(_close(plateau_minutes, 240), "SOURCE_HORIZON_MISMATCH")
    person = profile.person_covariates
    nm = profile.prediction_request.model_id == "nasa_2004_nm" or profile.prediction_request.window == "source_post_test"
    upper = 61.9 if nm else 62.1
    checks.require(person.vo2_peak_ml_kg_min is not None and 22.7 <= person.vo2_peak_ml_kg_min <= upper,
                   "SOURCE_FITNESS_OUTSIDE_RANGE", "person_covariates.vo2_peak_ml_kg_min"
                   if person.vo2_peak_ml_kg_min is None else None)
    checks.require(person.vo2_peak_method == "measured", "MEASURED_SOURCE_FITNESS_REQUIRED")


def _rest_protocol(profile, pre, plateau, p2, plateau_minutes, checks):
    r = profile.prediction_request
    rest, ascent = _split_final_ascent(pre)
    basic = (bool(ascent) and all(s.phase == "prebreathe" for s in rest)
             and all(s.activity and s.activity.type == "rest" and s.activity.ambulation is False
                     and _source_gas(s, 1) for s in pre))
    checks.require(basic, "SOURCE_PREBREATHE_MISMATCH")
    checks.require(all(s.activity and s.activity.ambulation is True and s.activity.type in
                       {"exercise", "ambulatory", "simulated_eva"} for s in plateau),
                   "ALTITUDE_ACTIVITY_OUTSIDE_SOURCE")
    checks.require(all(s.activity and s.activity.exercise_mode in {None, "source_simulated_eva"}
                       and s.activity.vo2_ml_kg_min is None and s.activity.vo2_l_min is None
                       and s.activity.percent_vo2_peak is None for s in plateau),
                   "ALTITUDE_WORKLOAD_UNVERIFIED")
    if r.source_protocol == APPENDIX_A:
        target, pb, slope = 6., 60., 15.
    else:
        target = next((p for p in TABLE5_ROWS if _close(p, p2)), None)
        if target is None:
            checks.require(False, "SOURCE_PRESSURE_TIME_PAIR_UNVERIFIED")
            return
        pb, slope = TABLE5_ROWS[target], 30.
    stages = ((pb, 14.7, 14.7, 1., 0., ""), (pb+slope, 14.7, target, 1., 0., ""))
    checks.require(_matching_stages(profile, pre, stages), "SOURCE_PRESSURE_TIME_PAIR_UNVERIFIED")
    checks.require(_close(_duration(profile, ascent), slope), "DEPRESSURIZATION_OUTSIDE_SOURCE")
    checks.require(_close(plateau_minutes, 240) or (
        r.source_protocol == TABLE5 and _close(target, 4.3) and _close(plateau_minutes, 360)
    ), "SOURCE_PLATEAU_DURATION_MISMATCH")


def _simple_rest_protocol(profile, prep, plateau, plateau_minutes, p2, checks):
    rest, ascent = _split_final_ascent(prep)
    slope = _duration(profile, ascent)
    checks.require(all(g and g.delivery_method and g.delivery_method != "unknown"
                       for s in prep+plateau for g in (s.gas, s.end_gas or s.gas)),
                   "SOURCE_GAS_DELIVERY_MISMATCH")
    checks.require(bool(rest) and all(s.phase == "prebreathe" and
                   is_sea_level(s.start_pressure.pascals()) and is_sea_level(s.end_pressure.pascals())
                   for s in rest), "RESTING_PREBREATHE_REQUIRED")
    checks.require(5 <= slope <= 30 and _matching_stages(profile, ascent, [(slope, 14.7, p2, 1, 0, "")]),
                   "DEPRESSURIZATION_OUTSIDE_SOURCE")
    checks.require(all(_source_gas(s, 1) and s.activity and s.activity.type == "rest"
                   and s.activity.ambulation is False and s.activity.posture in {"semi_recumbent", "recumbent"}
                   and s.activity.vo2_ml_kg_min is None and s.activity.vo2_l_min is None
                   and s.activity.percent_vo2_peak is None for s in prep), "RESTING_OXYGEN_PREPARATION_REQUIRED")
    activities = [s.activity for s in plateau]
    checks.require(all(a and a.ambulation is not None and a.type in {"simulated_eva", "exercise", "ambulatory"}
                   and a.exercise_mode == "source_simulated_eva" and a.vo2_ml_kg_min is None
                   and a.vo2_l_min is None and a.percent_vo2_peak is None
                   and (a.posture == "standing" if a.ambulation else a.posture in {"recumbent", "semi_recumbent"})
                   for a in activities)
                   and len({a.ambulation for a in activities if a}) == 1, "ALTITUDE_WORKLOAD_UNVERIFIED")
    checks.require(120 <= plateau_minutes <= 360, "SOURCE_PLATEAU_DURATION_MISMATCH")


def _post_test_course(profile, after, checks):
    """NM includes post-test diagnoses. Appendix D ends at minute 420."""
    if not after:
        reference = profile.prediction_request.post_test_course == "published_source_ascertainment"
        checks.require(reference, "POST_TEST_COURSE_UNSPECIFIED", "prediction_request.post_test_course")
        return "published_source_ascertainment" if reference else "unspecified"
    # The source does not specify a return gas/rate or fixed surveillance interval
    # to validate user-entered post-test schedules. Distinguish missing gas and
    # a physiologically contradictory return from an unverified, complete schedule.
    returning = [s for s in after if s.phase == "return"]
    checks.require(bool(returning), "POST_TEST_RETURN_MISSING", "segments.return")
    if returning:
        checks.require(after[:len(returning)] == returning and
                       all(_p(s, True) > _p(s) for s in returning) and
                       is_sea_level(returning[-1].end_pressure.pascals()) and
                       all(s.phase == "post_exposure" and is_sea_level(s.start_pressure.pascals())
                           and is_sea_level(s.end_pressure.pascals()) for s in after[len(returning):]),
                       "RETURN_PRESSURE_SEQUENCE_MISMATCH")
    checks.require(False, "POST_TEST_COURSE_UNVERIFIED")
    return "submitted_post_test_course"


def _reference(profile, model, pre, plateau, after, phys, checks):
    r, person = profile.prediction_request, profile.person_covariates
    plateau_minutes = _duration(profile, plateau)
    required = {s.id for s in _required_segments(profile, pre, plateau, after)}
    plateau = [s for s in plateau if s.id in required]
    _reference_checks(profile, model, pre, plateau, after, checks)
    if not plateau:
        return None, {}
    p2 = _p(plateau[0])
    prep = [s for s in pre if s.phase != "residence"]
    rep = _rep(profile, prep, p2)
    arrival = phys["arrival_nitrogen_pa"]
    tr = arrival/(PA_PER_PSIA*p2) if arrival is not None else None
    features = {"arrival_nitrogen_pa": arrival, "arrival_pressure_psia": p2,
                "arrival_tissue_ratio": tr, "source_repressurization_protocol": rep}
    checks.require(tr is not None, "SOURCE_ARRIVAL_NITROGEN_UNAVAILABLE")
    if any((s.phase == "oxygen_break" and s.break_kind != "exercise_only")
           or s.break_kind in {"breathing_gas", "mask_to_suit", "purge"}
           or s.phase == "purge" for s in pre+plateau):
        # Phase I specifies a particular gas switch; encode it as its nominal PB stage.
        checks.require(False, "BREAK_PROTOCOL_UNSUPPORTED")
    if any(s.break_kind == "exercise_only" for s in pre+plateau):
        checks.require(False, "EXERCISE_INTERRUPTION_OUTSIDE_PROTOCOL")
    if r.source_protocol == PHASE_I:
        _exercise_protocol(profile, pre, plateau, plateau_minutes, checks)
    elif r.source_protocol in {TABLE5, APPENDIX_A}:
        _rest_protocol(profile, prep, plateau, p2, plateau_minutes, checks)
    elif r.source_protocol == SIMPLE_OXYGEN:
        _simple_rest_protocol(profile, prep, plateau, plateau_minutes, p2, checks)
    if model["model_id"] in VGE_MODELS:
        # Concentration of the monitored data near 4.3 psia; the 6.0-psia
        # worked protocol is explicitly reproduced in Appendix A, example 1.
        pressure_supported = abs(p2 - 4.3) <= 0.005 or (
            r.source_protocol == APPENDIX_A and _close(p2, 6) and _close(r.horizon_minutes, 240))
        checks.require(pressure_supported, "VGE_PRESSURE_PROTOCOL_OUTSIDE_SUPPORT")
        checks.require(120 <= r.horizon_minutes <= 360, "SOURCE_HORIZON_MISMATCH")
        checks.require(tr is not None and .92 <= tr <= 2.02, "TISSUE_RATIO_OUTSIDE_SOURCE")
        checks.require(rep is not None, "SOURCE_REPRESSURIZATION_UNVERIFIED")
        checks.require(person.age_years is not None and 20 <= person.age_years <= 54,
                       "VGE_AGE_OUTSIDE_SUPPORT", "person_covariates.age_years" if person.age_years is None else None)
        checks.require(person.source_sex in {"male", "female"}, "SOURCE_SEX_REQUIRED", "person_covariates.source_sex")
        if checks.reasons:
            return None, features
        return vge_fraction(model["model_id"], hours=r.horizon_minutes/60, tissue_ratio=tr,
                            age=person.age_years, male=person.source_sex == "male",
                            ambulatory=plateau[0].activity.ambulation, staged=rep), features
    if model["model_id"] in {"nasa_2004_rm", "nasa_2004_nm"}:
        nm = model["model_id"] == "nasa_2004_nm"
        checks.require(_close(p2, 4.3) and rep is True, "SOURCE_PRESSURE_SEQUENCE_MISMATCH")
        checks.require(_close(r.horizon_minutes, 240), "SOURCE_HORIZON_MISMATCH")
        if nm:
            if r.window == "source_post_test":
                features["post_test_course"] = _post_test_course(profile, after, checks)
            checks.require(person.source_sex in {"male", "female"}, "SOURCE_SEX_REQUIRED",
                           "person_covariates.source_sex")
        else:
            checks.require(person.age_years is not None and 18 <= person.age_years <= 59,
                           "SOURCE_AGE_OUTSIDE_RANGE", "person_covariates.age_years"
                           if person.age_years is None else None)
        if not checks.reasons:
            kwargs = {"variant": "NM", "sex": person.source_sex.title()} if nm else {
                "variant": "RM", "age_years": person.age_years}
            return predict_endpoint(tr, **kwargs), features
        return None, features
    low = model["model_id"] == "nasa_2020_eq4"
    checks.require(4 <= p2 <= 5 if low else 5 < p2 <= 7.5, "PRESSURE_BRANCH_MISMATCH")
    checks.require(120 <= r.horizon_minutes <= (360 if low else 240), "SOURCE_HORIZON_MISMATCH")
    tr_min, tr_max = (.92, 2.02) if low else (1.23, 1.78)
    checks.require(tr is not None and tr_min <= tr <= tr_max, "TISSUE_RATIO_OUTSIDE_SOURCE")
    if low:
        checks.require(person.bmi_kg_m2 is not None and 18 <= person.bmi_kg_m2 <= 30,
                       "BMI_OUTSIDE_SOURCE", "person_covariates.bmi_kg_m2" if person.bmi_kg_m2 is None else None)
        checks.require(rep is not None, "SOURCE_REPRESSURIZATION_UNVERIFIED")
    else:
        checks.require(rep is False, "SOURCE_REPRESSURIZATION_UNVERIFIED")
    if checks.reasons:
        return None, features
    _, ascent = _split_final_ascent(prep)
    amb = plateau[0].activity.ambulation
    result = hypobaric_probability(HypobaricScenario(
        plateauPressurePsia=p2, elapsedPlateauHours=r.horizon_minutes/60,
        depressurizationMinutes=_duration(profile, ascent), singleConstantPlateau=True,
        arrivalTissueN2Psia=arrival/PA_PER_PSIA, ambulationAtPlateau=amb,
        bmiKgM2=person.bmi_kg_m2, sourceRepressurizationProtocol=rep,
        maleReferenceCohort=r.reference_population == "male_hypobaric_chamber",
    ))
    if result.pDcsPercent is None:
        checks.require(False, "OUTSIDE_EVALUATED_SUPPORT")
        features["software_guard"] = result.reason
        return None, features
    return result.pDcsPercent/100, features


def evaluate(profile: ExposureProfile) -> dict:
    """One entry point for prospective histories. Internal probabilities are fractions."""
    # Revalidate the current contents, including mutable lists on an existing Python object.
    if isinstance(profile, ExposureProfile):
        profile = profile.model_dump()
    profile = ExposureProfile.model_validate(profile)
    pre, plateau, after = _split(profile)
    p2 = _p(plateau[0]) if plateau else None
    r = profile.prediction_request
    chosen = _choose_model(profile, p2)
    model = _MODELS.get(chosen, _MODELS["physiology"])
    kinetics = ("nasa_2020" if chosen in {"nasa_2020_eq4", "conkin_1996_eq7", *VGE_MODELS} else
                chosen if chosen in {"nasa_2004_nm", "nasa_2004_rm"} else "fixed_360")
    # Model-specific physiological features may be unavailable while a declared-gas
    # trajectory remains computable (e.g. a missing workload for a 2004 reference).
    source_physics = derive_physiology(profile, kinetics)
    phys = source_physics
    if kinetics != "fixed_360" and source_physics["arrival_nitrogen_pa"] is None:
        phys = derive_physiology(profile)
    checks = Checks()
    required = _required_segments(profile, pre, plateau, after)
    relevant_fields = {f"segments.{s.id}.{name}" for s in required for name in ("gas", "activity")}
    for path in source_physics["missing_inputs"]:
        if path.startswith("initial_state.") or path in relevant_fields:
            checks.require(False, "DECISIVE_INPUT_MISSING", path)
    if any(path.startswith("initial_state.") or path in relevant_fields
           for path in source_physics["incompatible_inputs"]):
        checks.require(False, "SOURCE_INPUT_INCOMPATIBLE")
    if profile.initial_state.method == "unknown":
        checks.require(False, "INITIAL_STATE_UNKNOWN", "initial_state")
    if any(s.gas is None for s in required):
        checks.require(False, "GAS_HISTORY_INCOMPLETE")
    if r.endpoint != "physiology" and r.window in {"complete_exposure", "post_return", "through_follow_up"} and (
        not plateau or _duration(profile, plateau) < 120
    ):
        checks.require(False, "COMPLETE_SHORT_PROFILE_NOT_VALIDATED")
    if chosen not in _MODELS:
        checks.require(False, "MODEL_REPRODUCTION_UNRESOLVED" if chosen == "rut_mbe1" else "MODEL_UNAVAILABLE")
    if model["model_id"] == "physiology":
        if r.endpoint != "physiology":
            checks.require(False, "CLINICAL_OUTCOME_MODEL_UNAVAILABLE" if r.endpoint ==
                           "clinically_adjudicated_dcs" else "NO_ELIGIBLE_ENDPOINT_MODEL")
        elif checks.missing:
            checks.require(False, "INCOMPLETE_EXPOSURE_HISTORY")
        value, source_features = None, {}
    else:
        value, source_features = _reference(profile, model, pre, plateau, after, source_physics, checks)
    probability_enabled = value is not None and not checks.reasons
    personal = {k for k, v in profile.person_covariates.model_dump().items() if v is not None}
    source_person = {"nasa_2020_eq4": {"bmi_kg_m2"}, "conkin_1996_eq7": set(),
                     "nasa_2004_rm": {"age_years"}, "nasa_2004_nm": {"source_sex"}}.get(chosen, set())
    if chosen in VGE_MODELS:
        source_person = {"age_years", "source_sex"}
    if kinetics.startswith("nasa_2004") or r.source_protocol == PHASE_I:
        source_person = source_person | {"vo2_peak_ml_kg_min", "vo2_peak_method"}
    if any(s.activity and s.activity.vo2_l_min is not None for s in pre) and kinetics != "fixed_360":
        source_person = source_person | {"mass_kg"}
    included = ["initial_state", "body_pressure_history", "inspired_gas_history", "segment_duration"]
    if model["evidence_class"] == "published_reference":
        included += ["source_prebreathe_workload", "plateau_ambulation", "source_protocol"]
    unused = sorted(personal-source_person)
    if kinetics == "fixed_360":
        unused += ["activity (fixed 360-minute compartment)"]
    if any(s.vehicle_geometric_altitude_m is not None for s in profile.segments):
        unused.append("vehicle_geometric_altitude_m")
    assumptions = list(phys["assumptions"])
    if model["evidence_class"] == "published_reference":
        assumptions.append("The reference protocol and population are checked against the submitted timeline.")
    if source_features.get("post_test_course") == "published_source_ascertainment":
        assumptions.append("NM reproduces the Phase I group's published post-test ascertainment (Table 6). "
                           "The submitted plan ends at plateau exit; no return gas, rate or follow-up duration is assumed.")
    return {"schema_version": SCHEMA_VERSION, "core_version": CORE_VERSION,
            "profile_id": profile.profile_id, "input_fingerprint": profile.fingerprint(),
            **{k: model[k] for k in ("model_id", "model_version", "coefficient_version", "source",
                                     "artifact_hash", "artifact_hash_kind", "evidence_class", "applicability_version")},
            "requested_model_id": r.model_id, "probability_fraction": value if probability_enabled else None,
            "endpoint": r.endpoint, "prediction_origin": r.prediction_origin, "horizon_minutes": r.horizon_minutes,
            "outcome_window": r.window, "outcome_ascertainment": model["ascertainment"],
            "reference_population": r.reference_population, "source_population": model["population"],
            "source_protocol": r.source_protocol, "source_features": source_features,
            "applicability": {"status": "unsupported" if checks.reasons else
                              ("supported" if probability_enabled else "physiology_only"),
                              "reasons": checks.reasons},
            "quantitative_output_enabled": probability_enabled, "inherited_vetoes": list(checks.reasons),
            "uncertainty": {"status": "unavailable", "method": None, "level": None,
                            "lower": None, "upper": None,
                            "reason": ("Joint parameter uncertainty is unavailable for this reference prediction."
                                       if model["evidence_class"] == "published_reference" else
                                       "The deterministic exposure calculation has no fitted probability interval.")},
            "assumptions": assumptions, "included_factors": included+sorted(source_person & personal),
            "unused_factors": unused,
            "missing_decisive_inputs": checks.missing,
            "physiology": phys, "pressure_routing_boundary_psia": 5.0,
            "policy_conformance": interruption_record(profile)}
