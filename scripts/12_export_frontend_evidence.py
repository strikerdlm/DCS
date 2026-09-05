"""Export the train-only ADRAC fit and every frozen heldout cell for the UI."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import click
import joblib
import numpy as np

from mechanistic.adrac import AdracModel
from scripts.evidence_common import environment, identity, prepare_data, sha256, write_json
from tinydcs.metrics import point_errors


@click.command()
@click.option("--training", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--reference-metrics", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--baseline", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--output-dir", required=True, type=click.Path(file_okay=False))
@click.option("--refresh-baseline-metadata", is_flag=True,
              help="Repair prior accuracy-v3 baseline metadata without altering fitted coefficients.")
def main(training, reference_metrics, baseline, output_dir, refresh_baseline_metadata):
    raw, _, partition, ids = prepare_data(training, 42, reference_metrics)
    bundle = joblib.load(baseline)
    reference = json.loads(Path(reference_metrics).read_text())
    if (bundle.get("version") != "accuracy-v3" or
            bundle["metadata"]["dataset_id"] != sha256(training) or
            bundle["metadata"]["split_id"] != identity(ids)):
        raise click.ClickException("baseline provenance does not match primary frozen cells")
    model = AdracModel(bundle["beta_1"], bundle["beta_2"], np.asarray(bundle["beta"]),
                       tuple(bundle["feature_names"]))
    test = raw.iloc[partition["test"]]
    prediction = model.predict(test.altitude.to_numpy(), test.prebreathing_time.to_numpy(),
                               test.exercise_level.to_numpy(), test.time_at_altitude.to_numpy())
    target = test.risk_of_decompression_sickness.to_numpy()/100
    metrics = point_errors(target, prediction)
    expected = reference["adrac_baseline_random_test"]["point"]
    if not all(np.isclose(metrics[key], expected[key], atol=1e-12, rtol=0) for key in ("mae", "rmse", "r2")):
        raise click.ClickException("fresh baseline test predictions differ from recorded primary metrics")
    if refresh_baseline_metadata:
        # Mirrors the corrected baseline metadata in script 04. Fitted point
        # parameters are never recomputed, and the frozen model ID is retained.
        bundle["metadata"] = {key: value for key, value in reference["metadata"].items()
                              if key not in {"release_criteria", "vo2_provenance"}} | {
            "model_id": "adrac-train-only-"+identity(ids)[:12],
            "training_config": {"estimator": "bounded_linear_least_squares", "fit_rows": len(ids["train"])},
            "feature_names": list(model.feature_names),
            "interval_kind": "unavailable", "quantitative_enabled": True,
            "limitations": "Re-fitted model-grid baseline, not original published ADRAC coefficients or clinical validation. No uncertainty interval.",
        }
        joblib.dump(bundle, baseline)
    counts = {"n_total": len(raw), "n_train": len(ids["train"]),
              "n_calibration": len(ids["cal"]), "n_test": len(ids["test"])}
    metadata = {
        "schema_version": "accuracy-v3", "model_id": bundle["metadata"]["model_id"],
        "dataset_id": sha256(training), "split_id": identity(ids),
        "split": "held-out test", "split_seed": 42,
        "split_fractions": {"train": .65, "calibration": .20, "test": .15},
        **counts,
        "partition_cell_id_sha256": {k: identity(value) for k, value in ids.items()},
        "target_kind": "model_probability", "clinical_validation": False,
        "target_provenance": "primary cleaned ADRAC model-generated grid; disputed scaling cells excluded",
        "model_kind": "ADRAC log-logistic AFT functional form fitted on training cells only",
        "training_config": {"fit": "bounded least squares on logit targets", "probability_epsilon": 1e-6,
                            "feature_names": list(model.feature_names)},
        "validation_unit": "percentage_points", "row_risk_unit": "percent",
        "residual_definition": "predictedRisk - riskOfDcs; percentage points",
        "intervals": "none exported for the standalone closed-form baseline",
        "baseline_artifact": str(baseline), "baseline_artifact_sha256": sha256(baseline),
        "reference_metrics": str(reference_metrics), "reference_metrics_sha256": sha256(reference_metrics),
        "partition_file": str(Path(reference_metrics).with_suffix(".splits.json")),
        "partition_file_sha256": sha256(Path(reference_metrics).with_suffix(".splits.json")),
        "environment": environment(), "command": [sys.executable, *sys.argv],
    }
    coefficients = {"beta_1": float(model.beta_1), "beta_2": float(model.beta_2),
                    "beta": model.beta.tolist(), "feature_names": list(model.feature_names),
                    "metadata": metadata}
    records = []
    for row, p in zip(test.itertuples(index=False), prediction):
        value = float(p*100)
        residual = value - float(row.risk_of_decompression_sickness)
        records.append({"cellId": str(row.cell_id), "altitude": float(row.altitude),
                        "prebreathingTime": float(row.prebreathing_time),
                        "exerciseLevel": str(row.exercise_level), "timeAtAltitude": float(row.time_at_altitude),
                        "riskOfDcs": float(row.risk_of_decompression_sickness), "predictedRisk": value,
                        "residual": residual, "absError": abs(residual)})
    output = Path(output_dir)
    write_json(output / "adrac_coefficients.json", coefficients)
    write_json(output / "adrac_validation.json", {
        "metadata": metadata | {"coefficients_sha256": sha256(output / "adrac_coefficients.json")},
        "metrics": {"mae": metrics["mae"]*100, "rmse": metrics["rmse"]*100,
                    "r2": metrics["r2"], **counts, "n_sample": len(records), "split": "held-out test"},
        "deployed_surrogate_evidence": {"metadata": reference["metadata"],
                                         "random_test": reference["tinydcs_random_test"]},
        "rows": records,
    })
    click.echo(f"Exported train-only coefficients and {len(records)} heldout rows; baseline MAE {metrics['mae']*100:.6f} pp")


if __name__ == "__main__":
    main()
