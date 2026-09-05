"""Exploratory profile holdout and cleaning-policy sensitivity, without tuning.

Primary random cells stay frozen. Extra sensitivity cells are independently
assigned once and reused across policies. Shared cells use identical synthetic
features. The grouped experiment assigns whole altitude/prebreathe/exercise
profiles before either the baseline or surrogate is fit, keeping all durations
of one profile in the same fold.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import click
import joblib
import numpy as np
import pandas as pd

from mechanistic.adrac import fit_adrac
from scripts.evidence_common import (
    augment,
    cell_ids,
    environment,
    evidence_metadata,
    extend_partition,
    grouped_partition,
    identity,
    partition_from_ids,
    prepare_data,
    sha256,
    write_json,
)
from tinydcs.features import FEATURE_COLUMNS, extract_features
from tinydcs.metrics import empirical_coverage, point_errors
from tinydcs.simulator import ExposureProfile
from tinydcs.surrogate import TinyDcsSurrogate, TrainConfig, conformal_quantile, train_surrogate


def _baseline_prediction(model, raw):
    return model.predict(raw.altitude.to_numpy(), raw.prebreathing_time.to_numpy(),
                         raw.exercise_level.to_numpy(), raw.time_at_altitude.to_numpy())


def _agreement(y, point, lower, upper, accepted=None):
    result = {"point": point_errors(y, point), "coverage": empirical_coverage(y, lower, upper)}
    if accepted is not None:
        result["accepted_n"] = int(accepted.sum())
        result["accepted_subset_coverage"] = empirical_coverage(y[accepted], lower[accepted], upper[accepted])
    return result


def fit_comparison(raw, features, partition, training, directory, role):
    ids = cell_ids(raw, partition)
    directory.mkdir(parents=True, exist_ok=True)
    split_path = directory / "splits.json"
    write_json(split_path, ids)
    config = TrainConfig(random_state=42)
    # Baseline and final surrogate see exactly the same training cells.
    baseline = fit_adrac(raw.iloc[partition["train"]])
    base_cal = _baseline_prediction(baseline, raw.iloc[partition["cal"]])
    y_cal = raw.iloc[partition["cal"]].risk_of_decompression_sickness.to_numpy()/100
    base_q = conformal_quantile(np.abs(y_cal-base_cal), .95)
    model, splits = train_surrogate(features, FEATURE_COLUMNS, "pdcs_adrac_target",
                                   config=config, use_zero_inflated=True, partition=partition)
    prediction = model.predict(splits["test"])
    y = splits["test"].pdcs_adrac_target.to_numpy()
    base_test = _baseline_prediction(baseline, raw.iloc[partition["test"]])
    base_result = _agreement(y, base_test, np.maximum(0, base_test-base_q), np.minimum(1, base_test+base_q))
    result = _agreement(y, prediction["point"], prediction["lower"], prediction["upper"], prediction["in_envelope"])
    model.metadata = evidence_metadata(training, ids, config, model.feature_names, "zero_inflated", metrics=result)
    model.metadata.update(evidence_role=role, quantitative_enabled=False,
                          release_status="exploratory artifact, not the deployed model",
                          partition_ids_path=str(split_path), partition_ids_file_sha256=sha256(split_path))
    model.save(str(directory / "surrogate.joblib"))
    joblib.dump({"beta_1": baseline.beta_1, "beta_2": baseline.beta_2, "beta": baseline.beta.tolist(),
                 "feature_names": list(baseline.feature_names), "probability_q": float(base_q),
                 "metadata": evidence_metadata(training, ids,
                     {"fit": "bounded least squares on logit targets", "epsilon": 1e-6},
                     baseline.feature_names, "global_probability_residual") |
                     {"evidence_role": role, "quantitative_enabled": False}}, directory / "baseline.joblib")
    predictions = raw.iloc[partition["test"]].copy()
    predictions["target_probability"] = y
    predictions["baseline_probability"] = base_test
    for name in ("point", "lower", "upper", "in_envelope"):
        predictions["surrogate_" + name] = prediction[name]
    predictions.to_parquet(directory / "test_predictions.parquet", index=False)
    return {"metadata": model.metadata, "baseline": base_result, "surrogate": result,
            "baseline_probability_q": float(base_q),
            "partition_counts": {k: len(v) for k, v in partition.items()}}


def duration_audit(surrogate):
    """Sweep complete constant physical profiles, recomputing all features."""
    altitude = list(range(18000, 40001, 500))
    prebreathe = [0, 15, 30, 45, 60]
    workloads = [0., .1, .45, 1.1, 1.5]
    durations = list(range(10, 241, 10))
    profiles = [(alt, pb, work) for alt in altitude for pb in prebreathe for work in workloads]
    records = []
    for alt, pb, work in profiles:
        for duration in durations:
            records.append(asdict(extract_features(ExposureProfile(
                target_altitude_ft=alt, prebreathe_duration_min=pb,
                altitude_duration_min=duration, altitude_i_ex_trajectory=work))))
    X = pd.DataFrame(records)
    prediction = surrogate.predict(X)
    point = prediction["point"].reshape(len(profiles), len(durations))
    delta = np.diff(point, axis=1)
    violations = np.argwhere(delta < -1e-10)
    examples = [{"altitude_ft": profiles[i][0], "prebreathe_min": profiles[i][1],
                 "constant_i_ex_lmin": profiles[i][2], "time_before_min": durations[j],
                 "time_after_min": durations[j+1], "probability_change": float(delta[i, j])}
                for i, j in violations[:10]]
    return {"model_id": surrogate.metadata["model_id"], "feature_names": surrogate.feature_names,
            "fixture_kind": "complete constant physical profiles; dependent features recomputed at every duration",
            "altitude_ft": altitude, "prebreathe_min": prebreathe,
            "constant_i_ex_lmin": workloads, "duration_min": durations,
            "profiles_n": len(profiles), "rows_n": len(records),
            "adjacent_comparisons_n": int(delta.size), "violations_n": len(violations),
            "minimum_probability_change": float(delta.min()),
            "support_accepted_n": int(prediction["in_envelope"].sum()),
            "tolerance": 1e-10, "passed": not len(violations), "examples": examples,
            "interpretation": "finite grid check of duration monotonicity under constant workload, not a proof for arbitrary changing trajectories"}


@click.command()
@click.option("--training", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--raw-policy", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--rescaled-policy", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--reference-metrics", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--input-model", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--output-dir", required=True, type=click.Path(file_okay=False))
def main(training, raw_policy, rescaled_policy, reference_metrics, input_model, output_dir):
    raw, features, _frozen, frozen_ids = prepare_data(training, 42, reference_metrics)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    model = TinyDcsSurrogate.load(input_model)
    reference = json.loads(Path(reference_metrics).read_text())
    if model.metadata["model_id"] != reference["metadata"]["model_id"]:
        raise click.ClickException("duration audit model does not match primary metrics")
    click.echo("Auditing complete constant-workload duration profiles ...")
    audit = duration_audit(model)
    write_json(out / "duration_monotonicity.json", audit)
    click.echo(f"Duration audit: {audit['violations_n']} violations / {audit['adjacent_comparisons_n']} comparisons")

    grouped, groups = grouped_partition(raw, seed=42)
    click.echo("Fitting profile-grouped holdout ...")
    grouped_result = fit_comparison(raw, features, grouped, training, out / "grouped", "profile-grouped holdout")
    group_ids = {key: sorted(groups.iloc[idx].unique().tolist()) for key, idx in grouped.items()}
    if any(set(group_ids[a]) & set(group_ids[b]) for a, b in (("train", "cal"), ("train", "test"), ("cal", "test"))):
        raise ValueError("profile leakage across grouped partitions")
    write_json(out / "grouped/profile_groups.json", group_ids)
    grouped_result["profile_group_counts"] = {k: len(v) for k, v in group_ids.items()}
    grouped_result["group_definition"] = ["altitude", "prebreathing_time", "exercise_level"]
    grouped_result["group_ids_sha256"] = identity(group_ids)
    grouped_result["time_rows_never_cross_partitions"] = True

    policies = {"primary": (Path(training), raw),
                "raw": (Path(raw_policy), pd.read_parquet(raw_policy).reset_index(drop=True)),
                "rescaled": (Path(rescaled_policy), pd.read_parquet(rescaled_policy).reset_index(drop=True))}
    union = pd.concat([table for _, table in policies.values()]).drop_duplicates("cell_id").reset_index(drop=True)
    common_ids = extend_partition(union.cell_id.tolist(), frozen_ids, seed=42)
    write_json(out / "sensitivity_common_splits.json", common_ids)
    # Preserve primary synthetic features exactly; generate only additional cells.
    feature_lookup = features.copy()
    feature_lookup.index = raw.cell_id
    extras = union.loc[~union.cell_id.isin(raw.cell_id)].reset_index(drop=True)
    if len(extras):
        extra_features = augment(extras, seed=42)
        extra_features.index = extras.cell_id
        feature_lookup = pd.concat([feature_lookup, extra_features])
    results = {}
    for policy, (path, table) in policies.items():
        click.echo(f"Refitting cleaning sensitivity policy {policy} ({len(table)} cells) ...")
        policy_features = feature_lookup.loc[table.cell_id].reset_index(drop=True).copy()
        policy_features["pdcs_adrac_target"] = table.risk_of_decompression_sickness.to_numpy()/100
        partition = partition_from_ids(table, common_ids)
        results[policy] = fit_comparison(table, policy_features, partition, path,
                                         out / "sensitivity" / policy, "exploratory cleaning sensitivity")
    # Like-for-like target comparison on cells eligible under every policy.
    common_test = set.intersection(*(set(table.iloc[partition_from_ids(table, common_ids)["test"]].cell_id)
                                     for _, table in policies.values()))
    for policy in policies:
        rows = pd.read_parquet(out / "sensitivity" / policy / "test_predictions.parquet")
        common_rows = rows.loc[rows.cell_id.isin(common_test)]
        results[policy]["shared_test_cells"] = _agreement(common_rows.target_probability.to_numpy(),
            common_rows.surrogate_point.to_numpy(), common_rows.surrogate_lower.to_numpy(),
            common_rows.surrogate_upper.to_numpy())
    summary = {
        "schema_version": "accuracy-v3", "target_kind": "model_probability", "clinical_validation": False,
        "evidence_role": "exploratory robustness; primary specification and thresholds remain fixed",
        "coverage_interpretation": "95% Wilson bounds are descriptive; dependent grid cells are not IID clinical observations",
        "environment": environment(), "command": [sys.executable, *sys.argv],
        "random_heldout": {"reference": reference_metrics, "metadata": reference["metadata"],
                           "surrogate": reference["tinydcs_random_test"], "baseline": reference["adrac_baseline_random_test"]},
        "leave_one_altitude_out": {"surrogate": reference["leave_one_altitude_out_surrogate"],
                                   "baseline": reference["leave_one_altitude_out_baseline"]},
        "profile_grouped_holdout": grouped_result,
        "cleaning_sensitivity": {"policies": results, "common_partition_id": identity(common_ids),
                                  "shared_test_cells_n": len(common_test),
                                  "shared_feature_vectors_identical": True,
                                  "method": "Frozen primary cells retain membership and synthetic features; extra cells are seeded once. Each policy refits baseline and surrogate using training only, then recalibrates on calibration cells."},
        "duration_monotonicity": audit,
    }
    write_json(out / "robustness.json", summary)
    click.echo(f"Wrote {out / 'robustness.json'}")


if __name__ == "__main__":
    main()
