"""Versioned, finite-input EVA contract shared by direct Python and HTTP calls."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScientificInput(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, strict=True)


class HabitatAtmosphere(ScientificInput):
    pressurePsia: float = Field(gt=0, le=30)
    oxygenFraction: float = Field(ge=0, le=1)
    equilibrationHours: float = Field(ge=0, le=8760)


class SuitProfile(ScientificInput):
    pressurePsia: float = Field(gt=0, le=30)
    oxygenFraction: float = Field(ge=0, le=1)
    variablePressure: bool
    plssDurationMin: float = Field(ge=0, le=10080)
    oxygenReserveMin: float = Field(ge=0, le=10080)
    co2ScrubberMargin: float = Field(ge=0, le=1)
    coolingMargin: float = Field(ge=0, le=1)
    suitPort: bool


class EVAWorkloadBlock(ScientificInput):
    name: str = Field(max_length=200)
    durationMin: float = Field(gt=0, le=1440)
    vo2MlKgMin: float = Field(ge=0, le=120)


class PressureSegment(ScientificInput):
    durationMin: float = Field(gt=0, le=1440)
    pressurePsia: float = Field(gt=0, le=30)
    oxygenFraction: float = Field(ge=0, le=1)


class PrebreatheSegment(PressureSegment):
    vo2MlKgMin: float = Field(ge=0, le=120)


class EVAEnvironment(ScientificInput):
    dustLevel: float = Field(ge=0, le=1)
    sunExposure: float = Field(ge=0, le=1)
    commDelaySec: float = Field(ge=0, le=86400)
    radiationWeather: Literal["quiet", "elevated", "storm"]
    shelterReturnMin: float = Field(ge=0, le=1440)


class EVACrewState(ScientificInput):
    ageYears: float = Field(gt=0, le=120)
    sex: Literal["Male", "Female"]
    massKg: float = Field(gt=0, le=500)
    spo2Percent: float = Field(ge=0, le=100)
    hydration: float = Field(ge=0, le=1)
    symptomFlag: bool


class EVAScenario(ScientificInput):
    id: str = Field(min_length=1, max_length=200)
    kind: Literal[
        "scenario_a_commercial_standup",
        "scenario_b_artemis_lunar_day",
        "scenario_c_habitat_pressure_decision",
    ]
    name: str = Field(max_length=300)
    shortName: str = Field(max_length=200)
    summary: str = Field(max_length=5000)
    habitat: HabitatAtmosphere
    prebreatheProtocol: Literal["iss_four_hour", "campout", "exploration_atmosphere", "custom"]
    prebreatheMin: float = Field(ge=0, le=1440)
    prebreatheOxygenFraction: float = Field(ge=0, le=1)
    prebreatheVo2MlKgMin: float = Field(default=3.5, ge=0, le=120)
    prebreatheSegments: list[PrebreatheSegment] = Field(default_factory=list, max_length=100)
    suit: SuitProfile
    evaDurationMin: float = Field(ge=0, le=1440)
    meanVo2MlKgMin: float = Field(ge=0, le=120)
    peakVo2MlKgMin: float = Field(ge=0, le=120)
    workload: list[EVAWorkloadBlock] = Field(max_length=100)
    pressureSegments: list[PressureSegment] = Field(default_factory=list, max_length=100)
    nasaAdynamicReference: bool = False
    environment: EVAEnvironment
    crew: EVACrewState
    evidence: list[str] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def check_schedules(self):
        for label, blocks, duration in [
            ("workload", self.workload, self.evaDurationMin),
            ("pressure", self.pressureSegments, self.evaDurationMin),
            ("prebreathe", self.prebreatheSegments, self.prebreatheMin),
        ]:
            if blocks and abs(sum(b.durationMin for b in blocks) - duration) > 1e-6:
                raise ValueError(f"{label} segment durations must sum to the phase duration")
            if blocks:
                # Resolve accepted floating-point roundoff at the final boundary.
                remaining = duration - sum(b.durationMin for b in blocks[:-1])
                if remaining <= 0:
                    raise ValueError(f"{label} final segment must have positive duration")
                blocks[-1].durationMin = remaining
        if self.suit.variablePressure and not self.pressureSegments:
            raise ValueError("variable pressure requires an explicit pressure schedule")
        if self.peakVo2MlKgMin < self.meanVo2MlKgMin:
            raise ValueError("peak VO2 must be at least mean VO2")
        return self


class TelemetrySample(ScientificInput):
    kind: str = Field(max_length=80)
    value: float | None = None
    unit: str | None = Field(default=None, max_length=40)
    source: str | None = Field(default=None, max_length=200)
    confidence: float = Field(default=1, ge=0, le=1)
    timestampSec: float | None = Field(default=None, ge=0)
    x: float | None = None
    y: float | None = None
    z: float | None = None
