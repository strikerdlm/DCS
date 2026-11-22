"""Publish the review and model databases as one reproducible, immutable release."""

import argparse
import csv
from contextlib import closing, contextmanager
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile

from scripts.build_chamber_database import ROOT, build, sha256


# Prefixes are the original extraction namespaces. All public numerical
# supplements through this release remain available for qualified analyses.
SOURCE_REGISTERS = {
    "v1": "source", "v1.1": "zotero_source", "v1.2": "web_source",
    "v1.3": "literature_source", "v1.4": "cohort_source", "v1.5": "citation_source",
    "v1.6": "discovery_source", "v1.155": "discovery_source",
    "sharepoint-2026-11-19": "sharepoint_source",
    "fac-official": "fac_official_source", "rojas-2015": "rojas_source",
    "attachments-2026-11-19": "attachment_source", "zotero-dcs-2026-11-19": "zotero_dcs_source",
}
REVIEW_ONLY = {
    "publication_search_run", "publication_search_hit", "citation_reference", "citation_citer",
    "citation_reference_reprint", "citation_deduplicated_reference",
}
# These views use extraction tables outside the review schema. Freeze their rows
# in the review file so that it remains useful without the modeling database.
REVIEW_SNAPSHOTS = {
    "review_historical_search_record": "record_key", "review_seed_role_cell": "study_id,source_cell",
    "review_supplementary_role_cell": "study_id,stratum",
    "review_secondary_role_cell": "study_id,source_cell",
}
PRODUCTS = {"review": "systematic-review.sqlite", "model": "dcs-model.sqlite"}


def link_published_cases(db):
    db.execute("""
        CREATE TABLE shared_case_evidence(
            source_id TEXT, stratum TEXT, endpoint TEXT, record_key TEXT NOT NULL,
            observation_id TEXT NOT NULL, report_id TEXT NOT NULL, onset_min INTEGER CHECK(onset_min>=0),
            first_assessment_min INTEGER CHECK(first_assessment_min>=0),
            recurrence_report_day INTEGER CHECK(recurrence_report_day>=0),
            recurrence_free_followup_min INTEGER CHECK(recurrence_free_followup_min>=0), review_locator TEXT NOT NULL,
            extraction_locator TEXT NOT NULL, PRIMARY KEY(source_id,stratum,endpoint,record_key,observation_id),
            UNIQUE(record_key,observation_id)
        ) STRICT
    """)
    key = "data/chamber/publication-review/case-links.csv"
    content = (ROOT / key).read_bytes()
    expected = db.execute("SELECT sha256 FROM evidence.frozen_input WHERE path=?", (key,)).fetchone()
    if expected != (hashlib.sha256(content).hexdigest(),):
        raise ValueError("Case links differ from the verified release")
    with io.StringIO(content.decode("utf-8-sig"), newline="") as f:
        for row in csv.DictReader(f):
            values = {k: v or None for k, v in row.items()}
            # Both independently acquired extracts must describe the single
            # published case before any new time fields can enter its record.
            matched = db.execute("""
                INSERT INTO shared_case_evidence
                WITH model_cases AS (
                    SELECT source_id,stratum,endpoint,locator FROM evidence.publication_observation
                    WHERE numerator=1 AND denominator IS NULL
                    UNION ALL
                    SELECT source_id,stratum,endpoint,locator FROM evidence.web_chamber_clinical_case
                )
                SELECT p.source_id,p.stratum,p.endpoint,r.record_key,r.observation_id,r.report_id,
                       :onset_min,:first_assessment_min,:recurrence_report_day,
                       :recurrence_free_followup_min,r.locator,p.locator
                FROM model_cases p JOIN evidence.review_search_observation r
                WHERE (p.source_id,p.stratum,p.endpoint)=(:source_id,:stratum,:endpoint)
                  AND (r.record_key,r.observation_id,r.report_id)=(:record_key,:observation_id,:report_id)
                  AND r.cases=1 AND r.denominator IS NULL
                  AND EXISTS (
                      SELECT 1 FROM evidence.review_record a WHERE a.source_key=p.source_id
                      AND a.stream GLOB 'data/chamber/v1.*/sources.csv'
                      AND (a.report_id=r.report_id OR EXISTS (
                          SELECT 1 FROM evidence.review_report_relation rel
                          WHERE rel.relationship='same_published_case' AND
                          ((rel.left_report=a.report_id AND rel.right_report=r.report_id)
                          OR (rel.right_report=a.report_id AND rel.left_report=r.report_id))
                      ))
                  )
            """, values)
            if matched.rowcount != 1:
                raise ValueError(f"Unreconciled case evidence for {row['source_id']}")
    for field in ("onset_min", "first_assessment_min", "recurrence_report_day", "recurrence_free_followup_min"):
        if db.execute(f"SELECT 1 FROM shared_case_evidence GROUP BY source_id,stratum,endpoint "
                      f"HAVING count(DISTINCT {field})>1").fetchone():
            raise ValueError(f"Conflicting case evidence for {field}")


def copy_schema_object(db, kind, name):
    stmt, = db.execute(
        "SELECT sql FROM evidence.sqlite_schema WHERE type=? AND name=?", (kind, name)
    ).fetchone()
    db.execute(stmt)
    if kind == "table":
        db.execute(f'INSERT INTO main."{name}" SELECT * FROM evidence."{name}" ORDER BY rowid')


def export_product(source, path, kind, release):
    with closing(sqlite3.connect(path.resolve().as_uri(), uri=True)) as db, db:
        db.execute("ATTACH DATABASE ? AS evidence", (source.resolve().as_uri() + "?mode=ro",))
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("CREATE TABLE dataset_release(kind TEXT PRIMARY KEY, release_id TEXT NOT NULL) STRICT")
        db.execute("INSERT INTO dataset_release VALUES (?,?)", (kind, release))
        copy_schema_object(db, "table", "frozen_input")
        link_published_cases(db)
        if kind == "review":
            objects = db.execute(
                "SELECT type,name FROM evidence.sqlite_schema WHERE name GLOB 'review_*' "
                "ORDER BY rowid"
            ).fetchall()
            for obj_type, name in objects:
                if name in REVIEW_SNAPSHOTS:
                    db.execute(f'CREATE TABLE "{name}" AS SELECT * FROM evidence."{name}"')
                    db.execute(f'CREATE UNIQUE INDEX "{name}_key" ON "{name}" ({REVIEW_SNAPSHOTS[name]})')
                else:
                    copy_schema_object(db, obj_type, name)
        else:
            for obj_type, name in db.execute(
                "SELECT type,name FROM evidence.sqlite_schema WHERE type IN ('table','view','trigger') "
                "AND name NOT GLOB 'review_*' AND name NOT GLOB 'sqlite_*' ORDER BY rowid"
            ).fetchall():
                if name not in REVIEW_ONLY and name != "frozen_input":
                    copy_schema_object(db, obj_type, name)
            # Transfer only the review's curated original role cells. Historical
            # reprints and search hits remain traceable in the review database.
            db.execute("""
                CREATE TABLE chamber_group_evidence (
                    study_id TEXT, stratum TEXT, cases INTEGER NOT NULL,
                    exposures INTEGER NOT NULL CHECK(cases BETWEEN 0 AND exposures),
                    report_id TEXT NOT NULL, source_table TEXT NOT NULL, locator TEXT NOT NULL,
                    denominator_note TEXT NOT NULL, PRIMARY KEY(study_id,stratum)
                ) STRICT
            """)
            db.execute("""
                INSERT INTO chamber_group_evidence
                SELECT study_id,source_cell,cases,exposures,report_id,source_table,locator,
                       'See original role-specific cohort definition'
                FROM evidence.review_seed_role_cell
                UNION ALL
                SELECT study_id,stratum,cases,exposures,report_id,source_table,locator,
                       denominator_basis || ' / ' || note
                FROM evidence.review_supplementary_role_cell
            """)
            db.execute(
                "CREATE TABLE model_report_link(source_table TEXT,source_id TEXT,record_key TEXT UNIQUE NOT NULL,"
                "report_id TEXT NOT NULL, PRIMARY KEY(source_table,source_id)) STRICT"
            )
            for stream, source_id, record_key, report_id in db.execute(
                "SELECT stream,source_key,record_key,report_id FROM evidence.review_record "
                "WHERE stream GLOB 'data/chamber/*/sources.csv' ORDER BY stream,source_key"
            ):
                version = stream.split("/")[-2]
                table = SOURCE_REGISTERS.get(version, "publication_source")
                db.execute("INSERT INTO model_report_link VALUES (?,?,?,?)",
                           (table, source_id, record_key, report_id))
            for table in dict.fromkeys((*SOURCE_REGISTERS.values(), "publication_source")):
                if db.execute(f"SELECT source_id FROM {table} EXCEPT SELECT source_id FROM "
                              "model_report_link WHERE source_table=?", (table,)).fetchone():
                    raise ValueError(f"Missing review provenance for {table}")
            db.execute("""
                CREATE VIEW dcs_case AS
                SELECT c.*, l.record_key, l.report_id,
                       coalesce(t.narrative_time_min,c.dcs_time_min) AS preferred_dcs_time_min,
                       coalesce(t.narrative_locator,c.locator) AS preferred_dcs_locator
                FROM literature_case_index c JOIN model_report_link l USING(source_id)
                LEFT JOIN literature_case_timing_review t ON t.source_id=c.source_id
                  AND t.published_case_number=c.published_case_number AND t.endpoint='dcs'
                  AND t.interpretation='narrative_preferred'
                WHERE l.source_table='literature_source'
            """)
            db.execute("""
                CREATE VIEW historical_case_catalog AS
                SELECT source_id || ':' || published_case_number AS case_id,source_id,endpoint,
                       report_id,record_key,preferred_dcs_time_min AS source_time_min,
                       dcs_time_basis AS time_basis,preferred_dcs_locator AS locator,
                       NULL AS first_assessment_min,NULL AS recurrence_report_day,
                       NULL AS recurrence_free_followup_min
                FROM dcs_case
                UNION ALL
                SELECT e.source_id || ':' || e.stratum,e.source_id,e.endpoint,e.report_id,e.record_key,
                       t.onset_min,CASE WHEN t.onset_min IS NOT NULL
                            THEN coalesce(c.source_time_basis,'symptom_onset_after_exposure') END,
                       e.extraction_locator,t.first_assessment_min,t.recurrence_report_day,t.recurrence_free_followup_min
                FROM shared_case_evidence e JOIN (
                    SELECT source_id,stratum,endpoint,min(record_key) AS record_key,max(onset_min) AS onset_min,
                           max(first_assessment_min) AS first_assessment_min,max(recurrence_report_day) AS recurrence_report_day,
                           max(recurrence_free_followup_min) AS recurrence_free_followup_min
                    FROM shared_case_evidence GROUP BY source_id,stratum,endpoint
                ) t USING(source_id,stratum,endpoint,record_key)
                LEFT JOIN web_chamber_clinical_case c ON (c.source_id,c.stratum,c.endpoint)=(e.source_id,e.stratum,e.endpoint)
                GROUP BY e.source_id,e.stratum,e.endpoint
            """)
            if db.execute("SELECT 1 FROM historical_case_catalog GROUP BY case_id HAVING count(*)>1").fetchone():
                raise ValueError("Duplicate historical case identifier")
            if db.execute("SELECT 1 FROM dcs_case GROUP BY source_id,published_case_number "
                          "HAVING count(*)>1").fetchone():
                raise ValueError("Duplicate published case key")
        if db.execute("PRAGMA main.foreign_key_check").fetchone() or (
            db.execute("PRAGMA main.integrity_check").fetchone() != ("ok",)
        ):
            raise ValueError(f"Failed integrity check for {kind}")


def publish_pair(folder):
    folder = Path(folder).resolve()
    folder.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=folder.parent) as tmp:
        temp = Path(tmp)
        master = temp / "evidence.sqlite"
        release = build(master, publication_review=True)
        pair = temp / "release"
        pair.mkdir()
        for kind, filename in PRODUCTS.items():
            export_product(master, pair / filename, kind, release)
        hashes = {name: sha256(pair / name) for name in PRODUCTS.values()}
        manifest = {"evidence_sha256": release, "files": hashes}
        (pair / "release.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        try:
            pair.rename(folder)
        except OSError:
            if not folder.is_dir():
                raise
            try:
                unchanged = json.loads((folder / "release.json").read_bytes()) == manifest and all(
                    sha256(folder / name) == digest for name, digest in hashes.items()
                )
            except (FileNotFoundError, ValueError):
                unchanged = False
            if not unchanged:
                raise FileExistsError(f"A different release exists at {folder}. Select a new output folder.")
        return manifest


def verify_product(path, kind):
    manifest = json.loads((path.parent / "release.json").read_bytes())
    if sha256(path) != manifest["files"][PRODUCTS[kind]]:
        raise ValueError(f"Release checksum mismatch for {kind} database")
    return manifest["evidence_sha256"]


@contextmanager
def connect_pair(folder):
    """Join review citations to model evidence without copying records between files."""
    folder = Path(folder).resolve()
    expected = verify_product(folder / PRODUCTS["model"], "model")
    verify_product(folder / PRODUCTS["review"], "review")
    with closing(sqlite3.connect((folder / PRODUCTS["model"]).as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("ATTACH DATABASE ? AS review", ((folder / PRODUCTS["review"]).as_uri() + "?mode=ro",))
        model = db.execute("SELECT release_id FROM main.dataset_release WHERE kind='model'").fetchone()
        review = db.execute("SELECT release_id FROM review.dataset_release WHERE kind='review'").fetchone()
        if model != (expected,) or model != review:
            raise ValueError("The two databases belong to different releases.")
        db.execute("PRAGMA query_only=ON")
        yield db


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    print(json.dumps(publish_pair(parser.parse_args().output_dir), indent=2))
