"""Attach the bibliographic register to a complete public chamber database."""

import csv
import json
from pathlib import Path

from scripts.build_chamber_database import sha256
from scripts.review_identity import resolve
from scripts.review_legacy import legacy_records

DIRECTORY = Path("data/chamber/publication-review")


def _insert(db, table, columns, rows):
    """Table and column names come only from this module."""
    names = columns.split()
    values = ",".join(":" + name for name in names)
    db.executemany(f"INSERT INTO {table} ({','.join(names)}) VALUES ({values})", rows)


def _load_inputs(db, root, directory, legacy):
    manifest = json.loads((directory / "manifest.json").read_bytes())
    streams = {r["stream"] for r in legacy}
    files = {
        p.relative_to(root).as_posix()
        for p in directory.iterdir()
        if p.is_file() and p.name != "manifest.json"
    }
    if manifest.keys() != files | streams:
        raise ValueError("Publication register manifest does not match input files")
    for name, expected in sorted(manifest.items()):
        if sha256(root / name) != expected:
            raise ValueError(f"Publication register digest mismatch: {name}")
        existing = db.execute("SELECT sha256 FROM frozen_input WHERE path=?", (name,)).fetchone()
        if existing is None:
            db.execute("INSERT INTO frozen_input VALUES (?,?)", (name, expected))
        elif existing[0] != expected:
            raise ValueError(f"Conflicting frozen input: {name}")


def _new_records(db, directory):
    for path in sorted(directory.glob("retrievals-*.json")):
        snapshot = (DIRECTORY / path.name).as_posix()
        for run in json.loads(path.read_bytes()):
            run_id = run["id"]
            db.execute(
                "INSERT INTO review_retrieval VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    run_id,
                    run["date"],
                    run["provider"],
                    run["operation"],
                    json.dumps(run["params"]),
                    run["reported_total"],
                    len(run["records"]),
                    run["status"],
                    run["note"],
                    snapshot,
                ),
            )
            for position, raw in enumerate(run["records"], 1):
                yield {
                    "record_key": run_id + "#" + raw["id"],
                    "stream": run_id,
                    "source_key": raw["id"],
                    "input_path": snapshot,
                    "run_id": run_id,
                    "result_position": position,
                    "title": raw["title"],
                    "year": raw.get("year"),
                    "doi": (raw.get("doi") or "").lower() or None,
                    "pmid": raw.get("pmid"),
                    "openalex_id": raw.get("openalex_id"),
                    "url": raw.get("url"),
                    "raw": raw,
                }


def _display_priority(record):
    """Prefer a MED record or indexed title over an intake label or printed reference."""
    return (
        not (record["run_id"] and record["pmid"]),
        not bool(record["run_id"]),
        "title" not in record["raw"],
        record["record_key"],
    )


def load_register(db, root):
    directory = root / DIRECTORY
    records = [
        dict(row, input_path=row["stream"], run_id=None, result_position=None)
        for row in legacy_records(root)
    ]
    _load_inputs(db, root, directory, records)
    db.executescript((directory / "schema.sql").read_text(encoding="utf-8"))
    records.extend(_new_records(db, directory))
    curation = json.loads((directory / "curation.json").read_bytes())
    aliases = {r["record_key"]: r["report_id"] for r in curation["aliases"]}
    mapping, candidates = resolve(records, aliases)

    titles = {}
    for record in sorted(records, key=_display_priority):
        report_id = mapping[record["record_key"]]
        titles.setdefault(report_id, record["title"])
        record["report_id"] = report_id
        record["metadata_json"] = json.dumps(record["raw"], ensure_ascii=False, sort_keys=True)
    preferred_titles = curation.get("report_titles", {})
    if unknown_reports := preferred_titles.keys() - titles.keys():
        raise ValueError(f"Preferred titles reference unknown reports: {sorted(unknown_reports)}")
    titles.update(preferred_titles)
    db.executemany("INSERT INTO review_report VALUES (?,?)", sorted(titles.items()))
    _insert(
        db,
        "review_record",
        "record_key report_id stream source_key input_path run_id result_position "
        "title year doi pmid openalex_id url metadata_json",
        records,
    )
    db.executemany("INSERT INTO review_identity_candidate VALUES (?,?,?)", candidates)
    _insert(
        db,
        "review_identity_assignment",
        "record_key report_id basis evidence_url",
        curation["aliases"],
    )
    _insert(db, "review_study", "study_id label period setting", curation["studies"])
    _insert(db, "review_study_report", "study_id report_id role locator", curation["study_reports"])
    _insert(
        db,
        "review_report_relation",
        "left_report right_report relationship evidence evidence_url",
        curation["relations"],
    )
    _insert(
        db,
        "review_quality_check",
        "doi checked_on provider query status detail evidence_url",
        json.loads((directory / "quality.json").read_bytes()),
    )
    workflow_paths = [
        *directory.glob("*pilot*.json"),
        *directory.glob("screening-batch-*.json"),
        *directory.glob("analysis-selection-batch-*.json"),
        directory / "prisma-flow.json",
    ]
    for path in sorted(workflow_paths):
        input_path = (DIRECTORY / path.name).as_posix()
        content = path.read_text(encoding="utf-8")
        db.execute(
            "INSERT INTO review_workflow_document VALUES (?,?)",
            (input_path, content),
        )
        if path.name.startswith("analysis-selection-batch-"):
            selections = json.loads(content)["selections"]
            _insert(
                db,
                "review_analysis_selection",
                "input_path selection_id study_id report_id record_key risk_set_id analysis "
                "chamber_role cases denominator counting_unit exposure_period endpoint outcome_window "
                "disposition locator primary_url source_cells_json rationale reported_effect_json",
                (
                    dict(
                        row,
                        input_path=input_path,
                        source_cells_json=json.dumps(row["source_cells"], ensure_ascii=False),
                        reported_effect_json=(
                            json.dumps(row["reported_effect"], ensure_ascii=False)
                            if row.get("reported_effect") is not None else None
                        ),
                    )
                    for row in selections
                ),
            )
    if db.execute("""
        SELECT 1 FROM review_analysis_selection s JOIN review_record r USING(record_key)
        WHERE s.report_id != r.report_id LIMIT 1
    """).fetchone():
        raise ValueError("Analysis selection refers to a source occurrence for a different report")
    with (directory / "screening.csv").open(encoding="utf-8", newline="") as stream:
        _insert(
            db,
            "review_screening",
            "record_key reviewer stage revision decided_on decision reason locator",
            csv.DictReader(stream),
        )
    if db.execute("PRAGMA foreign_key_check").fetchone():
        raise ValueError("Invalid reference in publication register")
    if db.execute("PRAGMA integrity_check").fetchone() != ("ok",):
        raise ValueError("Invalid publication database")
