"""Unit tests for tinydcs.simulator and tinydcs.features."""

from __future__ import annotations

import numpy as np
import pytest

from tinydcs.features import extract_features
from tinydcs.simulator import (
    ExposureProfile,
    altitude_ft_to_atm,
    build_segments,
    ornstein_uhlenbeck_vo2,
    simulate_final_pdcs,
    vo2_ml_per_kg_per_min_to_i_ex_l_per_min,
)


def test_altitude_conversion_monotone() -> None:
    atms = [altitude_ft_to_atm(alt) for alt in (0, 10_000, 18_000, 25_000, 40_000, 60_000)]
    assert atms == sorted(atms, reverse=True)
    assert atms[0] == pytest.approx(1.0, abs=1e-6)
    assert 0.22 <= atms[3] <= 0.38  # 25,000 ft is ~0.37 atm


def test_vo2_conversion_clips_to_zero_below_rest() -> None:
    # Resting subject reports 3.5 mL/kg/min → I_ex = 0
    ex = vo2_ml_per_kg_per_min_to_i_ex_l_per_min(3.5, subject_mass_kg=75)
    assert ex == pytest.approx(0.0, abs=1e-9)
    # A 30 mL/kg/min effort in a 75 kg subject: (30-3.5)*75/1000 ≈ 1.99 L/min
    ex = vo2_ml_per_kg_per_min_to_i_ex_l_per_min(30.0, subject_mass_kg=75)
    assert ex == pytest.approx(1.9875, abs=1e-3)


def test_ornstein_uhlenbeck_stays_bounded() -> None:
    rng = np.random.default_rng(0)
    traj = ornstein_uhlenbeck_vo2(duration_min=120.0, dt_min=1.0, mean_i_ex=0.4, lo=0.0, hi=1.5, rng=rng)
    assert traj.shape == (120,)
    assert float(traj.min()) >= 0.0
    assert float(traj.max()) <= 1.5


def test_build_segments_covers_all_phases() -> None:
    profile = ExposureProfile(
        target_altitude_ft=25_000.0,
        prebreathe_duration_min=30.0,
        prebreathe_fio2=1.0,
        prebreathe_fin2=0.0,
        prebreathe_i_ex_trajectory=0.0,
        altitude_duration_min=60.0,
        altitude_fio2=0.21,
        altitude_fin2=0.79,
        altitude_i_ex_trajectory=0.3,
        vo2_dt_min=5.0,
        acclimatization_min=5.0,
    )
    segs = build_segments(profile)
    # 1 acclim + ceil(30/5)=6 prebreathe + 1 ascent + ceil(60/5)=12 altitude = 20
    assert len(segs) == 1 + 6 + 1 + 12


def test_simulate_final_pdcs_in_unit_interval() -> None:
    profile = ExposureProfile(
        target_altitude_ft=30_000.0,
        prebreathe_duration_min=30.0,
        prebreathe_fio2=1.0,
        prebreathe_fin2=0.0,
        prebreathe_i_ex_trajectory=0.0,
        altitude_duration_min=60.0,
        altitude_fio2=0.21,
        altitude_fin2=0.79,
        altitude_i_ex_trajectory=0.3,
        vo2_dt_min=5.0,
    )
    p = simulate_final_pdcs(profile, dt_min=0.5)
    assert 0.0 <= p <= 1.0


def test_feature_extraction_schema() -> None:
    rng = np.random.default_rng(1)
    profile = ExposureProfile(
        target_altitude_ft=28_000.0,
        prebreathe_duration_min=60.0,
        prebreathe_fio2=1.0,
        prebreathe_fin2=0.0,
        prebreathe_i_ex_trajectory=0.0,
        altitude_duration_min=180.0,
        altitude_fio2=0.21,
        altitude_fin2=0.79,
        altitude_i_ex_trajectory=ornstein_uhlenbeck_vo2(
            duration_min=180.0, dt_min=5.0, mean_i_ex=0.4, rng=rng
        ),
        vo2_dt_min=5.0,
    )
    rec = extract_features(profile)
    assert 0.0 <= rec.altitude_vo2_mean_lmin <= 1.5
    assert rec.altitude_vo2_peak_1min_lmin >= rec.altitude_vo2_mean_lmin - 1e-9
    assert rec.tissue_n2_ratio_360min > 1.0  # supersaturation expected at altitude
