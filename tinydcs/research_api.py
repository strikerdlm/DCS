"""Shared HTTP routes for chamber outcomes and the evaluated workbook."""

from __future__ import annotations

from functools import lru_cache
import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from tinydcs.aviation_models import evaluate, model_registry
from tinydcs.chamber_outcomes import OutcomeInputs, predict_outcomes, protocols
from tinydcs.exposure import ExposureProfile
from tinydcs.label_bundle import BundleError, LabelBundle, LabelInput, load_bundle

router = APIRouter(prefix="/api/v3")


@lru_cache(maxsize=1)
def verified_bundle(path: str, digest: str) -> LabelBundle:
    return load_bundle(path, digest)


def configured_bundle() -> LabelBundle:
    path = os.getenv("TINYDCS_LABEL_BUNDLE")
    digest = os.getenv("TINYDCS_LABEL_BUNDLE_SHA256")
    if not path or not digest:
        raise HTTPException(
            503, "Configure a trusted workbook bundle and its SHA-256 digest."
        )
    try:
        return verified_bundle(path, digest)
    except (OSError, BundleError) as exc:
        raise HTTPException(
            503, "The configured workbook bundle failed verification."
        ) from exc


BundleDependency = Annotated[LabelBundle, Depends(configured_bundle)]


@router.post("/aviation/evaluate")
def evaluate_aviation(profile: ExposureProfile) -> dict:
    return evaluate(profile)


@router.get("/aviation/models")
def aviation_models() -> list[dict]:
    return model_registry()


@router.get("/hypobaric/outcomes/models")
def chamber_models() -> dict:
    return protocols()


@router.post("/hypobaric/outcomes/predict")
def chamber_predictions(inputs: OutcomeInputs) -> dict:
    return predict_outcomes(inputs)


@router.post("/workbook/predict")
def workbook_prediction(inputs: LabelInput, bundle: BundleDependency) -> dict:
    try:
        return bundle.predict(inputs)
    except BundleError as exc:
        raise HTTPException(
            503, "The fitted workbook predictor returned an invalid value."
        ) from exc


@router.get("/workbook/evaluation")
def workbook_evaluation(bundle: BundleDependency) -> dict:
    return {
        "model_id": bundle.manifest["model_id"],
        "model_version": bundle.manifest["model_version"],
        "artifact_hash": bundle.artifact_hash,
        "target_type": bundle.manifest["target_type"],
        "report": bundle.report,
    }


@router.get("/workbook/support")
def workbook_support(bundle: BundleDependency) -> dict:
    return {
        "artifact_hash": bundle.artifact_hash,
        "profiles": bundle.manifest["support_profiles"],
    }


@router.get("/workbook/coverage")
def workbook_coverage(bundle: BundleDependency) -> dict:
    return {
        "artifact_hash": bundle.artifact_hash,
        "nominal_level": bundle.manifest["interval"]["confidence"],
        "strata": bundle.coverage,
    }
