"""Feature extraction for the TinyDCS surrogate.

Given an :class:`ExposureProfile` (continuous VO2 trajectories + scalar inputs)
this module produces a compact feature vector suitable for both:
  - training the surrogate on simulated 3RUT-MBe1 outputs, and
  - on-device inference from a wearable VO2 stream + altitude log.

The feature set is deliberately small (≤ 12 features) so the trained model
remains under 100 KB after INT8 quantization.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

import numpy as np

from .simulator import ExposureProfile, ProfileRecord, altitude_ft_to_atm, _expand_trajectory


_SEA_LEVEL_PRESSURE_MMHG = 760.0
_P_H2O_MMHG = 47.0
_N2_FRACTION_AIR = 0.79


def _atm_to_mmhg(p_atm: float) -> float:
    return float(p_atm) * _SEA_LEVEL_PRESSURE_MMHG


def _tissue_n2_ratio_360(
    *,
    altitude_ft: float,
    prebreathe_time_min: float,
    prebreathe_fio2: float,
    altitude_time_min: float,
    altitude_fio2: float,
    half_time_min: float = 360.0,
) -> float:
    """Fixed-half-time, humidified single-compartment tissue N2 supersaturation ratio at exit.

    Starts at sea-level air equilibrium, applies prebreathe with given FiO2,
    assumes instantaneous ascent, then altitude exposure with given FiO2.
    Returns P_tissue_N2 / P_ambient at the end of altitude exposure (a classic
    hypobaric DCS decompression-dose surrogate).
    """
    p_amb_alt_mmhg = _atm_to_mmhg(altitude_ft_to_atm(altitude_ft))
    p_amb_alt_mmhg = max(p_amb_alt_mmhg, 1e-6)
    p_amb_ground = _SEA_LEVEL_PRESSURE_MMHG

    fn2_pre = 1.0 - float(prebreathe_fio2)
    fn2_alt = 1.0 - float(altitude_fio2)

    p_insp_n2_ground_air = max(p_amb_ground - _P_H2O_MMHG, 0.0) * _N2_FRACTION_AIR
    p_insp_n2_pre = max(p_amb_ground - _P_H2O_MMHG, 0.0) * fn2_pre
    p_insp_n2_alt = max(p_amb_alt_mmhg - _P_H2O_MMHG, 0.0) * fn2_alt

    tau = half_time_min / np.log(2.0)
    p_after_pre = p_insp_n2_pre - (p_insp_n2_pre - p_insp_n2_ground_air) * np.exp(-prebreathe_time_min / tau)
    p_end = p_insp_n2_alt - (p_insp_n2_alt - p_after_pre) * np.exp(-altitude_time_min / tau)
    return float(p_end / p_amb_alt_mmhg)


def _peak_1min(traj: np.ndarray, dt_min: float, duration_min: float | None = None) -> float:
    """Exact maximum up-to-one-minute mean of a piecewise-constant signal.

    Coarse samples imply a constant within-sample assumption, not measured
    one-minute resolution. Partial final intervals retain their true duration.
    """
    arr = np.asarray(traj, dtype=float).ravel()
    if not np.isfinite(dt_min) or dt_min <= 0 or not np.isfinite(arr).all() or np.any(arr < 0):
        raise ValueError("finite nonnegative trajectory and positive sampling interval required")
    duration = arr.size*dt_min if duration_min is None else duration_min
    if duration <= 0 or arr.size == 0:
        return 0.0
    edges = np.append(np.arange(arr.size)*dt_min, duration)
    if np.any(np.diff(edges) <= 0):
        raise ValueError("trajectory does not match duration")
    cumulative = np.append(0., np.cumsum(arr*np.diff(edges)))
    width = min(1., duration)
    starts = np.unique(np.clip(np.concatenate([edges, edges-width]), 0, duration-width))
    values = (np.interp(starts+width, edges, cumulative)-np.interp(starts, edges, cumulative))/width
    return float(values.max())


def extract_features(profile: ExposureProfile) -> ProfileRecord:
    """Derive the TinyDCS feature vector from a profile."""
    pre_traj = _expand_trajectory(profile.prebreathe_i_ex_trajectory, profile.prebreathe_duration_min, profile.vo2_dt_min)
    alt_traj = _expand_trajectory(profile.altitude_i_ex_trajectory, profile.altitude_duration_min, profile.vo2_dt_min)
    def integral(arr, duration):
        widths = np.minimum(profile.vo2_dt_min, duration-np.arange(len(arr))*profile.vo2_dt_min)
        return float(np.dot(arr, widths))
    pre_mean = integral(pre_traj, profile.prebreathe_duration_min)/profile.prebreathe_duration_min if profile.prebreathe_duration_min else 0.
    pre_peak = float(pre_traj.max()) if pre_traj.size else 0.
    alt_integral = integral(alt_traj, profile.altitude_duration_min)
    alt_mean = alt_integral/profile.altitude_duration_min if profile.altitude_duration_min else 0.
    alt_peak_1 = _peak_1min(alt_traj, profile.vo2_dt_min, profile.altitude_duration_min)

    tr360 = _tissue_n2_ratio_360(
        altitude_ft=profile.target_altitude_ft,
        prebreathe_time_min=profile.prebreathe_duration_min,
        prebreathe_fio2=profile.prebreathe_fio2,
        altitude_time_min=profile.altitude_duration_min,
        altitude_fio2=profile.altitude_fio2,
    )

    return ProfileRecord(
        altitude_ft=float(profile.target_altitude_ft),
        ambient_pressure_atm=float(altitude_ft_to_atm(profile.target_altitude_ft)),
        prebreathe_time_min=float(profile.prebreathe_duration_min),
        prebreathe_fio2=float(profile.prebreathe_fio2),
        ascent_rate_fpm=float(profile.ascent_rate_fpm),
        altitude_time_min=float(profile.altitude_duration_min),
        altitude_fio2=float(profile.altitude_fio2),
        prebreathe_vo2_mean_lmin=pre_mean,
        prebreathe_vo2_peak_lmin=pre_peak,
        altitude_vo2_mean_lmin=alt_mean,
        altitude_vo2_peak_1min_lmin=alt_peak_1,
        altitude_vo2_integral_lmin_min=alt_integral,
        tissue_n2_ratio_360min=tr360,
    )


FEATURE_COLUMNS: tuple[str, ...] = (
    "altitude_ft",
    "ambient_pressure_atm",
    "prebreathe_time_min",
    "prebreathe_fio2",
    "ascent_rate_fpm",
    "altitude_time_min",
    "altitude_fio2",
    "prebreathe_vo2_mean_lmin",
    "prebreathe_vo2_peak_lmin",
    "altitude_vo2_mean_lmin",
    "altitude_vo2_peak_1min_lmin",
    "altitude_vo2_integral_lmin_min",
    "tissue_n2_ratio_360min",
)


def records_to_rows(records: Iterable[ProfileRecord]) -> list[dict[str, float]]:
    """Convert a sequence of :class:`ProfileRecord` to plain dicts."""
    return [asdict(r) for r in records]
