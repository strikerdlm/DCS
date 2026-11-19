"""Cross-surface fixtures for the aviation form and source routing."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tinydcs.api import app
from tinydcs.aviation_models import evaluate
from tinydcs.exposure import ExposureProfile


def test_website_example_routes_identically_in_python_and_http():
    path = Path(__file__).resolve().parents[1] / "docs/examples/aviation-table5.json"
    raw = json.loads(path.read_text())
    client = TestClient(app)
    response = client.post("/api/v3/aviation/evaluate", json=raw)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result == evaluate(ExposureProfile.model_validate(raw))
    assert result["model_id"] == "conkin_1996_eq7"
    assert result["probability_fraction"] == pytest.approx(.03, abs=.003)
    assert result["evidence_class"] == "published_reference"
    assert len(result["input_fingerprint"]) == 64
    assert result["quantitative_output_enabled"]
    assert result["physiology"]["arrival_nitrogen_pa"] != result["physiology"]["plateau_exit_nitrogen_pa"]
    assert client.get("/api/v3/aviation/models").status_code == 200


def test_compatibility_switch_is_visible_at_five_psia():
    client = TestClient(app)
    base = dict(elapsedPlateauHours=4, depressurizationMinutes=15, singleConstantPlateau=True,
                arrivalTissueN2Psia=7.5, ambulationAtPlateau=True, bmiKgM2=24,
                sourceRepressurizationProtocol=False, maleReferenceCohort=True)
    for pressure, model, expected in [(5, "NASA-2020-Eq4", 8.261463),
                                      (5.000001, "Conkin-1996-Eq7", 11.350402)]:
        data = client.post("/api/v2/hypobaric/probability", json={**base, "plateauPressurePsia": pressure}).json()
        assert data["model"] == model
        assert data["pDcsPercent"] == pytest.approx(expected, abs=.000001)
