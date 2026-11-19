import io
import json
import zipfile
from hashlib import sha256
from importlib.metadata import version

import joblib
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from tinydcs.api import app
from tinydcs.label_bundle import LabelInput


def make_bundle(path, enabled, full_support):
    rows = [LabelInput(altitude_ft=26000, prebreathing_min=30, time_at_altitude_min=60,
                       exercise_level=level).model_dump() for level in ["Rest", "Mild", "Heavy"]]
    encoder = ColumnTransformer([("work", OneHotEncoder(), ["exercise_level"])], remainder="passthrough")
    pipe = Pipeline([("inputs", encoder), ("model", DummyRegressor(strategy="constant", constant=.2))])
    pipe.fit(pd.DataFrame(rows), [.1, .2, .3])
    buffer = io.BytesIO()
    joblib.dump(pipe, buffer)
    interval = dict(method="split_conformal_profile_max_abs", confidence=.9, q=1 if full_support else .1,
                    n_calibration_profiles=2 if full_support else 19, rank=3 if full_support else 18,
                    full_support=full_support)
    deps = {"scikit-learn": version("scikit-learn")}
    experiment = dict(model_id="workbook-label-v1", selected_model="test constant",
                      target_type="unverified_probability_label", target_units="fraction", endpoint="test label")
    report = dict(**experiment, calibration=interval, clinical_probability_available=False, final_test={"fixture": True})
    members = {"pipeline.joblib": buffer.getvalue(), "report.json": json.dumps(report).encode(),
               "calibration.json": json.dumps({"interval": interval}).encode(),
               "dependency-lock.json": json.dumps(deps).encode(), "model-card.md": b"test fixture",
               "data-card.md": b"test fixture", "data-audit.json": b"{}", "analysis-plan.json": b"{}",
               "splits.json": b"{}", "final-predictions.json": b"[]"}
    manifest = {
        **experiment, "model_version": "1.0.0", "schema_version": "1.0.0", "core_version": "1.0.0",
        "clinical_available": False, "operational_use": False, "label_output_enabled": enabled,
        "probability_calibration": None,
        "feature_names": list(LabelInput.model_fields), "exercise_levels": ["Rest", "Mild", "Heavy"],
        "dependencies": deps,
        "members_sha256": {k: sha256(v).hexdigest() for k, v in members.items()},
        "support_profiles": [dict(altitude_ft=26000, prebreathing_min=30, exercise_level=row["exercise_level"],
                                  times_min=[60]) for row in rows],
        "interval": interval,
    }
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
        archive.writestr("manifest.json", json.dumps(manifest))
    return rows, sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize(("enabled", "full_support"), [(True, False), (True, True), (False, False)])
def test_frozen_bundle_eligibility_interval_and_provenance(tmp_path, monkeypatch, enabled, full_support):
    path = tmp_path / "experiment.dcsbundle"
    rows, digest = make_bundle(path, enabled, full_support)
    monkeypatch.setenv("TINYDCS_LABEL_BUNDLE", str(path))
    monkeypatch.setenv("TINYDCS_LABEL_BUNDLE_SHA256", digest)
    client = TestClient(app)
    endpoint = "/api/v3/workbook/predict"
    for row in rows:
        response = client.post(endpoint, json=row)
        assert response.status_code == 200, response.text
        result = response.json()
        assert result["artifact_hash"] == digest
        assert result["inputs"] == row and len(result["input_fingerprint"]) == 64
        assert result["clinical_probability_fraction"] is None
        assert result["quantitative_output_enabled"] is enabled
        if enabled:
            assert result["predicted_label_fraction"] == .2
            bounds = result["uncertainty"]
            assert [bounds["lower"], bounds["upper"]] == pytest.approx([0, 1] if full_support else [.1, .3])
        else:
            assert result["predicted_label_fraction"] is None and result["uncertainty"]["lower"] is None
    unsupported = client.post(endpoint, json={**rows[0], "altitude_ft": 26001}).json()
    assert unsupported["predicted_label_fraction"] is None
    assert "OUTSIDE_EVALUATED_SUPPORT" in unsupported["applicability"]["reasons"]
    assert client.post(endpoint, json={**rows[0], "exercise_level": "other"}).status_code == 422
    assert client.get("/api/v3/workbook/evaluation").json()["report"]["final_test"] == {"fixture": True}
    monkeypatch.setenv("TINYDCS_LABEL_BUNDLE_SHA256", "0" * 64)
    assert client.get("/api/v3/workbook/evaluation").status_code == 503
    monkeypatch.delenv("TINYDCS_LABEL_BUNDLE_SHA256")
    assert client.post(endpoint, json=rows[0]).status_code == 503
