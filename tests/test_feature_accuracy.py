import numpy as np
import pytest
from tinydcs.features import extract_features, _peak_1min
from tinydcs.simulator import ExposureProfile, vo2_ml_per_kg_per_min_to_i_ex_l_per_min
from tinydcs.simulator import build_segments


def test_features_weight_partial_final_interval():
    profile = ExposureProfile(target_altitude_ft=25000, altitude_duration_min=1.5,
                              vo2_dt_min=1, altitude_i_ex_trajectory=np.array([0., 1.]))
    features = extract_features(profile)
    assert features.altitude_vo2_mean_lmin == pytest.approx(1/3)
    assert features.altitude_vo2_integral_lmin_min == pytest.approx(.5)
    assert features.altitude_vo2_peak_1min_lmin == pytest.approx(.5)
    phases = build_segments(profile)
    assert sum(p.duration_min*p.i_ex_l_min_wb for p in phases) == pytest.approx(.5)


def test_one_minute_window_handles_non_divisor_sampling():
    assert _peak_1min(np.array([0, 1, 0]), .6) == pytest.approx(.6)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -1])
def test_invalid_vo2_conversion_rejected(bad):
    with pytest.raises(ValueError):
        vo2_ml_per_kg_per_min_to_i_ex_l_per_min(bad, 70)


def test_trajectory_length_mismatch_is_not_silently_resampled():
    with pytest.raises(ValueError):
        profile = ExposureProfile(target_altitude_ft=25000, altitude_duration_min=10,
                                  vo2_dt_min=1, altitude_i_ex_trajectory=np.array([0, 1]))
        extract_features(profile)
def test_zero_duration_allows_an_empty_sampled_trajectory():
    import numpy as np
    from tinydcs.simulator import _expand_trajectory
    assert _expand_trajectory(np.empty(0), 0, 1).size == 0
