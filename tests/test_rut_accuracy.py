import math
import pytest
from mechanistic.rut_mbe1 import RutMbe1Model, ProfileSegment
from tinydcs.simulator import ExposureProfile, simulate_final_pdcs, simulate_trajectory, build_segments


def test_nitrogen_bubble_coefficient_matches_a44_including_first_recruitment():
    model = RutMbe1Model()
    p = model.params
    alpha = p.k_alpha_n2*p.alpha_t_o2_ml_per_ml_per_atm
    expected = 4*math.pi/3 * .1/(alpha*p.v_hat_t)
    assert model._g_hat_inert(alpha_t_k=alpha, v_hat_t=p.v_hat_t, n_b_n=.1, n_b_prev=0) == pytest.approx(expected)
    assert model._g_hat_inert(alpha_t_k=alpha, v_hat_t=p.v_hat_t, n_b_n=.1, n_b_prev=.1) == pytest.approx(expected)
    assert model._delta_g_hat_inert(alpha_t_k=alpha, v_hat_t=p.v_hat_t, delta_n_b=.1) == pytest.approx(expected)


def test_resting_nitrogen_half_time_matches_source_table2():
    model = RutMbe1Model()
    initial = model.initialize_state(p_amb_atm=1., fio2=.21, fin2=.79)
    history = model.run_profile([ProfileSegment(90., 1., 1., 0., 0.)], dt_min=.01)
    ratio = history[-1].pt_n2_atm/initial.pt_n2_atm
    assert ratio == pytest.approx(2**(-90/284.05), abs=2e-5)


def test_alveolar_co2_is_distinct_from_tissue_co2():
    m = RutMbe1Model()
    oxygen = m._pa_o2_atm(1., m._pa_inert_atm(1., .79))*760
    assert oxygen == pytest.approx(114.73)
    assert m.params.p_infty_atm*760 == pytest.approx(92)


@pytest.mark.parametrize("fn", [simulate_final_pdcs, simulate_trajectory])
def test_all_quantitative_wrappers_enforce_unreconciled_gate(fn):
    with pytest.raises(RuntimeError, match="disabled"):
        fn(ExposureProfile(target_altitude_ft=25000, altitude_duration_min=1))


def test_incomplete_mixture_is_rejected():
    with pytest.raises(ValueError):
        ProfileSegment(1, 1, 0, 0, 0)


def test_ascent_has_explicit_pressure_ramp():
    profile = ExposureProfile(target_altitude_ft=25000, ascent_rate_fpm=1000,
                              acclimatization_min=0, altitude_duration_min=0)
    ascent = build_segments(profile)[0]
    assert ascent.duration_min == 25
    assert ascent.start_p_amb_atm == 1.
    assert ascent.p_amb_atm < ascent.start_p_amb_atm


def test_unstable_recursion_is_rejected_and_stage_state_restored():
    from mechanistic.rut_mbe1 import NumericalReconciliationError
    model = RutMbe1Model()
    initial = model.initialize_state(p_amb_atm=1, fio2=.21, fin2=.79)
    with pytest.raises(NumericalReconciliationError):
        model.run_profile([ProfileSegment(5, .37, 1, 0, .3)], dt_min=.5)
    assert model.state is initial
