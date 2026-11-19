"""Regression checks for denominators, endpoints, holdout leakage and prospective ascertainment."""

import hashlib
import json
import sqlite3
from contextlib import closing
from copy import deepcopy

import pytest

from scripts.build_chamber_database import ROOT, build, populate
from scripts.evaluate_chamber_benchmark import assess_external, family_blocks, vge_check
from scripts.fac_chamber_registry import append, initialize
from tinydcs.study_models import GROUP, read_study


@pytest.fixture
def evidence():
    with closing(sqlite3.connect(":memory:")) as db:
        db.row_factory = sqlite3.Row
        populate(db)
        yield db


def test_source_counts_and_noninterchangeable_endpoints(evidence):
    row = evidence.execute("SELECT * FROM a1309_profile WHERE profile='PRP IV'").fetchone()
    assert (row["exposures"], row["printed_events"], row["exact_cases"]) == (69, "8.3", None)
    assert evidence.execute("SELECT count(*) FROM a1309_nasa_overlap").fetchone()[0] == 35
    assert (
        evidence.execute(
            "SELECT denominator FROM aviation_count WHERE stratum='flight'"
        ).fetchone()[0]
        is None
    )
    assert evidence.execute("SELECT count(*) FROM air_break_estimate").fetchone()[0] == 24
    assert (
        evidence.execute(
            "SELECT any_grade_vge_cases FROM nasa_test WHERE test_id='1b10.2'"
        ).fetchone()[0]
        is None
    )
    rows = evidence.execute("SELECT * FROM development_counts").fetchall()
    assert len(set(family_blocks(rows))) == 8
    assert tuple(
        evidence.execute(
            "SELECT sum(dcs_cases),sum(dcs_denominator) FROM development_counts"
        ).fetchone()
    ) == (124, 885)
    assert vge_check(evidence)["interval_nll"]["predictor"] == pytest.approx(1.1912390611)


def test_eligibility_precedes_scoring(evidence):
    model = read_study(GROUP)
    external = evidence.execute("SELECT * FROM locked_external").fetchall()
    assert len(external) == 5
    assert all(assess_external(r, model)["expected"] is None for r in external)
    # Source-compatible positive control uses the actual F1 test 2a covariates and outcomes.
    context = dict(
        source_id="nasa19",
        stratum="2a",
        endpoint="dcs",
        cases=7,
        denominator=23,
        denominator_unit="exposures",
        population_scope="nasa_chamber_research",
        window_code="nasa_test_ascertainment",
        single_protocol=True,
        plateau_min=240,
        body_pressure_psia=4.3,
        mean_tr360=1.69,
        ambulatory=True,
    )
    fit = assess_external(context, model)
    assert fit["expected"] == pytest.approx(23 * 0.2266, abs=0.002)
    assert fit["observed_to_expected"] == pytest.approx(7 / fit["expected"])
    assert assess_external({**context, "mean_tr360": 1.68}, model)["expected"] is None
    assert assess_external({**context, "plateau_min": 10}, model)["log_loss"] is None
    assert assess_external({**context, "endpoint": "grade_iv_vge"}, model)["brier"] is None


def test_database_build_is_idempotent_and_preserves_other_files(tmp_path):
    target = tmp_path / "out.sqlite"
    assert build(target) == build(target)
    other = tmp_path / "other"
    other.write_bytes(b"existing research file")
    with pytest.raises(FileExistsError):
        build(other)
    assert other.read_bytes() == b"existing research file"


def test_consecutive_registry_revisions_and_missing_followup(tmp_path):
    dbfile = tmp_path / "private.sqlite"
    initialize(dbfile)
    entry = dict(
        schema_version="fac-chamber/1",
        participant_id="P1",
        exposure_id="E1",
        chamber_session_id="S1",
        protocol_id="research",
        protocol_version="draft",
        revision=1,
        revision_reason="synthetic first entry",
        start_utc="2026-01-01T12:00:00Z",
        recorded_at_utc="2026-01-01T12:00:00Z",
        source_reference="fixture",
        source_version="v1",
        source_sha256=hashlib.sha256(b"fixture").hexdigest(),
        extraction_method="synthetic test",
    )
    planned = json.loads((ROOT / "docs/examples/aviation-table5.json").read_bytes())
    planned["prediction_request"]["prediction_origin"] = "profile_start"
    entry.update(planned=planned, planned_as_of_utc="2026-01-01T11:00:00Z")

    def enc(doc):
        return json.dumps(doc).encode()

    assert append(dbfile, enc(entry)) == "recorded"
    assert append(dbfile, enc(entry)) == "already_recorded"
    with closing(sqlite3.connect(dbfile)) as db:
        assert db.execute("SELECT count(*) FROM clinical_followup").fetchone() == (0,)
    actual = deepcopy(planned)
    del actual["prediction_request"]
    for seg in actual["segments"]:
        seg["timing_basis"] = "observed"
    observation = dict(
        endpoint="dcs",
        status="no_event_observed",
        certainty="confirmed",
        definition_version="example",
        followup_through_min=400.0,
        event_free_through_min=400.0,
        censor_min=400.0,
        ascertainment="scheduled interview",
        source_reference="fixture",
    )
    later = {
        **entry,
        "revision": 2,
        "revision_reason": "actual history and first follow-up",
        "recorded_at_utc": "2026-01-02T12:00:00Z",
        "actual": actual,
        "clinical": [observation],
        "segments": [
            dict(
                history="actual",
                segment_id=actual["segments"][0]["id"],
                mask_state="on",
                gas_basis="documented",
                workload_basis="unknown",
                source_reference="fixture",
            )
        ],
    }
    with pytest.raises(ValueError, match="event-free coverage"):
        append(
            dbfile, enc({**later, "clinical": [{**observation, "event_free_through_min": None}]})
        )
    with pytest.raises(ValueError, match="forecast is frozen"):
        append(dbfile, enc({**later, "planned": None, "planned_as_of_utc": None}))
    late_evidence = {
        **later["segments"][0],
        "history": "planned",
        "available_at_utc": later["recorded_at_utc"],
    }
    with pytest.raises(ValueError, match="available by the forecast"):
        append(dbfile, enc({**later, "segments": [late_evidence]}))
    assert append(dbfile, enc(later)) == "recorded"
    with pytest.raises(ValueError, match="conflicting"):
        append(dbfile, enc({**later, "revision_reason": "different snapshot at revision 2"}))
    with pytest.raises(FileExistsError):
        initialize(dbfile)
    with closing(sqlite3.connect(dbfile)) as db:
        assert db.execute("SELECT count(*) FROM snapshot").fetchone() == (2,)
        assert db.execute("SELECT count(*) FROM current_exposure").fetchone() == (1,)
        assert db.execute("SELECT count(*) FROM doppler_observation").fetchone() == (0,)
        assert db.execute(
            "SELECT json_extract(observation,'$.event_free_through_min') FROM clinical_followup"
        ).fetchone() == (400.0,)
