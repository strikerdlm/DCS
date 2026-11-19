import pytest
from fastapi.testclient import TestClient

from mechanistic.atmosphere import PSIA_PER_ATM, pressure_atm_to_altitude_ft
from tinydcs.api import app
from tinydcs.aviation_models import evaluate
from tinydcs.chamber_outcomes import (
    OutcomeInputs,
    _profile,
    predict_outcomes,
    protocols,
)
from tinydcs.exposure import ExposureProfile

ROUTE = "/api/v3/hypobaric/outcomes"
PRESETS = {p["id"]: p["defaults"] for p in protocols()["protocols"]}


def published(result):
    return {
        o["id"]: o
        for o in result["outcomes"]
        if o["evidence_class"] == "published_reference"
    }


def test_full_history_and_http_agree_for_each_source_equation():
    raw = PRESETS["nasa_2020_simple_oxygen"]
    client = TestClient(app)
    assert client.get(ROUTE + "/models").json() == protocols()
    http = client.post(ROUTE + "/predict", json=raw)
    assert http.status_code == 200
    result = http.json()
    assert result == predict_outcomes(OutcomeInputs(**raw))
    assert result["clinical_individual_probability_available"] is False
    assert len(result["input_fingerprint"]) == 64
    for endpoint, row in published(result).items():
        request = dict(
            model_id="auto",
            endpoint=endpoint,
            window="during_plateau",
            source_protocol=raw["protocol_id"],
            horizon_minutes=240,
            reference_population="nasa_hypobaric_chamber",
            prediction_origin="plateau_arrival",
        )
        full = evaluate(
            ExposureProfile.model_validate(
                _profile(OutcomeInputs(**raw)) | {"prediction_request": request}
            )
        )
        assert full["probability_fraction"] == row["probability_fraction"]
        assert (
            full["artifact_hash"] == row["model_digest"]
            and row["applicability"]["status"] == "supported"
        )


def test_nasa_appendix_a_rest_worked_bubble_results_and_pressure_specific_dcs():
    # NASA 2020 Appendix A p.28 rounds Eq5/6 to 58.8% and 33.5%.
    result = predict_outcomes(PRESETS["nasa_2020_appendix_a_rest"])
    rows = published(result)
    assert result["physiology"]["arrival_tissue_ratio"] == pytest.approx(
        1.675, abs=0.002
    )
    assert rows["vge"]["probability_fraction"] == pytest.approx(0.588, abs=0.001)
    assert rows["grade_iv_vge"]["probability_fraction"] == pytest.approx(
        0.335, abs=0.001
    )
    assert rows["symptomatic_dcs"]["model_id"] == "conkin_1996_eq7"
    assert rows["symptomatic_dcs"]["probability_fraction"] == pytest.approx(0.19132994)
    table = published(predict_outcomes(PRESETS["nasa_2020_table5"]))
    assert table["symptomatic_dcs"]["probability_fraction"] == pytest.approx(
        0.0310109751
    )
    assert table["vge"]["probability_fraction"] is None


def test_source_inputs_are_endpoint_specific_and_time_is_in_hours():
    raw = PRESETS["nasa_2020_simple_oxygen"]
    a = published(predict_outcomes(raw))
    short = published(predict_outcomes(raw | {"time_at_altitude_min": 120}))
    older = published(predict_outcomes(raw | {"age_years": 48}))
    missing_bmi = published(predict_outcomes(raw | {"bmi_kg_m2": None}))
    missing_sex = published(predict_outcomes(raw | {"source_sex": None}))
    for k in a:
        assert 0 < short[k]["probability_fraction"] < a[k]["probability_fraction"] < 1
    assert (
        older["symptomatic_dcs"]["probability_fraction"]
        == a["symptomatic_dcs"]["probability_fraction"]
    )
    assert missing_bmi["symptomatic_dcs"]["probability_fraction"] is None
    for k in ("vge", "grade_iv_vge"):
        assert older[k]["probability_fraction"] > a[k]["probability_fraction"]
        assert missing_bmi[k]["probability_fraction"] == a[k]["probability_fraction"]
        assert missing_sex[k]["probability_fraction"] is None


@pytest.mark.parametrize(
    "changes",
    [
        {"time_at_altitude_min": 10},
        {"oxygen_interrupted": True},
        {"starting_pressure_psia": 10.8},
        {"ascent_min": 45},
    ],
)
def test_outside_reference_exposure_withholds_all_source_estimates(changes):
    result = predict_outcomes(PRESETS["nasa_2020_simple_oxygen"] | changes)
    assert all(
        row["probability_fraction"] is None and row["applicability"]["reasons"]
        for row in result["outcomes"]
    )
    if changes.get("oxygen_interrupted"):
        assert result["physiology"]["arrival_tissue_n2_psia"] is None


def test_pressure_altitude_parity_and_invalid_inputs():
    raw = PRESETS["nasa_2020_simple_oxygen"]
    altitude = float(pressure_atm_to_altitude_ft(4.3 / PSIA_PER_ATM))
    result = predict_outcomes(
        {**raw, "plateau_pressure_psia": None, "altitude_ft": altitude}
    )
    original = predict_outcomes(raw)
    assert result["physiology"]["plateau_pressure_psia"] == pytest.approx(4.3)
    for key, row in published(original).items():
        assert published(result)[key]["probability_fraction"] == pytest.approx(
            row["probability_fraction"], abs=1e-11
        )
    assert result["input_fingerprint"] != original["input_fingerprint"]
    client = TestClient(app)
    for wrong in (
        {"altitude_ft": altitude},
        {"plateau_pressure_psia": None},
        {"plateau_pressure_psia": 16},
        {"source_sex": "unknown"},
        {"activity": "Heavy"},
    ):
        assert client.post(ROUTE + "/predict", json=raw | wrong).status_code == 422


def test_observed_studies_attach_to_different_cohorts_and_windows():
    raw = PRESETS["nasa_2020_simple_oxygen"] | {"prebreathing_min": 229}
    result = predict_outcomes(raw)
    rows = {r["id"]: r for r in result["outcomes"]}
    group, study = rows["nasa-chamber-dcs-v1"], rows["grade-iv-vge-v1"]
    assert group["probability_fraction"] == pytest.approx(0.2265677831794107)
    assert group["matched_test_ids"] == ["2a"] and (
        group["observed_cases"],
        group["dcs_denominator"],
    ) == (7, 23)
    assert (
        group["evidence_class"] == "protocol_group_benchmark"
        and "after the test" in group["window"]
    )
    assert study["probability_fraction"] == pytest.approx(0.399876022456535)
    assert study["evidence_class"] == "interval_censored_benchmark"
    assert result["clinical_individual_probability_available"] is False
    for r in (group, study):
        assert (
            len(r["model_digest"]) == 64 and r["uncertainty"]["status"] == "unavailable"
        )
    outside = predict_outcomes(raw | {"prebreathing_min": 225})
    group, study = outside["outcomes"][-2:]
    assert group["probability_fraction"] is None and group["observed_cases"] is None
    assert (
        "OUTSIDE_OBSERVED_PROTOCOL_GROUP_SETTINGS" in group["applicability"]["reasons"]
    )
    assert study["probability_fraction"] is not None


def test_simple_oxygen_reference_requires_declared_gas_delivery():
    raw = PRESETS["nasa_2020_simple_oxygen"]
    profile = _profile(OutcomeInputs(**raw))
    profile["segments"][1]["gas"] = dict(
        profile["segments"][1]["gas"], delivery_method=None
    )
    req = dict(
        model_id="nasa_2020_eq5",
        endpoint="vge",
        window="during_plateau",
        source_protocol=raw["protocol_id"],
        horizon_minutes=240,
        reference_population="nasa_hypobaric_chamber",
        prediction_origin="plateau_arrival",
    )
    result = evaluate(
        ExposureProfile.model_validate(profile | {"prediction_request": req})
    )
    assert (
        result["probability_fraction"] is None
        and "SOURCE_GAS_DELIVERY_MISMATCH" in result["applicability"]["reasons"]
    )
