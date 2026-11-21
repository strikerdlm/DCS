"""Build the offline, source-locked SQLite release of published chamber observations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sqlite3
import tempfile
from itertools import chain
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "chamber" / "v1"
DEFAULT_OUTPUT = ROOT / "artifacts" / "chamber-v1" / "observed.sqlite"
ZOTERO_DATA = ROOT / "data" / "chamber" / "v1.1"
ZOTERO_OUTPUT = ROOT / "artifacts" / "chamber-v1.1" / "observed.sqlite"
WEB_DATA = ROOT / "data" / "chamber" / "v1.2"
WEB_OUTPUT = ROOT / "artifacts" / "chamber-v1.2" / "observed.sqlite"
LITERATURE_DATA = ROOT / "data" / "chamber" / "v1.3"
LITERATURE_OUTPUT = ROOT / "artifacts" / "chamber-v1.3" / "observed.sqlite"
COHORT_DATA = ROOT / "data" / "chamber" / "v1.4"
COHORT_OUTPUT = ROOT / "artifacts" / "chamber-v1.4" / "observed.sqlite"
SHAREPOINT_DATA = ROOT / "data" / "chamber" / "sharepoint-2026-11-19"
SHAREPOINT_OUTPUT = ROOT / "artifacts" / "chamber-deduplicated" / "observed.sqlite"
ROJAS_DATA = ROOT / "data" / "chamber" / "rojas-2015"
ROJAS_OUTPUT = ROOT / "artifacts" / "chamber-rojas-2015" / "observed.sqlite"
ATTACHMENT_DATA = ROOT / "data" / "chamber" / "attachments-2026-11-19"
ATTACHMENT_OUTPUT = ROOT / "artifacts" / "chamber-six-pdfs" / "observed.sqlite"
DCS_COLLECTION_DATA = ROOT / "data" / "chamber" / "zotero-dcs-2026-11-19"
DCS_COLLECTION_OUTPUT = ROOT / "artifacts" / "chamber-zotero-dcs" / "observed.sqlite"
CITATION_DATA = ROOT / "data" / "chamber" / "v1.5"
CITATION_OUTPUT = ROOT / "artifacts" / "chamber-v1.5" / "observed.sqlite"
DISCOVERY_DATA = ROOT / "data" / "chamber" / "v1.6"
DISCOVERY_OUTPUT = ROOT / "artifacts" / "chamber-v1.6" / "observed.sqlite"
PUBLICATION_DATA = ROOT / "data" / "chamber" / "v1.7"
PUBLICATION_OUTPUT = ROOT / "artifacts" / "chamber-v1.7" / "observed.sqlite"
HISTORICAL_DATA = ROOT / "data" / "chamber" / "v1.8"
HISTORICAL_OUTPUT = ROOT / "artifacts" / "chamber-v1.8" / "observed.sqlite"
PROTOCOL_DATA = ROOT / "data" / "chamber" / "v1.9"
PROTOCOL_OUTPUT = ROOT / "artifacts" / "chamber-v1.9" / "observed.sqlite"
EXPEDITION_DATA = ROOT / "data" / "chamber" / "v1.10"
EXPEDITION_OUTPUT = ROOT / "artifacts" / "chamber-v1.10" / "observed.sqlite"
CADET_DATA = ROOT / "data" / "chamber" / "v1.11"
CADET_OUTPUT = ROOT / "artifacts" / "chamber-v1.11" / "observed.sqlite"
RAF_DATA = ROOT / "data" / "chamber" / "v1.12"
RAF_OUTPUT = ROOT / "artifacts" / "chamber-v1.12" / "observed.sqlite"
CLINICAL_SERIES_DATA = ROOT / "data" / "chamber" / "v1.13"
CLINICAL_SERIES_OUTPUT = ROOT / "artifacts" / "chamber-v1.13" / "observed.sqlite"
CROSSOVER_DATA = ROOT / "data" / "chamber" / "v1.14"
CROSSOVER_OUTPUT = ROOT / "artifacts" / "chamber-v1.14" / "observed.sqlite"
HISTORIC_CHAMBER_DATA = ROOT / "data" / "chamber" / "v1.15"
HISTORIC_CHAMBER_OUTPUT = ROOT / "artifacts" / "chamber-v1.15" / "observed.sqlite"
SPACEFLIGHT_DATA = ROOT / "data" / "chamber" / "v1.16"
SPACEFLIGHT_OUTPUT = ROOT / "artifacts" / "chamber-v1.16" / "observed.sqlite"
DENITROGENATION_DATA = ROOT / "data" / "chamber" / "v1.17"
DENITROGENATION_OUTPUT = ROOT / "artifacts" / "chamber-v1.17" / "observed.sqlite"
INTERNATIONAL_DATA = ROOT / "data" / "chamber" / "v1.18"
INTERNATIONAL_OUTPUT = ROOT / "artifacts" / "chamber-v1.18" / "observed.sqlite"
ARCHIVAL_TRIAL_DATA = ROOT / "data" / "chamber" / "v1.19"
ARCHIVAL_TRIAL_OUTPUT = ROOT / "artifacts" / "chamber-v1.19" / "observed.sqlite"
RAPID_DECOMPRESSION_DATA = ROOT / "data" / "chamber" / "v1.20"
RAPID_DECOMPRESSION_OUTPUT = ROOT / "artifacts" / "chamber-v1.20" / "observed.sqlite"
CHAMBER_PROGRAM_DATA = ROOT / "data" / "chamber" / "v1.21"
CHAMBER_PROGRAM_OUTPUT = ROOT / "artifacts" / "chamber-v1.21" / "observed.sqlite"
FLIGHT_SURVEILLANCE_DATA = ROOT / "data" / "chamber" / "v1.22"
FLIGHT_SURVEILLANCE_OUTPUT = ROOT / "artifacts" / "chamber-v1.22" / "observed.sqlite"
ARCHIVE_FOLLOWUP_DATA = ROOT / "data" / "chamber" / "v1.23"
ARCHIVE_FOLLOWUP_OUTPUT = ROOT / "artifacts" / "chamber-v1.23" / "observed.sqlite"
HISTORICAL_OUTCOMES_DATA = ROOT / "data" / "chamber" / "v1.24"
HISTORICAL_OUTCOMES_OUTPUT = ROOT / "artifacts" / "chamber-v1.24" / "observed.sqlite"
CHAMBER_CASE_DATA = ROOT / "data" / "chamber" / "v1.25"
CHAMBER_CASE_OUTPUT = ROOT / "artifacts" / "chamber-v1.25" / "observed.sqlite"
CHAMBER_TIMING_DATA = ROOT / "data" / "chamber" / "v1.26"
CHAMBER_TIMING_OUTPUT = ROOT / "artifacts" / "chamber-v1.26" / "observed.sqlite"
CHAMBER_ARCHIVE_DATA = ROOT / "data" / "chamber" / "v1.27"
CHAMBER_ARCHIVE_OUTPUT = ROOT / "artifacts" / "chamber-v1.27" / "observed.sqlite"
CHAMBER_SYMPTOM_DATA = ROOT / "data" / "chamber" / "v1.28"
CHAMBER_SYMPTOM_OUTPUT = ROOT / "artifacts" / "chamber-v1.28" / "observed.sqlite"
CHAMBER_CASE_SERIES_DATA = ROOT / "data" / "chamber" / "v1.29"
CHAMBER_CASE_SERIES_OUTPUT = ROOT / "artifacts" / "chamber-v1.29" / "observed.sqlite"
CHAMBER_AGE_STRATA_DATA = ROOT / "data" / "chamber" / "v1.30"
CHAMBER_AGE_STRATA_OUTPUT = ROOT / "artifacts" / "chamber-v1.30" / "observed.sqlite"
CHAMBER_RECONCILIATION_DATA = ROOT / "data" / "chamber" / "v1.31"
CHAMBER_RECONCILIATION_OUTPUT = ROOT / "artifacts" / "chamber-v1.31" / "observed.sqlite"
CHAMBER_NASA_STRATA_DATA = ROOT / "data" / "chamber" / "v1.32"
CHAMBER_NASA_STRATA_OUTPUT = ROOT / "artifacts" / "chamber-v1.32" / "observed.sqlite"
CHAMBER_NASA_CASES_DATA = ROOT / "data" / "chamber" / "v1.33"
CHAMBER_NASA_CASES_OUTPUT = ROOT / "artifacts" / "chamber-v1.33" / "observed.sqlite"
CHAMBER_PAIRED_EXPOSURES_DATA = ROOT / "data" / "chamber" / "v1.34"
CHAMBER_PAIRED_EXPOSURES_OUTPUT = ROOT / "artifacts" / "chamber-v1.34" / "observed.sqlite"
CHAMBER_STAGED_EXPOSURES_DATA = ROOT / "data" / "chamber" / "v1.35"
CHAMBER_STAGED_EXPOSURES_OUTPUT = ROOT / "artifacts" / "chamber-v1.35" / "observed.sqlite"
CHAMBER_TREATED_CASE_DATA = ROOT / "data" / "chamber" / "v1.36"
CHAMBER_TREATED_CASE_OUTPUT = ROOT / "artifacts" / "chamber-v1.36" / "observed.sqlite"
CHAMBER_CASE_DETAIL_DATA = ROOT / "data" / "chamber" / "v1.37"
CHAMBER_CASE_DETAIL_OUTPUT = ROOT / "artifacts" / "chamber-v1.37" / "observed.sqlite"
CHAMBER_THRESHOLD_DATA = ROOT / "data" / "chamber" / "v1.38"
CHAMBER_THRESHOLD_OUTPUT = ROOT / "artifacts" / "chamber-v1.38" / "observed.sqlite"
CHAMBER_BUBBLE_OUTCOMES_DATA = ROOT / "data" / "chamber" / "v1.39"
CHAMBER_BUBBLE_OUTCOMES_OUTPUT = ROOT / "artifacts" / "chamber-v1.39" / "observed.sqlite"
CHAMBER_DIAGNOSIS_DATA = ROOT / "data" / "chamber" / "v1.40"
CHAMBER_DIAGNOSIS_OUTPUT = ROOT / "artifacts" / "chamber-v1.40" / "observed.sqlite"
CHAMBER_VGE_RECONCILIATION_DATA = ROOT / "data" / "chamber" / "v1.41"
CHAMBER_VGE_RECONCILIATION_OUTPUT = ROOT / "artifacts" / "chamber-v1.41" / "observed.sqlite"
CHAMBER_REPEATED_EVA_DATA = ROOT / "data" / "chamber" / "v1.42"
CHAMBER_REPEATED_EVA_OUTPUT = ROOT / "artifacts" / "chamber-v1.42" / "observed.sqlite"
CHAMBER_ARMSTRONG_ARCHIVE_DATA = ROOT / "data" / "chamber" / "v1.43"
CHAMBER_JPRS_TRANSLATION_DATA = ROOT / "data" / "chamber" / "v1.44"
CHAMBER_USAFSAM_ARCHIVE_DATA = ROOT / "data" / "chamber" / "v1.45"
CHAMBER_BROOKS_JOINT_DATA = ROOT / "data" / "chamber" / "v1.46"
CHAMBER_KANNAN_REPORT_DATA = ROOT / "data" / "chamber" / "v1.47"
CHAMBER_ADRAC_PROCEEDINGS = ROOT / "data" / "chamber" / "v1.48"
CHAMBER_BERRY_TRAINING = ROOT / "data" / "chamber" / "v1.49"
CHAMBER_HALBOUTY_CASE = ROOT / "data" / "chamber" / "v1.50"
CHAMBER_NASA_ASCENT = ROOT / "data" / "chamber" / "v1.51"
CHAMBER_HDSD_COMPILATION = ROOT / "data" / "chamber" / "v1.52"
CHAMBER_ASCENT_RECONCILIATION = ROOT / "data" / "chamber" / "v1.53"
CHAMBER_HISTORICAL_CROSSOVER = ROOT / "data" / "chamber" / "v1.54"
CHAMBER_HISTORICAL_PRESELECTION = ROOT / "data" / "chamber" / "v1.55"
CHAMBER_HISTORICAL_PREOXYGENATION = ROOT / "data" / "chamber" / "v1.56"
CHAMBER_CAM_MEETING = ROOT / "data" / "chamber" / "v1.57"
CHAMBER_CAM_BULLETIN = ROOT / "data" / "chamber" / "v1.58"
CHAMBER_CAM_MULTICENTER = ROOT / "data" / "chamber" / "v1.59"
CHAMBER_CAM_PAIRED = ROOT / "data" / "chamber" / "v1.60"
CHAMBER_GRAY_STRATA = ROOT / "data" / "chamber" / "v1.61"
CHAMBER_NEUROLOGICAL_TIMING = ROOT / "data" / "chamber" / "v1.62"
CHAMBER_OPERATION_EVEREST = ROOT / "data" / "chamber" / "v1.63"
CHAMBER_ASMA_CASE = ROOT / "data" / "chamber" / "v1.64"
AVIATION_DEPRESSURIZATION = ROOT / "data" / "chamber" / "v1.65"
AVIATION_U2_HISTORY = ROOT / "data" / "chamber" / "v1.66"
CHAMBER_NEUROLOGICAL_ARCHIVE = ROOT / "data" / "chamber" / "v1.67"
AVIATION_LEWIS_ARCHIVE = ROOT / "data" / "chamber" / "v1.68"
CHAMBER_DAVIS_CASES = ROOT / "data" / "chamber" / "v1.69"
CHAMBER_OPERATOR_TREATMENT_ARCHIVE = ROOT / "data" / "chamber" / "v1.70"
CHAMBER_KATUNTSEV_PROGRAM = ROOT / "data" / "chamber" / "v1.71"
CHAMBER_NASA_TRIAL_CASES = ROOT / "data" / "chamber" / "v1.72"
CHAMBER_NASA_PRP = ROOT / "data" / "chamber" / "v1.73"
CHAMBER_SOAR_GAS = ROOT / "data" / "chamber" / "v1.74"
CHAMBER_ARGO = ROOT / "data" / "chamber" / "v1.75"
CHAMBER_LBA_COMPARISONS = ROOT / "data" / "chamber" / "v1.76"
CHAMBER_POSTDIVE_CASES = ROOT / "data" / "chamber" / "v1.77"
CHAMBER_IAF_CASES = ROOT / "data" / "chamber" / "v1.78"
CHAMBER_U2_CASES = ROOT / "data" / "chamber" / "v1.79"
CHAMBER_U2_CASE_SERIES = ROOT / "data" / "chamber" / "v1.80"
CHAMBER_TRAINING_HISTORIES = ROOT / "data" / "chamber" / "v1.81"
CHAMBER_HALO_AND_USAF_ONSET = ROOT / "data" / "chamber" / "v1.82"
CHAMBER_PFO_AND_HEADACHE = ROOT / "data" / "chamber" / "v1.83"
CHAMBER_POSTEXPOSURE_EXERCISE = ROOT / "data" / "chamber" / "v1.84"
CHAMBER_GROUND_OXYGEN = ROOT / "data" / "chamber" / "v1.85"
CHAMBER_INCIDENTS_AND_PREFLIGHT = ROOT / "data" / "chamber" / "v1.86"
CHAMBER_FRYER_FATALITIES = ROOT / "data" / "chamber" / "v1.87"
CHAMBER_MOON_PATHOLOGY = ROOT / "data" / "chamber" / "v1.88"
CHAMBER_FLINN_WOMACK = ROOT / "data" / "chamber" / "v1.89"
CHAMBER_HISTORICAL_VISUAL_SUMMARIES = ROOT / "data" / "chamber" / "v1.90"
CHAMBER_REGIONAL_ECCENTRIC_EXERCISE = ROOT / "data" / "chamber" / "v1.91"
CHAMBER_NASA_REHEARSALS = ROOT / "data" / "chamber" / "v1.92"
PUBLICATION_SEARCH_TABLES = {
    "publication_search_run": "search_runs.csv",
    "publication_search_hit": "search_hits.csv",
}
FAC_DATA = ROOT / "data" / "chamber" / "fac-official"
FAC_OUTPUT = ROOT / "artifacts" / "chamber-fac-official" / "observed.sqlite"
FAC_PRIVATE_OUTPUT = FAC_OUTPUT.with_name("case-records.local.sqlite")
REVIEW_OUTPUT = ROOT / "artifacts" / "chamber-publication-review" / "observed.sqlite"

# Names are internal constants. Values from the publications are always SQL parameters.
TABLE_FILES = {
    "cohort": "cohorts.csv",
    "source": "sources.csv",
    "source_overlap": "source_overlap.csv",
    "source_statistic": "source_statistics.csv",
    "source_finding": "source_findings.csv",
    "nasa_test": "nasa_f1.csv",
    "afrl_test": "afrl_table_i.csv",
    "air_break_arm": "air_break_arms.csv",
    "air_break_estimate": "air_break_table_ii.csv",
    "aviation_count": "aviation_counts.csv",
    "adf_exposure_margin": "adf_year_profile_denominators.csv",
    "activity_summary": "activity_summary.csv",
}
ENDPOINTS = {
    "dcs": "Source-diagnosed symptomatic decompression sickness within the source window.",
    "dci": "Source-diagnosed decompression illness, with source-specific certainty.",
    "any_vge": "Detection of any venous gas emboli by the source monitoring protocol.",
    "grade_iv_vge": "First detection of Grade IV venous gas emboli on the source scale.",
}


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        digest = hashlib.sha256()
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
        return digest.hexdigest()


def read_csv(name, *, directory=DATA):
    with (directory / name).open(encoding="utf-8", newline="") as stream:
        yield from csv.DictReader(stream)


def load_table(db, table, filename, *, directory=DATA):
    records = read_csv(filename, directory=directory)
    first = next(records)
    columns = list(first)
    if columns != [r[1] for r in db.execute(f"PRAGMA table_info({table})")][: len(columns)]:
        raise ValueError(f"Unexpected columns in {filename}")
    sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})"
    db.executemany(
        sql, ([v if v != "" else None for v in row.values()] for row in chain([first], records))
    )


def load_compilation(db):
    for row in read_csv("nedu_appendix_e.csv"):
        token = row["printed_events"]
        exact = int(token) if token.isdigit() else None
        db.execute(
            "INSERT INTO a1309_profile(page,program,profile,source_schedule,exposures,"
            "printed_events,exact_cases) VALUES (?,?,?,?,?,?,?)",
            (*row.values(), exact),
        )
        if row["program"] == "NASA":
            name = row["profile"]
            test = name.split(";")[0].removeprefix("Test ").replace("PRP ", "P ")
            n, y = db.execute(
                "SELECT dcs_denominator,dcs_cases FROM nasa_test WHERE test_id=?", (test,)
            ).fetchone()
            agrees = int(row["exposures"]) == n and exact == y
            db.execute(
                "INSERT INTO a1309_nasa_overlap VALUES (?,?,?)",
                (
                    name,
                    test,
                    "same printed n and cases" if agrees else "related protocol; values differ",
                ),
            )


def load_vge(db):
    for row in read_csv("hdsd.csv"):
        right_censored = row["right"] == "Inf"
        db.execute(
            "INSERT INTO vge_interval(id,age_years,source_male,tr360,ambulatory,left_h,"
            "right_h,censoring) VALUES (?,?,?,?,?,?,?,?)",
            (
                row["id"],
                row["Age"],
                row["Sex"],
                row["TR360"],
                row["Noadyn"],
                row["left"],
                None if right_censored else row["right"],
                "right" if right_censored else "interval",
            ),
        )


def verify(db):
    checks = [
        (
            "NASA source",
            "SELECT count(*),sum(dcs_denominator),sum(dcs_cases),"
            "sum(male_exposures+female_exposures) FROM nasa_test",
            (49, 1030, 125, 1031),
        ),
        (
            "NASA development",
            "SELECT count(*),count(DISTINCT family),sum(dcs_denominator),"
            "sum(dcs_cases) FROM development_counts",
            (41, 12, 885, 124),
        ),
        (
            "NASA VGE transcription",
            "SELECT count(any_grade_vge_cases),sum(any_grade_vge_cases),"
            "sum(grade_iv_vge_cases) FROM nasa_test",
            (42, 371, 168),
        ),
        (
            "AFRL Table I",
            "SELECT count(*),sum(exposures),sum(dcs_cases) FROM afrl_test",
            (29, 708, 340),
        ),
        (
            "NEDU Appendix E",
            "SELECT count(*),sum(exposures),"
            "round(sum(CAST(printed_events AS REAL)),1),count(exact_cases) FROM a1309_profile",
            (117, 2594, 858.3, 116),
        ),
        ("NASA/NEDU linkage", "SELECT count(*) FROM a1309_nasa_overlap", (35,)),
        ("USAF time points", "SELECT count(*) FROM air_break_estimate", (24,)),
        ("hdsd", "SELECT count(*),count(right_h) FROM vge_interval", (238, 69)),
        (
            "external partition",
            "SELECT count(*),count(DISTINCT source_id) FROM locked_external",
            (5, 4),
        ),
        (
            "ADF year margins",
            "SELECT sum(a.denominator),sum(a.cases),"
            "sum(a.denominator<>m.profile_a+m.profile_b+m.profile_c+m.other) FROM adf_exposure_margin m "
            "JOIN aviation_count a ON a.source_id=m.source_id AND a.stratum=m.year",
            (10851, 42, 0),
        ),
    ]
    for label, query, expected in checks:
        actual = tuple(db.execute(query).fetchone())
        if actual != expected:
            raise ValueError(f"{label}: expected {expected}, found {actual}")
    if (
        db.execute("PRAGMA foreign_key_check").fetchone()
        or db.execute("PRAGMA integrity_check").fetchone()[0] != "ok"
    ):
        raise ValueError("SQLite integrity check failed")


def populate(db):
    lock = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    required = set(TABLE_FILES.values()) | {
        "hdsd.csv",
        "nedu_appendix_e.csv",
        "schema.sql",
        "design.json",
    }
    if required != set(lock):
        raise ValueError("Release manifest does not match the expected source tables")
    for name, expected in lock.items():
        if sha256(DATA / name) != expected:
            raise ValueError(f"Curated input digest mismatch: {name}")
    design = json.loads((DATA / "design.json").read_text(encoding="utf-8"))
    for name, expected in design["frozen_models"].items():
        if sha256(ROOT / name) != expected:
            raise ValueError(f"Frozen comparator digest mismatch: {name}")
    db.executescript((DATA / "schema.sql").read_text(encoding="utf-8"))
    db.executemany("INSERT INTO endpoint VALUES (?,?)", ENDPOINTS.items())
    for table, filename in TABLE_FILES.items():
        load_table(db, table, filename)
    load_compilation(db)
    load_vge(db)
    if design["external_columns"] != [r[1] for r in db.execute("PRAGMA table_info(external_lock)")]:
        raise ValueError("External lock columns differ from the reviewed schema")
    db.executemany("INSERT INTO external_lock VALUES (?,?,?,?,?,?,?,?)", design["external"])
    db.executemany(
        "INSERT INTO frozen_input VALUES (?,?)",
        sorted(
            {
                **{f"data/chamber/v1/{name}": digest for name, digest in lock.items()},
                **design["frozen_models"],
            }.items()
        ),
    )
    verify(db)
    crossing = db.execute("""
        SELECT o.source_a,o.source_b FROM source_overlap o
        JOIN source a ON o.source_a=a.source_id JOIN cohort ca ON ca.cohort_id=a.cohort_id
        JOIN source b ON o.source_b=b.source_id JOIN cohort cb ON cb.cohort_id=b.cohort_id
        WHERE (ca.partition IN ('development','separate_study') AND cb.partition='locked_external')
           OR (cb.partition IN ('development','separate_study') AND ca.partition='locked_external')
    """).fetchall()
    if crossing:
        raise ValueError(f"Known source overlap crosses the locked partition: {crossing}")
    db.commit()
    return design


def verify_cache(folder):
    for source in read_csv("sources.csv"):
        path = folder / source["cache_file"]
        if not path.is_file() or sha256(path) != source["sha256"]:
            raise ValueError(f"Original missing or changed for {source['source_id']}: {path.name}")


def publish(path, output, *, allow_identical=True):
    """Publish a finished sibling file atomically without replacing an existing file."""
    try:
        if os.name == "nt":
            os.rename(path, output)  # Windows rename fails if the destination exists.
        else:
            os.link(path, output)
    except FileExistsError:
        if not allow_identical or sha256(path) != sha256(output):
            raise FileExistsError(f"A file exists at {output}. Choose a new path.") from None


def load_supplement(
    db, directory, prefix, *, extra_tables=None, create_schema=True, include_observations=True
):
    tables = {
        f"{prefix}_source": "sources.csv",
        **({f"{prefix}_observation": "observations.csv"} if include_observations else {}),
        f"{prefix}_overlap": "overlap.csv",
        **(extra_tables or {}),
    }
    load_version_tables(db, directory, tables, create_schema=create_schema)


def load_version_tables(db, directory, tables, *, create_schema=True):
    manifest = json.loads((directory / "manifest.json").read_bytes())
    required = set(tables.values())
    if create_schema:
        required.add("schema.sql")
    if set(manifest) != required:
        raise ValueError(f"Unexpected {directory.name} supplement manifest entries")
    for name, expected in manifest.items():
        if sha256(directory / name) != expected:
            raise ValueError(f"{directory.name} supplement input digest mismatch: {name}")
    if create_schema:
        db.executescript((directory / "schema.sql").read_text(encoding="utf-8"))
    for table, filename in tables.items():
        load_table(db, table, filename, directory=directory)
    relative_directory = directory.relative_to(ROOT).as_posix()
    db.executemany(
        "INSERT INTO frozen_input VALUES (?,?)",
        [(f"{relative_directory}/{name}", digest) for name, digest in sorted(manifest.items())],
    )
    verify(db)
    db.commit()


def promote_comex_counts(db):
    margins = {
        "all-investigator-flights": 0,
        "flights-above-8000m": 8000,
    }
    for stratum, minimum_altitude in margins.items():
        cases, denominator = db.execute(
            "SELECT sum(dcs_symptoms), count(*) FROM publication_chamber_flight "
            "WHERE source_id='molenat02_fulltext' AND altitude_m >= ?",
            (minimum_altitude,),
        ).fetchone()
        update = db.execute(
            "UPDATE literature_observation SET observation_kind='exact_count', "
            "cases=?, reported_percent=NULL, locator='Full article, Table 1 and Results', "
            "outcome_window='During the recorded chamber flight. Fixed follow-up unavailable.', "
            "note=? WHERE source_id='molenat02' AND stratum=? AND endpoint='dcs_symptoms' "
            "AND observation_kind='reported_percent' AND denominator=? "
            "AND round(100.0 * ? / ?, 1)=reported_percent",
            (
                cases,
                "Reconciled using v1.10 primary flight table. The high-altitude margin "
                "includes flights at 8,000 and 8,848 m.",
                stratum,
                denominator,
                cases,
                denominator,
            ),
        )
        if update.rowcount != 1:
            raise ValueError(f"COMEX full-text counts do not reconcile with {stratum}")
    db.execute(
        "UPDATE literature_source SET access='full_text', extraction=?, note=? "
        "WHERE source_id='molenat02'",
        (
            "Publisher article verified via author-posted full text, v1.10/molenat02_fulltext",
            "Original published percentages retained in v1.3. This release uses the "
            "exact reported outcome counts and flight table.",
        ),
    )


def apply_publication_revisions(db):
    revisions = db.execute("""
        SELECT denominator, outcome_window, locator, note, source_id, stratum, endpoint,
               numerator, previous_denominator
        FROM publication_observation_revision
    """)
    for revision in revisions:
        update = db.execute(
            "UPDATE publication_observation SET denominator=?, outcome_window=?, locator=?, note=? "
            "WHERE source_id=? AND stratum=? AND endpoint=? AND numerator=? AND denominator=?",
            revision,
        )
        if update.rowcount != 1:
            raise ValueError(f"Published observation revision does not reconcile: {revision[4:7]}")


def build(
    output,
    *,
    zotero_supplement=False,
    web_supplement=False,
    literature_supplement=False,
    cohort_supplement=False,
    citation_supplement=False,
    sharepoint_supplement=False,
    rojas_supplement=False,
    attachment_supplement=False,
    zotero_dcs_supplement=False,
    discovery_supplement=False,
    publication_supplement=False,
    historical_supplement=False,
    protocol_supplement=False,
    expedition_supplement=False,
    cadet_supplement=False,
    raf_supplement=False,
    clinical_series_supplement=False,
    crossover_supplement=False,
    historic_chamber_supplement=False,
    spaceflight_supplement=False,
    denitrogenation_supplement=False,
    international_supplement=False,
    archival_trial_supplement=False,
    rapid_decompression_supplement=False,
    chamber_program_supplement=False,
    flight_surveillance_supplement=False,
    archive_followup_supplement=False,
    historical_outcomes_supplement=False,
    chamber_case_supplement=False,
    chamber_timing_supplement=False,
    chamber_archive_supplement=False,
    chamber_symptom_supplement=False,
    chamber_case_series_supplement=False,
    chamber_age_strata_supplement=False,
    chamber_reconciliation_supplement=False,
    chamber_nasa_strata_supplement=False,
    chamber_nasa_cases_supplement=False,
    chamber_paired_exposures_supplement=False,
    chamber_staged_exposures_supplement=False,
    chamber_treated_case_supplement=False,
    chamber_case_detail_supplement=False,
    chamber_threshold_supplement=False,
    chamber_bubble_outcomes_supplement=False,
    chamber_diagnosis_supplement=False,
    chamber_vge_reconciliation_supplement=False,
    chamber_repeated_eva_supplement=False,
    fac_official=False,
    fac_workbooks=None,
    publication_review=False,
):
    include_fac = fac_official or fac_workbooks is not None or publication_review
    cadet_supplement = cadet_supplement or publication_review
    rojas_supplement = rojas_supplement or publication_review
    zotero_dcs_supplement = zotero_dcs_supplement or publication_review
    include_attachments = attachment_supplement or zotero_dcs_supplement
    chamber_repeated_eva_supplement = chamber_repeated_eva_supplement or publication_review
    include_chamber_vge_reconciliation = (
        chamber_vge_reconciliation_supplement or chamber_repeated_eva_supplement
    )
    chamber_diagnosis_supplement = (
        chamber_diagnosis_supplement or publication_review or include_chamber_vge_reconciliation
    )
    include_chamber_bubble_outcomes = (
        chamber_bubble_outcomes_supplement or chamber_diagnosis_supplement
    )
    include_chamber_threshold = chamber_threshold_supplement or include_chamber_bubble_outcomes
    include_chamber_case_details = chamber_case_detail_supplement or include_chamber_threshold
    include_chamber_treated_cases = chamber_treated_case_supplement or include_chamber_case_details
    include_chamber_staged_exposures = (
        chamber_staged_exposures_supplement or include_chamber_treated_cases
    )
    include_chamber_paired_exposures = (
        chamber_paired_exposures_supplement or include_chamber_staged_exposures
    )
    include_chamber_nasa_cases = chamber_nasa_cases_supplement or include_chamber_paired_exposures
    include_chamber_nasa_strata = chamber_nasa_strata_supplement or include_chamber_nasa_cases
    include_chamber_reconciliation = (
        chamber_reconciliation_supplement or include_chamber_nasa_strata
    )
    include_chamber_age_strata = chamber_age_strata_supplement or include_chamber_reconciliation
    include_chamber_case_series = chamber_case_series_supplement or include_chamber_age_strata
    include_chamber_symptoms = chamber_symptom_supplement or include_chamber_case_series
    include_chamber_archive = chamber_archive_supplement or include_chamber_symptoms
    include_chamber_timing = chamber_timing_supplement or include_chamber_archive
    include_chamber_cases = chamber_case_supplement or include_chamber_timing
    include_historical_outcomes = historical_outcomes_supplement or include_chamber_cases
    include_archive_followup = archive_followup_supplement or include_historical_outcomes
    include_flight_surveillance = flight_surveillance_supplement or include_archive_followup
    include_chamber_program = chamber_program_supplement or include_flight_surveillance
    include_rapid_decompression = rapid_decompression_supplement or include_chamber_program
    include_archival = archival_trial_supplement or include_rapid_decompression
    include_international = international_supplement or include_archival
    include_denitrogenation = denitrogenation_supplement or include_international
    include_spaceflight = spaceflight_supplement or include_denitrogenation
    include_historic_chamber = historic_chamber_supplement or include_spaceflight
    include_crossover = crossover_supplement or include_historic_chamber
    include_clinical_series = clinical_series_supplement or include_crossover
    include_raf = raf_supplement or include_clinical_series
    include_cadet = cadet_supplement or include_raf
    include_expedition = expedition_supplement or include_cadet
    include_protocols = protocol_supplement or include_expedition
    include_historical = historical_supplement or include_protocols
    include_publications = publication_supplement or include_historical
    include_discovery = discovery_supplement or include_publications
    include_sharepoint = (
        sharepoint_supplement
        or rojas_supplement
        or include_attachments
        or include_discovery
        or include_fac
    )
    include_citation = citation_supplement or include_sharepoint
    include_cohort = cohort_supplement or include_citation
    include_literature = literature_supplement or include_cohort
    include_web = web_supplement or include_literature
    include_zotero = zotero_supplement or include_web
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as folder:
        path = Path(folder) / "build.sqlite"
        db = sqlite3.connect(path)
        try:
            populate(db)
            if include_zotero:
                load_supplement(db, ZOTERO_DATA, "zotero")
            if include_web:
                load_supplement(db, WEB_DATA, "web")
            if include_literature:
                load_supplement(
                    db, LITERATURE_DATA, "literature", extra_tables={"literature_case": "cases.csv"}
                )
            if include_cohort:
                load_supplement(db, COHORT_DATA, "cohort")
            if include_citation:
                load_supplement(
                    db,
                    CITATION_DATA,
                    "citation",
                    extra_tables={
                        "citation_reference": "references.csv",
                        "citation_citer": "citers.csv",
                        "citation_paired_dcs": "paired_dcs.csv",
                        "citation_participant_cell": "participant_cells.csv",
                    },
                )
            if include_sharepoint:
                load_supplement(
                    db,
                    SHAREPOINT_DATA,
                    "sharepoint",
                    extra_tables={"sharepoint_vge_positive_record": "vge_positive_records.csv"},
                )
            if include_fac:
                load_supplement(
                    db, FAC_DATA, "fac_official", extra_tables={"fac_official_annual": "annual.csv"}
                )
            if include_discovery:
                load_supplement(
                    db,
                    DISCOVERY_DATA,
                    "discovery",
                    extra_tables={"discovery_adjudication": "adjudications.csv"},
                )
            if include_publications:
                load_supplement(
                    db,
                    PUBLICATION_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                )
            if include_historical:
                load_supplement(
                    db,
                    HISTORICAL_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                    create_schema=False,
                )
            if include_protocols:
                load_supplement(
                    db,
                    PROTOCOL_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                    create_schema=False,
                )
            if include_expedition:
                load_supplement(
                    db,
                    EXPEDITION_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_chamber_flight": "flights.csv",
                    },
                )
                promote_comex_counts(db)
                verify(db)
                db.commit()
            if include_cadet:
                load_supplement(
                    db,
                    CADET_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_reported_rate": "reported_rates.csv",
                    },
                )
            if include_raf:
                load_supplement(
                    db,
                    RAF_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                    create_schema=False,
                )
            if include_clinical_series:
                load_supplement(
                    db,
                    CLINICAL_SERIES_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                    create_schema=False,
                )
            if include_crossover:
                load_supplement(
                    db,
                    CROSSOVER_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                    create_schema=False,
                )
            if include_historic_chamber:
                load_supplement(
                    db,
                    HISTORIC_CHAMBER_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_selection_course": "selection_courses.csv",
                    },
                )
            if include_spaceflight:
                load_supplement(
                    db,
                    SPACEFLIGHT_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_observation_revision": "observation_revisions.csv",
                    },
                )
                apply_publication_revisions(db)
                verify(db)
                db.commit()
            if include_denitrogenation:
                load_supplement(
                    db,
                    DENITROGENATION_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_reported_rate": "reported_rates.csv",
                    },
                    create_schema=False,
                )
            if include_international:
                load_supplement(
                    db,
                    INTERNATIONAL_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                    create_schema=False,
                )
            if include_archival:
                load_supplement(
                    db,
                    ARCHIVAL_TRIAL_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                )
            if include_rapid_decompression:
                load_supplement(
                    db,
                    RAPID_DECOMPRESSION_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                    create_schema=False,
                )
            if include_chamber_program:
                load_supplement(
                    db,
                    CHAMBER_PROGRAM_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                    create_schema=False,
                )
            if include_flight_surveillance:
                load_supplement(
                    db,
                    FLIGHT_SURVEILLANCE_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                    create_schema=False,
                )
            if include_archive_followup:
                load_supplement(
                    db,
                    ARCHIVE_FOLLOWUP_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                )
            if include_historical_outcomes:
                load_supplement(
                    db,
                    HISTORICAL_OUTCOMES_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_reported_rate": "reported_rates.csv",
                    },
                )
            if include_chamber_cases:
                load_supplement(
                    db,
                    CHAMBER_CASE_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                    create_schema=False,
                )
            if include_chamber_timing:
                load_supplement(
                    db,
                    CHAMBER_TIMING_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_chamber_participant": "participants.csv",
                        "publication_chamber_trial_time": "trial_times.csv",
                    },
                )
            if include_chamber_archive:
                load_supplement(
                    db,
                    CHAMBER_ARCHIVE_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_reported_rate": "reported_rates.csv",
                    },
                )
            if include_chamber_symptoms:
                load_supplement(
                    db,
                    CHAMBER_SYMPTOM_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_reported_rate": "reported_rates.csv",
                    },
                    create_schema=False,
                )
            if include_chamber_case_series:
                load_supplement(
                    db,
                    CHAMBER_CASE_SERIES_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_reported_rate": "reported_rates.csv",
                    },
                )
            if include_chamber_age_strata:
                load_supplement(
                    db,
                    CHAMBER_AGE_STRATA_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_reported_rate": "reported_rates.csv",
                    },
                )
            if include_chamber_reconciliation:
                load_supplement(
                    db,
                    CHAMBER_RECONCILIATION_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                )
            if include_chamber_nasa_strata:
                load_supplement(
                    db,
                    CHAMBER_NASA_STRATA_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "discovery_observation": "daily_exposures.csv",
                    },
                    create_schema=False,
                )
            if include_chamber_nasa_cases:
                load_supplement(
                    db,
                    CHAMBER_NASA_CASES_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "literature_case_table_i": "nasa_table_i_cases.csv",
                        "literature_case_timing_review": "nasa_timing_review.csv",
                    },
                )
            if include_chamber_paired_exposures:
                load_supplement(
                    db,
                    CHAMBER_PAIRED_EXPOSURES_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_postdive_exposure": "postdive_exposures.csv",
                        "publication_vge_peak": "vge_peaks.csv",
                    },
                )
            if include_chamber_staged_exposures:
                load_supplement(
                    db,
                    CHAMBER_STAGED_EXPOSURES_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_staged_symptom": "staged_symptoms.csv",
                    },
                )
            if include_chamber_treated_cases:
                load_supplement(
                    db,
                    CHAMBER_TREATED_CASE_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_reported_rate": "reported_rates.csv",
                    },
                    create_schema=False,
                )
            if include_chamber_case_details:
                load_supplement(
                    db,
                    CHAMBER_CASE_DETAIL_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "citation_observation": "krause_outcomes.csv",
                        "publication_menstrual_case_margin": "case_margins.csv",
                        "web_vge_exercise_peak": "eiken_stage_peaks.csv",
                    },
                )
            if include_chamber_threshold:
                load_supplement(
                    db,
                    CHAMBER_THRESHOLD_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_threshold_profile": "threshold_profiles.csv",
                    },
                )
            if include_chamber_bubble_outcomes:
                load_supplement(
                    db,
                    CHAMBER_BUBBLE_OUTCOMES_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_reported_rate": "reported_rates.csv",
                    },
                    create_schema=False,
                )
            if chamber_diagnosis_supplement:
                load_supplement(
                    db,
                    CHAMBER_DIAGNOSIS_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_diagnostic_stratum": "diagnostic_strata.csv",
                        "literature_symptomatic_noncase": "symptomatic_noncases.csv",
                    },
                )
            if include_chamber_vge_reconciliation:
                load_supplement(
                    db,
                    CHAMBER_VGE_RECONCILIATION_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "literature_overlap": "literature_overlap.csv",
                    },
                )
            if chamber_repeated_eva_supplement:
                load_supplement(
                    db,
                    CHAMBER_REPEATED_EVA_DATA,
                    "publication",
                    extra_tables=PUBLICATION_SEARCH_TABLES,
                    create_schema=False,
                )
            if publication_review:
                load_supplement(
                    db,
                    CHAMBER_ARMSTRONG_ARCHIVE_DATA,
                    "publication",
                    extra_tables={"publication_reported_rate": "reported_rates.csv"},
                    create_schema=False,
                )
                load_supplement(
                    db,
                    CHAMBER_JPRS_TRANSLATION_DATA,
                    "publication",
                    extra_tables={"publication_chamber_reported_onset": "reported_onsets.csv"},
                )
                load_supplement(
                    db,
                    CHAMBER_USAFSAM_ARCHIVE_DATA,
                    "publication",
                    extra_tables={
                        "publication_adrac_profile_inventory": "archive_profiles.csv",
                        "publication_archive_protocol_summary": "protocol_summaries.csv",
                        "literature_observation_case_annotation": "case_annotations.csv",
                    },
                )
                load_supplement(
                    db,
                    CHAMBER_BROOKS_JOINT_DATA,
                    "publication",
                    extra_tables={
                        "publication_joint_dcs_vge": "joint_outcomes.csv",
                        "publication_validation_snapshot": "validation_estimates.csv",
                    },
                )
                load_supplement(
                    db,
                    CHAMBER_KANNAN_REPORT_DATA,
                    "publication",
                    extra_tables={"publication_exposure_outcome_margin": "outcome_margins.csv"},
                )
                load_supplement(
                    db,
                    CHAMBER_ADRAC_PROCEEDINGS,
                    "publication",
                    extra_tables={"publication_validation_snapshot": "validation_estimates.csv"},
                    include_observations=False,
                )
                load_supplement(
                    db,
                    CHAMBER_BERRY_TRAINING,
                    "publication",
                    extra_tables={"publication_reported_rate": "reported_rates.csv"},
                    create_schema=False,
                )
                load_version_tables(
                    db,
                    CHAMBER_HALBOUTY_CASE,
                    {"publication_case_milestone": "case_milestones.csv"},
                )
                load_version_tables(
                    db,
                    CHAMBER_NASA_ASCENT,
                    {
                        "publication_ascent_reference": "references.csv",
                        "publication_ascent_compilation": "appendix_b.csv",
                        "publication_ascent_compilation_total": "analysis_totals.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_HDSD_COMPILATION,
                    {"literature_hdsd_compilation": "table_iii.csv"},
                )
                load_supplement(
                    db,
                    CHAMBER_ASCENT_RECONCILIATION,
                    "publication",
                )
                load_supplement(
                    db,
                    CHAMBER_HISTORICAL_CROSSOVER,
                    "publication",
                    extra_tables={"publication_crossover_run": "crossover_runs.csv"},
                    include_observations=False,
                )
                load_supplement(
                    db,
                    CHAMBER_HISTORICAL_PRESELECTION,
                    "publication",
                    extra_tables={"publication_preselection_rate": "preselection_rates.csv"},
                    include_observations=False,
                )
                load_supplement(
                    db,
                    CHAMBER_HISTORICAL_PREOXYGENATION,
                    "publication",
                    extra_tables={
                        "publication_preoxygen_group": "groups.csv",
                        "publication_preoxygen_measure": "measures.csv",
                    },
                    include_observations=False,
                )
                load_supplement(
                    db,
                    CHAMBER_CAM_MEETING,
                    "publication",
                    extra_tables={"publication_meeting_measure": "measures.csv"},
                )
                load_supplement(
                    db,
                    CHAMBER_CAM_BULLETIN,
                    "publication",
                    extra_tables={
                        "publication_repeat_descent": "flight_descents.csv",
                        "publication_repeat_classification": "flight_classification.csv",
                        "publication_archival_cohort_size": "cohort_sizes.csv",
                    },
                )
                load_supplement(
                    db,
                    CHAMBER_CAM_MULTICENTER,
                    "publication",
                    extra_tables={
                        "publication_repeat_flight_profile": "repeat_profiles.csv",
                        "publication_repeat_flight_count": "repeat_counts.csv",
                        "publication_descent_interval": "descent_intervals.csv",
                        "publication_reported_rate": "reported_rates.csv",
                    },
                )
                load_supplement(
                    db,
                    CHAMBER_CAM_PAIRED,
                    "publication",
                    extra_tables={
                        "publication_paired_chamber_arm": "paired_arms.csv",
                        "publication_paired_chamber_count": "paired_counts.csv",
                        "publication_narrative_chamber_rate": "narrative_rates.csv",
                    },
                )
                load_supplement(
                    db,
                    CHAMBER_GRAY_STRATA,
                    "publication",
                    include_observations=False,
                    extra_tables={
                        "publication_gray_age_comparison": "age_comparison.csv",
                        "publication_gray_density": "gray_density.csv",
                        "publication_motley_density": "motley_density.csv",
                    },
                )
                load_supplement(
                    db,
                    CHAMBER_NEUROLOGICAL_TIMING,
                    "publication",
                    extra_tables={
                        "publication_neurological_episode_margin": "episode_margins.csv",
                        "publication_case_milestone": "case_milestones.csv",
                    },
                )
                load_supplement(
                    db,
                    CHAMBER_OPERATION_EVEREST,
                    "publication",
                    extra_tables={"publication_everest_context": "context.csv"},
                )
                load_supplement(
                    db,
                    CHAMBER_ASMA_CASE,
                    "publication",
                    create_schema=False,
                    extra_tables={"publication_case_milestone": "case_milestones.csv"},
                )
                load_version_tables(
                    db,
                    AVIATION_DEPRESSURIZATION,
                    {
                        "publication_source": "sources.csv",
                        "publication_aircraft_incident": "incidents.csv",
                        "publication_aircraft_incident_count": "counts.csv",
                    },
                )
                load_version_tables(
                    db,
                    AVIATION_U2_HISTORY,
                    {
                        "publication_source": "sources.csv",
                        "publication_overlap": "overlap.csv",
                        "publication_aviation_group": "flight_groups.csv",
                        "publication_meader_reported_flight": "meader_flights.csv",
                    },
                )
                load_supplement(
                    db,
                    CHAMBER_NEUROLOGICAL_ARCHIVE,
                    "publication",
                    extra_tables={
                        "publication_liske_case_profile": "liske_cases.csv",
                        "publication_case_milestone": "case_milestones.csv",
                    },
                )
                load_supplement(
                    db,
                    AVIATION_LEWIS_ARCHIVE,
                    "publication",
                    extra_tables={"publication_lewis_case_profile": "lewis_cases.csv"},
                )
                load_supplement(
                    db,
                    CHAMBER_DAVIS_CASES,
                    "publication",
                    create_schema=False,
                    extra_tables={"publication_case_milestone": "case_milestones.csv"},
                )
                load_supplement(db, CHAMBER_OPERATOR_TREATMENT_ARCHIVE, "publication", create_schema=False)
                load_version_tables(db, CHAMBER_KATUNTSEV_PROGRAM, {"publication_observation": "observations.csv"})
                load_version_tables(
                    db,
                    CHAMBER_NASA_TRIAL_CASES,
                    {
                        "publication_source": "sources.csv",
                        "publication_trial_case_profile": "case_profiles.csv",
                        "publication_trial_case_milestone": "case_milestones.csv",
                    },
                )
                load_version_tables(
                    db, CHAMBER_NASA_PRP, {"publication_prp_analysis_counts": "prp_analysis_counts.csv"}
                )
                load_version_tables(
                    db,
                    CHAMBER_SOAR_GAS,
                    {
                        "publication_source": "sources.csv",
                        "publication_observation": "observations.csv",
                        "publication_overlap": "overlap.csv",
                        "publication_left_heart_gas_case": "left_heart_gas_cases.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_ARGO,
                    {
                        "publication_source": "sources.csv",
                        "publication_argo_phase_i_arm": "arms.csv",
                        "publication_argo_phase_i_doppler": "doppler.csv",
                        "publication_argo_phase_i_clinical": "clinical.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_LBA_COMPARISONS,
                    {
                        "publication_source": "sources.csv",
                        "publication_observation": "observations.csv",
                        "publication_lba_argo_arm": "argo_arms.csv",
                        "publication_lba_argo_test_link": "argo_test_links.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_POSTDIVE_CASES,
                    {
                        "publication_vann04_dive_profile": "dive_profiles.csv",
                        "publication_vann04_flight_group": "flight_groups.csv",
                        "publication_vann04_case": "case_profiles.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_IAF_CASES,
                    {
                        "publication_source": "sources.csv",
                        "publication_observation": "observations.csv",
                        "publication_case_milestone": "case_milestones.csv",
                        "publication_iaf_adcs_case": "iaf_cases.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_U2_CASES,
                    {
                        "publication_source": "sources.csv",
                        "publication_observation": "observations.csv",
                        "publication_case_milestone": "case_milestones.csv",
                        "publication_u2_episode": "episodes.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_U2_CASE_SERIES,
                    {
                        "publication_source": "sources.csv",
                        "publication_observation": "observations.csv",
                        "publication_u2_series_row": "case_table_rows.csv",
                        "publication_u2_series_case_link": "case_crosswalk.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_TRAINING_HISTORIES,
                    {
                        "publication_source": "sources.csv",
                        "publication_allan_chamber_plateau": "allan_plateaus.csv",
                        "publication_allan_dci_case": "allan_case_details.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_HALO_AND_USAF_ONSET,
                    {
                        "publication_source": "sources.csv",
                        "publication_observation": "observations.csv",
                        "publication_case_milestone": "case_milestones.csv",
                        "publication_piwinski_halo_case": "halo_case_details.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_PFO_AND_HEADACHE,
                    {
                        "publication_source": "sources.csv",
                        "publication_observation": "observations.csv",
                        "publication_bryce_headache_sequence": "headache_histories.csv",
                        "publication_case_milestone": "case_milestones.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_POSTEXPOSURE_EXERCISE,
                    {
                        "publication_source": "sources.csv",
                        "publication_observation": "observations.csv",
                        "publication_postexercise_flow": "postexercise_flow.csv",
                        "publication_repeated_exposure_timing": "repeat_timing.csv",
                        "publication_repeated_exposure_joint_count": "repeat_joint_counts.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_GROUND_OXYGEN,
                    {
                        "publication_source": "sources.csv",
                        "publication_ground_oxygen_flow": "treatment_flow.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_INCIDENTS_AND_PREFLIGHT,
                    {
                        "publication_crowell83_chamber_incidents": "chamber_incidents.csv",
                        "publication_vann04_preflight_group": "preflight_groups.csv",
                        "publication_vann04_preflight_case": "preflight_cases.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_FRYER_FATALITIES,
                    {
                        "publication_fryer69_chamber_fatality": "chamber_fatalities.csv",
                        "publication_fryer69_fatality_citation": "case_citations.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_MOON_PATHOLOGY,
                    {"publication_moon48_chamber_case": "chamber_cases.csv"},
                )
                load_version_tables(
                    db,
                    CHAMBER_FLINN_WOMACK,
                    {
                        "publication_source": "sources.csv",
                        "publication_flinn63_exposure": "exposures.csv",
                        "publication_flinn63_milestone": "milestones.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_HISTORICAL_VISUAL_SUMMARIES,
                    {"publication_historical_visual_summary": "cited_observations.csv"},
                )
                load_version_tables(
                    db,
                    CHAMBER_REGIONAL_ECCENTRIC_EXERCISE,
                    {
                        "publication_gottschalk24_protocol": "protocols.csv",
                        "publication_gottschalk24_vge_peak": "vge_peaks.csv",
                        "publication_gottschalk24_safety_stop": "safety_stops.csv",
                    },
                )
                load_version_tables(
                    db,
                    CHAMBER_NASA_REHEARSALS,
                    {
                        "publication_source": "sources.csv",
                        "publication_observation": "observations.csv",
                        "publication_ea_rehearsal_pilot": "pilot_profiles.csv",
                        "publication_ea_rehearsal_summary": "campaign_rehearsals.csv",
                    },
                )
            if rojas_supplement:
                load_supplement(
                    db, ROJAS_DATA, "rojas", extra_tables={"rojas_result": "results.csv"}
                )
            if include_attachments:
                load_supplement(
                    db,
                    ATTACHMENT_DATA,
                    "attachment",
                    extra_tables={
                        "attachment_nasa_test": "nasa_tests.csv",
                        "attachment_u2_flight": "u2_flights.csv",
                    },
                )
            if zotero_dcs_supplement:
                load_supplement(
                    db,
                    DCS_COLLECTION_DATA,
                    "zotero_dcs",
                    extra_tables={
                        "zotero_dcs_case": "cases.csv",
                        "zotero_dcs_eva_break": "eva_breaks.csv",
                    },
                )
            if fac_workbooks is not None:
                from scripts.fac_official import ingest_workbooks

                ingest_workbooks(db, *fac_workbooks)
                verify(db)
                db.commit()
            if publication_review:
                from scripts.publication_review import load_register

                load_register(db, ROOT)
                db.commit()
        finally:
            db.close()
        publish(path, output)
    return sha256(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    release = parser.add_mutually_exclusive_group()
    release.add_argument(
        "--zotero-supplement",
        action="store_true",
        help="Build v1.1 with the verified Zotero supplement tables.",
    )
    release.add_argument(
        "--web-supplement",
        action="store_true",
        help="Build v1.2 with the Zotero and public web source supplements.",
    )
    release.add_argument(
        "--literature-supplement",
        action="store_true",
        help="Build v1.3 with the additional public literature and all prior supplements.",
    )
    release.add_argument(
        "--cohort-supplement",
        action="store_true",
        help="Build v1.4 with the expanded primary cohort tables and all prior supplements.",
    )
    release.add_argument(
        "--citation-supplement",
        action="store_true",
        help="Build v1.5 with the Mahon citation network and primary outcome extractions.",
    )
    release.add_argument(
        "--sharepoint-supplement",
        action="store_true",
        help="Build the combined database with the SharePoint intake and deduplicated views.",
    )
    parser.add_argument(
        "--discovery-supplement",
        action="store_true",
        help="Build v1.6 with the public chamber discovery and earlier deduplicated evidence.",
    )
    parser.add_argument(
        "--publication-supplement",
        action="store_true",
        help="Build v1.7 with screened chamber publications, search provenance and prior releases.",
    )
    parser.add_argument(
        "--historical-supplement",
        action="store_true",
        help="Build v1.8 with verified historical chamber studies and the v1.7 evidence.",
    )
    parser.add_argument(
        "--protocol-supplement",
        action="store_true",
        help="Build v1.9 with pressure-suit and crossover outcomes and the v1.8 evidence.",
    )
    parser.add_argument(
        "--expedition-supplement",
        action="store_true",
        help="Build v1.10 with original chamber flight tables and the v1.9 evidence.",
    )
    parser.add_argument(
        "--cadet-supplement",
        action="store_true",
        help="Build v1.11 with historical cadet chamber results and the v1.10 evidence.",
    )
    parser.add_argument(
        "--raf-supplement",
        action="store_true",
        help="Build v1.12 with public Royal Air Force chamber observations and earlier evidence.",
    )
    parser.add_argument(
        "--clinical-series-supplement",
        action="store_true",
        help="Build v1.13 with NASA, AFRL and Russian clinical chamber series.",
    )
    parser.add_argument(
        "--crossover-supplement",
        action="store_true",
        help="Build v1.14 with British and Swedish chamber outcomes and earlier evidence.",
    )
    parser.add_argument(
        "--historic-chamber-supplement",
        action="store_true",
        help="Build v1.15 with historic pressure trials and Royal Navy selection courses.",
    )
    parser.add_argument(
        "--spaceflight-supplement",
        action="store_true",
        help="Build v1.16 with historical simulated spaceflight and interruption trials.",
    )
    parser.add_argument(
        "--denitrogenation-supplement",
        action="store_true",
        help="Build v1.17 with denitrogenation strata and source-level NASA reconciliation.",
    )
    parser.add_argument(
        "--international-supplement",
        action="store_true",
        help="Build v1.18 with additional international chamber sources and clinical evidence.",
    )
    parser.add_argument(
        "--archival-trial-supplement",
        action="store_true",
        help="Build v1.19 with original historical flight and chamber outcomes.",
    )
    parser.add_argument(
        "--rapid-decompression-supplement",
        action="store_true",
        help="Build v1.20 with the Canadian rapid-decompression cohort and source crosswalk.",
    )
    parser.add_argument(
        "--chamber-program-supplement",
        action="store_true",
        help="Build v1.21 with Russian chamber trials and historical case reports.",
    )
    parser.add_argument(
        "--flight-surveillance-supplement",
        action="store_true",
        help="Build v1.22 with chamber Doppler evidence and operational flight surveillance.",
    )
    parser.add_argument(
        "--archive-followup-supplement",
        action="store_true",
        help="Build v1.23 with verified archive follow-up evidence and cohort links.",
    )
    parser.add_argument(
        "--historical-outcomes-supplement",
        action="store_true",
        help="Build v1.24 with original chamber surveillance and clinical outcome reports.",
    )
    parser.add_argument(
        "--chamber-case-supplement",
        action="store_true",
        help="Build v1.25 with published chamber case and cluster observations.",
    )
    parser.add_argument(
        "--chamber-timing-supplement",
        action="store_true",
        help="Build v1.26 with published chamber trial timing and censoring data.",
    )
    parser.add_argument(
        "--chamber-archive-supplement",
        action="store_true",
        help="Build v1.27 with original chamber archives and trial outcome tables.",
    )
    parser.add_argument(
        "--chamber-symptom-supplement",
        action="store_true",
        help="Build v1.28 with chamber symptom counts and crossover outcomes.",
    )
    parser.add_argument(
        "--chamber-case-series-supplement",
        action="store_true",
        help="Build v1.29 with chamber case series, onset counts and diagnostic reports.",
    )
    parser.add_argument(
        "--chamber-age-strata-supplement",
        action="store_true",
        help="Build v1.30 with age-stratified counts from historical chamber reports.",
    )
    parser.add_argument(
        "--chamber-reconciliation-supplement",
        action="store_true",
        help="Build v1.31 with historical chamber outcomes and a verified cohort merge.",
    )
    parser.add_argument(
        "--chamber-nasa-strata-supplement",
        action="store_true",
        help="Build v1.32 with NASA technician and session outcomes, plus FAA source verification.",
    )
    parser.add_argument(
        "--chamber-nasa-cases-supplement",
        action="store_true",
        help="Build v1.33 with NASA case timing and Swedish crossover outcomes.",
    )
    parser.add_argument(
        "--chamber-paired-exposures-supplement",
        action="store_true",
        help="Build v1.34 with Swedish post-dive exposures and crossover VGE grades.",
    )
    parser.add_argument(
        "--chamber-staged-exposures-supplement",
        action="store_true",
        help="Build v1.35 with historical staged chamber symptoms and NASA series counts.",
    )
    parser.add_argument(
        "--chamber-treated-case-supplement",
        action="store_true",
        help="Build v1.36 with USAF treated-case surveillance and passenger flight outcomes.",
    )
    parser.add_argument(
        "--chamber-case-detail-supplement",
        action="store_true",
        help="Build v1.37 with verified treated-case distributions and research follow-up.",
    )
    parser.add_argument(
        "--chamber-threshold-supplement",
        action="store_true",
        help="Build v1.38 with Polaris Dawn ground-test outcomes and historical table provenance.",
    )
    parser.add_argument(
        "--chamber-bubble-outcomes-supplement",
        action="store_true",
        help="Build v1.39 with 8.3-psia Doppler outcomes and a chamber training case.",
    )
    parser.add_argument(
        "--chamber-diagnosis-supplement",
        action="store_true",
        help="Build v1.40 with NASA symptom reports and diagnostic ratings.",
    )
    parser.add_argument(
        "--chamber-vge-reconciliation-supplement",
        action="store_true",
        help="Build v1.41 with reconciled historical Doppler counts.",
    )
    parser.add_argument(
        "--chamber-repeated-eva-supplement",
        action="store_true",
        help="Build v1.42 with a Russian repeat-exposure chamber series.",
    )
    release.add_argument(
        "--fac-official",
        action="store_true",
        help="Build the combined database with the official Colombian aggregates.",
    )
    release.add_argument(
        "--publication-review",
        action="store_true",
        help="Build the combined public chamber database and the bibliographic review register.",
    )
    release.add_argument(
        "--fac-workbooks",
        type=Path,
        nargs=2,
        metavar=("CASE_XLS", "TRAINING_XLSX"),
        help="Verify the official originals and include local case-level records.",
    )
    parser.add_argument(
        "--rojas-supplement",
        action="store_true",
        help="Include the Rojas USAF case-control data and table reconciliation.",
    )
    parser.add_argument(
        "--attachment-supplement",
        action="store_true",
        help="Include the six-PDF chamber evidence intake and source crosswalk.",
    )
    parser.add_argument(
        "--zotero-dcs-supplement",
        action="store_true",
        help="Include the Zotero DCS collection review and earlier six-PDF intake.",
    )
    parser.add_argument(
        "--verify-cache", type=Path, help="Also verify all original local source snapshots."
    )
    args = parser.parse_args()
    if args.verify_cache:
        verify_cache(args.verify_cache)
    default_output = DEFAULT_OUTPUT
    if args.zotero_supplement:
        default_output = ZOTERO_OUTPUT
    if args.web_supplement:
        default_output = WEB_OUTPUT
    if args.literature_supplement:
        default_output = LITERATURE_OUTPUT
    if args.cohort_supplement:
        default_output = COHORT_OUTPUT
    if args.citation_supplement:
        default_output = CITATION_OUTPUT
    if args.sharepoint_supplement:
        default_output = SHAREPOINT_OUTPUT
    if args.discovery_supplement:
        default_output = DISCOVERY_OUTPUT
    if args.publication_supplement:
        default_output = PUBLICATION_OUTPUT
    if args.historical_supplement:
        default_output = HISTORICAL_OUTPUT
    if args.protocol_supplement:
        default_output = PROTOCOL_OUTPUT
    if args.expedition_supplement:
        default_output = EXPEDITION_OUTPUT
    if args.cadet_supplement:
        default_output = CADET_OUTPUT
    if args.raf_supplement:
        default_output = RAF_OUTPUT
    if args.clinical_series_supplement:
        default_output = CLINICAL_SERIES_OUTPUT
    if args.crossover_supplement:
        default_output = CROSSOVER_OUTPUT
    if args.historic_chamber_supplement:
        default_output = HISTORIC_CHAMBER_OUTPUT
    if args.spaceflight_supplement:
        default_output = SPACEFLIGHT_OUTPUT
    if args.denitrogenation_supplement:
        default_output = DENITROGENATION_OUTPUT
    if args.international_supplement:
        default_output = INTERNATIONAL_OUTPUT
    if args.archival_trial_supplement:
        default_output = ARCHIVAL_TRIAL_OUTPUT
    if args.rapid_decompression_supplement:
        default_output = RAPID_DECOMPRESSION_OUTPUT
    if args.chamber_program_supplement:
        default_output = CHAMBER_PROGRAM_OUTPUT
    if args.flight_surveillance_supplement:
        default_output = FLIGHT_SURVEILLANCE_OUTPUT
    if args.archive_followup_supplement:
        default_output = ARCHIVE_FOLLOWUP_OUTPUT
    if args.historical_outcomes_supplement:
        default_output = HISTORICAL_OUTCOMES_OUTPUT
    if args.chamber_case_supplement:
        default_output = CHAMBER_CASE_OUTPUT
    if args.chamber_timing_supplement:
        default_output = CHAMBER_TIMING_OUTPUT
    if args.chamber_archive_supplement:
        default_output = CHAMBER_ARCHIVE_OUTPUT
    if args.chamber_symptom_supplement:
        default_output = CHAMBER_SYMPTOM_OUTPUT
    if args.chamber_case_series_supplement:
        default_output = CHAMBER_CASE_SERIES_OUTPUT
    if args.chamber_age_strata_supplement:
        default_output = CHAMBER_AGE_STRATA_OUTPUT
    if args.chamber_reconciliation_supplement:
        default_output = CHAMBER_RECONCILIATION_OUTPUT
    if args.chamber_nasa_strata_supplement:
        default_output = CHAMBER_NASA_STRATA_OUTPUT
    if args.chamber_nasa_cases_supplement:
        default_output = CHAMBER_NASA_CASES_OUTPUT
    if args.chamber_paired_exposures_supplement:
        default_output = CHAMBER_PAIRED_EXPOSURES_OUTPUT
    if args.chamber_staged_exposures_supplement:
        default_output = CHAMBER_STAGED_EXPOSURES_OUTPUT
    if args.chamber_treated_case_supplement:
        default_output = CHAMBER_TREATED_CASE_OUTPUT
    if args.chamber_case_detail_supplement:
        default_output = CHAMBER_CASE_DETAIL_OUTPUT
    if args.chamber_threshold_supplement:
        default_output = CHAMBER_THRESHOLD_OUTPUT
    if args.chamber_bubble_outcomes_supplement:
        default_output = CHAMBER_BUBBLE_OUTCOMES_OUTPUT
    if args.chamber_diagnosis_supplement:
        default_output = CHAMBER_DIAGNOSIS_OUTPUT
    if args.chamber_vge_reconciliation_supplement:
        default_output = CHAMBER_VGE_RECONCILIATION_OUTPUT
    if args.chamber_repeated_eva_supplement:
        default_output = CHAMBER_REPEATED_EVA_OUTPUT
    supplement_version = (
        CHAMBER_REPEATED_EVA_DATA.name
        if args.chamber_repeated_eva_supplement
        else CHAMBER_VGE_RECONCILIATION_DATA.name
        if args.chamber_vge_reconciliation_supplement
        else CHAMBER_DIAGNOSIS_DATA.name
        if args.chamber_diagnosis_supplement
        else CHAMBER_BUBBLE_OUTCOMES_DATA.name
        if args.chamber_bubble_outcomes_supplement
        else CHAMBER_THRESHOLD_DATA.name
        if args.chamber_threshold_supplement
        else CHAMBER_CASE_DETAIL_DATA.name
        if args.chamber_case_detail_supplement
        else CHAMBER_TREATED_CASE_DATA.name
        if args.chamber_treated_case_supplement
        else CHAMBER_STAGED_EXPOSURES_DATA.name
        if args.chamber_staged_exposures_supplement
        else CHAMBER_PAIRED_EXPOSURES_DATA.name
        if args.chamber_paired_exposures_supplement
        else CHAMBER_NASA_CASES_DATA.name
        if args.chamber_nasa_cases_supplement
        else CHAMBER_NASA_STRATA_DATA.name
        if args.chamber_nasa_strata_supplement
        else CHAMBER_RECONCILIATION_DATA.name
        if args.chamber_reconciliation_supplement
        else CHAMBER_AGE_STRATA_DATA.name
        if args.chamber_age_strata_supplement
        else CHAMBER_CASE_SERIES_DATA.name
        if args.chamber_case_series_supplement
        else CHAMBER_SYMPTOM_DATA.name
        if args.chamber_symptom_supplement
        else CHAMBER_ARCHIVE_DATA.name
        if args.chamber_archive_supplement
        else CHAMBER_TIMING_DATA.name
        if args.chamber_timing_supplement
        else CHAMBER_CASE_DATA.name
        if args.chamber_case_supplement
        else HISTORICAL_OUTCOMES_DATA.name
        if args.historical_outcomes_supplement
        else ARCHIVE_FOLLOWUP_DATA.name
        if args.archive_followup_supplement
        else FLIGHT_SURVEILLANCE_DATA.name
        if args.flight_surveillance_supplement
        else CHAMBER_PROGRAM_DATA.name
        if args.chamber_program_supplement
        else RAPID_DECOMPRESSION_DATA.name
        if args.rapid_decompression_supplement
        else ARCHIVAL_TRIAL_DATA.name
        if args.archival_trial_supplement
        else INTERNATIONAL_DATA.name
        if args.international_supplement
        else DENITROGENATION_DATA.name
        if args.denitrogenation_supplement
        else SPACEFLIGHT_DATA.name
        if args.spaceflight_supplement
        else HISTORIC_CHAMBER_DATA.name
        if args.historic_chamber_supplement
        else CROSSOVER_DATA.name
        if args.crossover_supplement
        else CLINICAL_SERIES_DATA.name
        if args.clinical_series_supplement
        else RAF_DATA.name
        if args.raf_supplement
        else CADET_DATA.name
        if args.cadet_supplement
        else EXPEDITION_DATA.name
        if args.expedition_supplement
        else PROTOCOL_DATA.name
        if args.protocol_supplement
        else HISTORICAL_DATA.name
        if args.historical_supplement
        else PUBLICATION_DATA.name
        if args.publication_supplement
        else DISCOVERY_DATA.name
        if args.discovery_supplement
        else None
    )
    if args.fac_official:
        default_output = (
            FAC_OUTPUT.with_name(f"observed-{supplement_version}.sqlite")
            if supplement_version
            else FAC_OUTPUT
        )
    if args.fac_workbooks:
        default_output = (
            FAC_PRIVATE_OUTPUT.with_name(f"case-records-{supplement_version}.local.sqlite")
            if supplement_version
            else FAC_PRIVATE_OUTPUT
        )
    if args.rojas_supplement:
        if supplement_version or args.fac_official or args.fac_workbooks:
            default_output = default_output.with_name(f"{default_output.stem}-rojas.sqlite")
        else:
            default_output = ROJAS_OUTPUT
    if args.attachment_supplement:
        if supplement_version or args.fac_official or args.fac_workbooks or args.rojas_supplement:
            default_output = default_output.with_name(f"{default_output.stem}-attachments.sqlite")
        else:
            default_output = ATTACHMENT_OUTPUT
    if args.zotero_dcs_supplement:
        if supplement_version or args.fac_official or args.fac_workbooks or args.rojas_supplement:
            default_output = default_output.with_name(f"{default_output.stem}-zotero-dcs.sqlite")
        else:
            default_output = DCS_COLLECTION_OUTPUT
    if args.publication_review:
        default_output = REVIEW_OUTPUT
    output = args.output or default_output
    digest = build(
        output,
        zotero_supplement=args.zotero_supplement,
        web_supplement=args.web_supplement,
        literature_supplement=args.literature_supplement,
        cohort_supplement=args.cohort_supplement,
        sharepoint_supplement=args.sharepoint_supplement,
        rojas_supplement=args.rojas_supplement,
        attachment_supplement=args.attachment_supplement,
        zotero_dcs_supplement=args.zotero_dcs_supplement,
        discovery_supplement=args.discovery_supplement,
        publication_supplement=args.publication_supplement,
        historical_supplement=args.historical_supplement,
        protocol_supplement=args.protocol_supplement,
        expedition_supplement=args.expedition_supplement,
        cadet_supplement=args.cadet_supplement,
        raf_supplement=args.raf_supplement,
        clinical_series_supplement=args.clinical_series_supplement,
        crossover_supplement=args.crossover_supplement,
        historic_chamber_supplement=args.historic_chamber_supplement,
        spaceflight_supplement=args.spaceflight_supplement,
        denitrogenation_supplement=args.denitrogenation_supplement,
        international_supplement=args.international_supplement,
        archival_trial_supplement=args.archival_trial_supplement,
        rapid_decompression_supplement=args.rapid_decompression_supplement,
        chamber_program_supplement=args.chamber_program_supplement,
        flight_surveillance_supplement=args.flight_surveillance_supplement,
        archive_followup_supplement=args.archive_followup_supplement,
        historical_outcomes_supplement=args.historical_outcomes_supplement,
        chamber_case_supplement=args.chamber_case_supplement,
        chamber_timing_supplement=args.chamber_timing_supplement,
        chamber_archive_supplement=args.chamber_archive_supplement,
        chamber_symptom_supplement=args.chamber_symptom_supplement,
        chamber_case_series_supplement=args.chamber_case_series_supplement,
        chamber_age_strata_supplement=args.chamber_age_strata_supplement,
        chamber_reconciliation_supplement=args.chamber_reconciliation_supplement,
        chamber_nasa_strata_supplement=args.chamber_nasa_strata_supplement,
        chamber_nasa_cases_supplement=args.chamber_nasa_cases_supplement,
        chamber_paired_exposures_supplement=args.chamber_paired_exposures_supplement,
        chamber_staged_exposures_supplement=args.chamber_staged_exposures_supplement,
        chamber_treated_case_supplement=args.chamber_treated_case_supplement,
        chamber_case_detail_supplement=args.chamber_case_detail_supplement,
        chamber_threshold_supplement=args.chamber_threshold_supplement,
        chamber_bubble_outcomes_supplement=args.chamber_bubble_outcomes_supplement,
        chamber_diagnosis_supplement=args.chamber_diagnosis_supplement,
        chamber_vge_reconciliation_supplement=args.chamber_vge_reconciliation_supplement,
        chamber_repeated_eva_supplement=args.chamber_repeated_eva_supplement,
        citation_supplement=args.citation_supplement,
        fac_official=args.fac_official,
        fac_workbooks=args.fac_workbooks,
        publication_review=args.publication_review,
    )
    print(json.dumps({"sha256": digest, "database": str(output)}))
