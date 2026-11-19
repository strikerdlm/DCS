"""Optional Streamlit checks. Install the app extra to exercise these views."""

import json
import os
from pathlib import Path

import pytest

from tinydcs.aviation_models import evaluate
from tinydcs.exposure import ExposureProfile

testing = pytest.importorskip("streamlit.testing.v1")
ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/streamlit/app.py"
SOURCE = ROOT / "docs/examples/aviation-table5.json"


def launch():
    return testing.AppTest.from_file(str(APP), default_timeout=45).run()


def test_reference_display_matches_core_and_short_clinical_veto():
    raw = SOURCE.read_text(encoding="utf-8")
    result = evaluate(ExposureProfile.model_validate_json(raw))
    ui = launch()
    ui.button[0].click().run()
    assert not ui.exception
    values = {metric.label: metric.value for metric in ui.metric}
    assert values["Published reference probability"] == f"{result['probability_fraction']:.3%}"
    assert (
        values["Tissue nitrogen at arrival (kPa)"]
        != values["Tissue nitrogen at plateau exit (kPa)"]
    )
    assert any(result["input_fingerprint"] in line.value for line in ui.caption)
    short = json.loads(raw)
    plateau = next(s for s in short["segments"] if s["phase"] == "plateau")
    plateau["end"] = plateau["start"] + 10
    short["segments"] = short["segments"][: short["segments"].index(plateau) + 1]
    short["prediction_request"].update(
        endpoint="clinically_adjudicated_dcs",
        prediction_origin="profile_start",
        window="complete_exposure",
        horizon_minutes=10,
        reference_population="aviation",
    )
    ui.text_area[0].set_value(json.dumps(short)).run()
    assert not ui.metric
    ui.button[0].click().run()
    assert not ui.exception
    assert "COMPLETE_SHORT_PROFILE_NOT_VALIDATED" in ui.warning[0].value
    assert all(m.label != "Published reference probability" for m in ui.metric)


def test_unconfigured_workbook_and_3rut_are_unavailable(monkeypatch):
    monkeypatch.delenv("TINYDCS_LABEL_BUNDLE", raising=False)
    monkeypatch.delenv("TINYDCS_LABEL_BUNDLE_SHA256", raising=False)
    ui = launch()
    ui.sidebar.radio[0].set_value("Workbook labels").run()
    assert not ui.exception and not ui.metric
    assert "unavailable" in ui.warning[0].value
    ui.sidebar.radio[0].set_value("3RUT-MBe1").run()
    assert not ui.exception and not ui.metric
    assert "disabled" in ui.warning[0].value.lower()


@pytest.mark.skipif(
    not (os.environ.get("TINYDCS_LABEL_BUNDLE") and os.environ.get("TINYDCS_LABEL_BUNDLE_SHA256")),
    reason="optional integration with an independently supplied evaluated ML bundle",
)
def test_configured_workbook_matches_pinned_bundle():
    from tinydcs.label_bundle import LabelInput, load_bundle

    bundle = load_bundle(
        os.environ["TINYDCS_LABEL_BUNDLE"], os.environ["TINYDCS_LABEL_BUNDLE_SHA256"]
    )
    ui = launch()
    ui.sidebar.radio[0].set_value("Workbook labels").run()
    for level in ("Rest", "Mild", "Heavy"):
        ui.selectbox[0].set_value(level)
        ui.button[0].click().run()
        result = bundle.predict(
            LabelInput(
                altitude_ft=30000, prebreathing_min=0, time_at_altitude_min=60, exercise_level=level
            )
        )
        assert not ui.exception
        assert ui.metric[0].value == f"{result['predicted_label_fraction']:.2%}"
        assert any(bundle.artifact_hash in line.value for line in ui.caption)
