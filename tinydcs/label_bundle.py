"""Load a locally configured, digest-pinned workbook experiment and its evaluation.

The producer is DCS-model-with-Machine-Learning. Only an administrator-supplied
archive may be loaded: joblib is executable serialization. HTTP clients supply
four profile fields and have no control over the archive or its expected hash.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import re
import zipfile
from importlib.metadata import version
from pathlib import Path
from pickle import UnpicklingError
from typing import Literal

import joblib
import numpy as np
import pandas as pd
from pydantic import Field
from sklearn.pipeline import Pipeline

from tinydcs.eva_contract import ScientificInput
from tinydcs.exposure import CORE_VERSION, SCHEMA_VERSION

_EXPERIMENT_FILES = {
    "pipeline.joblib", "report.json", "calibration.json", "splits.json", "final-predictions.json",
    "analysis-plan.json", "dependency-lock.json", "data-audit.json", "data-card.md", "model-card.md",
}


class LabelInput(ScientificInput):
    altitude_ft: float = Field(ge=0)
    prebreathing_min: float = Field(ge=0)
    time_at_altitude_min: float = Field(ge=0)
    exercise_level: Literal["Rest", "Mild", "Heavy"]


class _SupportProfile(ScientificInput):
    altitude_ft: float = Field(ge=0)
    prebreathing_min: float = Field(ge=0)
    exercise_level: Literal["Rest", "Mild", "Heavy"]
    times_min: list[float] = Field(min_length=1)


class _Interval(ScientificInput):
    method: Literal["split_conformal_profile_max_abs"]
    confidence: float = Field(gt=0, lt=1)
    q: float = Field(ge=0, le=1)
    n_calibration_profiles: int = Field(gt=0)
    rank: int = Field(gt=0)
    full_support: bool


class BundleError(ValueError):
    """The configured artifact cannot be used with this reader."""


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class LabelBundle:
    def __init__(self, manifest, report, pipeline, digest, support, interval):
        self.manifest = manifest
        self.report = report
        self.artifact_hash = digest
        self._pipeline = pipeline
        self._support = support
        self._interval = interval

    def predict(self, inputs: LabelInput) -> dict:
        raw = inputs.model_dump()
        fingerprint = _sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode())
        reasons = []
        if self.manifest["label_output_enabled"] is not True:
            reasons.append("LABEL_RELEASE_DISABLED")
        key = (inputs.altitude_ft, inputs.prebreathing_min, inputs.time_at_altitude_min, inputs.exercise_level)
        if key not in self._support:
            reasons.append("OUTSIDE_EVALUATED_SUPPORT")
        point = None
        interval = self._interval
        bounds = {"status": "unavailable", "method": None, "level": None, "lower": None, "upper": None}
        if not reasons:
            values = np.asarray(self._pipeline.predict(pd.DataFrame([raw])), dtype=float)
            if values.shape != (1,) or not math.isfinite(values[0]) or not 0 <= values[0] <= 1:
                raise BundleError("The fitted predictor returned an invalid label fraction.")
            point = float(values[0])
            bounds = {
                "status": "available", "method": interval.method, "level": interval.confidence,
                "lower": 0.0 if interval.full_support else max(0.0, point - interval.q),
                "upper": 1.0 if interval.full_support else min(1.0, point + interval.q),
            }
        return {
            "schema_version": SCHEMA_VERSION, "core_version": CORE_VERSION,
            "model_id": self.manifest["model_id"], "model_version": self.manifest["model_version"],
            "evidence_class": "unverified_probability_labels", "target_type": self.manifest["target_type"],
            "artifact_hash": self.artifact_hash, "input_fingerprint": fingerprint, "inputs": raw,
            "endpoint": self.manifest["endpoint"], "horizon_minutes": inputs.time_at_altitude_min,
            "predicted_label_fraction": point, "clinical_probability_fraction": None,
            "quantitative_output_enabled": not reasons,
            "applicability": {"status": "unsupported" if reasons else "supported", "reasons": reasons},
            "uncertainty": bounds, "clinical_output_enabled": False,
        }


def load_bundle(path: str | Path, expected_sha256: str) -> LabelBundle:
    """Verify the expected SHA-256 *before* reading any persisted estimator."""
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256 or ""):
        raise BundleError("A trusted SHA-256 digest is required.")
    content = Path(path).read_bytes()
    digest = _sha256(content)
    if digest != expected_sha256.lower():
        raise BundleError("Workbook bundle SHA-256 mismatch.")
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise BundleError("Duplicate bundle member names.")
            manifest = json.loads(archive.read("manifest.json"))
            members = manifest["members_sha256"]
            if set(members) != set(names) - {"manifest.json"} or not _EXPERIMENT_FILES <= set(members):
                raise BundleError("Incomplete bundle integrity manifest.")
            payload = {name: archive.read(name) for name in members}
            if any(_sha256(data) != members[name] for name, data in payload.items()):
                raise BundleError("A bundle member failed its integrity check.")
        if (manifest["schema_version"] != SCHEMA_VERSION or manifest["core_version"] != CORE_VERSION
                or manifest["model_id"] != "workbook-label-v1" or not manifest["model_version"]
                or manifest["target_type"] != "unverified_probability_label"
                or manifest["target_units"] != "fraction" or not manifest["endpoint"]
                or manifest["clinical_available"] is not False or manifest["operational_use"] is not False
                or type(manifest["label_output_enabled"]) is not bool
                or manifest["feature_names"] != list(LabelInput.model_fields)
                or manifest["exercise_levels"] != ["Rest", "Mild", "Heavy"]):
            raise BundleError("Unsupported workbook contract or release declaration.")
        if manifest["dependencies"]["scikit-learn"] != version("scikit-learn"):
            raise BundleError("Install the scikit-learn version pinned by the experiment.")
        interval = _Interval.model_validate(manifest["interval"])
        rank = math.ceil((interval.n_calibration_profiles + 1) * interval.confidence)
        if interval.rank != rank or interval.full_support != (rank > interval.n_calibration_profiles):
            raise BundleError("Inconsistent profile calibration rank.")
        support = set()
        for row in manifest["support_profiles"]:
            profile = _SupportProfile.model_validate(row)
            for t in profile.times_min:
                if t < 0:
                    raise BundleError("Invalid exposure duration in the workbook support grid.")
                support.add((profile.altitude_ft, profile.prebreathing_min, t, profile.exercise_level))
        report = json.loads(payload["report.json"])
        if (not support or not isinstance(report, dict) or not report.get("final_test")
                or any(report.get(key) != manifest[key]
                       for key in ("model_id", "selected_model", "target_type", "target_units", "endpoint"))
                or report.get("clinical_probability_available") is not False
                or report.get("calibration") != manifest["interval"]
                or json.loads(payload["calibration.json"])["interval"] != manifest["interval"]
                or json.loads(payload["dependency-lock.json"]) != manifest["dependencies"]
                or manifest["probability_calibration"] is not None):
            raise BundleError("Workbook evaluation or calibration disagrees with its manifest.")
        pipeline = joblib.load(io.BytesIO(payload["pipeline.joblib"]))
        if (not isinstance(pipeline, Pipeline)
                or list(getattr(pipeline, "feature_names_in_", [])) != manifest["feature_names"]):
            raise BundleError("Fitted pipeline input fields disagree with its manifest.")
    except BundleError:
        raise
    except (OSError, EOFError, KeyError, ValueError, TypeError, AttributeError,
            ImportError, UnpicklingError, zipfile.BadZipFile) as exc:
        raise BundleError("Invalid or incompatible workbook bundle.") from exc
    return LabelBundle(manifest, report, pipeline, digest, frozenset(support), interval)
