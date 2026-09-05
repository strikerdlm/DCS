"""Compare prespecified zero-inflated model sizes on one frozen partition.

This reports model-grid agreement and serialized ONNX size. It does not
establish wearable hardware performance. Every candidate is fit on training
cells, calibrated on calibration cells, and evaluated on the same test cells.

Usage
-----
    python scripts/06_train_compact_surrogate.py \\
        --training artifacts/DCS_Risk_DB_2025_clean.parquet \\
        --output-full artifacts/tinydcs_full.joblib \\
        --output-compact artifacts/tinydcs_compact.joblib \\
        --output-metrics artifacts/compact_vs_full.json
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

import click
import pandas as pd

_THIS = Path(__file__).resolve()
_ROOT = _THIS.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.evidence_common import (
    augment,
    evidence_metadata,
    prepare_data,
    sha256,
    write_json,
)
from tinydcs.features import FEATURE_COLUMNS
from tinydcs.metrics import (
    calibration_slope_intercept,
    empirical_coverage,
    point_errors,
    probability_mse,
)
from tinydcs.surrogate import TrainConfig, train_surrogate


def _augment_with_vo2(df: pd.DataFrame, *, seed: int = 42) -> pd.DataFrame:
    return augment(df, seed=seed)


def _onnx_size_kb(surrogate, feature_names: list[str], tmp_dir: Path) -> float:
    """Export to ONNX and return the serialized file size in KB."""
    from onnxmltools import convert_lightgbm
    from onnxmltools.convert.common.data_types import FloatTensorType

    models = [surrogate.conformal.zero_classifier, surrogate.conformal.continuous_model]
    return sum(len(convert_lightgbm(
        model, initial_types=[("input", FloatTensorType([None, len(feature_names)]))],
        target_opset=13, zipmap=False).SerializeToString()) for model in models)/1024


def _train_and_report(df, config, tag, tmp_dir, *, partition, training, ids, split_path) -> dict:
    surrogate, splits = train_surrogate(
        df,
        feature_names=FEATURE_COLUMNS,
        target_col="pdcs_adrac_target",
        test_fraction=0.15,
        calibration_fraction=0.20,
        config=config,
        partition=partition,
        use_zero_inflated=True,
    )
    y_true = splits["test"]["pdcs_adrac_target"].to_numpy(dtype=float)
    pred = surrogate.predict(splits["test"])
    pe = point_errors(y_true, pred["point"])
    slope, intercept = calibration_slope_intercept(y_true, pred["point"])
    size_kb = _onnx_size_kb(surrogate, surrogate.feature_names, tmp_dir)
    coverage = empirical_coverage(y_true, pred["lower"], pred["upper"])
    surrogate.metadata = evidence_metadata(training, ids, config, surrogate.feature_names,
                                          "zero_inflated", metrics={"point": pe, "coverage": coverage},
                                          seed=config.random_state)
    surrogate.metadata.update(variant=tag, partition_ids_path=str(split_path),
                              partition_ids_file_sha256=sha256(split_path))
    surrogate.save(str(tmp_dir.parent / (tag + ".joblib")))
    return {
        "coverage": coverage,
        "metadata": surrogate.metadata,
        "tag": tag,
        "config": asdict(config) | {"monotonic_constraints": dict(config.monotonic_constraints)},
        "point": pe,
        "probability_mse": probability_mse(y_true, pred["point"]),
        "calibration_slope": slope,
        "calibration_intercept": intercept,
        "onnx_size_kb": size_kb,
        "size_scope": "classifier plus continuous regressor; host metadata additional",
        "accepted_subset_coverage": empirical_coverage(y_true[pred["in_envelope"]],
            pred["lower"][pred["in_envelope"]], pred["upper"][pred["in_envelope"]]),
    }


@click.command()
@click.option("--training", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--output-metrics", type=click.Path(dir_okay=False), required=True)
@click.option("--seed", type=int, default=42, show_default=True)
@click.option("--reference-metrics", type=click.Path(exists=True, dir_okay=False), default=None,
              help="Verify frozen IDs and reuse the exact primary feature matrix.")
def main(training: str, output_metrics: str, seed: int, reference_metrics: str | None) -> None:
    _df_raw, df_aug, partition, ids = prepare_data(training, seed, reference_metrics)
    split_path = Path(output_metrics).with_suffix(".splits.json")
    write_json(split_path, ids)

    tmp_dir = Path(output_metrics).parent / "_tmp_onnx"
    variants = [
        ("full", TrainConfig(n_estimators=400, num_leaves=31, learning_rate=0.05, random_state=seed)),
        ("medium", TrainConfig(n_estimators=200, num_leaves=15, learning_rate=0.07, random_state=seed)),
        ("compact", TrainConfig(n_estimators=100, num_leaves=7, learning_rate=0.10, random_state=seed)),
        ("tiny", TrainConfig(n_estimators=50, num_leaves=5, learning_rate=0.15, random_state=seed)),
    ]

    results = []
    for tag, cfg in variants:
        click.echo(f"Training '{tag}' variant ...")
        r = _train_and_report(df_aug, cfg, tag, tmp_dir, partition=partition,
                              training=training, ids=ids, split_path=split_path)
        results.append(r)
        click.echo(
            "  MAE={mae:.4f}, R2={r2:.4f}, MSE={brier:.4f}, "
            "slope={sl:.3f}, ONNX size={sz:.1f} KB".format(
                mae=r["point"]["mae"],
                r2=r["point"]["r2"],
                brier=r["probability_mse"],
                sl=r["calibration_slope"],
                sz=r["onnx_size_kb"],
            )
        )

    Path(output_metrics).parent.mkdir(parents=True, exist_ok=True)
    write_json(output_metrics, results)
    click.echo(f"\nWrote comparison → {output_metrics}")


if __name__ == "__main__":
    main()
