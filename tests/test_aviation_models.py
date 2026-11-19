"""Published-equation reproductions and prospective applicability."""
import json
import math

import pytest

from mechanistic.conkin_nasa import (
    compute_p1n2, nitrogen_half_time, nitrogen_rate_constant, predict_endpoint,
)
from tinydcs.aviation_models import evaluate, model_registry
from tinydcs.exposure import PA_PER_PSIA, ExposureProfile
from tinydcs.exposure_physics import derive_physiology
from tinydcs.hypobaric import HypobaricScenario, probability


def pressure(p):
    return {"kind": "absolute", "value": p, "unit": "psia"}


def gas(o2):
    return {"basis": "dry", "oxygen_fraction": o2, "nitrogen_fraction": 1-o2}


def segment(phase, t0, t1, p0, p1, oxygen=1., kind="rest", amb=False, **kwargs):
    return {"id": f"{phase}-{t0}", "phase": phase, "start": t0, "end": t1,
            "start_pressure": pressure(p0), "end_pressure": pressure(p1),
            "interpolation": "constant" if p0 == p1 else "linear_pressure",
            "gas": gas(oxygen), "activity": {"type": kind, "ambulation": amb} | kwargs,
            "provenance": "source schedule"}


def table5(p=6.5, duration=240):
    pb = {4.3:380, 5.3:245, 6.5:115, 7.5:25}[p]
    return {"schema_version": "1.0.0", "profile_id": "reference", "purpose": "research",
            "provenance": "NASA/TP-2020-220529 Table 5", "time_unit": "min",
            "initial_state": {"method": "assumed_equilibrium", "body_pressure": pressure(14.7),
                              "gas": gas(.21), "provenance": "source nominal sea-level air"},
            "history": {"recent_diving": False, "previous_altitude_exposure": False},
            "segments": [segment("prebreathe", 0, pb, 14.7, 14.7),
                         segment("ascent", pb, pb+30, 14.7, p),
                         segment("plateau", pb+30, pb+30+duration, p, p, kind="exercise", amb=True)],
            "person_covariates": {"bmi_kg_m2": 24.},
            "prediction_request": {"model_id":"auto", "endpoint":"symptomatic_dcs",
                                   "prediction_origin":"plateau_arrival", "window":"during_plateau",
                                   "horizon_minutes":duration, "source_protocol":"nasa_2020_table5",
                                   "reference_population":"male_hypobaric_chamber" if p>5
                                   else "nasa_hypobaric_chamber"}}


def phase_i(model="nasa_2004_rm"):
    # Direct transcription of the source input, independent of program manifest.
    d = table5(4.3)
    d["history"]["segments"] = [segment("residence", -100, 0, 14.7, 14.7, .21, posture="recumbent")]
    d["segments"] = [
        segment("prebreathe", 0, 3, 14.7, 14.7, kind="warmup", exercise_mode="dual_cycle", percent_vo2_peak=37.5),
        segment("prebreathe", 3, 10, 14.7, 14.7, kind="exercise", exercise_mode="dual_cycle", percent_vo2_peak=75.),
        segment("recovery", 10, 13, 14.7, 14.7, kind="recovery", percent_vo2_peak=37.5),
        segment("recovery", 13, 30, 14.7, 14.7, kind="recovery", percent_vo2_peak=25.),
        segment("prebreathe", 30, 50, 14.7, 14.7),
        segment("prebreathe", 50, 70, 14.7, 9.6),
        segment("prebreathe", 70, 80, 9.6, 10.2),
        segment("prebreathe", 80, 110, 10.2, 10.2, .265),
        segment("prebreathe", 110, 115, 10.2, 14.7),
        segment("prebreathe", 115, 150, 14.7, 14.7),
        segment("ascent", 150, 180, 14.7, 4.3),
        segment("plateau", 180, 420, 4.3, 4.3, kind="simulated_eva", exercise_mode="crank_and_yank",
                posture="semi_recumbent"),
    ]
    d["person_covariates"] = {"source_sex":"male", "age_years":43., "vo2_peak_ml_kg_min":50.,
                               "vo2_peak_method":"measured", "bmi_kg_m2":24.}
    for s in d["segments"]:
        s["activity"]["posture"] = "semi_recumbent"
    d["prediction_request"].update(model_id=model, source_protocol="nasa_2004_phase_i",
                                    reference_population="nasa_2004_adynamic_chamber",
                                    window="source_post_test" if model.endswith("nm") else "during_plateau")
    if model.endswith("nm"):
        d["prediction_request"]["post_test_course"] = "published_source_ascertainment"
    return d


def test_rates_are_per_minute_and_legacy_name_stays_compatible():
    assert nitrogen_rate_constant(0, .03) == 1/519.37
    k = nitrogen_rate_constant(10, .03)
    assert k == pytest.approx(.00259903114846)
    assert math.log(2)/k == pytest.approx(266.694449)
    assert nitrogen_half_time(10, .03) == k


@pytest.mark.parametrize("variant,expected", [
    ("NM", (6.617188602, 1.538881070, .00105500325)),
    ("RM", (6.696488860, 1.557322991, .00114414770)),
])
def test_table17_print_and_percentage_derived_are_distinct(variant, expected):
    lam = .03 if variant == "NM" else .025
    def fixture(quiet):
        n = 8.
        for duration, q, target in [(3,12.5,0), (17,25,0), (3,12.5,0), (17,10,0),
                                    (20,10,8), (30,quiet,0)]:
            n = compute_p1n2(n, target, q, duration, lam)
        tr = n/4.3
        return n, tr, predict_endpoint(tr, variant=variant, age_years=43, sex="Male")
    assert fixture(4.7) == pytest.approx(expected, rel=2e-8)
    assert fixture(9.5/100*50)[0] < fixture(4.7)[0]


def test_primary_2020_appendix_a_rest_and_1996_eq7():
    d = table5()
    d["segments"] = [segment("prebreathe", 0, 60, 14.7, 14.7),
                     segment("ascent", 60, 75, 14.7, 6),
                     segment("plateau", 75, 315, 6, 6, kind="exercise", amb=True)]
    d["prediction_request"]["source_protocol"] = "nasa_2020_appendix_a_rest"
    result = evaluate(d)
    assert result["source_features"]["arrival_nitrogen_pa"]/PA_PER_PSIA == pytest.approx(10.0488788734)
    assert result["probability_fraction"] == pytest.approx(.191329937695)
    assert result["source_features"]["source_repressurization_protocol"] is False


@pytest.mark.parametrize("p", [4.3, 5.3, 6.5, 7.5])
def test_supported_table5_and_earlier_cumulative_horizon(p):
    d = table5(p)
    result = evaluate(d)
    assert result["quantitative_output_enabled"], result["applicability"]
    assert result["model_id"] == ("nasa_2020_eq4" if p == 4.3 else "conkin_1996_eq7")
    # Integrated (unrounded) Table 5 arrivals and the routed equations. The paper
    # labels a 3% Eq. 7 isopleth; its 7.5-psia time and coefficients give 3.3134%.
    target = {4.3:.017622009349, 5.3:.029579822872, 6.5:.031010975099, 7.5:.033134340312}
    assert result["probability_fraction"] == pytest.approx(target[p], rel=1e-9)
    assert result["uncertainty"]["lower"] is None
    assert len(result["input_fingerprint"]) == len(result["artifact_hash"]) == 64
    json.dumps(result, allow_nan=False)
    d["prediction_request"]["horizon_minutes"] = 120
    early = evaluate(d)
    assert 0 < early["probability_fraction"] < result["probability_fraction"]
    assert early["physiology"]["arrival_nitrogen_pa"] == result["physiology"]["arrival_nitrogen_pa"]


@pytest.mark.parametrize("model,variant", [("nasa_2004_nm","NM"),("nasa_2004_rm","RM")])
def test_phase_i_compared_with_table3_direct_recursion(model, variant):
    d = phase_i(model)
    r = evaluate(d)
    assert r["quantitative_output_enabled"], r["applicability"]
    n = 11.6
    lam = .030 if variant == "NM" else .025
    for t, q, pi in [(3,18.75,0), (7,37.5,0), (3,18.75,0), (17,12.5,0), (50,4.75,0),
                     (30,4.75,10.2*.735), (70,4.75,0)]:
        n = pi+(n-pi)*math.exp(-t*math.exp(q*lam)/519.37)
    assert r["source_features"]["arrival_nitrogen_pa"]/PA_PER_PSIA == pytest.approx(n)
    x = -25.56+12.83*n/4.3-1.037 if variant == "NM" else -31.71+14.55*n/4.3+.053*43
    assert r["probability_fraction"] == pytest.approx(1/(1+math.exp(-x)))
    assert r["source_features"]["source_repressurization_protocol"] is True
    assert ("after" in r["outcome_ascertainment"]) == (variant == "NM")
    d["prediction_request"]["window"] = "during_plateau" if variant == "NM" else "source_post_test"
    assert "OUTCOME_WINDOW_MISMATCH" in evaluate(d)["applicability"]["reasons"]


def test_staged_2020_rep_is_not_prior_altitude_or_a_duration_only_id():
    d = phase_i("nasa_2020_eq4")
    d["prediction_request"]["reference_population"] = "nasa_hypobaric_chamber"
    r = evaluate(d)
    assert r["quantitative_output_enabled"], r["applicability"]
    assert r["source_features"]["source_repressurization_protocol"] is True
    d["segments"][7]["gas"] = gas(.21)
    assert evaluate(d)["probability_fraction"] is None
    assert evaluate(d)["source_features"]["source_repressurization_protocol"] is None
    other = table5()
    other["history"]["previous_altitude_exposure"] = True
    r = evaluate(other)
    assert r["probability_fraction"] is None
    assert r["source_features"]["source_repressurization_protocol"] is False
    assert "PRIOR_EXPOSURE_OUTSIDE_SOURCE" in r["inherited_vetoes"]


@pytest.mark.parametrize("key,value,reason", [
    ("reference_population", "aviation", "SOURCE_POPULATION_MISMATCH"),
    ("endpoint", "grade_iv_vge", "ENDPOINT_MISMATCH"),
    ("prediction_origin", "profile_start", "PREDICTION_ORIGIN_MISMATCH"),
    ("window", "post_return", "OUTCOME_WINDOW_MISMATCH"),
    ("horizon_minutes", 10., "SOURCE_HORIZON_MISMATCH"),
    ("source_protocol", "user_verified", "SOURCE_PROTOCOL_UNVERIFIED"),
])
def test_endpoint_population_and_protocol_fail_closed(key,value,reason):
    d = table5()
    d["prediction_request"].update(model_id="conkin_1996_eq7", **{key:value})
    r = evaluate(d)
    assert r["probability_fraction"] is None and not r["quantitative_output_enabled"]
    assert reason in r["applicability"]["reasons"]


def test_independent_2020_rounded_fixture_and_five_psia_discontinuity():
    common = dict(plateauPressurePsia=4.3, elapsedPlateauHours=6., depressurizationMinutes=15.,
                  singleConstantPlateau=True, arrivalTissueN2Psia=4.3*1.23, ambulationAtPlateau=True,
                  bmiKgM2=24., sourceRepressurizationProtocol=False, maleReferenceCohort=True)
    s = probability(HypobaricScenario(**common))
    assert s.pDcsPercent == pytest.approx(3.055, abs=.001)
    common.update(elapsedPlateauHours=4., arrivalTissueN2Psia=7.5, plateauPressurePsia=5.)
    one = probability(HypobaricScenario(**common))
    common["plateauPressurePsia"] = 5.000001
    two = probability(HypobaricScenario(**common))
    assert (one.model,two.model) == ("NASA-2020-Eq4","Conkin-1996-Eq7")
    assert one.pDcsPercent == pytest.approx(8.261463, abs=1e-6)
    assert two.pDcsPercent == pytest.approx(11.350402, abs=1e-6)


def test_2020_recovery_five_minutes_across_subdivision_and_2004_quiet_differ():
    d = table5()
    d["segments"][:1] = [segment("prebreathe",0,10,14.7,14.7,kind="exercise",vo2_ml_kg_min=23.5),
                          segment("recovery",10,12,14.7,14.7), segment("prebreathe",12,115,14.7,14.7)]
    p = ExposureProfile.model_validate(d)
    trajectory = derive_physiology(p,"nasa_2020")["trajectory"]
    assert trajectory[1]["rate_blocks"][0]["source_vo2_ml_kg_min"] == 10.
    assert trajectory[2]["rate_blocks"][0]["duration_minutes"] == 3
    assert trajectory[2]["rate_blocks"][1]["source_vo2_ml_kg_min"] == 3.5
    q = derive_physiology(ExposureProfile.model_validate(phase_i()),"nasa_2004_rm")
    assert q["trajectory"][-2]["rate_blocks"][0]["source_vo2_ml_kg_min"] == 4.75


def test_registry_preserves_gas_equation_and_distinct_ascertainment():
    m = {x["model_id"]:x for x in model_registry()}
    assert m["nasa_2004_nm"]["coefficient_version"].endswith("Eq14")
    assert m["nasa_2004_rm"]["coefficient_version"].endswith("Eq15")
    assert m["nasa_2004_nm"]["ascertainment"] != m["nasa_2004_rm"]["ascertainment"]
    assert all(len(x["source_pdf_sha256"]) == 64 for x in m.values())
