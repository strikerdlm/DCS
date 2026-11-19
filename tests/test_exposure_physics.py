"""History, units, gas delivery, arbitrary subdivision, and prospective data integrity."""
import copy
import json
import math

import numpy as np
import pytest
from pydantic import ValidationError
from scipy.integrate import solve_ivp

from tests.test_aviation_models import gas, pressure, segment, table5
from tinydcs.aviation_models import evaluate
from tinydcs.exposure import PA_PER_PSIA, ExposureProfile, ObservedExposureProfile, Pressure
from tinydcs.exposure_physics import Ramp, derive_physiology


def test_units_isa_suit_and_breathing_pressures_are_distinct():
    for unit, value in [("Pa",101325),("kPa",101.325),("atm",1),("mmHg",760),("psia",101325/PA_PER_PSIA)]:
        assert Pressure(kind="absolute", unit=unit, value=value).pascals() == pytest.approx(101325)
    for m, expected in [(0,101325),(11000,22632.06),(20000,5474.89)]:
        for unit, value in [("ft",m/.3048), ("m",m)]:
            assert Pressure(kind="pressure_altitude", value=value, unit=unit).pascals() == pytest.approx(expected,rel=3e-5)
    diff = Pressure(kind="suit_differential",value=3,unit="psia",ambient=pressure(1.3))
    assert diff.pascals() == pytest.approx(4.3*PA_PER_PSIA)
    d = table5()
    d["segments"][1]["vehicle_geometric_altitude_m"] = 20000
    raw = derive_physiology(ExposureProfile.model_validate(d))
    d["segments"][1]["breathing_overpressure_pa"] = 5000
    # With N2 present the driving pressure changes, while the body denominator stays fixed.
    d["segments"][1]["gas"] = gas(.50)
    r = derive_physiology(ExposureProfile.model_validate(d))
    assert r["arrival_pressure_pa"] == raw["arrival_pressure_pa"]
    assert r["arrival_nitrogen_pa"] > raw["arrival_nitrogen_pa"]


@pytest.mark.parametrize("data", [
    {"kind":"absolute","value":0,"unit":"psia"},
    {"kind":"absolute","value":5,"unit":"ft"},
    {"kind":"absolute","value":float("nan"),"unit":"Pa"},
    {"kind":"absolute","value":4.3,"unit":"psia","ambient":pressure(1.3)},
    {"kind":"suit_differential","value":4.3,"unit":"psia"},
    {"kind":"pressure_altitude","value":21000,"unit":"m"},
])
def test_bad_pressure_definitions(data):
    with pytest.raises(ValidationError):
        Pressure.model_validate(data)


def test_continuity_fraction_missingness_and_prospective_separation():
    base = table5()
    for change in [
        lambda d: d["segments"][1].update(start=116),
        lambda d: d["segments"][1].update(start=114),
        lambda d: d["segments"][1].update(id=d["segments"][0]["id"]),
        lambda d: d["segments"][1].update(start_pressure=pressure(12)),
        lambda d: d["segments"][0]["gas"].update(oxygen_fraction=.75),
        lambda d: d["segments"][0]["gas"].update(basis="dry",water_fraction=.1),
        lambda d: d["segments"][2].update(timing_basis="observed"),
        lambda d: d["segments"][0].update(treatment="oxygen"),
        lambda d: d.update(outcome_record={"event":True}),
        lambda d: d["segments"][0]["activity"].update(ambulation="false"),
        lambda d: d["prediction_request"].update(horizon_minutes=float("inf")),
    ]:
        d = copy.deepcopy(base)
        change(d)
        with pytest.raises(ValidationError):
            ExposureProfile.model_validate(d)
    observed = copy.deepcopy(base)
    observed.pop("prediction_request")
    for s in observed["segments"]:
        s["timing_basis"]="observed"
    assert ObservedExposureProfile.model_validate(observed).segments[-1].timing_basis == "observed"
    with pytest.raises(ValidationError):
        evaluate(ObservedExposureProfile.model_validate(observed))


def test_residence_no_hidden_sea_level_and_pure_o2_equilibrium():
    d = table5()
    d["initial_state"]["body_pressure"] = pressure(9.)
    d["segments"][0]["start_pressure"] = pressure(9.)
    d["segments"][0]["end_pressure"] = pressure(9.)
    d["segments"][1]["start_pressure"] = pressure(9.)
    r = evaluate(d)
    assert r["physiology"]["initial_nitrogen_pa"] == pytest.approx(9*.79*PA_PER_PSIA)
    assert "STARTING_RESIDENCE_OUTSIDE_SOURCE" in r["applicability"]["reasons"]
    d["initial_state"]["gas"] = gas(1.)
    p = ExposureProfile.model_validate(d)
    f = derive_physiology(p)
    assert f["arrival_nitrogen_pa"] == f["plateau_exit_nitrogen_pa"] == 0
    d["initial_state"]["method"] = "unknown"
    r = evaluate(d)
    assert r["physiology"]["arrival_nitrogen_pa"] is None
    assert "INITIAL_STATE_UNKNOWN" in r["applicability"]["reasons"]


def test_history_propagates_without_reset_and_dose_starts_at_time_zero():
    d = table5()
    d["history"]["segments"] = [segment("prior_exposure",-60,0,14.7,14.7,oxygen=1.)]
    d["history"]["previous_altitude_exposure"] = True
    f = derive_physiology(ExposureProfile.model_validate(d))
    start = d["initial_state"]["body_pressure"]["value"]*.79*PA_PER_PSIA
    assert f["trajectory"][1]["start_nitrogen_pa"] == pytest.approx(start*2**(-60/360))
    assert f["supersaturation_dose_pa_s"] == pytest.approx(
        sum(x["supersaturation_dose_pa_s"] for x in f["trajectory"][1:]))
    assert "PRIOR_EXPOSURE_OUTSIDE_SOURCE" in evaluate(d)["inherited_vetoes"]


def test_independent_exact_ramp_and_nonendpoint_maximum_and_dose():
    # Increasing pressure after an initially supersaturated driving gas can give
    # an interior peak. Reference integrates tissue and positive excess directly.
    r = Ramp(41000.,40000.,60000.,90000.,0.,16000.,1/2000.)
    def change(t, y):
        u = t/r.seconds
        return [r.rate*(r.target_start*(1-u)-y[0]), max(0.,y[0]-r.pressure(u))]
    sol = solve_ivp(change,(0.,r.seconds),[r.tissue_start,0.],rtol=1e-11,atol=1e-8,
                    dense_output=True,max_step=r.seconds/400)
    end, peak, dose = r.metrics()
    dense = np.linspace(0.,1.,20001)
    ratios = sol.sol(dense*r.seconds)[0]/r.pressure(dense)
    assert 0 < np.argmax(ratios) < len(ratios)-1
    assert end == pytest.approx(sol.y[0,-1],rel=2e-9)
    assert peak == pytest.approx(np.max(ratios),rel=2e-8)
    assert dose == pytest.approx(sol.y[1,-1],rel=3e-9)


def test_linear_mixing_with_pressure_change_subdivision_and_independent_solution():
    d = table5()
    last = d["segments"][1]
    last["gas"], last["end_gas"] = gas(.85), gas(.25)
    p = ExposureProfile.model_validate(d)
    f = derive_physiology(p)
    n0 = f["trajectory"][1]["start_nitrogen_pa"]
    def equation(t,n):
        u=t/1800
        return math.log(2)/(360*60)*((14.7*(1-u)+6.5*u)*PA_PER_PSIA*(.15+.60*u)-n[0])
    ref = solve_ivp(equation,(0.,1800.),[n0],rtol=2e-12,atol=1e-9)
    assert f["arrival_nitrogen_pa"] == pytest.approx(ref.y[0,-1], rel=1e-10)
    new1=segment("ascent",115,130,14.7,10.6,.85)
    new1["end_gas"]=gas(.55)
    new2=segment("ascent",130,145,10.6,6.5,.55)
    new2["end_gas"]=gas(.25)
    d["segments"][1:2]=[new1,new2]
    split = derive_physiology(ExposureProfile.model_validate(d))
    for k in ("arrival_nitrogen_pa","plateau_exit_nitrogen_pa","maximum_tissue_ratio","supersaturation_dose_pa_s"):
        assert split[k] == pytest.approx(f[k],rel=5e-12)


def test_early_late_interruption_and_category_specific_durations():
    def interrupted(at):
        d=table5()
        d["segments"][:1] = [segment("prebreathe",0,at,14.7,14.7),
                             segment("oxygen_break",at,at+8,14.7,14.7,.21),
                             segment("prebreathe",at+8,115,14.7,14.7)]
        return d
    early, late = (evaluate(interrupted(i)) for i in (5,100))
    assert early["physiology"]["arrival_nitrogen_pa"] < late["physiology"]["arrival_nitrogen_pa"]
    assert "BREAK_PROTOCOL_UNSUPPORTED" in early["inherited_vetoes"]
    assert early["policy_conformance"]["events"][0]["start_seconds"] == 300
    d = interrupted(10)
    d["segments"][1]["break_kind"] = "exercise_only"
    d["segments"][1]["gas"] = gas(1.)
    r=evaluate(d)
    assert "EXERCISE_INTERRUPTION_OUTSIDE_PROTOCOL" in r["inherited_vetoes"]
    assert "BREAK_PROTOCOL_UNSUPPORTED" not in r["inherited_vetoes"]
    d["segments"][2:3] = [segment("oxygen_break",18,22,14.7,14.7,.21),
                           segment("transfer",22,28,14.7,14.7,.265),
                           segment("purge",28,32,14.7,14.7,1.),segment("prebreathe",32,115,14.7,14.7)]
    d["segments"][3]["break_kind"]="mask_to_suit"
    pol=evaluate(d)["policy_conformance"]
    assert [x["kind"] for x in pol["events"]] == ["exercise_only","breathing_gas","mask_to_suit","purge"]
    assert pol["documented_nitrogen_break_minutes"] == 10
    assert pol["operational_cumulative_break_minutes"] is None
    assert "≤10" in pol["boundary_note"] and "<10" in pol["boundary_note"]
    ramp = interrupted(5)
    ramp["segments"][1].update(gas=gas(1), end_gas=gas(.21))
    pol = evaluate(ramp)["policy_conformance"]
    assert pol["documented_nitrogen_break_minutes"] == 8
    assert pol["events"][0]["start_nitrogen_fraction"] == 0
    assert pol["events"][0]["next_oxygen_fraction"] == 1


def test_future_horizon_changes_exit_only_and_missing_later_gas_keeps_arrival():
    d = table5(4.3)
    r = evaluate(d)
    original = r["physiology"]
    d["segments"][-1]["end"] += 120
    d["prediction_request"]["horizon_minutes"] = 360
    later=evaluate(d)
    assert original["arrival_nitrogen_pa"] == later["physiology"]["arrival_nitrogen_pa"]
    assert original["plateau_exit_nitrogen_pa"] > later["physiology"]["plateau_exit_nitrogen_pa"]
    assert r["input_fingerprint"] != later["input_fingerprint"]
    d["segments"][-1]["gas"] = None
    f=derive_physiology(ExposureProfile.model_validate(d),"nasa_2020")
    assert f["arrival_nitrogen_pa"] == original["arrival_nitrogen_pa"]
    assert f["plateau_exit_nitrogen_pa"] is None and f["status"] == "partial"
    assert evaluate(d)["probability_fraction"] is None
    assert evaluate(d)["physiology"]["arrival_nitrogen_pa"] == original["arrival_nitrogen_pa"]
    json.dumps(evaluate(d),allow_nan=False)


def test_interspersed_residence_cannot_bypass_the_gas_history_check():
    d = table5()
    d["segments"] = [
        segment("prebreathe",0,45,14.7,14.7),
        segment("residence",45,60,14.7,14.7,.21),
        segment("prebreathe",60,130,14.7,14.7),
        segment("ascent",130,160,14.7,6.5),
        segment("plateau",160,400,6.5,6.5,kind="exercise",amb=True),
    ]
    r = evaluate(d)
    assert r["probability_fraction"] is None
    assert "RESIDENCE_INTERRUPTS_PREBREATHE" in r["inherited_vetoes"]


def test_short_physiology_request_is_supported_and_short_complete_clinical_is_null():
    d = table5(4.3,duration=10)
    d["prediction_request"].update(model_id="physiology",endpoint="physiology",
            reference_population="aviation",window="complete_exposure",prediction_origin="profile_start")
    r = evaluate(d)
    assert r["applicability"] == {"status":"physiology_only","reasons":[]}
    d["prediction_request"].update(model_id="auto",endpoint="clinically_adjudicated_dcs")
    r = evaluate(d)
    assert r["probability_fraction"] is None and "COMPLETE_SHORT_PROFILE_NOT_VALIDATED" in r["inherited_vetoes"]
