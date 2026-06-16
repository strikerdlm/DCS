"""EVA DCS scenario engine for TinyDCS space-operations workflows.

The functions in this module mirror the browser-side EVA simulator while
making mission rules, telemetry inputs, and report/API integration available to
the Python stack. Outputs are research/planning artifacts only.
"""

from __future__ import annotations

import copy
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Any, Mapping

import yaml

from tinydcs.eva_telemetry import TelemetryAdjustment, apply_telemetry_adjustment


LN2 = math.log(2.0)
SEA_LEVEL_PSIA = 14.7
WATER_VAPOR_PSIA = 0.91
N2_AIR_FRACTION = 0.79
TISSUE_HALF_TIME_MIN = 360.0
TISSUE_TAU_MIN = TISSUE_HALF_TIME_MIN / LN2
MODEL_VERSION = "eva-conkin-planning-v1"

MissionRules = dict[str, Any]
Scenario = dict[str, Any]


@dataclass(frozen=True)
class RutReconciliationStatus:
    """Status gate for quantitative use of 3RUT-MBe1."""

    model: str = "3RUT-MBe1"
    absolute_risk_enabled: bool = False
    status: str = "reconciliation_required"
    reason: str = (
        "3RUT-MBe1 remains available for shape studies only until source-equation "
        "and benchmark-profile reconciliation passes."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "absoluteRiskEnabled": self.absolute_risk_enabled,
            "status": self.status,
            "reason": self.reason,
        }


def clamp(value: float, lo: float, hi: float) -> float:
    return min(max(float(value), lo), hi)


def stable_sigmoid(x: float) -> float:
    if not math.isfinite(x):
        return 1.0 if x > 0 else 0.0
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def psia_to_kpa(psia: float) -> float:
    return float(psia) * 6.894757


def psia_to_mmhg(psia: float) -> float:
    return float(psia) * 51.7149


def inspired_gas_psia(total_pressure_psia: float, fraction: float) -> float:
    return max(float(total_pressure_psia) - WATER_VAPOR_PSIA, 0.0) * clamp(fraction, 0.0, 1.0)


def tissue_toward(initial_psia: float, target_psia: float, duration_min: float) -> float:
    if duration_min <= 0:
        return float(initial_psia)
    return float(target_psia) + (float(initial_psia) - float(target_psia)) * math.exp(
        -float(duration_min) / TISSUE_TAU_MIN
    )


def exercise_adjusted_k(vo2_ml_kg_min: float) -> float:
    lambda_ex = 0.03
    return (1.0 - math.exp(-lambda_ex * max(float(vo2_ml_kg_min), 0.0))) / 51.937 + LN2 / TISSUE_HALF_TIME_MIN


def tissue_toward_with_exercise(
    initial_psia: float,
    target_psia: float,
    duration_min: float,
    vo2_ml_kg_min: float,
) -> float:
    if duration_min <= 0:
        return float(initial_psia)
    k = exercise_adjusted_k(vo2_ml_kg_min)
    return float(target_psia) + (float(initial_psia) - float(target_psia)) * math.exp(
        -k * float(duration_min)
    )


def conkin_research_pdcs(etr: float, age_years: float) -> float:
    return stable_sigmoid(-31.71 + 14.55 * float(etr) + 0.053 * float(age_years)) * 100.0


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
            "modify_integrated_risk_percent_hours_min": 30.0,
            "monitor_lxc_score_min": 5,
            "monitor_risk_percent_min": 1.0,
            "monitor_integrated_risk_percent_hours_min": 5.0,
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
            "workload_blend": 0.65,
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
    return sorted(path.name.removesuffix(".yaml") for path in rules_package.iterdir() if path.name.endswith(".yaml"))


def interval_for_risk_percent(risk_percent: float, scenario: Mapping[str, Any], rules: MissionRules | None = None) -> dict[str, float]:
    p = clamp(float(risk_percent) / 100.0, 1e-6, 1.0 - 1e-6)
    logit = math.log(p / (1.0 - p))
    novel_profile = (
        scenario["kind"] == "scenario_c_habitat_pressure_decision"
        or scenario["habitat"]["pressurePsia"] < 11.0
        or bool(scenario["suit"]["variablePressure"])
    )
    workload_width = clamp((scenario["peakVo2MlKgMin"] - 20.0) / 30.0, 0.0, 1.0)
    uncertainty = (rules or {}).get("uncertainty", {})
    base_width = float(uncertainty.get("base_logit_half_width", 0.72))
    novel_width = float(uncertainty.get("novel_profile_logit_add", 0.32))
    workload_add = float(uncertainty.get("workload_logit_add", 0.22))
    half_width = base_width + (novel_width if novel_profile else 0.0) + workload_width * workload_add
    return {
        "low": stable_sigmoid(logit - half_width) * 100.0,
        "high": stable_sigmoid(logit + half_width) * 100.0,
    }


def likelihood_from_probability(percent: float, rules: MissionRules) -> int:
    thresholds = rules["lxc_probability_thresholds_percent"]
    if percent < thresholds["level_2_min"]:
        return 1
    if percent < thresholds["level_3_min"]:
        return 2
    if percent < thresholds["level_4_min"]:
        return 3
    if percent < thresholds["level_5_min"]:
        return 4
    return 5


def posture(score: int, rules: MissionRules) -> str:
    max_scores = rules["posture_score_max"]
    if score <= max_scores["green"]:
        return "green"
    if score <= max_scores["yellow"]:
        return "yellow"
    if score <= max_scores["orange"]:
        return "orange"
    return "red"


def hazard(
    hazard_id: str,
    name: str,
    probability_percent: float,
    consequence: int,
    driver: str,
    rules: MissionRules,
) -> dict[str, Any]:
    likelihood = likelihood_from_probability(probability_percent, rules)
    score = likelihood * int(consequence)
    return {
        "id": hazard_id,
        "name": name,
        "probabilityPercent": clamp(probability_percent, 0.0, 100.0),
        "likelihood": likelihood,
        "consequence": int(clamp(consequence, 1, 5)),
        "score": score,
        "posture": posture(score, rules),
        "driver": driver,
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

    if suit_pressure < envelope["suit_pressure_psia_min"] or suit_pressure > envelope["suit_pressure_psia_max"]:
        warnings.append(
            f"Suit pressure is outside the {envelope['suit_pressure_psia_min']:.1f}-"
            f"{envelope['suit_pressure_psia_max']:.1f} psia exploration comparison range."
        )
    if habitat_pressure < envelope["habitat_pressure_psia_min"] or habitat_pressure > envelope["habitat_pressure_psia_max"]:
        warnings.append(
            f"Habitat pressure is outside the {envelope['habitat_pressure_psia_min']:.1f}-"
            f"{envelope['habitat_pressure_psia_max']:.1f} psia planning range."
        )
    if habitat_o2 < envelope["habitat_oxygen_fraction_min"] or habitat_o2 > envelope["habitat_oxygen_fraction_max"]:
        warnings.append("Habitat oxygen fraction is outside the configured planning range.")
    if prebreathe_o2 < envelope["prebreathe_oxygen_fraction_min"] or prebreathe_o2 > envelope["prebreathe_oxygen_fraction_max"]:
        warnings.append("Prebreathe oxygen fraction is outside the configured planning range.")
    if prebreathe_min < envelope["prebreathe_min_min"] or prebreathe_min > envelope["prebreathe_min_max"]:
        warnings.append("Prebreathe duration is outside the configured planning range.")
    if eva_duration < envelope["eva_duration_min_min"] or eva_duration > envelope["eva_duration_min_max"]:
        warnings.append("EVA duration is outside the configured planning range.")
    if (
        prebreathe_min < envelope["short_prebreathe_high_pressure_min"]
        and habitat_pressure > envelope["short_prebreathe_high_pressure_psia"]
    ):
        warnings.append("Short prebreathe from a high-pressure habitat is an unsupported extrapolation.")
    return warnings


def build_timeline(
    scenario: Mapping[str, Any],
    tissue_n2_start_psia: float,
    tissue_n2_after_prebreathe_psia: float,
    p_dcs_percent: float,
    rules: MissionRules,
) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    habitat_n2_psia = inspired_gas_psia(scenario["habitat"]["pressurePsia"], 1.0 - scenario["habitat"]["oxygenFraction"])
    prebreathe_n2_psia = inspired_gas_psia(scenario["habitat"]["pressurePsia"], 1.0 - scenario["prebreatheOxygenFraction"])
    suit_n2_psia = inspired_gas_psia(scenario["suit"]["pressurePsia"], 1.0 - scenario["suit"]["oxygenFraction"])
    duration = max(float(scenario["evaDurationMin"]), 1.0)
    step = max(5, round(duration / 48.0))

    timeline.append(
        {
            "timeMin": -float(scenario["prebreatheMin"]),
            "phase": "habitat",
            "ambientPressurePsia": scenario["habitat"]["pressurePsia"],
            "inspiredN2Psia": habitat_n2_psia,
            "tissueN2Psia": tissue_n2_start_psia,
            "vo2MlKgMin": 3.5,
            "cumulativePDcsPercent": 0.0,
            "intervalLowPercent": 0.0,
            "intervalHighPercent": 0.0,
        }
    )
    timeline.append(
        {
            "timeMin": 0.0,
            "phase": "prebreathe",
            "ambientPressurePsia": scenario["habitat"]["pressurePsia"],
            "inspiredN2Psia": prebreathe_n2_psia,
            "tissueN2Psia": tissue_n2_after_prebreathe_psia,
            "vo2MlKgMin": scenario["meanVo2MlKgMin"],
            "cumulativePDcsPercent": 0.0,
            "intervalLowPercent": 0.0,
            "intervalHighPercent": 0.0,
        }
    )

    t = float(step)
    while t <= duration + 1e-9:
        frac = clamp(t / duration, 0.0, 1.0)
        workload_pulse = scenario["meanVo2MlKgMin"] + math.sin(frac * math.pi * 2.0) * max(
            0.0, scenario["peakVo2MlKgMin"] - scenario["meanVo2MlKgMin"]
        ) * 0.35
        tissue_n2 = tissue_toward_with_exercise(
            tissue_n2_after_prebreathe_psia,
            suit_n2_psia,
            t,
            workload_pulse,
        )
        cumulative = p_dcs_percent * (frac**1.22)
        interval = interval_for_risk_percent(cumulative, scenario, rules)
        timeline.append(
            {
                "timeMin": t,
                "phase": "eva",
                "ambientPressurePsia": scenario["suit"]["pressurePsia"],
                "inspiredN2Psia": suit_n2_psia,
                "tissueN2Psia": tissue_n2,
                "vo2MlKgMin": workload_pulse,
                "cumulativePDcsPercent": cumulative,
                "intervalLowPercent": interval["low"],
                "intervalHighPercent": interval["high"],
            }
        )
        t += float(step)

    if timeline[-1]["timeMin"] < duration:
        frac = 1.0
        cumulative = p_dcs_percent
        interval = interval_for_risk_percent(cumulative, scenario, rules)
        timeline.append(
            {
                "timeMin": duration,
                "phase": "eva",
                "ambientPressurePsia": scenario["suit"]["pressurePsia"],
                "inspiredN2Psia": suit_n2_psia,
                "tissueN2Psia": tissue_toward_with_exercise(
                    tissue_n2_after_prebreathe_psia,
                    suit_n2_psia,
                    duration,
                    scenario["meanVo2MlKgMin"],
                ),
                "vo2MlKgMin": scenario["meanVo2MlKgMin"],
                "cumulativePDcsPercent": cumulative,
                "intervalLowPercent": interval["low"],
                "intervalHighPercent": interval["high"],
            }
        )
    return timeline


def integrate_risk_percent_hours(timeline: list[Mapping[str, Any]]) -> float:
    eva_points = [point for point in timeline if point["timeMin"] >= 0]
    area_percent_min = 0.0
    for a, b in zip(eva_points, eva_points[1:]):
        dt = max(0.0, b["timeMin"] - a["timeMin"])
        area_percent_min += ((a["cumulativePDcsPercent"] + b["cumulativePDcsPercent"]) / 2.0) * dt
    return area_percent_min / 60.0


def max_risk(timeline: list[Mapping[str, Any]]) -> dict[str, float]:
    best = {"percent": 0.0, "timeMin": 0.0}
    for point in timeline:
        if point["cumulativePDcsPercent"] > best["percent"]:
            best = {"percent": point["cumulativePDcsPercent"], "timeMin": point["timeMin"]}
    return best


def choose_decision(
    *,
    abstain: bool,
    lxc_score: int,
    max_risk_percent: float,
    integrated_risk_percent_hours: float,
    consumables_margin_min: float,
    radiation_weather: str,
    symptom_flag: bool,
    rules: MissionRules,
) -> dict[str, str]:
    thresholds = rules["decision_thresholds"]
    if abstain:
        return {
            "decision": "abstain",
            "rationale": "Model inputs are outside the supported planning envelope.",
        }
    if radiation_weather == "storm" or consumables_margin_min < 0 or symptom_flag:
        return {
            "decision": "abort",
            "rationale": "A hard operational stop is present: radiation storm, negative consumables margin, or active symptoms.",
        }
    if lxc_score >= thresholds["delay_lxc_score_min"] or max_risk_percent >= thresholds["delay_risk_percent_min"]:
        return {
            "decision": "delay",
            "rationale": "LxC is red or DCS point risk exceeds the high-risk planning threshold.",
        }
    if (
        lxc_score >= thresholds["modify_lxc_score_min"]
        or max_risk_percent >= thresholds["modify_risk_percent_min"]
        or integrated_risk_percent_hours >= thresholds["modify_integrated_risk_percent_hours_min"]
    ):
        return {
            "decision": "modify",
            "rationale": "Risk is elevated; modify prebreathe, suit pressure, workload, or EVA duration.",
        }
    if (
        lxc_score >= thresholds["monitor_lxc_score_min"]
        or max_risk_percent >= thresholds["monitor_risk_percent_min"]
        or integrated_risk_percent_hours >= thresholds["monitor_integrated_risk_percent_hours_min"]
    ):
        return {
            "decision": "monitor",
            "rationale": "Risk remains manageable but requires telemetry and symptom surveillance.",
        }
    return {
        "decision": "proceed",
        "rationale": "Risk is low and inside the model envelope with positive operational margins.",
    }


def build_hazards(
    scenario: Mapping[str, Any],
    p_dcs_percent: float,
    etr: float,
    suit_inspired_o2_mmhg: float,
    habitat_inspired_o2_mmhg: float,
    consumables_margin_min: float,
    rules: MissionRules,
) -> list[dict[str, Any]]:
    duration_factor = clamp(scenario["evaDurationMin"] / 480.0, 0.0, 1.5)
    workload_factor = clamp((scenario["peakVo2MlKgMin"] - 15.0) / 25.0, 0.0, 1.5)
    low_o2_factor = clamp((120.0 - min(suit_inspired_o2_mmhg, habitat_inspired_o2_mmhg)) / 60.0, 0.0, 2.0)
    co2_probability = clamp((1.0 - scenario["suit"]["co2ScrubberMargin"]) * 34.0 + workload_factor * 18.0 + duration_factor * 8.0, 0.0, 80.0)
    thermal_probability = clamp(
        (1.0 - scenario["suit"]["coolingMargin"]) * 32.0 + scenario["environment"]["sunExposure"] * 17.0 + workload_factor * 20.0,
        0.0,
        85.0,
    )
    dust_probability = clamp(
        scenario["environment"]["dustLevel"] * 42.0 + (-10.0 if scenario["suit"]["suitPort"] else 10.0) + duration_factor * 8.0,
        0.0,
        90.0,
    )
    fatigue_probability = clamp(
        duration_factor * 24.0
        + workload_factor * 26.0
        + (10.0 if scenario["suit"]["pressurePsia"] > 5.5 else 0.0)
        + (12.0 if scenario["crew"]["hydration"] < 0.65 else 0.0),
        0.0,
        90.0,
    )
    radiation_base = 0.8 if scenario["environment"]["radiationWeather"] == "quiet" else 8.0
    if scenario["environment"]["radiationWeather"] == "storm":
        radiation_base = 45.0
    radiation_probability = clamp(
        radiation_base + duration_factor * 3.0 + max(0.0, scenario["environment"]["shelterReturnMin"] - 20.0) * 0.7,
        0.0,
        95.0,
    )
    consumables_probability = clamp(
        55.0 + abs(consumables_margin_min) * 0.5
        if consumables_margin_min < 0
        else max(0.0, 12.0 - consumables_margin_min) * 2.0,
        0.0,
        95.0,
    )
    hazard_rules = rules["hazards"]
    dcs_consequence = int(
        clamp(
            hazard_rules["dcs_base_consequence"]
            + (1 if etr > hazard_rules["dcs_etr_consequence_trigger"] else 0)
            + (1 if scenario["environment"]["shelterReturnMin"] > hazard_rules["dcs_shelter_return_consequence_trigger_min"] else 0),
            1,
            5,
        )
    )
    return [
        hazard("dcs", "DCS", p_dcs_percent, dcs_consequence, f"ETR {etr:.2f} with {scenario['prebreatheMin']} min prebreathe", rules),
        hazard("hypoxia", "Hypoxia", low_o2_factor * 18.0, 4, f"{round(min(suit_inspired_o2_mmhg, habitat_inspired_o2_mmhg))} mmHg lowest inspired O2", rules),
        hazard("co2", "CO2 retention", co2_probability, 4, f"{round(scenario['suit']['co2ScrubberMargin'] * 100)}% scrubber margin", rules),
        hazard("thermal", "Thermal strain", thermal_probability, 3, f"{round(scenario['suit']['coolingMargin'] * 100)}% cooling margin", rules),
        hazard("dust", "Dust contamination", dust_probability, 3, f"{round(scenario['environment']['dustLevel'] * 100)}% dust load", rules),
        hazard("fatigue", "Fatigue / injury", fatigue_probability, 3, f"{scenario['peakVo2MlKgMin']:.0f} mL/kg/min peak VO2", rules),
        hazard("radiation", "Radiation event", radiation_probability, 5, scenario["environment"]["radiationWeather"], rules),
        hazard("consumables", "Consumables margin", consumables_probability, 4, f"{round(consumables_margin_min)} min remaining", rules),
    ]


def simulate_eva(
    scenario: Mapping[str, Any],
    *,
    mission_rules: MissionRules | None = None,
    telemetry: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Simulate an EVA scenario and return the frontend/API contract result."""

    rules = mission_rules or load_mission_rules("default")
    working_scenario: Scenario = copy.deepcopy(dict(scenario))
    telemetry_adjustment = TelemetryAdjustment.empty()
    if telemetry:
        telemetry_adjustment = apply_telemetry_adjustment(working_scenario, telemetry, rules)

    sea_level_n2_psia = inspired_gas_psia(SEA_LEVEL_PSIA, N2_AIR_FRACTION)
    habitat_n2_psia = inspired_gas_psia(
        working_scenario["habitat"]["pressurePsia"],
        1.0 - working_scenario["habitat"]["oxygenFraction"],
    )
    tissue_n2_start_psia = tissue_toward(
        sea_level_n2_psia,
        habitat_n2_psia,
        working_scenario["habitat"]["equilibrationHours"] * 60.0,
    )
    prebreathe_n2_psia = inspired_gas_psia(
        working_scenario["habitat"]["pressurePsia"],
        1.0 - working_scenario["prebreatheOxygenFraction"],
    )
    tissue_n2_after_prebreathe_psia = tissue_toward_with_exercise(
        tissue_n2_start_psia,
        prebreathe_n2_psia,
        working_scenario["prebreatheMin"],
        working_scenario["meanVo2MlKgMin"],
    )
    p1n2_psia = tissue_n2_after_prebreathe_psia
    etr = p1n2_psia / max(working_scenario["suit"]["pressurePsia"], 0.1)
    raw_pdcs = conkin_research_pdcs(etr, working_scenario["crew"]["ageYears"])
    workload_penalty = max(0.0, working_scenario["peakVo2MlKgMin"] - 30.0) * 0.35
    hydration_penalty = 2.5 if working_scenario["crew"]["hydration"] < 0.65 else 0.0
    symptom_penalty = 6.0 if working_scenario["crew"]["symptomFlag"] else 0.0
    p_dcs_percent = clamp(raw_pdcs + workload_penalty + hydration_penalty + symptom_penalty, 0.0, 100.0)
    interval = interval_for_risk_percent(p_dcs_percent, working_scenario, rules)
    suit_inspired_o2_mmhg = psia_to_mmhg(
        inspired_gas_psia(working_scenario["suit"]["pressurePsia"], working_scenario["suit"]["oxygenFraction"])
    )
    habitat_inspired_o2_mmhg = psia_to_mmhg(
        inspired_gas_psia(
            working_scenario["habitat"]["pressurePsia"],
            working_scenario["habitat"]["oxygenFraction"],
        )
    )
    consumables_margin_min = (
        working_scenario["suit"]["plssDurationMin"]
        + working_scenario["suit"]["oxygenReserveMin"]
        - working_scenario["evaDurationMin"]
    )
    envelope_warnings = scenario_envelope_warnings(working_scenario, rules)
    in_envelope = len(envelope_warnings) == 0
    abstain = not in_envelope

    timeline = build_timeline(
        working_scenario,
        tissue_n2_start_psia,
        tissue_n2_after_prebreathe_psia,
        p_dcs_percent,
        rules,
    )
    hazards = build_hazards(
        working_scenario,
        p_dcs_percent,
        etr,
        suit_inspired_o2_mmhg,
        habitat_inspired_o2_mmhg,
        consumables_margin_min,
        rules,
    )
    dcs_hazard = next((item for item in hazards if item["id"] == "dcs"), hazards[0])
    max_point = max_risk(timeline)
    integrated_risk = integrate_risk_percent_hours(timeline)
    decision = choose_decision(
        abstain=abstain,
        lxc_score=dcs_hazard["score"],
        max_risk_percent=max_point["percent"],
        integrated_risk_percent_hours=integrated_risk,
        consumables_margin_min=consumables_margin_min,
        radiation_weather=working_scenario["environment"]["radiationWeather"],
        symptom_flag=working_scenario["crew"]["symptomFlag"],
        rules=rules,
    )

    return {
        "pDcsPercent": p_dcs_percent,
        "intervalLowPercent": interval["low"],
        "intervalHighPercent": interval["high"],
        "p1n2Psia": p1n2_psia,
        "etr": etr,
        "tissueN2StartPsia": tissue_n2_start_psia,
        "tissueN2AfterPrebreathePsia": tissue_n2_after_prebreathe_psia,
        "suitInspiredO2MmHg": suit_inspired_o2_mmhg,
        "habitatInspiredO2MmHg": habitat_inspired_o2_mmhg,
        "consumablesMarginMin": consumables_margin_min,
        "inEnvelope": in_envelope,
        "abstain": abstain,
        "envelopeWarnings": envelope_warnings,
        "maxRiskPercent": max_point["percent"],
        "maxRiskTimeMin": max_point["timeMin"],
        "integratedRiskPercentHours": integrated_risk,
        "lxcLikelihood": dcs_hazard["likelihood"],
        "lxcConsequence": dcs_hazard["consequence"],
        "lxcScore": dcs_hazard["score"],
        "lxcCategory": dcs_hazard["posture"],
        "decision": decision["decision"],
        "decisionRationale": decision["rationale"],
        "timeline": timeline,
        "hazards": hazards,
        "telemetryStatus": telemetry_adjustment.to_dict(),
    }


def simulation_response(
    scenario: Mapping[str, Any],
    *,
    mission_rule_profile: str = "default",
    telemetry: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    rules = load_mission_rules(mission_rule_profile)
    result = simulate_eva(scenario, mission_rules=rules, telemetry=telemetry)
    status = RutReconciliationStatus()
    return {
        "scenarioId": scenario["id"],
        "missionRuleProfile": rules["profile_id"],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "modelMetadata": {
            "modelVersion": MODEL_VERSION,
            "absoluteRiskSource": "Conkin-style ETR planning logic",
            "researchUseOnly": True,
            "rutReconciliation": status.to_dict(),
        },
        "missionRules": rules,
        "result": result,
    }


def response_to_json(response: Mapping[str, Any]) -> str:
    return json.dumps(response, indent=2, sort_keys=True)
