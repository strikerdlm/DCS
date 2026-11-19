"""Versioned, prospective aviation pressure histories. Public quantities use declared units."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import date
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from mechanistic.atmosphere import KPA_PER_PSIA, altitude_ft_to_atm
from tinydcs.eva_contract import ScientificInput

SCHEMA_VERSION = CORE_VERSION = "1.0.0"
PRESSURE_CONVERSION = "US-Standard-Atmosphere-1976-0-to-20-km/v1"
PA_PER_PSIA = KPA_PER_PSIA * 1000
PA_PER_UNIT = {"Pa": 1.0, "kPa": 1000.0, "psia": PA_PER_PSIA,
               "atm": 101325.0, "mmHg": 101325.0 / 760.0}
SECONDS_PER_UNIT = {"s": 1.0, "min": 60.0, "h": 3600.0}
Text = Annotated[str, Field(min_length=1, max_length=500, pattern=r"\S")]
Fraction = Annotated[float, Field(ge=0, le=1)]
Positive = Annotated[float, Field(gt=0)]
Nonnegative = Annotated[float, Field(ge=0)]


class Pressure(ScientificInput):
    kind: Literal["absolute", "pressure_altitude", "suit_differential"]
    value: float
    unit: Literal["Pa", "kPa", "psia", "atm", "mmHg", "ft", "m"]
    ambient: Pressure | None = None

    @model_validator(mode="after")
    def check_definition(self):
        if self.kind == "pressure_altitude":
            if self.unit not in {"m", "ft"} or self.ambient is not None:
                raise ValueError("pressure altitude requires a length unit without ambient pressure")
        elif self.unit not in PA_PER_UNIT:
            raise ValueError("pressure requires an absolute or differential pressure unit")
        elif self.kind == "suit_differential":
            if self.value < 0 or self.ambient is None or self.ambient.kind == "suit_differential":
                raise ValueError("suit differential requires a nonnegative value and absolute ambient")
        elif self.value <= 0 or self.ambient is not None:
            raise ValueError("absolute pressure must be positive and excludes an additional ambient")
        pa = self.pascals()
        if not math.isfinite(pa) or not 2e12/sys.float_info.max <= pa <= 1e12:
            raise ValueError("normalized pressure exceeds the finite tissue-ratio calculation range")
        return self

    def pascals(self) -> float:
        if self.kind == "pressure_altitude":
            feet = self.value if self.unit == "ft" else self.value / 0.3048
            return 101325.0 * float(altitude_ft_to_atm(feet))
        pressure = self.value * PA_PER_UNIT[self.unit]
        if self.ambient is not None:
            pressure += self.ambient.pascals()
        return pressure


class Gas(ScientificInput):
    oxygen_fraction: Fraction
    nitrogen_fraction: Fraction
    argon_fraction: Fraction = 0
    other_inert_fraction: Fraction = 0
    water_fraction: Fraction = 0
    basis: Literal["dry", "wet"]
    delivery_method: Text | None = None
    delivery_uncertainty: Text | None = None

    @model_validator(mode="after")
    def check_fractions(self):
        total = math.fsum((self.oxygen_fraction, self.nitrogen_fraction, self.argon_fraction,
                           self.other_inert_fraction, self.water_fraction))
        if not math.isclose(total, 1.0, rel_tol=0, abs_tol=1e-8):
            raise ValueError("declared gas fractions must sum to one")
        if self.basis == "dry" and self.water_fraction:
            raise ValueError("water cannot be a component of dry-basis fractions")
        return self


class Activity(ScientificInput):
    type: Literal["rest", "exercise", "warmup", "recovery", "absolute_work", "ambulatory",
                  "simulated_eva", "unknown"]
    ambulation: bool | None = None
    vo2_ml_kg_min: Annotated[float, Field(ge=0, le=200)] | None = None
    vo2_l_min: Nonnegative | None = None
    percent_vo2_peak: Annotated[float, Field(ge=0, le=150)] | None = None
    method: Literal["measured", "estimated", "source_assigned"] | None = None
    posture: Literal["recumbent", "semi_recumbent", "seated", "standing", "unknown"] | None = None
    exercise_mode: Text | None = None

    @model_validator(mode="after")
    def check_workload(self):
        if sum(x is not None for x in (
            self.vo2_ml_kg_min, self.vo2_l_min, self.percent_vo2_peak
        )) > 1:
            raise ValueError("declare oxygen consumption once, in a single unit")
        if self.type == "ambulatory" and self.ambulation is False:
            raise ValueError("ambulatory activity conflicts with ambulation=false")
        return self

    def workload(self, person: PersonCovariates) -> float | None:
        if self.vo2_ml_kg_min is not None:
            return self.vo2_ml_kg_min
        if self.vo2_l_min is not None and person.mass_kg is not None:
            return 1000.0 * self.vo2_l_min / person.mass_kg
        if self.percent_vo2_peak is not None and person.vo2_peak_ml_kg_min is not None:
            return self.percent_vo2_peak / 100.0 * person.vo2_peak_ml_kg_min
        return None


class PersonCovariates(ScientificInput):
    age_years: Positive | None = None
    bmi_kg_m2: Positive | None = None
    source_sex: Literal["male", "female", "unknown"] | None = None
    mass_kg: Positive | None = None
    vo2_peak_ml_kg_min: Annotated[float, Field(gt=0, le=200)] | None = None
    vo2_peak_method: Literal["measured", "estimated"] | None = None
    vo2_peak_test_date: str | None = None
    measurement_date: str | None = None
    provenance: Text | None = None

    @field_validator("vo2_peak_test_date", "measurement_date")
    @classmethod
    def iso_date(cls, value):
        if value is not None:
            date.fromisoformat(value)
        return value


class InitialState(ScientificInput):
    method: Literal["assumed_equilibrium", "measured", "history_derived", "unknown"]
    body_pressure: Pressure
    gas: Gas | None
    provenance: Text
    history_duration_minutes: Nonnegative | None = None
    tissue_nitrogen_pa: Nonnegative | None = None
    tissue_convention: Literal["declared_nitrogen", "source_dry_nitrogen"] | None = None
    uncertainty: Text | None = None

    @model_validator(mode="after")
    def check_tissue(self):
        if (self.tissue_nitrogen_pa is None) != (self.tissue_convention is None):
            raise ValueError("an external tissue value and its gas convention must be supplied together")
        if self.tissue_nitrogen_pa is not None:
            if self.method not in {"measured", "history_derived"}:
                raise ValueError("an external tissue value requires a measured or history-derived state")
            if self.tissue_nitrogen_pa > 1e12:
                raise ValueError("external tissue pressure exceeds the calculation range")
        return self


class Segment(ScientificInput):
    id: Text
    phase: Literal["residence", "prior_exposure", "prebreathe", "oxygen_break", "recovery",
                   "ascent", "plateau", "return", "post_exposure", "purge", "transfer"]
    start: float
    end: float
    start_pressure: Pressure
    end_pressure: Pressure
    interpolation: Literal["constant", "linear_pressure"]
    gas: Gas | None
    end_gas: Gas | None = None  # If supplied, linearly interpolate fractions on this basis.
    activity: Activity | None
    provenance: Text
    timing_basis: Literal["planned", "observed"] = "planned"
    break_kind: Literal["breathing_gas", "exercise_only", "mask_to_suit", "purge"] | None = None
    breathing_overpressure_pa: Annotated[float, Field(ge=0, le=1e8)] = 0
    vehicle_geometric_altitude_m: float | None = None

    @model_validator(mode="after")
    def check_interval(self):
        if self.end <= self.start:
            raise ValueError("each segment must have positive duration")
        p0, p1 = self.start_pressure.pascals(), self.end_pressure.pascals()
        if self.interpolation == "constant" and not same_pressure(p0, p1):
            raise ValueError("constant pressure requires equal start and end absolute pressure")
        if self.end_gas is not None and (self.gas is None or self.gas.basis != self.end_gas.basis):
            raise ValueError("a gas ramp requires known start and end mixtures on the same basis")
        return self


class History(ScientificInput):
    recent_diving: bool | None = None
    previous_altitude_exposure: bool | None = None
    segments: list[Segment] = Field(default_factory=list, max_length=1000)
    provenance: Text | None = None


class PredictionRequest(ScientificInput):
    model_id: Text
    endpoint: Literal["clinically_adjudicated_dcs", "symptomatic_dcs", "vge", "grade_iv_vge",
                      "decompression_illness", "physiology"]
    prediction_origin: Literal["profile_start", "plateau_arrival", "return_to_baseline"]
    window: Literal["complete_exposure", "during_plateau", "source_post_test", "post_return",
                    "through_follow_up"]
    horizon_minutes: Positive
    reference_population: Text
    source_protocol: Text | None = None


def same_pressure(a: float, b: float) -> bool:
    """Roundoff only, including representations of the same pressure in different units."""
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-5)


class ExposureTimeline(ScientificInput):
    schema_version: Literal["1.0.0"]
    profile_id: Text
    purpose: Text
    provenance: Text
    time_unit: Literal["s", "min", "h"]
    initial_state: InitialState
    history: History = Field(default_factory=History)
    person_covariates: PersonCovariates = Field(default_factory=PersonCovariates)
    segments: list[Segment] = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def check_timeline(self):
        scale = SECONDS_PER_UNIT[self.time_unit]
        if self.segments[0].start != 0:
            raise ValueError("profile segments must begin at zero")
        if self.history.segments and self.history.segments[-1].end != 0:
            raise ValueError("preceding history must end at profile time zero")
        timeline = self.history.segments + self.segments
        if len({s.id for s in timeline}) != len(timeline):
            raise ValueError("segment IDs must be unique across history and profile")
        prior_t = timeline[0].start
        prior_pa = self.initial_state.body_pressure.pascals()
        for segment in timeline:
            if max(abs(segment.start), abs(segment.end)) * scale > 1e12:
                raise ValueError("time exceeds the calculation range of 1e12 seconds")
            if (segment.end-segment.start)*scale/60 == 0:
                raise ValueError("segment duration is below floating-point resolution")
            if not math.isclose(segment.start, prior_t, rel_tol=0, abs_tol=1e-8/scale):
                raise ValueError("out-of-order segments, gaps and overlaps are invalid")
            if not same_pressure(prior_pa, segment.start_pressure.pascals()):
                raise ValueError("an explicit transition is required between different body pressures")
            prior_t, prior_pa = segment.end, segment.end_pressure.pascals()
        return self

    def fingerprint(self) -> str:
        payload = json.dumps(self.model_dump(mode="json"), sort_keys=True,
                             ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def minutes(self, segment: Segment) -> float:
        return (segment.end - segment.start) * SECONDS_PER_UNIT[self.time_unit] / 60


class ExposureProfile(ExposureTimeline):
    prediction_request: PredictionRequest

    @model_validator(mode="after")
    def check_forecast_origin(self):
        origin = 0.0
        if self.prediction_request.prediction_origin == "plateau_arrival":
            origin = next((s.start for s in self.segments if s.phase == "plateau"), 0.0)
        elif self.prediction_request.prediction_origin == "return_to_baseline":
            origin = next((s.end for s in self.segments if s.phase == "return"), 0.0)
        if any(s.timing_basis == "observed" and s.end > origin for s in self.segments):
            raise ValueError("observations after the prediction origin cannot enter a forecast")
        return self


class ObservedExposureProfile(ExposureTimeline):
    """Retrospective actual exposure, with no prospective prediction request."""

    @model_validator(mode="after")
    def check_observed(self):
        if any(s.timing_basis != "observed" for s in self.history.segments + self.segments):
            raise ValueError("actual history and exposure segments must declare observed timing")
        return self


class OutcomeRecord(ScientificInput):
    """Separate research follow-up, never accepted by ExposureProfile or evaluate()."""

    schema_version: Literal["1.0.0"]
    profile_id: Text
    endpoint: Text
    adjudication: Text
    event: bool | None
    follow_up_minutes: Nonnegative
    onset_lower_minutes: Nonnegative | None = None
    onset_upper_minutes: Nonnegative | None = None
    censoring: Literal["none", "right", "interval", "unknown"]
    severity: Text | None = None
    treatment: Text | None = None

    @model_validator(mode="after")
    def check_onset(self):
        lo, hi = self.onset_lower_minutes, self.onset_upper_minutes
        if lo is not None or hi is not None:
            if self.event is not True or lo is None or hi is None or not lo <= hi <= self.follow_up_minutes:
                raise ValueError("onset requires an event and ordered bounds within follow-up")
        return self
