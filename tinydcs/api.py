"""FastAPI contract for TinyDCS EVA scenario simulation."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from tinydcs.eva import (
    MODEL_VERSION,
    RutReconciliationStatus,
    available_mission_rule_profiles,
    load_mission_rules,
    simulation_response,
)
from tinydcs.eva_reports import report_artifacts


class HabitatAtmosphere(BaseModel):
    pressurePsia: float
    oxygenFraction: float
    equilibrationHours: float


class SuitProfile(BaseModel):
    pressurePsia: float
    oxygenFraction: float
    variablePressure: bool
    plssDurationMin: float
    oxygenReserveMin: float
    co2ScrubberMargin: float
    coolingMargin: float
    suitPort: bool


class EVAWorkloadBlock(BaseModel):
    name: str
    durationMin: float
    vo2MlKgMin: float


class EVAEnvironment(BaseModel):
    dustLevel: float
    sunExposure: float
    commDelaySec: float
    radiationWeather: Literal["quiet", "elevated", "storm"]
    shelterReturnMin: float


class EVACrewState(BaseModel):
    ageYears: float
    sex: Literal["Male", "Female"]
    massKg: float
    spo2Percent: float
    hydration: float
    symptomFlag: bool


class EVAScenario(BaseModel):
    id: str
    kind: Literal[
        "scenario_a_commercial_standup",
        "scenario_b_artemis_lunar_day",
        "scenario_c_habitat_pressure_decision",
    ]
    name: str
    shortName: str
    summary: str
    habitat: HabitatAtmosphere
    prebreatheProtocol: Literal["iss_four_hour", "campout", "exploration_atmosphere", "custom"]
    prebreatheMin: float
    prebreatheOxygenFraction: float
    suit: SuitProfile
    evaDurationMin: float
    meanVo2MlKgMin: float
    peakVo2MlKgMin: float
    workload: list[EVAWorkloadBlock]
    environment: EVAEnvironment
    crew: EVACrewState
    evidence: list[str] = Field(default_factory=list)


class TelemetrySample(BaseModel):
    kind: str
    value: float | None = None
    unit: str | None = None
    source: str | None = None
    confidence: float = 1.0
    timestampSec: float | None = None
    x: float | None = None
    y: float | None = None
    z: float | None = None


class EVASimulationRequest(BaseModel):
    scenario: EVAScenario
    missionRuleProfile: str = "default"
    telemetry: list[TelemetrySample] = Field(default_factory=list)


class EVAReportRequest(BaseModel):
    scenario: EVAScenario
    result: dict[str, Any] | None = None
    missionRuleProfile: str = "default"
    telemetry: list[TelemetrySample] = Field(default_factory=list)


class EVASimulationResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    scenarioId: str
    missionRuleProfile: str
    generatedAt: str
    modelMetadata: dict[str, Any]
    missionRules: dict[str, Any]
    result: dict[str, Any]


class EVAReportResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    reportId: str
    generatedAt: str
    artifacts: dict[str, dict[str, str]]


app = FastAPI(
    title="TinyDCS EVA API",
    version=MODEL_VERSION,
    description="Research-use EVA DCS scenario simulation API for frontend and planning-report integration.",
)


@app.post("/api/v1/eva/simulate", response_model=EVASimulationResponse)
def simulate_eva_endpoint(request: EVASimulationRequest) -> dict[str, Any]:
    try:
        return simulation_response(
            request.scenario.model_dump(),
            mission_rule_profile=request.missionRuleProfile,
            telemetry=[sample.model_dump(exclude_none=True) for sample in request.telemetry],
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v1/eva/report", response_model=EVAReportResponse)
def report_eva_endpoint(request: EVAReportRequest) -> dict[str, Any]:
    try:
        response = simulation_response(
            request.scenario.model_dump(),
            mission_rule_profile=request.missionRuleProfile,
            telemetry=[sample.model_dump(exclude_none=True) for sample in request.telemetry],
        )
        if request.result is not None:
            response["result"] = request.result
        return report_artifacts(response)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/v1/eva/mission-rules/{profile}")
def get_mission_rules(profile: str) -> dict[str, Any]:
    try:
        return load_mission_rules(profile)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/v1/eva/model-metadata")
def get_model_metadata() -> dict[str, Any]:
    return {
        "modelVersion": MODEL_VERSION,
        "researchUseOnly": True,
        "supportedScenarioKinds": [
            "scenario_a_commercial_standup",
            "scenario_b_artemis_lunar_day",
            "scenario_c_habitat_pressure_decision",
        ],
        "missionRuleProfiles": available_mission_rule_profiles(),
        "rutReconciliation": RutReconciliationStatus().to_dict(),
    }
