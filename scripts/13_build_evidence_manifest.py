"""Validate artifact links and emit a hashed, reproducible evidence inventory."""
from __future__ import annotations

import json
import subprocess
import sys
from importlib import metadata as packages
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import click
import numpy as np

from scripts.evidence_common import environment, identity, sha256, write_json


def _read(path):
    return json.loads(Path(path).read_text())


def _require(condition, message):
    if not condition:
        raise click.ClickException(message)


def validate(artifacts, frontend):
    primary = _read(artifacts / "metrics.json")
    meta = primary["metadata"]
    ids = _read(artifacts / "metrics.splits.json")
    _require(meta["dataset_id"] == sha256(artifacts / "clean.parquet"), "primary dataset SHA is stale")
    _require(meta["split_id"] == identity(ids), "primary split SHA is stale")
    expected_release = (primary["tinydcs_random_test"]["point"]["mae"] <= .03 and
                        primary["tinydcs_random_test"]["conformal_coverage"]["coverage"] >= .94)
    _require(meta["quantitative_enabled"] == expected_release, "primary release flag differs from fixed criteria")
    compact = _read(artifacts / "compact_comparison.json")
    fair = _read(artifacts / "fair_baseline_ablation.json")
    for bundle in [*(row["metadata"] for row in compact), fair["metadata"]]:
        _require(bundle["dataset_id"] == meta["dataset_id"] and bundle["split_id"] == meta["split_id"],
                 "comparison does not share the primary data and partition")
        _require(bundle["partition_counts"] == {k: len(v) for k, v in ids.items()}, "comparison partition counts differ")
    for row in compact:
        expected = row["point"]["mae"] <= .03 and row["coverage"]["coverage"] >= .94
        _require(row["metadata"]["quantitative_enabled"] == expected, "compact release gate differs from fixed criteria")
    exported = _read(artifacts / "onnx/metadata.json")
    _require(exported["source_model_sha256"] == sha256(artifacts / "surrogate.joblib"), "ONNX source model changed; rerun export")
    _require(exported["evidence"]["model_id"] == meta["model_id"], "ONNX model identifier is stale")
    for filename, expected in exported["graph_sha256"].items():
        _require(sha256(artifacts / "onnx" / filename) == expected, "ONNX graph SHA mismatch")
    benchmark = _read(artifacts / "onnx/benchmark.json")
    _require(benchmark["parity"]["support_gate_identical"] and
             max(benchmark["parity"]["final_output_max_abs_error"].values()) <= benchmark["parity"]["tolerance"],
             "ONNX final output parity failed")
    validation = _read(frontend / "adrac_validation.json")
    coefficients = _read(frontend / "adrac_coefficients.json")
    _require(validation["metadata"]["coefficients_sha256"] == sha256(frontend / "adrac_coefficients.json"), "frontend coefficients changed after export")
    for payload in (validation, coefficients):
        _require(payload["metadata"]["dataset_id"] == meta["dataset_id"] and
                 payload["metadata"]["split_id"] == meta["split_id"] and
                 payload["metadata"]["baseline_artifact_sha256"] == sha256(artifacts / "adrac.joblib"),
                 "frontend baseline provenance is stale")
    _require([row["cellId"] for row in validation["rows"]] == ids["test"], "frontend rows are not the frozen test cells in order")
    _require(all(np.isclose(row["residual"], row["predictedRisk"]-row["riskOfDcs"], rtol=0, atol=1e-12)
                 and np.isclose(row["absError"], abs(row["residual"]), rtol=0, atol=1e-12)
                 for row in validation["rows"]), "frontend residual arithmetic is inconsistent")
    robust = _read(artifacts / "robustness/robustness.json")
    _require(robust["random_heldout"]["metadata"]["model_id"] == meta["model_id"], "robustness reference is stale")
    _require(robust["profile_grouped_holdout"]["time_rows_never_cross_partitions"], "profile groups leak")
    _require(robust["duration_monotonicity"]["passed"], "physical duration monotonicity audit failed")
    _require(robust["cleaning_sensitivity"]["shared_test_cells_n"] == len(ids["test"]), "sensitivity lost primary test cells")
    return primary, compact, fair, robust, benchmark


def commands(artifact_dir, frontend_dir):
    a, f = str(artifact_dir), str(frontend_dir)
    prefix = "env OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 MPLCONFIGDIR=/tmp/dcs-matplotlib .venv/bin/python3.12"
    return [
        f"{prefix} scripts/01_clean_data.py --input legacy/Model_Rel_Candidate/DCS_Risk_DB_2025.csv --output {a}/clean.parquet --report {a}/data_quality.md",
        f"{prefix} scripts/04_train_adrac_surrogate.py --training {a}/clean.parquet --output-surrogate {a}/surrogate.joblib --output-baseline {a}/adrac.joblib --output-metrics {a}/metrics.json --output-figures {a}/figures --run-leave-one-altitude-out --zi",
        f"{prefix} scripts/06_train_compact_surrogate.py --training {a}/clean.parquet --reference-metrics {a}/metrics.json --output-metrics {a}/compact_comparison.json",
        f"{prefix} scripts/07_export_zero_inflated_onnx.py --input-model {a}/surrogate.joblib --output-dir {a}/onnx --benchmark-n 10000 --tolerance 1e-4",
        f"{prefix} scripts/10_fair_baseline_and_ablation.py --training {a}/clean.parquet --reference-metrics {a}/metrics.json --output {a}/fair_baseline_ablation.json",
        f"{prefix} scripts/11_grouped_cleaning_validation.py --training {a}/clean.parquet --raw-policy {a}/clean_sensitivity_raw.parquet --rescaled-policy {a}/clean_sensitivity_rescaled.parquet --reference-metrics {a}/metrics.json --input-model {a}/surrogate.joblib --output-dir {a}/robustness",
        f"{prefix} scripts/12_export_frontend_evidence.py --training {a}/clean.parquet --reference-metrics {a}/metrics.json --baseline {a}/adrac.joblib --output-dir {f}",
        f"{prefix} -m pytest tests/test_evidence_pipeline.py tests/test_statistical_accuracy.py -q",
        f"{prefix} scripts/13_build_evidence_manifest.py --artifact-dir {a} --frontend-data-dir {f}",
    ]


@click.command()
@click.option("--artifact-dir", required=True, type=click.Path(exists=True, file_okay=False))
@click.option("--frontend-data-dir", default="frontend/src/data", type=click.Path(exists=True, file_okay=False))
@click.option("--tracked-summary", default="docs/evidence/accuracy-v3.json", type=click.Path(dir_okay=False),
              help="Small tracked evidence summary; generated model binaries remain ignored.")
def main(artifact_dir, frontend_data_dir, tracked_summary):
    artifact_dir, frontend = Path(artifact_dir), Path(frontend_data_dir)
    primary, compact, fair, robust, benchmark = validate(artifact_dir, frontend)
    env = environment()
    env["all_installed_packages"] = dict(sorted((dist.metadata["Name"], dist.version) for dist in packages.distributions() if dist.metadata["Name"]))
    write_json(artifact_dir / "environment.json", env)
    (artifact_dir / "requirements.lock.txt").write_text("\n".join(
        f"{name}=={version}" for name, version in env["all_installed_packages"].items()) + "\n")
    reproduce = commands(artifact_dir, frontend)
    write_json(artifact_dir / "reproduce_commands.json", {"cwd": str(ROOT), "commands": reproduce,
               "note": "Use the recorded environment; rerun in order. Runtime latency depends on host load. Legacy artifacts are retained and superseded."})
    s = primary["tinydcs_random_test"]
    g = robust["profile_grouped_holdout"]
    rows = ["# Accuracy-v3 evidence", "", "Research model-grid emulation; no clinical or operational validation.", "",
            "| Evidence | Cells tested | Surrogate MAE | Descriptive coverage | Baseline MAE |",
            "|---|---:|---:|---:|---:|",
            f"| Frozen random cells | {s['n']} | {s['point']['mae']:.6f} | {s['conformal_coverage']['coverage']:.6f} | {primary['adrac_baseline_random_test']['point']['mae']:.6f} |",
            f"| Whole-profile holdout | {g['surrogate']['point']['n']} | {g['surrogate']['point']['mae']:.6f} | {g['surrogate']['coverage']['coverage']:.6f} | {g['baseline']['point']['mae']:.6f} |"]
    for policy, result in robust["cleaning_sensitivity"]["policies"].items():
        rows.append(f"| Cleaning: {policy} | {result['surrogate']['point']['n']} | {result['surrogate']['point']['mae']:.6f} | {result['surrogate']['coverage']['coverage']:.6f} | {result['baseline']['point']['mae']:.6f} |")
    rows.extend(["", "MAE and interval widths use probabilities, not percentage points. The 95% Wilson bounds in JSON are descriptive because grid cells are dependent. Grouped and cleaning results are exploratory; no thresholds or model choices were tuned to these tests.", "",
                 "Leave-one-altitude-out extrapolation is reported separately in metrics.json and robustness/robustness.json; its errors do not support unrestricted altitude extrapolation.", "",
                 f"The fair calibration-selected altitude-band baseline has MAE {fair['fair_baseline']['best_aft_mae']:.6f}; the primary surrogate's improvement over it is {fair['honest_multipliers']['vs_best_aft']:.3f}x. Ordinal exercise outperforms the synthetic-VO2 feature version on this grid; continuous workload was not independently measured.", "",
                 f"Both deployed ONNX graphs total {benchmark['combined_inference']['total_size_kb']:.1f} KiB. Final probability/interval parity error is at most {benchmark['parity']['max_abs_probability_and_interval']:.3g} on 10,000 feasible profiles. CPU batch-amortized and single-row timing are separate; no wearable or MCU timing is claimed.", "",
                 f"The duration check found {robust['duration_monotonicity']['violations_n']} decreases in {robust['duration_monotonicity']['adjacent_comparisons_n']} adjacent comparisons from complete constant-workload profiles. This finite check is not a proof for changing workloads.", "",
                 "All smaller variants are reported without replacing the prespecified primary model. Fixed release checks use MAE ≤0.03 and empirical coverage ≥0.94 at nominal 0.95; unsupported profiles still abstain. Standalone ADRAC baseline exports contain no invented interval.", "",
                 "Reproduction commands, exact installed package versions, source/artifact SHA-256 hashes, and stable partition cell identifiers accompany this report. Other artifact directories and legacy results are preserved but superseded for current accuracy claims."])
    (artifact_dir / "EVIDENCE.md").write_text("\n".join(rows) + "\n")
    files = [p for p in artifact_dir.rglob("*") if p.is_file() and p.name != "manifest.json"]
    files.extend([frontend / "adrac_coefficients.json", frontend / "adrac_validation.json"])
    sources = [*ROOT.glob("scripts/*.py"), *ROOT.glob("tinydcs/*.py"), *ROOT.glob("mechanistic/*.py"),
               ROOT / "pyproject.toml", ROOT / "tests/test_evidence_pipeline.py"]
    manifest = {"schema_version": "accuracy-v3", "status": "validated model-emulation evidence, research only",
                "primary_metadata": primary["metadata"], "validation": "artifact links, frozen cell IDs, release criteria, final ONNX outputs and frontend residuals checked",
                "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "source_snapshot": "working tree at manifest generation; hashes cover uncommitted corrections",
                "artifact_sha256": {str(p): {"sha256": sha256(p), "bytes": p.stat().st_size} for p in sorted(files)},
                "source_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in sorted(sources)},
                "superseded_artifact_locations": [str(p) for p in artifact_dir.parent.iterdir() if p.is_dir() and p != artifact_dir],
                "legacy_policy": "preserved for provenance; not authoritative for current model or validation claims",
                "commands": reproduce, "environment_file": str(artifact_dir / "environment.json")}
    write_json(artifact_dir / "manifest.json", manifest)
    # Preserve sufficient evidence in source control without duplicating model
    # binaries, synthetic feature tables, full split IDs, or repeated metadata.
    def without_metadata(value):
        return {key: item for key, item in value.items() if key != "metadata"}
    grouped = robust["profile_grouped_holdout"]
    policy_results = robust["cleaning_sensitivity"]["policies"]
    summary = {
        "schema_version": "accuracy-v3", "scope": "model-generated grid emulation; research only",
        "clinical_validation": False,
        "interpretation": "Probability-valued model targets are not binary outcomes. Coverage and Wilson95 bounds are descriptive for dependent grid cells. No clinical Brier score, clinical AUROC, clinical calibration, or prospective validation is claimed.",
        "primary_metadata": primary["metadata"],
        "primary_partition_counts": {k: len(v) for k, v in _read(artifact_dir / "metrics.splits.json").items()},
        "random_heldout": {"surrogate": primary["tinydcs_random_test"], "baseline": primary["adrac_baseline_random_test"]},
        "leave_one_altitude_out": robust["leave_one_altitude_out"],
        "profile_grouped_holdout": without_metadata(grouped) | {
            "dataset_id": grouped["metadata"]["dataset_id"], "split_id": grouped["metadata"]["split_id"],
            "model_id": grouped["metadata"]["model_id"], "quantitative_enabled": False},
        "cleaning_sensitivity": {key: value for key, value in robust["cleaning_sensitivity"].items() if key != "policies"} | {
            "policies": {policy: without_metadata(result) | {
                "dataset_id": result["metadata"]["dataset_id"], "split_id": result["metadata"]["split_id"],
                "model_id": result["metadata"]["model_id"], "quantitative_enabled": False}
                for policy, result in policy_results.items()}},
        "fair_baseline": fair["fair_baseline"],
        "ablation": {key: without_metadata(value) if isinstance(value, dict) else value
                     for key, value in fair["ablation"].items()},
        "honest_multipliers": fair["honest_multipliers"],
        "circularity_verdict": fair["circularity_verdict"],
        "compact_variants": [without_metadata(row) | {"model_id": row["metadata"]["model_id"],
                             "quantitative_enabled": row["metadata"]["quantitative_enabled"]} for row in compact],
        "onnx": without_metadata(benchmark),
        "duration_monotonicity": robust["duration_monotonicity"],
        "environment": environment(),
        "requirements_lock_sha256": sha256(artifact_dir / "requirements.lock.txt"),
        "commands": reproduce,
        "raw_source_sha256": sha256(ROOT / "legacy/Model_Rel_Candidate/DCS_Risk_DB_2025.csv"),
        "artifact_sha256": manifest["artifact_sha256"], "source_sha256": manifest["source_sha256"],
        "manifest_sha256": sha256(artifact_dir / "manifest.json"),
        "superseded_artifact_locations": manifest["superseded_artifact_locations"],
        "legacy_policy": manifest["legacy_policy"],
    }
    write_json(tracked_summary, summary)
    click.echo(f"Validated {len(files)} artifacts; wrote {artifact_dir / 'manifest.json'}")
    click.echo(f"Tracked evidence summary: {tracked_summary}")


if __name__ == "__main__":
    main()
