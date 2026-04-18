#!/usr/bin/env python3
"""Train TinyDCS surrogate + emit metrics JSON and figures.

Usage
-----
    python scripts/03_train_surrogate.py \
        --training artifacts/training_pilot.parquet \
        --test-fraction 0.15 --calibration-fraction 0.15 \
        --output-model artifacts/tinydcs_v0.1.joblib \
        --output-metrics artifacts/metrics_v0.1.json \
        --output-figures artifacts/figures_v0.1
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

_THIS = Path(__file__).resolve()
_ROOT = _THIS.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tinydcs.features import FEATURE_COLUMNS  # noqa: E402
from tinydcs.metrics import (  # noqa: E402
    binarized_roc_auc,
    bland_altman,
    brier_score,
    calibration_slope_intercept,
    empirical_coverage,
    point_errors,
    reliability_bins,
)
from tinydcs.surrogate import TrainConfig, train_surrogate  # noqa: E402


def _plot_reliability(rbin, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    ax.plot([0, 1], [0, 1], "k--", alpha=0.6, label="perfect")
    mask = np.isfinite(rbin.bin_mean_pred)
    ax.plot(rbin.bin_mean_pred[mask], rbin.bin_mean_true[mask], "o-", label="surrogate")
    ax.set_xlabel("Predicted P(DCS)")
    ax.set_ylabel("Observed P(DCS) [3RUT-MBe1]")
    ax.set_title("Reliability diagram")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _plot_bland_altman(y_ref: np.ndarray, y_pred: np.ndarray, path: Path) -> None:
    diff = y_pred - y_ref
    mean = (y_pred + y_ref) / 2
    bias = float(diff.mean())
    sd = float(diff.std(ddof=1))
    fig, ax = plt.subplots(figsize=(5.0, 4.0))
    ax.scatter(mean, diff, s=6, alpha=0.5)
    ax.axhline(bias, color="k", linestyle="-", label=f"bias = {bias:+.3f}")
    ax.axhline(bias + 1.96 * sd, color="gray", linestyle="--", label=f"+1.96 SD = {bias + 1.96*sd:+.3f}")
    ax.axhline(bias - 1.96 * sd, color="gray", linestyle="--", label=f"-1.96 SD = {bias - 1.96*sd:+.3f}")
    ax.set_xlabel("Mean of surrogate + 3RUT-MBe1 P(DCS)")
    ax.set_ylabel("Surrogate − 3RUT-MBe1 P(DCS)")
    ax.set_title("Bland–Altman")
    ax.legend(loc="best", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


@click.command()
@click.option("--training", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--test-fraction", type=float, default=0.15, show_default=True)
@click.option("--calibration-fraction", type=float, default=0.15, show_default=True)
@click.option("--output-model", type=click.Path(dir_okay=False), required=True)
@click.option("--output-metrics", type=click.Path(dir_okay=False), required=True)
@click.option("--output-figures", type=click.Path(file_okay=False), required=False, default=None)
def main(
    training: str,
    test_fraction: float,
    calibration_fraction: float,
    output_model: str,
    output_metrics: str,
    output_figures: str | None,
) -> None:
    training_path = Path(training)
    if training_path.suffix.lower() == ".parquet":
        df = pd.read_parquet(training_path)
    else:
        df = pd.read_csv(training_path)

    surrogate, splits = train_surrogate(
        df,
        feature_names=FEATURE_COLUMNS,
        test_fraction=test_fraction,
        calibration_fraction=calibration_fraction,
        config=TrainConfig(),
    )

    # Predict on the held-out test fold.
    test_df = splits["test"]
    pred = surrogate.predict(test_df)
    y_true = test_df["pdcs_3rut_mbe1"].to_numpy(dtype=float)

    metrics = {
        "n_train": int(len(splits["train"])),
        "n_cal": int(len(splits["cal"])),
        "n_test": int(len(test_df)),
        "point": point_errors(y_true, pred["point"]),
        "brier": brier_score(y_true, pred["point"]),
        "roc_auc_at_0.10": binarized_roc_auc(y_true, pred["point"], threshold=0.10),
        "calibration": {
            "slope": float(calibration_slope_intercept(y_true, pred["point"])[0]),
            "intercept": float(calibration_slope_intercept(y_true, pred["point"])[1]),
        },
        "bland_altman": bland_altman(y_true, pred["point"]),
        "conformal_coverage": empirical_coverage(
            y_true, pred["lower"], pred["upper"], nominal=surrogate.conformal.confidence
        ),
        "conformal_q_logit": float(surrogate.conformal.q),
        "ood_threshold": float(surrogate.ood.threshold),
        "features": list(FEATURE_COLUMNS),
    }

    Path(output_model).parent.mkdir(parents=True, exist_ok=True)
    Path(output_metrics).parent.mkdir(parents=True, exist_ok=True)
    surrogate.save(output_model)
    Path(output_metrics).write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    if output_figures:
        fig_dir = Path(output_figures)
        fig_dir.mkdir(parents=True, exist_ok=True)
        rbin = reliability_bins(y_true, pred["point"], n_bins=10)
        _plot_reliability(rbin, fig_dir / "reliability.png")
        _plot_bland_altman(y_true, pred["point"], fig_dir / "bland_altman.png")

    click.echo(
        "Trained surrogate on {n_tr} rows (cal={n_cal}, test={n_te}). "
        "MAE={mae:.4f}, R²={r2:.3f}, Brier={br:.4f}, coverage={cov:.3f} (nominal {nom:.2f}).".format(
            n_tr=metrics["n_train"],
            n_cal=metrics["n_cal"],
            n_te=metrics["n_test"],
            mae=metrics["point"]["mae"],
            r2=metrics["point"]["r2"],
            br=metrics["brier"],
            cov=metrics["conformal_coverage"]["coverage"],
            nom=metrics["conformal_coverage"]["nominal"],
        )
    )


if __name__ == "__main__":
    main()
