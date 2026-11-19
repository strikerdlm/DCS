"""A source projection requires its own gas, posture, and endpoint history."""
from copy import deepcopy
from pathlib import Path

import pytest

from tests.test_aviation_models import gas, phase_i, segment, table5
from tinydcs.aviation_models import evaluate
from tinydcs.exposure import ExposureProfile


def test_v1_input_digest_is_stable_and_includes_the_new_information():
    fixture = Path(__file__).resolve().parents[1] / "docs/examples/aviation-table5.json"
    profile = ExposureProfile.model_validate_json(fixture.read_text())
    legacy = "632c5bb4c2bcb8420093273d52f02ec000b11723bb1d7ea0fa55f2b251b0ef2a"
    assert profile.fingerprint() == legacy
    document = profile.model_dump()
    document["prediction_request"]["post_test_course"] = "published_source_ascertainment"
    assert ExposureProfile.model_validate(document).fingerprint() != legacy
    document["prediction_request"]["post_test_course"] = None
    gas = document["initial_state"]["gas"]
    gas["carbon_dioxide_fraction"] = .0004
    gas["nitrogen_fraction"] -= .0004
    assert ExposureProfile.model_validate(document).fingerprint() != legacy


@pytest.mark.parametrize("idx", [0, 2, 7, 10])
@pytest.mark.parametrize("posture,unknown", [("standing", False), ("seated", False),
                                             ("unknown", True), (None, True)])
def test_phase_i_posture_in_warmup_recovery_mixed_gas_and_final_ascent(idx, posture, unknown):
    d = phase_i()
    s = d["segments"][idx]
    s["activity"]["posture"] = posture
    result = evaluate(d)
    assert result["probability_fraction"] is None
    reasons = result["applicability"]["reasons"]
    assert ("PREBREATHE_POSTURE_UNKNOWN" if unknown else "PREBREATHE_POSTURE_OUTSIDE_SOURCE") in reasons
    assert (f"segments.{s['id']}.activity.posture" in result["missing_decisive_inputs"]) == unknown
    assert result["physiology"]["arrival_nitrogen_pa"] is not None


def test_preconditioning_plateau_and_preparation_have_distinct_posture_rules():
    for where, wrong, reason in [
        ("conditioning","semi_recumbent","PRETEST_ADYNAMIA_NOT_MATCHED"),
        ("plateau","standing","ALTITUDE_ACTIVITY_OUTSIDE_SOURCE"),
        ("prebreathe","recumbent","PREBREATHE_POSTURE_OUTSIDE_SOURCE"),
    ]:
        d = phase_i()
        s = d["history"]["segments"][0] if where == "conditioning" else d["segments"][
            -1 if where == "plateau" else 0]
        s["activity"]["posture"] = wrong
        r = evaluate(d)
        assert r["probability_fraction"] is None and reason in r["applicability"]["reasons"]


@pytest.mark.parametrize("mixture", [
    gas(.21),
    {"basis":"dry","oxygen_fraction":.21,"nitrogen_fraction":.78,"argon_fraction":.01},
    {"basis":"dry","oxygen_fraction":.20947,"nitrogen_fraction":.78084,"argon_fraction":.00934,
     "carbon_dioxide_fraction":.00033,"other_inert_fraction":.00002},
])
def test_source_normal_air_as_explicit_components_or_legacy_equivalent(mixture):
    ordinary = table5()
    expected = evaluate(ordinary)["probability_fraction"]
    ordinary["initial_state"]["gas"] = mixture
    r = evaluate(ordinary)
    assert r["quantitative_output_enabled"] and r["probability_fraction"] == expected
    assert r["missing_decisive_inputs"] == []


@pytest.mark.parametrize("model", ["nasa_2004_nm","nasa_2004_rm","nasa_2020_eq4","conkin_1996_eq7"])
def test_exotic_argon_does_not_become_source_nitrogen(model):
    d = phase_i(model) if "2004" in model else table5(4.3 if "2020" in model else 6.5)
    abnormal = {"basis":"dry","oxygen_fraction":.21,"nitrogen_fraction":0.,"argon_fraction":.79}
    d["initial_state"]["gas"] = abnormal
    r = evaluate(d)
    assert not r["quantitative_output_enabled"] and r["probability_fraction"] is None
    assert "INITIAL_GAS_OUTSIDE_SOURCE" in r["applicability"]["reasons"]
    assert "initial_state.gas" not in r["missing_decisive_inputs"]
    assert r["physiology"]["kinetics"] == "fixed_360" and r["physiology"]["initial_nitrogen_pa"] == 0


def test_bottled_stage_with_argon_instead_of_nitrogen_is_not_the_fitted_gas():
    d = phase_i()
    d["segments"][7]["end_gas"] = {"basis":"dry","oxygen_fraction":.265,"nitrogen_fraction":.70,
                                   "argon_fraction":.035}
    r = evaluate(d)
    assert r["probability_fraction"] is None
    assert "SOURCE_INPUT_INCOMPATIBLE" in r["inherited_vetoes"]
    assert r["missing_decisive_inputs"] == []


def test_nm_historical_ascertainment_requires_explicit_reference_without_a_return():
    d = phase_i("nasa_2004_nm")
    r = evaluate(d)
    assert r["quantitative_output_enabled"] and r["missing_decisive_inputs"] == []
    assert r["source_features"]["post_test_course"] == "published_source_ascertainment"
    assert any("Table 6" in item for item in r["assumptions"])
    d["prediction_request"].pop("post_test_course")
    r = evaluate(d)
    assert r["probability_fraction"] is None and "POST_TEST_COURSE_UNSPECIFIED" in r["inherited_vetoes"]
    assert "prediction_request.post_test_course" in r["missing_decisive_inputs"]


@pytest.mark.parametrize("p1,known,reason", [(14.7,False,"GAS_HISTORY_INCOMPLETE"),
                                           (3.,True,"RETURN_PRESSURE_SEQUENCE_MISMATCH"),
                                           (14.7,True,"POST_TEST_COURSE_UNVERIFIED")])
def test_post_test_course_is_decisive_for_nm_and_irrelevant_for_rm(p1, known, reason):
    after = segment("return",420,435,4.3,p1)
    if not known:
        after["gas"] = None
    for model in ("nasa_2004_nm","nasa_2004_rm"):
        d = phase_i(model)
        base = evaluate(d)
        d["segments"].append(deepcopy(after))
        r = evaluate(d)
        if model.endswith("nm"):
            assert r["probability_fraction"] is None and reason in r["inherited_vetoes"]
            assert ("segments.return-420.gas" in r["missing_decisive_inputs"]) == (not known)
        else:
            assert r["probability_fraction"] == base["probability_fraction"]
            assert r["missing_decisive_inputs"] == []
        if not known:
            assert "segments.return-420.gas" in r["physiology"]["missing_inputs"]


@pytest.mark.parametrize("late_gas", [None,gas(.21)])
def test_exact_plateau_horizon_excludes_later_missing_or_conflicting_gas(late_gas):
    d = table5()
    d["prediction_request"]["horizon_minutes"] = 120.
    full = evaluate(d)
    d["segments"][2:] = [segment("plateau",145,265,6.5,6.5,kind="exercise",amb=True),
                         segment("plateau",265,385,6.5,6.5,kind="exercise",amb=True)]
    d["segments"][-1]["gas"] = late_gas
    early = evaluate(d)
    assert early["probability_fraction"] == full["probability_fraction"]
    assert early["quantitative_output_enabled"] and early["missing_decisive_inputs"] == []
    d["prediction_request"]["horizon_minutes"] = 121.
    later = evaluate(d)
    assert later["probability_fraction"] is None
    assert ("segments.plateau-265.gas" in later["missing_decisive_inputs"]) == (late_gas is None)
