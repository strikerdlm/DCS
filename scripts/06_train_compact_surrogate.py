#!/usr/bin/env python3
"""Train a *compact* TinyDCS surrogate budgeted for microcontroller deployment.

The v0.5 surrogate (n_estimators=400, num_leaves=31) is the Paper-1 headline
model for accuracy claims; it exports to ~894 KB ONNX. For the "runs on a
smartwatch" claim we also train a compact variant (fewer trees / fewer leaves)
and benchmark its accuracy vs. the full model. This script runs both and
writes a comparison table.

Usage
-----
    python scripts/06_train_compact_surrogate.py \\
        --training artifacts/DCS_Risk_DB_2025_clean.parquet \\
        --output-full artifacts/tinydcs_full.joblib \\
        --output-compact artifacts/tinydcs_compact.joblib \\
        --output-metrics artifacts/compact_vs_full.json
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import click
import numpy as np
import pandas as pd

_THIS = Path(__file__).resolve()
_ROOT = _THIS.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tinydcs.features import FEATURE_COLUMNS, extract_features  # noqa: E402
from tinydcs.metrics import brier_score, calibration_slope_intercept, point_errors  # noqa: E402
from tinydcs.simulator import ExposureProfile, ornstein_uhlenbeck_vo2  # noqa: E402
from tinydcs.surrogate import TrainConfig, train_surrogate  # noqa: E402


_EXERCISE_VO2_LOOKUP = {
    "Rest":  {"mean": 0.10, "sd": 0.05},
    "Mild":  {"mean": 0.45, "sd": 0.10},
    "Heavy": {"mean": 1.10, "sd": 0.15},
}


def _augment_with_vo2(df: pd.DataFrame, *, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records = []
    for _, row in df.iterrows():
        level = str(row["exercise_level"])
        vp = _EXERCISE_VO2_LOOKUP.get(level, _EXERCISE_VO2_LOOKUP["Rest"])
        mean_i_ex = max(0.0, rng.normal(loc=vp["mean"], scale=vp["sd"]))
        alt_time = float(row["time_at_altitude"])
        alt_traj = ornstein_uhlenbeck_vo2(
            duration_min=alt_time, dt_min=5.0, mean_i_ex=mean_i_ex, rng=rng,
        )
        profile = ExposureProfile(
            target_altitude_ft=float(row["altitude"]),
            prebreathe_duration_min=float(row["prebreathing_time"]),
            prebreathe_fio2=1.0, prebreathe_fin2=0.0,
            prebreathe_i_ex_trajectory=0.0,
            ascent_rate_fpm=5000.0,
            altitude_duration_min=alt_time,
            altitude_fio2=0.21, altitude_fin2=0.79,
            altitude_i_ex_trajectory=alt_traj,
            vo2_dt_min=5.0,
        )
        feats = extract_features(profile)
        rec = asdict(feats)
        rec["pdcs_3rut_mbe1"] = float(row["risk_of_decompression_sickness"]) / 100.0
        records.append(rec)
    return pd.DataFrame(records)


def _onnx_size_kb(surrogate, feature_names: list[str], tmp_dir: Path) -> float:
    """Export to ONNX and return the serialized file size in KB."""
    from onnxconverter_common import FloatTensorType
    from onnxmltools import convert_lightgbm

    onnx_model = convert_lightgbm(
        surrogate.model,
        initial_types=[("input", FloatTensorType([None, len(feature_names)]))],
        target_opset=13,
        zipmap=False,
    )
    tmp_dir.mkdir(parents=True, exist_ok=True)
    out = tmp_dir / "tmp_model.onnx"
    with open(out, "wb") as f:
        f.write(onnx_model.SerializeToString())
    size_kb = out.stat().st_size / 1024
    out.unlink(missing_ok=True)
    return size_kb


def _train_and_report(df: pd.DataFrame, config: TrainConfig, tag: str, tmp_dir: Path) -> dict:
    surrogate, splits = train_surrogate(
        df,
        feature_names=FEATURE_COLUMNS,
        target_col="pdcs_3rut_mbe1",
        test_fraction=0.15,
        calibration_fraction=0.20,
        config=config,
        mondrian_feature="altitude_ft",
        mondrian_band_width=5000.0,
        mondrian_band_origin=18000.0,
    )
    y_true = splits["test"]["pdcs_3rut_mbe1"].to_numpy(dtype=float)
    pred = surrogate.predict(splits["test"])
    pe = point_errors(y_true, pred["point"])
    slope, intercept = calibration_slope_intercept(y_true, pred["point"])
    size_kb = _onnx_size_kb(surrogate, FEATURE_COLUMNS, tmp_dir)
    return {
        "tag": tag,
        "config": asdict(config) | {"monotonic_constraints": dict(config.monotonic_constraints)},
        "point": pe,
        "brier": brier_score(y_true, pred["point"]),
        "calibration_slope": slope,
        "calibration_intercept": intercept,
        "onnx_size_kb": size_kb,
    }


@click.command()
@click.option("--training", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--output-metrics", type=click.Path(dir_okay=False), required=True)
@click.option("--seed", type=int, default=42, show_default=True)
def main(training: str, output_metrics: str, seed: int) -> None:
    df_raw = pd.read_parquet(training) if training.endswith(".parquet") else pd.read_csv(training)
    df_aug = _augment_with_vo2(df_raw, seed=seed)

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
        r = _train_and_report(df_aug, cfg, tag, tmp_dir)
        results.append(r)
        click.echo(
            "  MAE={mae:.4f}, R2={r2:.4f}, Brier={brier:.4f}, "
            "slope={sl:.3f}, ONNX size={sz:.1f} KB".format(
                mae=r["point"]["mae"],
                r2=r["point"]["r2"],
                brier=r["brier"],
                sl=r["calibration_slope"],
                sz=r["onnx_size_kb"],
            )
        )

    Path(output_metrics).parent.mkdir(parents=True, exist_ok=True)
    Path(output_metrics).write_text(json.dumps(results, indent=2), encoding="utf-8")
    click.echo(f"\nWrote comparison → {output_metrics}")


if __name__ == "__main__":
    main()
