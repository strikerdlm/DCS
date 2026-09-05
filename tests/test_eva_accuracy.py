import copy
import math
import json
import pytest
from fastapi.testclient import TestClient
from tinydcs.api import app
from tinydcs.eva import simulate_eva, load_mission_rules
from tinydcs.eva_telemetry import apply_telemetry_adjustment
from tests.test_eva import eva_scenario


def scenario():
    value = eva_scenario()
    value["suit"]["variablePressure"] = False
    return value


def test_unsupported_eva_probabilities_are_unavailable_not_zero():
    result = simulate_eva(scenario())
    for name in ["pDcsPercent", "intervalLowPercent", "intervalHighPercent", "integratedRiskPercentHours", "maxRiskPercent", "lxcScore"]:
        assert result[name] is None
    assert result["lxcCategory"] == "unavailable"
    assert result["modelApplicability"]["applicable"] is False
    assert all(row["cumulativePDcsPercent"] is None for row in result["timeline"])
    assert all(row["probabilityPercent"] is None for row in result["hazards"] if row["id"] != "dcs")
    pb_end = next(row for row in result["timeline"] if row["timeMin"] == 0)
    assert pb_end["tissueN2Psia"] == pytest.approx(result["p1n2Psia"], abs=1e-10)
    json.dumps(result, allow_nan=False)


def test_prebreathe_workload_is_separate_from_eva_workload():
    a, b = scenario(), scenario()
    a["prebreatheVo2MlKgMin"] = b["prebreatheVo2MlKgMin"] = 5
    b["meanVo2MlKgMin"], b["peakVo2MlKgMin"] = 30, 40
    for block in b["workload"]:
        block["vo2MlKgMin"] = 30
    assert simulate_eva(a)["p1n2Psia"] == pytest.approx(simulate_eva(b)["p1n2Psia"], abs=1e-12)


def test_timeline_has_exact_endpoint_and_sequential_compartment_updates():
    s = scenario()
    s["evaDurationMin"] = 83
    s["workload"] = [{"name": "first", "durationMin": 20, "vo2MlKgMin": 5},
                     {"name": "second", "durationMin": 63, "vo2MlKgMin": 25}]
    s["pressureSegments"] = [{"durationMin": 20, "pressurePsia": 5.8, "oxygenFraction": 1},
                             {"durationMin": 63, "pressurePsia": 4.3, "oxygenFraction": 1}]
    s["suit"]["variablePressure"] = True
    result = simulate_eva(s)
    final = result["timeline"][-1]
    expected = result["p1n2Psia"]*math.exp(-(20*math.exp(.025*5)+63*math.exp(.025*25))/519.37)
    assert final["timeMin"] == 83
    assert final["ambientPressurePsia"] == 4.3
    assert final["tissueN2Psia"] == pytest.approx(expected, abs=1e-10)


def test_operational_stop_is_not_hidden_by_abstention():
    s = scenario()
    s["crew"]["symptomFlag"] = True
    result = simulate_eva(s)
    assert result["abstain"] is True
    assert result["decision"] == "abort"
    assert "active_symptoms" in result["stopReasons"]


def test_reference_endpoint_is_not_a_time_dependent_risk_curve():
    s = scenario()
    s["evaDurationMin"] = 240
    s["suit"]["pressurePsia"] = 4.3
    s["nasaAdynamicReference"] = True
    s["workload"] = [{"name": "reference", "durationMin": 240, "vo2MlKgMin": 3.5}]
    result = simulate_eva(s)
    expected = 100/(1+math.exp(-(-31.71+14.55*result["etr"]+.053*s["crew"]["ageYears"])))
    assert result["pDcsPercent"] == pytest.approx(expected)
    assert result["intervalLowPercent"] is None
    assert result["modelApplicability"]["horizonMin"] == 240
    assert all(row["cumulativePDcsPercent"] is None for row in result["timeline"])


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -10])
def test_api_rejects_invalid_pressure(bad):
    s = scenario()
    s["suit"]["pressurePsia"] = bad
    with TestClient(app) as client:
        # Raw JSON deliberately tests nonstandard nonfinite tokens as well.
        response = client.post("/api/v1/eva/simulate", content=json.dumps({"scenario": s}), headers={"Content-Type":"application/json"})
    assert response.status_code == 422


def test_report_recomputes_instead_of_trusting_client_result():
    with TestClient(app) as client:
        response = client.post("/api/v1/eva/report", json={"scenario": scenario(), "result": {"pDcsPercent": 99.12345}})
    assert response.status_code == 200
    report = json.loads(response.json()["artifacts"]["json"]["content"])
    assert report["result"]["pDcsPercent"] is None


def test_telemetry_honors_phase_freshness_units_and_unvalidated_proxies():
    s = scenario()
    original = copy.deepcopy(s)
    samples = [
        {"kind":"habitat_pressure", "value":8.0, "unit":"psia", "timestampSec":990},
        {"kind":"suit_pressure", "value":4.3, "unit":"psia", "timestampSec":800},
        {"kind":"suit_pressure", "value":5, "unit":"psia", "timestampSec":995, "confidence":float("nan")},
        {"kind":"accelerometer", "x":0, "y":0, "z":2, "unit":"g", "timestampSec":990},
        {"kind":"skin_temperature", "value":38, "unit":"c", "timestampSec":990},
    ]
    adjustment = apply_telemetry_adjustment(s, samples, load_mission_rules(), now_sec=1000)
    assert s["habitat"]["pressurePsia"] == 8
    assert s["suit"]["pressurePsia"] == original["suit"]["pressurePsia"]
    assert s["suit"]["coolingMargin"] == original["suit"]["coolingMargin"]
    assert s["meanVo2MlKgMin"] == original["meanVo2MlKgMin"]
    assert adjustment.rejected == 2


@pytest.mark.parametrize("bad", [True, "4.3"])
def test_api_does_not_coerce_pressure_types(bad):
    s = scenario()
    s["suit"]["pressurePsia"] = bad
    with TestClient(app) as client:
        response = client.post("/api/v2/eva/simulate", json={"scenario": s})
    assert response.status_code == 422


def test_inspired_oxygen_indicator_uses_lowest_explicit_suit_segment():
    s = scenario()
    s["pressureSegments"] = [dict(durationMin=180,pressurePsia=5.8,oxygenFraction=1),
                             dict(durationMin=180,pressurePsia=4.3,oxygenFraction=.21)]
    s["suit"]["variablePressure"] = True
    from mechanistic.atmosphere import MMHG_PER_PSIA
    assert simulate_eva(s)["suitInspiredO2MmHg"] == pytest.approx((4.3*MMHG_PER_PSIA-47)*.21)


def test_tolerated_schedule_roundoff_cannot_create_uncovered_tail():
    s = scenario()
    s["workload"][-1]["durationMin"] -= 5e-7
    assert simulate_eva(s)["timeline"][-1]["timeMin"] == s["evaDurationMin"]
