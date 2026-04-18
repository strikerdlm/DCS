"""Continuous-VO2(t) wrapper around the 3RUT-MBe1 mechanistic model.

This module does *not* modify the underlying ``mechanistic/rut_mbe1.py``.
It only composes piecewise-constant profile segments to approximate arbitrary
time-varying exercise intensity I_ex(t), as would be obtained from a wearable
accelerometer-derived VO2 proxy. Each sub-segment inherits 3RUT-MBe1's
parameters and validation envelope.

Known calibration issue
-----------------------
As of repo v0.2 the vendored ``mechanistic/rut_mbe1.py`` under-reports P(DCS)
by ~4-5 orders of magnitude on Gerth's published ADRAC-validation profiles
(DTIC AD1101527, Fig. 16). Until that reconciliation is complete this module
is useful for *shape* studies (monotonicity, trajectory effects) but NOT as a
trustworthy ground truth for the TinyDCS surrogate. See ``docs/methods.md``.

Key design decisions
--------------------
- Time discretization: user supplies a step size ``vo2_dt_min``. The at-altitude
  and prebreathe phases are split into segments of that duration, each with a
  constant ``i_ex_l_min_wb`` sampled from the VO2 trajectory. 3RUT-MBe1 then
  integrates each segment with its own ODE step (``dt_min`` argument to
  ``run_profile``), typically 0.5 min.
- Acclimatization + ascent + descent phases are kept simple (constant, at-rest
  defaults) and intentionally NOT exposed as VO2 trajectories. Adding them is a
  one-liner if ever needed but expands scope.
- Units: I_ex is the incremental whole-body O2 consumption above rest, in
  L·min⁻¹. A wearable typically reports VO2 as mL·kg⁻¹·min⁻¹ with resting ≈ 3.5.
  ``vo2_ml_per_kg_per_min_to_i_ex_l_per_min`` converts given a subject mass.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

# Import the mechanistic model from its new home at repo root.
_THIS = Path(__file__).resolve()
_REPO_ROOT = _THIS.parent.parent  # .../<repo>/ (tinydcs is a top-level package)
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mechanistic.rut_mbe1 import ModelState, ProfileSegment, RutMbe1Model  # noqa: E402


_AIR_FIO2 = 0.21
_AIR_FIN2 = 0.79
_SEA_LEVEL_ATM = 1.0
_DEFAULT_ASCENT_RATE_FPM = 5000.0
_DEFAULT_REST_VO2_ML_PER_KG_PER_MIN = 3.5  # resting whole-body
_O2_L_PER_ML = 1.0 / 1000.0


def altitude_ft_to_atm(altitude_ft: float) -> float:
    """Convert altitude (ft) to ambient pressure (atm) via ISA approximation."""
    if altitude_ft < 0.0:
        altitude_ft = 0.0
    p = (1.0 - 6.87535e-6 * float(altitude_ft)) ** 5.2559
    return float(max(p, 0.001))


def vo2_ml_per_kg_per_min_to_i_ex_l_per_min(
    vo2_ml_per_kg_per_min: np.ndarray | float,
    subject_mass_kg: float,
    rest_vo2_ml_per_kg_per_min: float = _DEFAULT_REST_VO2_ML_PER_KG_PER_MIN,
) -> np.ndarray:
    """Convert wearable-reported VO2 (mL·kg⁻¹·min⁻¹) to 3RUT-MBe1 ``I_ex`` (L·min⁻¹).

    I_ex is the increment in whole-body O2 consumption above rest; values below
    rest are clipped to zero. Negative outputs would violate the 3RUT-MBe1 input
    validator.
    """
    if subject_mass_kg <= 0.0:
        raise ValueError("subject_mass_kg must be > 0")
    vo2 = np.asarray(vo2_ml_per_kg_per_min, dtype=float)
    delta_ml_per_kg = np.clip(vo2 - float(rest_vo2_ml_per_kg_per_min), 0.0, None)
    i_ex_l_per_min = delta_ml_per_kg * float(subject_mass_kg) * _O2_L_PER_ML
    return i_ex_l_per_min


@dataclass(slots=True)
class ExposureProfile:
    """Compact description of a single hypobaric exposure.

    All arrays for VO2 trajectories are on a uniform ``vo2_dt_min`` grid covering
    the phase they annotate. Supplying a scalar is equivalent to a constant
    trajectory.
    """

    target_altitude_ft: float
    prebreathe_duration_min: float = 0.0
    prebreathe_fio2: float = 1.0
    prebreathe_fin2: float = 0.0
    prebreathe_i_ex_trajectory: np.ndarray | float = 0.0  # L·min⁻¹ whole-body
    ascent_rate_fpm: float = _DEFAULT_ASCENT_RATE_FPM
    ascent_fio2: float = _AIR_FIO2
    ascent_fin2: float = _AIR_FIN2
    altitude_duration_min: float = 60.0
    altitude_fio2: float = _AIR_FIO2
    altitude_fin2: float = _AIR_FIN2
    altitude_i_ex_trajectory: np.ndarray | float = 0.0  # L·min⁻¹ whole-body
    acclimatization_min: float = 5.0
    vo2_dt_min: float = 1.0  # grid for VO2 trajectories (prebreathe + altitude)

    def __post_init__(self) -> None:
        if self.target_altitude_ft <= 0.0:
            raise ValueError("target_altitude_ft must be > 0")
        if self.prebreathe_duration_min < 0.0:
            raise ValueError("prebreathe_duration_min must be >= 0")
        if self.altitude_duration_min < 0.0:
            raise ValueError("altitude_duration_min must be >= 0")
        if self.vo2_dt_min <= 0.0:
            raise ValueError("vo2_dt_min must be > 0")
        if self.ascent_rate_fpm <= 0.0:
            raise ValueError("ascent_rate_fpm must be > 0")
        for name, fio2, fin2 in (
            ("prebreathe", self.prebreathe_fio2, self.prebreathe_fin2),
            ("ascent", self.ascent_fio2, self.ascent_fin2),
            ("altitude", self.altitude_fio2, self.altitude_fin2),
        ):
            if fio2 < 0.0 or fio2 > 1.0:
                raise ValueError(f"{name}_fio2 must be in [0, 1]")
            if fin2 < 0.0 or fin2 > 1.0:
                raise ValueError(f"{name}_fin2 must be in [0, 1]")
            if fio2 + fin2 > 1.0 + 1e-9:
                raise ValueError(f"{name}_fio2 + {name}_fin2 must be <= 1")


def _expand_trajectory(traj: np.ndarray | float, duration_min: float, dt_min: float) -> np.ndarray:
    """Expand a scalar or length-mismatched array to ``ceil(duration/dt)`` samples."""
    if duration_min <= 0.0:
        return np.empty(0, dtype=float)
    n = max(1, int(np.ceil(duration_min / dt_min)))
    arr = np.atleast_1d(np.asarray(traj, dtype=float)).ravel()
    if arr.size == 1:
        return np.full(n, float(arr[0]), dtype=float)
    if arr.size == n:
        return arr.astype(float, copy=False)
    # Resample linearly to the target length.
    xp = np.linspace(0.0, 1.0, arr.size)
    x = np.linspace(0.0, 1.0, n)
    return np.clip(np.interp(x, xp, arr), 0.0, None)


def build_segments(profile: ExposureProfile) -> list[ProfileSegment]:
    """Compose 3RUT-MBe1 profile segments from a continuous-VO2 exposure profile."""
    segments: list[ProfileSegment] = []

    # Acclimatization (at sea level, breathing air, at rest).
    if profile.acclimatization_min > 0.0:
        segments.append(
            ProfileSegment(
                duration_min=profile.acclimatization_min,
                p_amb_atm=_SEA_LEVEL_ATM,
                fio2=_AIR_FIO2,
                fin2=_AIR_FIN2,
                i_ex_l_min_wb=0.0,
            )
        )

    # Prebreathe with per-dt VO2 trajectory.
    pre_traj = _expand_trajectory(profile.prebreathe_i_ex_trajectory, profile.prebreathe_duration_min, profile.vo2_dt_min)
    pre_dt = profile.prebreathe_duration_min / len(pre_traj) if len(pre_traj) > 0 else 0.0
    for i_ex in pre_traj:
        segments.append(
            ProfileSegment(
                duration_min=pre_dt,
                p_amb_atm=_SEA_LEVEL_ATM,
                fio2=profile.prebreathe_fio2,
                fin2=profile.prebreathe_fin2,
                i_ex_l_min_wb=float(i_ex),
            )
        )

    # Ascent (constant, fast).
    target_atm = altitude_ft_to_atm(profile.target_altitude_ft)
    ascent_duration = profile.target_altitude_ft / profile.ascent_rate_fpm
    if ascent_duration > 0.0:
        segments.append(
            ProfileSegment(
                duration_min=ascent_duration,
                p_amb_atm=target_atm,
                fio2=profile.ascent_fio2,
                fin2=profile.ascent_fin2,
                i_ex_l_min_wb=0.0,
            )
        )

    # Altitude exposure with per-dt VO2 trajectory.
    alt_traj = _expand_trajectory(profile.altitude_i_ex_trajectory, profile.altitude_duration_min, profile.vo2_dt_min)
    alt_dt = profile.altitude_duration_min / len(alt_traj) if len(alt_traj) > 0 else 0.0
    for i_ex in alt_traj:
        segments.append(
            ProfileSegment(
                duration_min=alt_dt,
                p_amb_atm=target_atm,
                fio2=profile.altitude_fio2,
                fin2=profile.altitude_fin2,
                i_ex_l_min_wb=float(i_ex),
            )
        )

    return segments


def simulate_final_pdcs(profile: ExposureProfile, *, dt_min: float = 0.5) -> float:
    """Run 3RUT-MBe1 on ``profile`` and return the final P(DCS)."""
    model = RutMbe1Model()
    model.initialize_state(
        p_amb_atm=_SEA_LEVEL_ATM,
        fio2=_AIR_FIO2,
        fin2=_AIR_FIN2,
        i_ex_l_min_wb=0.0,
    )
    segments = build_segments(profile)
    if not segments:
        return 0.0
    history = model.run_profile(segments, dt_min=dt_min)
    return float(history[-1].p_dcs)


def simulate_trajectory(profile: ExposureProfile, *, dt_min: float = 0.5) -> list[ModelState]:
    """Run 3RUT-MBe1 on ``profile`` and return the full state history."""
    model = RutMbe1Model()
    model.initialize_state(
        p_amb_atm=_SEA_LEVEL_ATM,
        fio2=_AIR_FIO2,
        fin2=_AIR_FIN2,
        i_ex_l_min_wb=0.0,
    )
    segments = build_segments(profile)
    if not segments:
        return []
    return model.run_profile(segments, dt_min=dt_min)


def ornstein_uhlenbeck_vo2(
    *,
    duration_min: float,
    dt_min: float,
    mean_i_ex: float,
    theta: float = 0.3,
    sigma: float = 0.15,
    lo: float = 0.0,
    hi: float = 1.5,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Generate a realistic-looking I_ex(t) trajectory with OU dynamics.

    Matches physiological intuition: activity fluctuates around a subject-level
    mean, with moderate persistence and bounded amplitude.
    """
    if duration_min <= 0.0:
        return np.empty(0, dtype=float)
    if rng is None:
        rng = np.random.default_rng()
    n = max(1, int(np.ceil(duration_min / dt_min)))
    x = np.empty(n, dtype=float)
    x[0] = mean_i_ex
    sqrt_dt = np.sqrt(dt_min)
    for k in range(1, n):
        x[k] = x[k - 1] + theta * (mean_i_ex - x[k - 1]) * dt_min + sigma * sqrt_dt * rng.standard_normal()
        x[k] = min(max(x[k], lo), hi)
    return x


@dataclass(slots=True)
class ProfileRecord:
    """Row-shaped record capturing inputs, features, and target for training."""

    # Core scalar inputs
    altitude_ft: float
    ambient_pressure_atm: float
    prebreathe_time_min: float
    prebreathe_fio2: float
    ascent_rate_fpm: float
    altitude_time_min: float
    altitude_fio2: float
    # Compressed VO2 summary features
    prebreathe_vo2_mean_lmin: float
    prebreathe_vo2_peak_lmin: float
    altitude_vo2_mean_lmin: float
    altitude_vo2_peak_1min_lmin: float
    altitude_vo2_integral_lmin_min: float
    # Physics-informed prior feature (Conkin 360-min TR, computed closed-form)
    tissue_n2_ratio_360min: float
    # Target
    pdcs_3rut_mbe1: float = field(default=0.0)


def smoke_test() -> float:
    """Tiny self-test that 3RUT-MBe1 is reachable and our wrapper runs."""
    profile = ExposureProfile(
        target_altitude_ft=25000.0,
        prebreathe_duration_min=30.0,
        prebreathe_fio2=1.0,
        prebreathe_fin2=0.0,
        prebreathe_i_ex_trajectory=0.0,
        altitude_duration_min=60.0,
        altitude_fio2=_AIR_FIO2,
        altitude_fin2=_AIR_FIN2,
        altitude_i_ex_trajectory=0.3,
        vo2_dt_min=5.0,
    )
    p = simulate_final_pdcs(profile, dt_min=0.5)
    if not (0.0 <= p <= 1.0):
        raise RuntimeError(f"smoke test failed: p_dcs out of [0,1]: {p}")
    print(f"TinyDCS smoke test OK: P(DCS) = {p:.6f}")
    return p


if __name__ == "__main__":
    smoke_test()
