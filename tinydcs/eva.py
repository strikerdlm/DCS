"""EVA single-compartment calculations with source applicability and nullability.

NASA's logistic equation is a four-hour, 4.3-psia endpoint model, not a hazard
function. No time-risk curve, confidence interval, or non-DCS event probability
is inferred. Mission-rule classifications are separate from scientific evidence.
"""

from __future__ import annotations
import copy
import hashlib
import json
import math
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Any, Mapping
import yaml
from mechanistic.conkin_nasa import nitrogen_half_time, compute_p1n2, predict_endpoint, SOURCE_URL
from mechanistic.atmosphere import KPA_PER_PSIA, MMHG_PER_PSIA
from tinydcs.eva_contract import EVAScenario
from tinydcs.eva_telemetry import TelemetryAdjustment, apply_telemetry_adjustment

LN2 = math.log(2)
WATER_VAPOR_PSIA = 47 / MMHG_PER_PSIA
TISSUE_HALF_TIME_MIN = 360.0
MODEL_VERSION = "eva-reference-v2"
MissionRules = dict[str, Any]
Scenario = dict[str, Any]


@dataclass(frozen=True)
class RutReconciliationStatus:
    model: str = "3RUT-MBe1"
    absolute_risk_enabled: bool = False
    status: str = "reconciliation_required"
    reason: str = "Absolute risk disabled: source gain/volume convention and full numerical/profile benchmarks remain unresolved."

    def to_dict(self):
        return {
            "model": self.model,
            "absoluteRiskEnabled": self.absolute_risk_enabled,
            "status": self.status,
            "reason": self.reason,
        }


def clamp(value, lo, hi):
    if not math.isfinite(value):
        raise ValueError("finite value required")
    return min(max(value, lo), hi)


def stable_sigmoid(x):
    if math.isnan(x):
        raise ValueError("NaN cannot represent a probability")
    if x >= 0:
        return 1 / (1 + math.exp(-x))
    value = math.exp(x)
    return value / (1 + value)


def psia_to_kpa(psia):
    return psia * KPA_PER_PSIA


def psia_to_mmhg(psia):
    return psia * MMHG_PER_PSIA


def inspired_gas_psia(total_pressure_psia, fraction):
    """Humidified inspired gas ONLY; NASA nitrogen dose uses dry ambient gas."""
    return max(total_pressure_psia - WATER_VAPOR_PSIA, 0) * fraction


def tissue_toward(initial_psia, target_psia, duration_min):
    return target_psia + (initial_psia - target_psia) * math.exp(-duration_min * LN2 / 360)


def exercise_adjusted_k(vo2_ml_kg_min):
    return nitrogen_half_time(vo2_ml_kg_min, 0.025)


def tissue_toward_with_exercise(initial_psia, target_psia, duration_min, vo2_ml_kg_min):
    return compute_p1n2(
        p0=initial_psia,
        pa=target_psia,
        pb_time_min=duration_min,
        vo2_ml_kg_min=vo2_ml_kg_min,
        lambda_param=0.025,
    )


def conkin_research_pdcs(etr, age_years):
    return 100 * predict_endpoint(etr, variant="RM", age_years=age_years)


def default_mission_rules() -> MissionRules:
    return {
        "profile_id": "default",
        "name": "Default EVA planning rules",
        "lxc_probability_thresholds_percent": {
            "level_2_min": 1.0,
            "level_3_min": 5.0,
            "level_4_min": 15.0,
            "level_5_min": 35.0,
        },
        "posture_score_max": {"green": 4, "yellow": 9, "orange": 15},
        "decision_thresholds": {
            "delay_lxc_score_min": 16,
            "delay_risk_percent_min": 20.0,
            "modify_lxc_score_min": 10,
            "modify_risk_percent_min": 10.0,
            "monitor_lxc_score_min": 5,
            "monitor_risk_percent_min": 1.0,
        },
        "envelope": {
            "suit_pressure_psia_min": 3.7,
            "suit_pressure_psia_max": 8.2,
            "habitat_pressure_psia_min": 5.0,
            "habitat_pressure_psia_max": 14.7,
            "habitat_oxygen_fraction_min": 0.20,
            "habitat_oxygen_fraction_max": 0.40,
            "prebreathe_oxygen_fraction_min": 0.21,
            "prebreathe_oxygen_fraction_max": 1.0,
            "prebreathe_min_min": 0.0,
            "prebreathe_min_max": 300.0,
            "eva_duration_min_min": 30.0,
            "eva_duration_min_max": 540.0,
            "short_prebreathe_high_pressure_min": 15.0,
            "short_prebreathe_high_pressure_psia": 8.2,
        },
        "hazards": {
            "dcs_base_consequence": 3,
            "dcs_etr_consequence_trigger": 1.4,
            "dcs_shelter_return_consequence_trigger_min": 20.0,
        },
        "telemetry": {
            "max_sample_age_sec": 120.0,
            "min_confidence": 0.5,
            "pressure_source": "suit",
        },
    }


def _deep_merge(base: MissionRules, override: Mapping[str, Any]) -> MissionRules:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def load_mission_rules(profile: str = "default", *, directory: Path | None = None) -> MissionRules:
    """Load a mission-rule profile and merge it over the built-in defaults."""

    profile = profile or "default"
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", profile):
        raise FileNotFoundError("Unknown mission-rule profile")
    base = default_mission_rules()
    if directory is not None:
        path = directory / f"{profile}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Mission-rule profile not found: {profile}")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return _deep_merge(base, data)

    try:
        rules_package = resources.files("tinydcs").joinpath("mission_rules")
        path = rules_package.joinpath(f"{profile}.yaml")
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Mission-rule profile not found: {profile}") from exc

    return _deep_merge(base, data)


def available_mission_rule_profiles() -> list[str]:
    rules_package = resources.files("tinydcs").joinpath("mission_rules")
    return sorted(
        path.name.removesuffix(".yaml")
        for path in rules_package.iterdir()
        if path.name.endswith(".yaml")
    )


def interval_for_risk_percent(risk_percent, scenario, rules=None):
    """No calibrated EVA interval exists for this reference equation."""
    return {"low": None, "high": None}


def likelihood_from_probability(percent, rules):
    if percent is None:
        return None
    if not math.isfinite(percent) or not 0 <= percent <= 100:
        raise ValueError("risk must be a finite percentage")
    thresholds = rules["lxc_probability_thresholds_percent"]
    for level in range(2, 6):
        if percent < thresholds[f"level_{level}_min"]:
            return level - 1
    return 5


def posture(score, rules):
    if score is None:
        return "unavailable"
    for color in ("green", "yellow", "orange"):
        if score <= rules["posture_score_max"][color]:
            return color
    return "red"


def hazard(hazard_id, name, probability_percent, consequence, driver, rules, indicator=None):
    likelihood = likelihood_from_probability(probability_percent, rules)
    score = likelihood * consequence if likelihood is not None else None
    return {
        "id": hazard_id,
        "name": name,
        "probabilityPercent": probability_percent,
        "likelihood": likelihood,
        "consequence": consequence,
        "score": score,
        "posture": posture(score, rules),
        "driver": driver,
        "indicator": indicator,
        "evidenceStatus": "reference_endpoint"
        if probability_percent is not None
        else "indicator_only",
    }


def scenario_envelope_warnings(scenario: Mapping[str, Any], rules: MissionRules) -> list[str]:
    envelope = rules["envelope"]
    warnings: list[str] = []
    suit_pressure = scenario["suit"]["pressurePsia"]
    habitat_pressure = scenario["habitat"]["pressurePsia"]
    habitat_o2 = scenario["habitat"]["oxygenFraction"]
    prebreathe_o2 = scenario["prebreatheOxygenFraction"]
    prebreathe_min = scenario["prebreatheMin"]
    eva_duration = scenario["evaDurationMin"]

    if (
        suit_pressure < envelope["suit_pressure_psia_min"]
        or suit_pressure > envelope["suit_pressure_psia_max"]
    ):
        warnings.append(
            f"Suit pressure is outside the {envelope['suit_pressure_psia_min']:.1f}-"
            f"{envelope['suit_pressure_psia_max']:.1f} psia exploration comparison range."
        )
    if (
        habitat_pressure < envelope["habitat_pressure_psia_min"]
        or habitat_pressure > envelope["habitat_pressure_psia_max"]
    ):
        warnings.append(
            f"Habitat pressure is outside the {envelope['habitat_pressure_psia_min']:.1f}-"
            f"{envelope['habitat_pressure_psia_max']:.1f} psia planning range."
        )
    if (
        habitat_o2 < envelope["habitat_oxygen_fraction_min"]
        or habitat_o2 > envelope["habitat_oxygen_fraction_max"]
    ):
        warnings.append("Habitat oxygen fraction is outside the configured planning range.")
    if (
        prebreathe_o2 < envelope["prebreathe_oxygen_fraction_min"]
        or prebreathe_o2 > envelope["prebreathe_oxygen_fraction_max"]
    ):
        warnings.append("Prebreathe oxygen fraction is outside the configured planning range.")
    if (
        prebreathe_min < envelope["prebreathe_min_min"]
        or prebreathe_min > envelope["prebreathe_min_max"]
    ):
        warnings.append("Prebreathe duration is outside the configured planning range.")
    if (
        eva_duration < envelope["eva_duration_min_min"]
        or eva_duration > envelope["eva_duration_min_max"]
    ):
        warnings.append("EVA duration is outside the configured planning range.")
    if (
        prebreathe_min < envelope["short_prebreathe_high_pressure_min"]
        and habitat_pressure > envelope["short_prebreathe_high_pressure_psia"]
    ):
        warnings.append(
            "Short prebreathe from a high-pressure habitat is an unsupported extrapolation."
        )
    return warnings


def model_applicability(scenario):
    reasons = []
    if abs(scenario["evaDurationMin"] - 240) > 1e-8:
        reasons.append("The NASA endpoint is four hours; no duration scaling is validated.")
    pressure = scenario["pressureSegments"]
    if scenario["suit"]["variablePressure"] or len(pressure) > 1:
        reasons.append("Variable-pressure EVA is outside the NASA reference endpoint.")
    pressures = pressure or [scenario["suit"]]
    if any(
        abs(p["pressurePsia"] - 4.3) > 1e-8 or abs(p["oxygenFraction"] - 1) > 1e-8
        for p in pressures
    ):
        reasons.append("Reference exposure requires constant 4.3 psia and oxygen breathing.")
    if not scenario["nasaAdynamicReference"]:
        reasons.append("Adynamic source-reference assumptions have not been declared.")
    return {
        "applicable": not reasons,
        "reasons": reasons,
        "modelId": "conkin-RM-equation-14",
        "horizonMin": 240,
        "referencePressurePsia": 4.3,
        "source": SOURCE_URL,
        "intervalKind": "unavailable",
        "clinicalValidation": False,
        "evidenceStatus": "reference_calculation" if not reasons else "outside_reference",
        "assumptions": [
            "Source-cohort transportability is not established.",
            "NASA dry ambient nitrogen convention; lambda=0.025.",
            "Exercise-dependent kinetics outside prebreathe are an exploratory compartment extension.",
        ],
    }


def _pb_segments(s):
    return s["prebreatheSegments"] or (
        [
            {
                "durationMin": s["prebreatheMin"],
                "pressurePsia": s["habitat"]["pressurePsia"],
                "oxygenFraction": s["prebreatheOxygenFraction"],
                "vo2MlKgMin": s["prebreatheVo2MlKgMin"],
            }
        ]
        if s["prebreatheMin"]
        else []
    )


def _point(time, phase, pressure, oxygen, tissue, vo2):
    dry_n2 = pressure * (1 - oxygen)
    return {
        "timeMin": time,
        "phase": phase,
        "ambientPressurePsia": pressure,
        "ambientN2Psia": dry_n2,
        "inspiredN2Psia": dry_n2,
        "tissueN2Psia": tissue,
        "vo2MlKgMin": vo2,
        "cumulativePDcsPercent": None,
        "intervalLowPercent": None,
        "intervalHighPercent": None,
    }


def build_timeline(
    scenario,
    tissue_n2_start_psia,
    tissue_n2_after_prebreathe_psia=None,
    p_dcs_percent=None,
    rules=None,
):
    """Sequential piecewise-constant integration over all pressure/workload cuts."""
    s, tissue = scenario, tissue_n2_start_psia
    time = -s["prebreatheMin"]
    timeline = [
        _point(
            time, "habitat", s["habitat"]["pressurePsia"], s["habitat"]["oxygenFraction"], tissue, 0
        )
    ]
    for segment in _pb_segments(s):
        count = max(1, math.ceil(segment["durationMin"] / 5))
        duration = segment["durationMin"] / count
        for _ in range(count):
            tissue = tissue_toward_with_exercise(
                tissue,
                segment["pressurePsia"] * (1 - segment["oxygenFraction"]),
                duration,
                segment["vo2MlKgMin"],
            )
            time += duration
            timeline.append(
                _point(
                    min(time, 0),
                    "prebreathe",
                    segment["pressurePsia"],
                    segment["oxygenFraction"],
                    tissue,
                    segment["vo2MlKgMin"],
                )
            )
    timeline[-1]["timeMin"] = 0.0
    duration = s["evaDurationMin"]
    if duration == 0:
        return timeline
    workload = s["workload"] or [{"durationMin": duration, "vo2MlKgMin": s["meanVo2MlKgMin"]}]
    pressure = s["pressureSegments"] or [{"durationMin": duration, **s["suit"]}]

    def endpoints(blocks):
        value, out = 0.0, []
        for block in blocks:
            value += block["durationMin"]
            out.append(value)
        return out

    work_ends, pressure_ends = endpoints(workload), endpoints(pressure)
    work_ends[-1] = pressure_ends[-1] = duration
    step = max(1, math.ceil(duration / 48))
    cuts = sorted(
        set(
            [
                0.0,
                duration,
                *work_ends,
                *pressure_ends,
                *[float(t) for t in range(step, math.ceil(duration), step)],
            ]
        )
    )
    for start, end in zip(cuts, cuts[1:]):
        if end - start <= 1e-10:
            continue
        middle = (start + end) / 2
        work = workload[next(i for i, t in enumerate(work_ends) if middle < t)]
        gas = pressure[next(i for i, t in enumerate(pressure_ends) if middle < t)]
        tissue = tissue_toward_with_exercise(
            tissue,
            gas["pressurePsia"] * (1 - gas["oxygenFraction"]),
            end - start,
            work["vo2MlKgMin"],
        )
        timeline.append(
            _point(
                end, "eva", gas["pressurePsia"], gas["oxygenFraction"], tissue, work["vo2MlKgMin"]
            )
        )
    return timeline


def integrate_risk_percent_hours(timeline):
    """Unavailable: an endpoint regression does not define a risk-time curve."""
    return None


def max_risk(timeline):
    return {"percent": None, "timeMin": None}


def choose_decision(
    *,
    abstain,
    lxc_score,
    max_risk_percent,
    integrated_risk_percent_hours=None,
    consumables_margin_min,
    radiation_weather,
    symptom_flag,
    rules,
):
    if radiation_weather == "storm" or consumables_margin_min < 0 or symptom_flag:
        return {
            "decision": "abort",
            "rationale": "A configured stop condition is present, independently of model availability.",
        }
    if abstain or max_risk_percent is None or lxc_score is None:
        return {
            "decision": "abstain",
            "rationale": "No applicable DCS endpoint estimate; indicators do not establish a safe operating decision.",
        }
    thresholds = rules["decision_thresholds"]
    for action in ("delay", "modify", "monitor"):
        if (
            lxc_score >= thresholds[f"{action}_lxc_score_min"]
            or max_risk_percent >= thresholds[f"{action}_risk_percent_min"]
        ):
            return {
                "decision": action,
                "rationale": f"Reference endpoint meets the configured {action} threshold; this is a planning classification.",
            }
    return {
        "decision": "proceed",
        "rationale": "Below configured reference-model thresholds; this is not operational clearance.",
    }


def build_hazards(
    s,
    p_dcs_percent,
    etr,
    suit_inspired_o2_mmhg,
    habitat_inspired_o2_mmhg,
    consumables_margin_min,
    rules,
):
    consequence = int(
        clamp(
            rules["hazards"]["dcs_base_consequence"]
            + int(etr > rules["hazards"]["dcs_etr_consequence_trigger"])
            + int(
                s["environment"]["shelterReturnMin"]
                > rules["hazards"]["dcs_shelter_return_consequence_trigger_min"]
            ),
            1,
            5,
        )
    )
    rows = [
        hazard(
            "dcs",
            "DCS",
            p_dcs_percent,
            consequence,
            f"ETR {etr:.2f}; source applicability required",
            rules,
        )
    ]
    indicators = [
        (
            "hypoxia",
            "Inspired oxygen",
            min(suit_inspired_o2_mmhg, habitat_inspired_o2_mmhg),
            "mmHg",
            4,
            "Lowest humidified inspired O2; not an event probability",
        ),
        (
            "co2",
            "CO2 scrubber",
            s["suit"]["co2ScrubberMargin"],
            "fraction",
            4,
            "Entered scrubber margin",
        ),
        ("thermal", "Cooling", s["suit"]["coolingMargin"], "fraction", 3, "Entered cooling margin"),
        (
            "dust",
            "Dust exposure",
            s["environment"]["dustLevel"],
            "index 0–1",
            3,
            "User-entered dust indicator",
        ),
        (
            "fatigue",
            "Workload",
            s["peakVo2MlKgMin"],
            "mL/kg/min",
            3,
            "Declared peak VO2; no fatigue probability model",
        ),
        (
            "radiation",
            "Radiation weather",
            s["environment"]["radiationWeather"],
            "category",
            5,
            "Declared weather state",
        ),
        (
            "consumables",
            "PLSS margin",
            consumables_margin_min,
            "min",
            4,
            "PLSS duration minus EVA duration; reserve is separate",
        ),
    ]
    for key, name, value, unit, consequence, driver in indicators:
        rows.append(
            hazard(
                key,
                name,
                None,
                consequence,
                driver,
                rules,
                {"value": value, "unit": unit, "source": "scenario_or_arithmetic"},
            )
        )
    return rows


def simulate_eva(scenario, *, mission_rules=None, telemetry=None, telemetry_now_sec=None):
    rules = mission_rules or load_mission_rules("default")
    s = EVAScenario.model_validate(scenario).model_dump()
    adjustment = TelemetryAdjustment.empty()
    if telemetry:
        adjustment = apply_telemetry_adjustment(s, telemetry, rules, now_sec=telemetry_now_sec)
        s = EVAScenario.model_validate(s).model_dump()
    habitat_n2 = s["habitat"]["pressurePsia"] * (1 - s["habitat"]["oxygenFraction"])
    initial = tissue_toward(11.6, habitat_n2, s["habitat"]["equilibrationHours"] * 60)
    p1 = initial
    for segment in _pb_segments(s):
        p1 = tissue_toward_with_exercise(
            p1,
            segment["pressurePsia"] * (1 - segment["oxygenFraction"]),
            segment["durationMin"],
            segment["vo2MlKgMin"],
        )
    exposure_pressure = (
        s["pressureSegments"][0]["pressurePsia"]
        if s["pressureSegments"]
        else s["suit"]["pressurePsia"]
    )
    etr = p1 / exposure_pressure
    applicability = model_applicability(s)
    probability = (
        conkin_research_pdcs(etr, s["crew"]["ageYears"]) if applicability["applicable"] else None
    )
    suit_o2 = min(
        psia_to_mmhg(inspired_gas_psia(p["pressurePsia"], p["oxygenFraction"]))
        for p in (s["pressureSegments"] or [s["suit"]])
    )
    habitat_o2 = psia_to_mmhg(
        inspired_gas_psia(s["habitat"]["pressurePsia"], s["habitat"]["oxygenFraction"])
    )
    margin = s["suit"]["plssDurationMin"] - s["evaDurationMin"]
    planning_warnings = scenario_envelope_warnings(s, rules)
    warnings = applicability["reasons"] + planning_warnings
    abstain = not applicability["applicable"] or bool(planning_warnings)
    timeline = build_timeline(s, initial)
    hazards = build_hazards(s, probability, etr, suit_o2, habitat_o2, margin, rules)
    dcs = hazards[0]
    stops = []
    if s["crew"]["symptomFlag"]:
        stops.append("active_symptoms")
    if s["environment"]["radiationWeather"] == "storm":
        stops.append("radiation_storm")
    if margin < 0:
        stops.append("negative_plss_margin")
    decision = choose_decision(
        abstain=abstain,
        lxc_score=dcs["score"],
        max_risk_percent=probability,
        consumables_margin_min=margin,
        radiation_weather=s["environment"]["radiationWeather"],
        symptom_flag=s["crew"]["symptomFlag"],
        rules=rules,
    )
    total_work = (
        sum(b["durationMin"] * b["vo2MlKgMin"] for b in s["workload"])
        if s["workload"]
        else s["evaDurationMin"] * s["meanVo2MlKgMin"]
    )
    return {
        "schemaVersion": 2,
        "pDcsPercent": probability,
        "intervalLowPercent": None,
        "intervalHighPercent": None,
        "modelApplicability": applicability,
        "p1n2Psia": p1,
        "etr": etr,
        "tissueN2StartPsia": initial,
        "tissueN2AfterPrebreathePsia": p1,
        "suitInspiredO2MmHg": suit_o2,
        "habitatInspiredO2MmHg": habitat_o2,
        "consumablesMarginMin": margin,
        "oxygenReserveMin": s["suit"]["oxygenReserveMin"],
        "workloadMeanVo2MlKgMin": total_work / s["evaDurationMin"] if s["evaDurationMin"] else 0.0,
        "workloadTotalO2Litres": total_work * s["crew"]["massKg"] / 1000,
        "inEnvelope": not abstain,
        "planningEnvelope": not planning_warnings,
        "abstain": abstain,
        "envelopeWarnings": warnings,
        "maxRiskPercent": None,
        "maxRiskTimeMin": None,
        "integratedRiskPercentHours": None,
        "lxcLikelihood": dcs["likelihood"],
        "lxcConsequence": dcs["consequence"],
        "lxcScore": dcs["score"],
        "lxcCategory": dcs["posture"],
        "decision": decision["decision"],
        "decisionRationale": decision["rationale"],
        "stopReasons": stops,
        "timeline": timeline,
        "hazards": hazards,
        "telemetryStatus": adjustment.to_dict(),
    }


def simulation_response(
    scenario, *, mission_rule_profile="default", telemetry=None, telemetry_now_sec=None
):
    rules = load_mission_rules(mission_rule_profile)
    validated = EVAScenario.model_validate(scenario).model_dump()
    telemetry_now_sec = time.time() if telemetry_now_sec is None else telemetry_now_sec
    result = simulate_eva(
        validated, mission_rules=rules, telemetry=telemetry, telemetry_now_sec=telemetry_now_sec
    )
    inputs = {
        "scenario": validated,
        "missionRules": rules,
        "telemetry": telemetry or [],
        "telemetryNowSec": telemetry_now_sec,
    }
    fingerprint = hashlib.sha256(
        json.dumps(inputs, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    return {
        "schemaVersion": 2,
        "scenarioId": validated["id"],
        "scenario": validated,
        "telemetry": telemetry or [],
        "telemetryNowSec": telemetry_now_sec,
        "inputFingerprint": fingerprint,
        "missionRuleProfile": rules["profile_id"],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "modelMetadata": {
            "modelVersion": MODEL_VERSION,
            "schemaVersion": 2,
            "absoluteRiskSource": "NASA TP-2004-213158 Eq.14 at declared reference conditions only",
            "intervalKind": "unavailable",
            "researchUseOnly": True,
            "rutReconciliation": RutReconciliationStatus().to_dict(),
        },
        "missionRules": rules,
        "result": result,
    }


def response_to_json(response):
    return json.dumps(response, indent=2, sort_keys=True, allow_nan=False)
