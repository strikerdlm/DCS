"""Stage page-cited clinical literature without changing TinyDCS training inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from tempfile import NamedTemporaryFile


SCHEMA_VERSION = 1
ENDPOINTS = {"clinical_dcs", "dcs_type_i", "test_aborting_bends", "vge", "evolved_gas", "other"}
DENOMINATORS = {"participants", "exposures", "sessions", "flights", "incidents", "indoctrinations", "person_time"}
SETTINGS = {"chamber", "flight", "eva", "mixed", "unknown"}
OVERLAP = {"independent", "overlapping", "unknown"}
PROFILE = (
    "altitude_ft", "prebreathe_time_min", "exercise_level", "altitude_time_min",
    "asc_rate_fpm", "prebreathe_fio2", "altitude_fio2",
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else digest(handle.read())


def write_atomic(path, payload):
    if path.is_file() and path.read_bytes() == payload:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(payload)
        temp = Path(handle.name)
    try:
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def source_slice(report):
    pages = report["physical_pages"]
    if (not isinstance(pages, list) or not pages or
            any(type(n) is not int or n < 1 for n in pages) or pages != sorted(set(pages))):
        raise ValueError("physical_pages must be an ordered list of distinct positive integers")
    path = Path(report["pdf"])
    if not path.is_file() or path.suffix.lower() != ".pdf":
        raise ValueError("A local source PDF is required")
    actual = file_hash(path)
    if actual != report["source_sha256"]:
        raise ValueError("Source PDF checksum changed")
    return path, pages, actual


def parse_local(report, cache, pdftotext, parser_version):
    path, pages, source_sha256 = source_slice(report)
    parse_key = digest(json_bytes([source_sha256, pages, parser_version, "poppler-layout"]))
    directory = cache / parse_key
    receipt_path = directory / "receipt.json"
    if receipt_path.is_file():
        receipt = read_json(receipt_path)
        if (receipt["parse_key"] == parse_key and
                {int(p["physical_page"]) for p in receipt["pages"]} == set(pages) and
                all(file_hash(directory / p["filename"]) == p["sha256"] for p in receipt["pages"])):
            return receipt
        raise ValueError("Cached page receipts failed verification")
    artifacts = []
    for number in pages:
        parsed = subprocess.run([pdftotext, "-f", str(number), "-l", str(number), "-layout",
                                 "-enc", "UTF-8", str(path), "-"], capture_output=True, timeout=90, check=True)
        body = parsed.stdout.decode("utf-8", errors="replace").strip()
        data = (f"<!-- source PDF page {number} -->\n\n{body}\n").encode()
        filename = f"pdf-page-{number:05d}.md"
        write_atomic(directory / filename, data)
        artifacts.append({"physical_page": number, "filename": filename, "sha256": digest(data),
                          "status": "extracted" if body else "ocr_required"})
    receipt = {"parse_key": parse_key, "source_sha256": source_sha256, "parser_version": parser_version,
               "parser": "poppler-layout", "pages": artifacts}
    write_atomic(receipt_path, json_bytes(receipt))
    return receipt


def check_observation(observation, pages):
    """Report missing values separately from invalid values. Zero is a valid observation."""
    essential = ("stratum_id", "cohort_id", "setting", "endpoint", "endpoint_definition",
                 "ascertainment", "numerator", "denominator", "denominator_unit", "overlap", "physical_page")
    missing = [k for k in essential if observation.get(k) in (None, "")]
    issues = []
    for field, allowed in (("setting", SETTINGS), ("endpoint", ENDPOINTS),
                           ("denominator_unit", DENOMINATORS), ("overlap", OVERLAP)):
        if field not in missing and observation[field] not in allowed:
            issues.append(f"invalid_{field}")
    if observation.get("physical_page") not in pages:
        issues.append("physical_page_outside_verified_source_range")
    n, d = observation.get("numerator"), observation.get("denominator")
    if n is not None and (type(n) is not int or n < 0):
        issues.append("invalid_numerator")
    if d is not None and (type(d) is not int or d <= 0):
        issues.append("invalid_denominator")
    if type(n) is int and type(d) is int and observation.get("denominator_unit") != "person_time" and n > d:
        issues.append("numerator_exceeds_denominator")
    if observation.get("rounded_rate_only") and n is not None:
        issues.append("integer_numerator_requires_source_evidence")
    if observation.get("review_status") != "source_verified":
        issues.append("requires_primary_source_review")
    if not observation.get("provenance_locator"):
        missing.append("provenance_locator")
    return missing, issues


def stage_report(report):
    """The extraction handoff stages observations only. Training and pooling have separate gates."""
    report_id = report["report_id"]
    report_source = {k: report[k] for k in ("source_sha256", "physical_pages")}
    report_source.update(parser=report.get("parser"), parser_version=report.get("parser_version"),
                         parse_key=report.get("parse_key"), report_id=report_id,
                         zotero_parent=report.get("zotero_parent"))
    review = {
        **report_source, "eligibility": report.get("eligibility", "pending"),
        "report_status": report.get("report_status", "available_pending"),
        "observations": [], "pooling_status": "requires_protocol_and_review",
    }
    model = {**report_source, "observations": [], "training_release": "withheld"}
    seen = set()
    for entry in report.get("observations", []):
        missing, issues = check_observation(entry, report["physical_pages"])
        identity = tuple(entry.get(k) for k in ("cohort_id", "stratum_id", "endpoint", "denominator_unit"))
        if identity in seen:
            issues.append("duplicate_observation_identity_in_report")
        seen.add(identity)
        base = {**entry, "missing_fields": missing, "validation_errors": issues}
        review["observations"].append(base)
        profile = entry.get("profile") or {}
        model_blockers = [f"missing_profile_{k}" for k in PROFILE if profile.get(k) is None]
        if entry.get("endpoint") != "clinical_dcs":
            model_blockers.append("requires_compatible_clinical_dcs_endpoint")
        if entry.get("denominator_unit") not in {"participants", "exposures"}:
            model_blockers.append("requires_eligible_people_or_exposures")
        if entry.get("overlap") != "independent":
            model_blockers.append("cohort_independence_unresolved")
        if not entry.get("repeat_exposure_handling"):
            model_blockers.append("repeat_exposure_handling_unreported")
        if not entry.get("outcome_window"):
            model_blockers.append("outcome_window_unreported")
        model["observations"].append({**base, "model_blockers": model_blockers, "release": "withheld"})
    return review, model


def project(manifest, output, *, dry_run, pdftotext=None):
    reports = manifest["reports"]
    ids = [entry["report_id"] for entry in reports]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate report IDs in manifest")
    revision = manifest["repo_revision"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("repo_revision must be a full Git object ID")
    manifest_sha256 = digest(json_bytes(manifest))
    summary = {"schema_version": SCHEMA_VERSION, "repo_revision": revision, "manifest_sha256": manifest_sha256,
               "reports": len(reports), "dry_run": dry_run}
    if dry_run:
        for report in reports:
            if report.get("pdf"):
                source_slice(report)
        return summary
    version = None
    if pdftotext:
        result = subprocess.run([pdftotext, "-v"], capture_output=True, check=True, text=True, timeout=15)
        version = next(iter((result.stderr or result.stdout).splitlines()), None)
        if not version:
            raise ValueError("Unable to identify local parser version")
    reviews, models, failures = [], [], []
    for source in reports:
        report = dict(source)
        try:
            if report.get("pdf"):
                if pdftotext:
                    cache = parse_local(report, output / "local-pages", pdftotext, version)
                    report.update(parser=cache["parser"], parser_version=cache["parser_version"],
                                  parse_key=cache["parse_key"])
                    report["parse_status"] = "ocr_required" if any(
                        row["status"] == "ocr_required" for row in cache["pages"]
                    ) else "text_extracted_pending_review"
                else:
                    source_slice(report)
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            failures.append({"report_id": report["report_id"], "error": type(error).__name__})
            report["parse_status"] = "parse_failed"
        review, model = stage_report(report)
        review["parse_status"] = report.get("parse_status", "not_run")
        reviews.append(review)
        models.append(model)
    for name, rows in (("systematic-review-staging", reviews), ("clinical-model-staging", models),
                       ("parse-errors", failures)):
        path = output / f"{name}.json"
        content = json_bytes(rows)
        write_atomic(path, content)
        summary[name + "_sha256"] = digest(content)
    summary["parse_failures"] = len(failures)
    write_atomic(output / "manifest.json", json_bytes(summary))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="Git-ignored output directory")
    parser.add_argument("--dry-run", action="store_true", help="Validate hashes and inspect scope without writing")
    parser.add_argument("--pdftotext", help="Path to the local Poppler executable. Without it, stage evidence only.")
    options = parser.parse_args()
    print(json_bytes(project(read_json(options.manifest), options.output,
                             dry_run=options.dry_run, pdftotext=options.pdftotext)).decode(), end="")


if __name__ == "__main__":
    main()
