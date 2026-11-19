"""Initialize a separate prospective FAC/CEMAE register and append pseudonymous snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import tempfile
from datetime import timezone
from pathlib import Path
from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, model_validator
from scripts.build_chamber_database import publish

from tinydcs.eva_contract import ScientificInput
from tinydcs.exposure import ExposureProfile, ObservedExposureProfile, Pressure, SECONDS_PER_UNIT

Code = Annotated[str, Field(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9_./:-]+$")]
Text = Annotated[str, Field(min_length=1, max_length=500, pattern=r"\S")]
Nonnegative = Annotated[float, Field(ge=0)]
Basis = Literal["measured", "documented", "reconstructed", "assumed", "unknown"]
APP_ID = 1178682184


class SegmentEvidence(ScientificInput):
    history: Literal["planned", "actual"]
    segment_id: Code
    mask_state: Literal["on", "off", "transition", "unknown"]
    gas_basis: Basis
    task_mean_vo2_ml_kg_min: Nonnegative | None = None
    highest_1min_vo2_ml_kg_min: Nonnegative | None = None
    workload_basis: Basis = "unknown"
    source_reference: Text
    available_at_utc: AwareDatetime | None = None

    @model_validator(mode="after")
    def check_vo2(self):
        if self.workload_basis == "unknown" and (
            self.task_mean_vo2_ml_kg_min is not None or self.highest_1min_vo2_ml_kg_min is not None
        ):
            raise ValueError("a workload value requires its measurement or assignment basis")
        return self


class ClinicalObservation(ScientificInput):
    endpoint: Literal["dcs", "dci"]
    definition_version: Code
    status: Literal["event", "no_event_observed", "indeterminate"]
    certainty: Literal["confirmed", "probable", "possible", "indeterminate"]
    onset_lower_min: Nonnegative | None = None
    onset_upper_min: Nonnegative | None = None
    censor_min: Nonnegative | None = None
    followup_through_min: Nonnegative | None = None
    event_free_through_min: Nonnegative | None = None
    ascertainment: Text
    source_reference: Text

    @model_validator(mode="after")
    def check_window(self):
        lo, hi = self.onset_lower_min, self.onset_upper_min
        if (lo is None) != (hi is None) or (lo is not None and lo > hi):
            raise ValueError("onset requires ordered bounds or an explicitly unknown time")
        if lo is not None and self.status != "event":
            raise ValueError("only a clinical event can carry onset bounds")
        if self.status == "no_event_observed" and self.event_free_through_min is None:
            raise ValueError("a non-event requires documented event-free coverage")
        if any(
            v is not None and (self.followup_through_min is None or v > self.followup_through_min)
            for v in (hi, self.censor_min, self.event_free_through_min)
        ):
            raise ValueError("observation times must lie inside documented follow-up")
        if (
            lo is not None
            and self.event_free_through_min is not None
            and self.event_free_through_min > lo
        ):
            raise ValueError("event-free coverage extends into the onset interval")
        return self


class DopplerObservation(ScientificInput):
    elapsed_min: Nonnegative
    grade: Text
    scale_version: Text
    acquisition: Text
    posture_and_provocation: Text
    source_reference: Text


class Snapshot(ScientificInput):
    schema_version: Literal["fac-chamber/1"]
    participant_id: Code
    exposure_id: Code
    chamber_session_id: Code
    protocol_id: Code
    protocol_version: Code
    revision: Annotated[int, Field(ge=1)]
    revision_reason: Text
    start_utc: AwareDatetime
    recorded_at_utc: AwareDatetime
    source_reference: Text
    source_version: Code
    source_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    extraction_method: Text
    previous_exposure_id: Code | None = None
    residence_history: Text | None = None
    measured_start_pressure: Pressure | None = None
    start_pressure_instrument: Text | None = None
    planned_as_of_utc: AwareDatetime | None = None
    planned: ExposureProfile | None = None
    actual: ObservedExposureProfile | None = None
    termination_min: Nonnegative | None = None
    termination_reason: Text | None = None
    return_to_site_min: Nonnegative | None = None
    segments: list[SegmentEvidence] = Field(default_factory=list)
    clinical: list[ClinicalObservation] = Field(default_factory=list)
    doppler: list[DopplerObservation] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_evidence(self):
        if (self.measured_start_pressure is None) != (self.start_pressure_instrument is None):
            raise ValueError("a measured starting pressure requires the measuring instrument")
        if (
            self.measured_start_pressure is not None
            and self.measured_start_pressure.kind != "absolute"
        ):
            raise ValueError("measured starting pressure must be an absolute measurement")
        if (self.planned is None) != (self.planned_as_of_utc is None):
            raise ValueError("a planned profile requires its original availability timestamp")
        if self.planned_as_of_utc and self.planned_as_of_utc > min(
            self.start_utc, self.recorded_at_utc
        ):
            raise ValueError("the pre-exposure plan must be available by the exposure origin")
        if self.planned and self.planned.prediction_request.prediction_origin != "profile_start":
            raise ValueError("the registry baseline plan uses the pre-exposure prediction origin")
        if self.previous_exposure_id == self.exposure_id:
            raise ValueError("an exposure cannot precede itself")
        if (self.termination_min is None) != (self.termination_reason is None):
            raise ValueError("termination requires both a time and a reason")
        observed_minutes = [self.termination_min, self.return_to_site_min]
        if self.actual is not None:
            observed_minutes.append(
                self.actual.segments[-1].end * SECONDS_PER_UNIT[self.actual.time_unit] / 60
            )
        for observation in self.clinical:
            observed_minutes.append(observation.followup_through_min)
        observed_minutes.extend(d.elapsed_min for d in self.doppler)
        as_of = (self.recorded_at_utc - self.start_utc).total_seconds() / 60
        if any(v is not None and v > as_of for v in observed_minutes):
            raise ValueError("actual observations cannot extend beyond the snapshot timestamp")
        keys = set()
        for detail in self.segments:
            profile = self.planned if detail.history == "planned" else self.actual
            segments = [] if profile is None else profile.history.segments + profile.segments
            if sum(s.id == detail.segment_id for s in segments) != 1:
                raise ValueError("mask and workload evidence must identify one recorded segment")
            key = (detail.history, detail.segment_id)
            if key in keys:
                raise ValueError("duplicate segment evidence")
            keys.add(key)
            if detail.history == "planned" and (
                detail.available_at_utc is None or detail.available_at_utc > self.planned_as_of_utc
            ):
                raise ValueError(
                    "planned segment evidence must be available by the forecast timestamp"
                )
            if (
                detail.available_at_utc is not None
                and detail.available_at_utc > self.recorded_at_utc
            ):
                raise ValueError("segment evidence must be available by the snapshot timestamp")
        return self


SCHEMA = """
CREATE TABLE exposure (
    enrollment_no INTEGER PRIMARY KEY, exposure_id TEXT NOT NULL UNIQUE,
    participant_id TEXT NOT NULL, start_utc TEXT NOT NULL
) STRICT;
CREATE TABLE snapshot (
    exposure_id TEXT REFERENCES exposure(exposure_id), revision INTEGER NOT NULL CHECK(revision>0),
    recorded_at_utc TEXT NOT NULL, source_sha256 TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
    submitted_sha256 TEXT NOT NULL,
    document TEXT NOT NULL CHECK(json_valid(document)), PRIMARY KEY(exposure_id,revision)
) STRICT;
CREATE VIEW current_exposure AS
    SELECT e.enrollment_no,e.participant_id,e.start_utc,s.* FROM exposure e JOIN snapshot s USING(exposure_id)
    WHERE s.revision=(SELECT max(p.revision) FROM snapshot p WHERE p.exposure_id=e.exposure_id);
CREATE VIEW clinical_followup AS
    SELECT e.exposure_id,e.revision,j.value AS observation
    FROM current_exposure e,json_each(e.document,'$.clinical') j;
CREATE VIEW doppler_observation AS
    SELECT e.exposure_id,e.revision,j.value AS observation
    FROM current_exposure e,json_each(e.document,'$.doppler') j;
CREATE TRIGGER snapshot_no_update BEFORE UPDATE ON snapshot
    BEGIN SELECT RAISE(ABORT,'append a new exposure revision'); END;
CREATE TRIGGER snapshot_no_delete BEFORE DELETE ON snapshot
    BEGIN SELECT RAISE(ABORT,'exposure revisions form an append-only history'); END;
"""


def initialize(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=path.parent) as folder:
        temp = Path(folder) / "registry.sqlite"
        db = sqlite3.connect(temp)
        try:
            db.executescript(f"PRAGMA application_id={APP_ID}; PRAGMA user_version=1;" + SCHEMA)
        finally:
            db.close()
        publish(temp, path, allow_identical=False)


def append(path, raw):
    entry = Snapshot.model_validate_json(raw)
    doc = json.dumps(
        entry.model_dump(mode="json"),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(doc.encode("utf-8")).hexdigest()
    start = entry.start_utc.astimezone(timezone.utc).isoformat(timespec="microseconds")
    recorded = entry.recorded_at_utc.astimezone(timezone.utc).isoformat(timespec="microseconds")
    db = sqlite3.connect(path.resolve().as_uri() + "?mode=rw", uri=True)
    try:
        if db.execute("PRAGMA application_id").fetchone()[0] != APP_ID:
            raise ValueError("selected file is not a FAC chamber registry")
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("BEGIN IMMEDIATE")
        existing = db.execute(
            "SELECT payload_sha256 FROM snapshot WHERE exposure_id=? AND revision=?",
            (entry.exposure_id, entry.revision),
        ).fetchone()
        if existing == (digest,):
            return "already_recorded"
        if existing:
            raise ValueError("conflicting content for an existing revision")
        previous = db.execute(
            "SELECT participant_id,start_utc,revision,recorded_at_utc,document FROM current_exposure "
            "WHERE exposure_id=?",
            (entry.exposure_id,),
        ).fetchone()
        if previous:
            if previous[:2] != (entry.participant_id, start):
                raise ValueError(
                    "participant and exposure origin must match the original registration"
                )
            if entry.revision != previous[2] + 1 or recorded < previous[3]:
                raise ValueError("append the next revision in chronological order")
            prior = json.loads(previous[4])
            if prior["planned"] is not None:
                current = json.loads(doc)
                if any(prior[key] != current[key] for key in ("planned", "planned_as_of_utc")):
                    raise ValueError("the original pre-exposure forecast is frozen")
                original_segments = [s for s in prior["segments"] if s["history"] == "planned"]
                revised_segments = [s for s in current["segments"] if s["history"] == "planned"]
                if revised_segments != original_segments:
                    raise ValueError("the segment evidence for the pre-exposure forecast is frozen")
        elif entry.revision == 1:
            db.execute(
                "INSERT INTO exposure(exposure_id,participant_id,start_utc) VALUES (?,?,?)",
                (entry.exposure_id, entry.participant_id, start),
            )
        else:
            raise ValueError("the first exposure snapshot must be revision 1")
        if entry.previous_exposure_id:
            linked = db.execute(
                "SELECT participant_id,start_utc FROM exposure WHERE exposure_id=?",
                (entry.previous_exposure_id,),
            ).fetchone()
            if not linked or linked[0] != entry.participant_id or linked[1] >= start:
                raise ValueError(
                    "the preceding exposure must belong to the same person and precede this one"
                )
        db.execute(
            "INSERT INTO snapshot VALUES (?,?,?,?,?,?,?)",
            (
                entry.exposure_id,
                entry.revision,
                recorded,
                entry.source_sha256,
                digest,
                hashlib.sha256(raw).hexdigest(),
                doc,
            ),
        )
        db.commit()
        return "recorded"
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("schema")
    sub.add_parser("init").add_argument("database", type=Path)
    ingest = sub.add_parser("append")
    ingest.add_argument("database", type=Path)
    ingest.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    if args.command == "schema":
        print(json.dumps(Snapshot.model_json_schema(), indent=2))
    elif args.command == "init":
        initialize(args.database)
        print("Initialized empty FAC/CEMAE registry.")
    else:
        print(append(args.database, args.snapshot.read_bytes()))
