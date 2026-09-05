"""FastAPI contract for TinyDCS EVA scenario simulation."""

from __future__ import annotations

from typing import Any
import os

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from tinydcs.eva_contract import ScientificInput, EVAScenario, TelemetrySample

from tinydcs.eva import (
    MODEL_VERSION,
    RutReconciliationStatus,
    available_mission_rule_profiles,
    load_mission_rules,
    simulation_response,
)
from tinydcs.eva_reports import report_artifacts


class EVASimulationRequest(ScientificInput):
    scenario: EVAScenario
    missionRuleProfile: str = "default"
    telemetry: list[TelemetrySample] = Field(default_factory=list, max_length=5000)
    telemetryNowSec: float | None = Field(default=None, ge=0)


class EVAReportRequest(ScientificInput):
    scenario: EVAScenario
    result: dict[str, Any] | None = None
    missionRuleProfile: str = "default"
    telemetry: list[TelemetrySample] = Field(default_factory=list, max_length=5000)
    telemetryNowSec: float | None = Field(default=None, ge=0)


class EVAResult(BaseModel):
    model_config = ConfigDict(extra="allow", allow_inf_nan=False)
    schemaVersion: int
    pDcsPercent: float | None
    intervalLowPercent: float | None
    intervalHighPercent: float | None
    p1n2Psia: float
    etr: float
    modelApplicability: dict[str, Any]
    abstain: bool
    stopReasons: list[str]
    timeline: list[dict[str, Any]]
    hazards: list[dict[str, Any]]


class EVASimulationResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    scenarioId: str
    missionRuleProfile: str
    generatedAt: str
    modelMetadata: dict[str, Any]
    missionRules: dict[str, Any]
    result: EVAResult


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


app.add_middleware(CORSMiddleware,
    allow_origins=os.getenv("TINYDCS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173").split(","),
    allow_methods=["GET", "POST"], allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def invalid_input_handler(request, exc):
    # Do not echo NaN/Infinity (invalid JSON), arbitrary input or exception objects.
    return JSONResponse(status_code=422, content={"detail": [
        {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]})


@app.post("/api/v2/eva/simulate", response_model=EVASimulationResponse)
@app.post("/api/v1/eva/simulate", response_model=EVASimulationResponse, deprecated=True)
def simulate_eva_endpoint(request: EVASimulationRequest) -> dict[str, Any]:
    try:
        return simulation_response(
            request.scenario.model_dump(),
            mission_rule_profile=request.missionRuleProfile,
            telemetry=[sample.model_dump(exclude_none=True) for sample in request.telemetry],
            telemetry_now_sec=request.telemetryNowSec,
        )
    except (ValidationError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/v2/eva/report", response_model=EVAReportResponse)
@app.post("/api/v1/eva/report", response_model=EVAReportResponse, deprecated=True)
def report_eva_endpoint(request: EVAReportRequest) -> dict[str, Any]:
    try:
        response = simulation_response(
            request.scenario.model_dump(),
            mission_rule_profile=request.missionRuleProfile,
            telemetry=[sample.model_dump(exclude_none=True) for sample in request.telemetry],
            telemetry_now_sec=request.telemetryNowSec,
        )
        # Client result is accepted only for migration and NEVER trusted.
        return report_artifacts(response)
    except (ValidationError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/v2/eva/mission-rules/{profile}")
@app.get("/api/v1/eva/mission-rules/{profile}", deprecated=True)
def get_mission_rules(profile: str) -> dict[str, Any]:
    try:
        return load_mission_rules(profile)
    except (ValidationError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/v2/eva/model-metadata")
@app.get("/api/v1/eva/model-metadata", deprecated=True)
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
