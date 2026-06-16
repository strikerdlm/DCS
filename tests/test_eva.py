"""Tests for EVA scenario calculations, mission rules, telemetry, reports, and API contract."""

from __future__ import annotations

import base64
import json

import pytest

from tinydcs.api import (
    EVAReportRequest,
    EVASimulationRequest,
    get_model_metadata,
    report_eva_endpoint,
    simulate_eva_endpoint,
)
from tinydcs.eva import (
    choose_decision,
    interval_for_risk_percent,
    likelihood_from_probability,
    load_mission_rules,
    simulation_response,
    simulate_eva,
)
from tinydcs.eva_reports import report_artifacts
from tinydcs.rut_reconciliation import (
    BENCHMARK_PROFILES,
    SOURCE_EQUATION_CHECKLIST,
    assert_rut_absolute_risk_enabled,
)


def eva_scenario() -> dict:
    return {
        "id": "scenario-b-artemis-lunar-day",
        "kind": "scenario_b_artemis_lunar_day",
        "name": "Scenario B: Artemis-relevant lunar EVA day",
        "shortName": "B · Lunar EVA Day",
        "summary": "Lunar EVA surface activity day.",
        "habitat": {"pressurePsia": 8.2, "oxygenFraction": 0.34, "equilibrationHours": 36},
        "prebreatheProtocol": "exploration_atmosphere",
        "prebreatheMin": 30,
        "prebreatheOxygenFraction": 0.95,
        "suit": {
            "pressurePsia": 5.8,
            "oxygenFraction": 1,
            "variablePressure": True,
            "plssDurationMin": 480,
            "oxygenReserveMin": 35,
            "co2ScrubberMargin": 0.82,
            "coolingMargin": 0.78,
            "suitPort": False,
        },
        "evaDurationMin": 360,
        "meanVo2MlKgMin": 19,
        "peakVo2MlKgMin": 34,
        "workload": [
            {"name": "Pre-egress checks", "durationMin": 25, "vo2MlKgMin": 10},
            {"name": "Traverse", "durationMin": 120, "vo2MlKgMin": 24},
            {"name": "Sampling", "durationMin": 120, "vo2MlKgMin": 30},
            {"name": "Return", "durationMin": 95, "vo2MlKgMin": 20},
        ],
        "environment": {
            "dustLevel": 0.72,
            "sunExposure": 0.68,
            "commDelaySec": 3,
            "radiationWeather": "elevated",
            "shelterReturnMin": 22,
        },
        "crew": {
            "ageYears": 40,
            "sex": "Male",
            "massKg": 78,
            "spo2Percent": 97,
            "hydration": 0.75,
            "symptomFlag": False,
        },
        "evidence": ["test fixture"],
    }


def test_eva_simulation_contract_and_intervals() -> None:
    scenario = eva_scenario()
    result = simulate_eva(scenario, mission_rules=load_mission_rules("artemis_lunar"))
    assert result["pDcsPercent"] >= 0
    assert result["intervalLowPercent"] <= result["pDcsPercent"] <= result["intervalHighPercent"]
    assert result["maxRiskPercent"] == pytest.approx(result["pDcsPercent"], rel=1e-6)
    assert result["maxRiskTimeMin"] == pytest.approx(scenario["evaDurationMin"], abs=8)
    assert result["integratedRiskPercentHours"] > 0
    assert result["lxcLikelihood"] in {1, 2, 3, 4, 5}
    assert result["lxcCategory"] in {"green", "yellow", "orange", "red"}
    assert result["decision"] in {"proceed", "monitor", "modify", "delay", "abort", "abstain"}
    assert len(result["timeline"]) >= 10


def test_interval_width_expands_for_novel_profiles() -> None:
    rules = load_mission_rules("default")
    baseline = eva_scenario()
    baseline["kind"] = "scenario_a_commercial_standup"
    baseline["habitat"]["pressurePsia"] = 14.7
    baseline["suit"]["variablePressure"] = False
    novel = eva_scenario()
    base_interval = interval_for_risk_percent(5.0, baseline, rules)
    novel_interval = interval_for_risk_percent(5.0, novel, rules)
    assert novel_interval["high"] - novel_interval["low"] > base_interval["high"] - base_interval["low"]


def test_lxc_threshold_mapping() -> None:
    rules = load_mission_rules("default")
    assert likelihood_from_probability(0.99, rules) == 1
    assert likelihood_from_probability(1.0, rules) == 2
    assert likelihood_from_probability(5.0, rules) == 3
    assert likelihood_from_probability(15.0, rules) == 4
    assert likelihood_from_probability(35.0, rules) == 5


def test_decision_implication_rules() -> None:
    rules = load_mission_rules("default")
    assert choose_decision(
        abstain=True,
        lxc_score=1,
        max_risk_percent=0,
        integrated_risk_percent_hours=0,
        consumables_margin_min=10,
        radiation_weather="quiet",
        symptom_flag=False,
        rules=rules,
    )["decision"] == "abstain"
    assert choose_decision(
        abstain=False,
        lxc_score=4,
        max_risk_percent=0.5,
        integrated_risk_percent_hours=0.2,
        consumables_margin_min=10,
        radiation_weather="storm",
        symptom_flag=False,
        rules=rules,
    )["decision"] == "abort"
    assert choose_decision(
        abstain=False,
        lxc_score=16,
        max_risk_percent=3,
        integrated_risk_percent_hours=1,
        consumables_margin_min=10,
        radiation_weather="quiet",
        symptom_flag=False,
        rules=rules,
    )["decision"] == "delay"
    assert choose_decision(
        abstain=False,
        lxc_score=10,
        max_risk_percent=3,
        integrated_risk_percent_hours=1,
        consumables_margin_min=10,
        radiation_weather="quiet",
        symptom_flag=False,
        rules=rules,
    )["decision"] == "modify"
    assert choose_decision(
        abstain=False,
        lxc_score=5,
        max_risk_percent=0.2,
        integrated_risk_percent_hours=0.1,
        consumables_margin_min=10,
        radiation_weather="quiet",
        symptom_flag=False,
        rules=rules,
    )["decision"] == "monitor"


def test_telemetry_adapters_update_scenario_inputs() -> None:
    scenario = eva_scenario()
    result = simulate_eva(
        scenario,
        mission_rules=load_mission_rules("default"),
        telemetry=[
            {"kind": "pressure", "value": 40.0, "unit": "kpa", "source": "bench"},
            {"kind": "workload", "value": 38.0, "unit": "vo2_ml_kg_min", "source": "bench"},
            {"kind": "spo2", "value": 94, "unit": "%", "source": "bench"},
            {"kind": "skin_temperature", "value": 100.4, "unit": "f", "source": "bench"},
            {"kind": "hrv", "value": 41, "unit": "rmssd_ms", "source": "bench"},
            {"kind": "heart_rate", "value": 132, "unit": "bpm", "source": "bench"},
            {"kind": "pressure", "value": 1, "unit": "unknown", "source": "bad"},
        ],
    )
    status = result["telemetryStatus"]
    assert status["accepted"] == 6
    assert status["rejected"] == 1
    assert status["suitPressurePsia"] == pytest.approx(40.0 / 6.894757)
    assert status["spo2Percent"] == 94
    assert status["heartRateBpm"] == 132
    assert status["hrvRmssdMs"] == 41
    assert status["skinTempC"] == pytest.approx(38.0)


def test_report_artifacts_are_exportable() -> None:
    response = simulation_response(eva_scenario(), mission_rule_profile="default")
    report = report_artifacts(response)
    assert set(report["artifacts"]) == {"json", "html", "pdf"}
    assert "EVA DCS Planning Report" in report["artifacts"]["html"]["content"]
    assert json.loads(report["artifacts"]["json"]["content"])["scenarioId"] == response["scenarioId"]
    pdf = base64.b64decode(report["artifacts"]["pdf"]["contentBase64"])
    assert pdf.startswith(b"%PDF")


def test_eva_api_contract() -> None:
    request = EVASimulationRequest(
        scenario=eva_scenario(),
        missionRuleProfile="default",
        telemetry=[{"kind": "spo2", "value": 96, "unit": "%"}],
    )
    body = simulate_eva_endpoint(request)
    assert body["scenarioId"] == request.scenario.id
    assert body["modelMetadata"]["rutReconciliation"]["absoluteRiskEnabled"] is False

    report = report_eva_endpoint(EVAReportRequest(scenario=eva_scenario(), missionRuleProfile="default"))
    assert "pdf" in report["artifacts"]

    metadata = get_model_metadata()
    assert "default" in metadata["missionRuleProfiles"]


def test_3rut_absolute_risk_guard_requires_reconciliation() -> None:
    assert len(BENCHMARK_PROFILES) == 5
    assert "final_probability_mapping" in SOURCE_EQUATION_CHECKLIST
    with pytest.raises(RuntimeError, match="absolute-risk use is disabled"):
        assert_rut_absolute_risk_enabled()
