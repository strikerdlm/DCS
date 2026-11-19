"""Single-compartment exposure calculations, independent of probability and policy."""
from __future__ import annotations

import math
from dataclasses import dataclass

from scipy.integrate import quad
from scipy.optimize import brentq

from mechanistic.conkin_nasa import LAMBDAS, nitrogen_rate_constant
from tinydcs.exposure import (
    PA_PER_PSIA, PRESSURE_CONVERSION, SECONDS_PER_UNIT, ExposureProfile, Gas, Segment,
)

FIXED_RATE = math.log(2) / 360.0  # min^-1, research feature used outside source prebreathe


@dataclass(frozen=True)
class Ramp:
    """Exact first-order response for linear body pressure and linear gas fractions.

    Independent variable u is fractional elapsed duration in [0, 1]. All pressures
    are Pa, duration is seconds and the rate is s^-1.
    """

    tissue_start: float
    pressure_start: float
    pressure_end: float
    target_start: float
    target_end: float
    seconds: float
    rate: float
    curvature: float = 0.0  # (end fraction - start fraction) * pressure change

    def tissue(self, u: float) -> float:
        x = self.rate * self.seconds * u
        wash = -math.expm1(-x)
        # The Taylor series avoids subtracting nearly identical numbers for short ramps.
        lag = x * (0.5 - x / 6.0 + x*x / 24.0) if x < 1e-4 else 1.0 - wash / x
        result = (self.tissue_start * math.exp(-x) + self.target_start * wash
                  + (self.target_end-self.target_start-self.curvature)*u*lag)
        if self.curvature:
            second = (x*(1/3-x/12+x*x/60-x**3/360) if x < .01
                      else 1.0 - 2.0/x + 2.0*wash/(x*x))
            result += self.curvature*u*u*second
        return result

    def pressure(self, u: float) -> float:
        return self.pressure_start * (1-u) + self.pressure_end * u

    def derivative(self, u: float) -> float:
        target = self.target_start*(1-u) + self.target_end*u + self.curvature*u*(u-1)
        return self.seconds * self.rate * (target - self.tissue(u))

    def metrics(self) -> tuple[float, float, float]:
        """Exit Pa, peak tissue/body ratio, and integral max(Pt-Pbody, 0) in Pa·s.

        For a quadratic gas-pressure drive, Pt'' is a constant plus one
        exponential. Its possible zero isolates monotone intervals of Pt'-P'
        and of Pt' P-Pt P'. Split at every crossing before integration.
        """
        slope = self.pressure_end - self.pressure_start

        def ratio_derivative(u):
            return self.derivative(u)*self.pressure(u) - self.tissue(u)*slope

        def excess(u):
            return self.tissue(u) - self.pressure(u)

        def excess_derivative(u):
            return self.derivative(u) - slope

        def zeros(fn, left, right):
            a, b = fn(left), fn(right)
            if (a < 0 < b) or (b < 0 < a):
                return [brentq(fn, left, right, xtol=1e-14)]
            return []

        def curvature_root(u):
            target_slope = self.target_end-self.target_start+self.curvature*(2*u-1)
            return target_slope-self.derivative(u)

        inflections = [0.0, *zeros(curvature_root, 0., 1.), 1.] if self.curvature else [0., 1.]
        def critical_points(fn):
            points = [0.]
            for a, b in zip(inflections, inflections[1:]):
                points.extend(zeros(fn, a, b))
                points.append(b)
            return points

        peak_points = critical_points(ratio_derivative)
        peak = max(self.tissue(u) / self.pressure(u) for u in peak_points)
        turns = critical_points(excess_derivative)
        dose = 0.0
        for a, b in zip(turns, turns[1:]):
            bounds = [a, *zeros(excess, a, b), b]
            for left, right in zip(bounds, bounds[1:]):
                if excess((left+right)/2) > 0:
                    integral, _ = quad(excess, left, right, epsabs=1e-9, epsrel=1e-10)
                    dose += integral * self.seconds
        return self.tissue(1.0), peak, dose


def _nitrogen_fraction(gas: Gas | None, kinetics: str) -> float | None:
    if gas is None:
        return None
    if kinetics == "fixed_360":
        return gas.nitrogen_fraction
    if gas.basis != "dry" or gas.other_inert_fraction:
        return None
    if kinetics == "nasa_2020":
        return gas.nitrogen_fraction + gas.argon_fraction
    # TP-2004-213158 defines a dry N2 target without a separate argon model.
    # Explicit argon in an inspired gas outside ordinary surface air has no fitted rule.
    if gas.argon_fraction and not is_source_air(gas):
        return None
    return gas.nitrogen_fraction + gas.argon_fraction


def is_source_air(gas: Gas | None) -> bool:
    return (gas is not None and gas.basis == "dry" and gas.other_inert_fraction == 0
            and math.isclose(gas.oxygen_fraction, 0.21, abs_tol=0.0001)
            and math.isclose(gas.nitrogen_fraction + gas.argon_fraction, 0.79, abs_tol=0.0001))


def is_sea_level(pressure_pa: float) -> bool:
    # Includes measured 14.700 psia and standard 1 atm = 14.69595 psia.
    return abs(pressure_pa / PA_PER_PSIA - 14.7) < 0.005


def _initial_tissue(profile, kinetics, assumptions, missing):
    state = profile.initial_state
    if state.method == "assumed_equilibrium":
        fraction = _nitrogen_fraction(state.gas, kinetics)
        if fraction is None:
            missing.append("initial_state.gas")
            return None
        start = state.body_pressure.pascals()
        if kinetics != "fixed_360" and is_source_air(state.gas) and is_sea_level(start):
            baseline = 11.61 if kinetics == "nasa_2020" else 11.6
            assumptions.append(f"Source sea-level equilibrium nitrogen = {baseline} psia.")
            return baseline * PA_PER_PSIA
        return start * fraction
    if state.method in {"measured", "history_derived"} and state.tissue_nitrogen_pa is not None:
        convention = "declared_nitrogen" if kinetics == "fixed_360" else "source_dry_nitrogen"
        if state.tissue_convention == convention:
            return state.tissue_nitrogen_pa
        missing.append("initial_state.tissue_convention")
        return None
    missing.append("initial_state.tissue_nitrogen_pa")
    return None


def _preparation_rates(profile: ExposureProfile, prep: list[Segment], kinetics: str):
    """Per-segment list of (minutes, rate per minute, source-coded q) intervals."""
    rates = {}
    exercise_types = {"exercise", "warmup", "absolute_work", "ambulatory", "simulated_eva"}
    mixed = any(s.activity and s.activity.type in exercise_types for s in prep)
    unknown_type = any(s.activity is None or s.activity.type == "unknown" for s in prep)
    previous_exercise = None
    recovery_remaining = 0.0
    for s in prep:
        minutes = profile.minutes(s)
        a = s.activity
        q = a.workload(profile.person_covariates) if a else None
        if kinetics == "fixed_360":
            rates[s.id] = [(minutes, FIXED_RATE, None)]
            continue
        if a is None or (a.type == "unknown" and q is None):
            rates[s.id] = None
            continue
        if kinetics != "nasa_2020":
            if q is None and a.type == "rest" and profile.person_covariates.vo2_peak_ml_kg_min:
                q = 0.095 * profile.person_covariates.vo2_peak_ml_kg_min
            blocks = [(minutes, q)]
            lam = LAMBDAS[kinetics[-2:].upper()]
        else:
            lam = 0.030
            if unknown_type:
                rates[s.id] = None
                continue
            if a.type in exercise_types:
                previous_exercise, recovery_remaining = q, 5.0
                blocks = [(minutes, q)]
            elif a.type == "recovery" and q is not None:
                # Measured/specified recovery supersedes Rule 3 for this interval.
                recovery_remaining = max(0.0, recovery_remaining - minutes)
                blocks = [(minutes, q)]
            else:
                rest = 3.5 if mixed else 0.0
                transition = min(minutes, recovery_remaining)
                blocks = []
                if transition > 0:
                    transition_q = None if previous_exercise is None else (previous_exercise-3.5)/2
                    blocks.append((transition, transition_q))
                    recovery_remaining -= transition
                if minutes > transition:
                    blocks.append((minutes-transition, rest))
        if any(q is None or not math.isfinite(q) or not 0 <= q <= 200 for _, q in blocks):
            rates[s.id] = None
        else:
            rates[s.id] = [(t, nitrogen_rate_constant(q, lam), q) for t, q in blocks]
    return rates


def derive_physiology(profile: ExposureProfile, kinetics: str = "fixed_360") -> dict:
    """Integrate from the declared initial state through history, plateau and return.

    Source workload models apply to preparation through arrival only. The subsequent
    diagnostic trajectory uses a fixed 360-minute half-time for those source routes.
    No trajectory feature is a fitted mapping to clinical probability.
    """
    if kinetics not in {"fixed_360", "nasa_2020", "nasa_2004_nm", "nasa_2004_rm"}:
        raise ValueError("unknown nitrogen kinetics")
    timeline = profile.history.segments + profile.segments
    prep = []
    for segment in profile.segments:
        if segment.phase == "plateau":
            break
        if segment.phase != "residence":
            prep.append(segment)
    rates = _preparation_rates(profile, prep, kinetics)
    assumptions = ["Equilibrium at the declared starting pressure and gas."] if (
        profile.initial_state.method == "assumed_equilibrium"
    ) else []
    missing = []
    tissue = _initial_tissue(profile, kinetics, assumptions, missing)
    nitrogen_start = tissue
    max_ratio, dose = 0.0, 0.0
    trajectory, plateaus = [], []
    previous_plateau = False
    complete = tissue is not None
    scale = SECONDS_PER_UNIT[profile.time_unit]
    for s in timeline:
        prior = s.end <= 0
        secs = (s.end-s.start)*scale
        p0, p1 = s.start_pressure.pascals(), s.end_pressure.pascals()
        initial = tissue
        fraction = _nitrogen_fraction(s.gas, kinetics)
        end_fraction = _nitrogen_fraction(s.end_gas or s.gas, kinetics)
        blocks = rates.get(s.id, [(secs / 60.0, FIXED_RATE, None)])
        if fraction is None or end_fraction is None:
            missing.append(f"segments.{s.id}.gas")
        if blocks is None:
            missing.append(f"segments.{s.id}.activity")
        point_peak, point_dose, elapsed = 0.0, 0.0, 0.0
        if tissue is not None and fraction is not None and end_fraction is not None and blocks is not None:
            for minutes, rate, _ in blocks:
                u0 = elapsed/secs
                a = p0 + (p1-p0)*u0
                elapsed += minutes*60
                u1 = elapsed/secs
                b = p0 + (p1-p0)*u1
                pressure_offset = s.breathing_overpressure_pa
                f0 = fraction + (end_fraction-fraction)*u0
                f1 = fraction + (end_fraction-fraction)*u1
                target0, target1 = f0*(a+pressure_offset), f1*(b+pressure_offset)
                if (kinetics != "fixed_360" and is_source_air(s.gas) and is_source_air(s.end_gas or s.gas)
                        and is_sea_level(a) and is_sea_level(b) and pressure_offset == 0):
                    target0 = target1 = (11.61 if kinetics == "nasa_2020" else 11.6)*PA_PER_PSIA
                ramp = Ramp(tissue, a, b, target0, target1, minutes*60, rate/60, (b-a)*(f1-f0))
                tissue, peak, integral = ramp.metrics()
                point_peak = max(point_peak, peak)
                point_dose += integral
            if not prior:
                max_ratio = max(max_ratio, point_peak)
                dose += point_dose
        else:
            tissue, point_peak, point_dose = None, None, None
            complete = False
        row = {"segment_id": s.id, "phase": s.phase, "start_seconds": s.start*scale,
               "end_seconds": s.end*scale, "start_pressure_pa": p0, "end_pressure_pa": p1,
               "start_nitrogen_pa": initial, "end_nitrogen_pa": tissue,
               "maximum_tissue_ratio": point_peak, "supersaturation_dose_pa_s": point_dose,
               "rate_blocks": ([{"duration_minutes": t, "rate_per_minute": r,
                                 "source_vo2_ml_kg_min": q} for t, r, q in blocks]
                               if blocks is not None else None)}
        trajectory.append(row)
        if not prior and s.phase == "plateau":
            if not previous_plateau:
                plateaus.append({"segment_id": s.id, "arrival_seconds": s.start*scale,
                                 "arrival_nitrogen_pa": initial, "arrival_pressure_pa": p0})
            plateaus[-1].update(exit_seconds=s.end*scale, exit_nitrogen_pa=tissue)
            previous_plateau = True
        else:
            previous_plateau = False
    plateau = plateaus[0] if plateaus else {}
    if not complete:
        status = "partial" if any(r["start_nitrogen_pa"] is not None for r in trajectory) else "unavailable"
    else:
        status = "available_under_declared_assumptions"
    return {
        "status": status, "kinetics": kinetics, "pressure_conversion": PRESSURE_CONVERSION,
        "gas_convention": ("declared-basis N2 only" if kinetics == "fixed_360"
                           else "source dry ambient N2 equivalent"),
        "post_arrival_kinetics": "fixed_360", "metric_window": "profile_start_to_profile_end",
        "assumptions": assumptions, "missing_inputs": missing, "initial_nitrogen_pa": nitrogen_start,
        "arrival_nitrogen_pa": plateau.get("arrival_nitrogen_pa"),
        "arrival_pressure_pa": plateau.get("arrival_pressure_pa"),
        "plateau_exit_nitrogen_pa": plateau.get("exit_nitrogen_pa"),
        "maximum_tissue_ratio": max_ratio if complete else None,
        "supersaturation_dose_pa_s": dose if complete else None,
        "plateaus": plateaus, "trajectory": trajectory,
    }
