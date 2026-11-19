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
CITATION_DATA = ROOT / "data" / "chamber" / "v1.5"
CITATION_OUTPUT = ROOT / "artifacts" / "chamber-v1.5" / "observed.sqlite"

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


def load_supplement(db, directory, prefix, *, extra_tables=None):
    tables = {
        f"{prefix}_source": "sources.csv",
        f"{prefix}_observation": "observations.csv",
        f"{prefix}_overlap": "overlap.csv",
        **(extra_tables or {}),
    }
    manifest = json.loads((directory / "manifest.json").read_bytes())
    if set(manifest) != {"schema.sql", *tables.values()}:
        raise ValueError(f"Unexpected {prefix} supplement manifest entries")
    for name, expected in manifest.items():
        if sha256(directory / name) != expected:
            raise ValueError(f"{prefix} supplement input digest mismatch: {name}")
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


def build(
    output,
    *,
    zotero_supplement=False,
    web_supplement=False,
    literature_supplement=False,
    cohort_supplement=False,
    citation_supplement=False,
    sharepoint_supplement=False,
):
    include_citation = citation_supplement or sharepoint_supplement
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
            if sharepoint_supplement:
                load_supplement(
                    db,
                    SHAREPOINT_DATA,
                    "sharepoint",
                    extra_tables={"sharepoint_vge_positive_record": "vge_positive_records.csv"},
                )
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
    output = args.output or default_output
    digest = build(
        output,
        zotero_supplement=args.zotero_supplement,
        web_supplement=args.web_supplement,
        literature_supplement=args.literature_supplement,
        cohort_supplement=args.cohort_supplement,
        sharepoint_supplement=args.sharepoint_supplement,
        citation_supplement=args.citation_supplement,
    )
    print(json.dumps({"sha256": digest, "database": str(output)}))
