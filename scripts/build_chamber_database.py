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


def load_supplement(db, directory, prefix, *, extra_tables=None, create_schema=True):
    tables = {
        f"{prefix}_source": "sources.csv",
        f"{prefix}_observation": "observations.csv",
        f"{prefix}_overlap": "overlap.csv",
        **(extra_tables or {}),
    }
    manifest = json.loads((directory / "manifest.json").read_bytes())
    required = set(tables.values())
    if create_schema:
        required.add("schema.sql")
    if set(manifest) != required:
        raise ValueError(f"Unexpected {directory.name} supplement manifest entries")
    for name, expected in manifest.items():
        if sha256(directory / name) != expected:
            raise ValueError(f"{prefix} supplement input digest mismatch: {name}")
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
    fac_official=False,
    fac_workbooks=None,
    publication_review=False,
):
    include_fac = fac_official or fac_workbooks is not None or publication_review
    cadet_supplement = cadet_supplement or publication_review
    rojas_supplement = rojas_supplement or publication_review
    zotero_dcs_supplement = zotero_dcs_supplement or publication_review
    include_attachments = attachment_supplement or zotero_dcs_supplement
    include_expedition = expedition_supplement or cadet_supplement
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
            if cadet_supplement:
                load_supplement(
                    db,
                    CADET_DATA,
                    "publication",
                    extra_tables={
                        **PUBLICATION_SEARCH_TABLES,
                        "publication_reported_rate": "reported_rates.csv",
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
    supplement_version = (
        CADET_DATA.name
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
        citation_supplement=args.citation_supplement,
        fac_official=args.fac_official,
        fac_workbooks=args.fac_workbooks,
        publication_review=args.publication_review,
    )
    print(json.dumps({"sha256": digest, "database": str(output)}))
