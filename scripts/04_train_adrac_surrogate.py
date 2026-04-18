#!/usr/bin/env python3
"""Train the TinyDCS surrogate on the cleaned ADRAC grid and benchmark it
against the closed-form ADRAC log-logistic baseline.

This is the primary Paper-1 training script. It:

  1. Loads the cleaned ADRAC grid (produced by scripts/01_clean_data.py).
  2. Fits the closed-form ADRAC log-logistic AFT baseline
     (``mechanistic.adrac.fit_adrac``).
  3. Augments every grid row with a plausible Conkin-style VO2 profile
     consistent with its categorical exercise level, then extracts the
     full 13-feature TinyDCS vector.
  4. Trains the TinyDCS LightGBM surrogate (on logit(P(DCS)) with
     split-conformal + Mahalanobis OOD, per ``tinydcs.surrogate.TrainConfig``).
  5. Evaluates both models on two held-out splits:
        (a) random 15% held-out,
        (b) leave-one-altitude-out (5,000-ft bands) — robustness.
  6. Emits a single metrics JSON + figure bundle.

The ADRAC baseline represents "what a closed-form operational model already
does". The TinyDCS surrogate's value beyond that is: (i) accepts continuous
VO2 at inference; (ii) ships a calibrated conformal interval; (iii) abstains
outside the validity envelope; (iv) quantizes cleanly to INT8 for edge
deployment (next script).

Usage
-----
    python scripts/04_train_adrac_surrogate.py \\
        --training artifacts/DCS_Risk_DB_2025_clean.parquet \\
        --output-surrogate artifacts/tinydcs_adrac_v0.2.joblib \\
        --output-baseline artifacts/adrac_baseline_v0.2.joblib \\
        --output-metrics artifacts/metrics_adrac_v0.2.json \\
        --output-figures artifacts/figures_adrac_v0.2
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import click
import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

_THIS = Path(__file__).resolve()
_ROOT = _THIS.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from mechanistic.adrac import AdracModel, fit_adrac  # noqa: E402
from tinydcs.features import FEATURE_COLUMNS, extract_features  # noqa: E402
from tinydcs.metrics import (  # noqa: E402
    binarized_roc_auc,
    bland_altman,
    brier_score,
    calibration_slope_intercept,
    empirical_coverage,
    point_errors,
    reliability_bins,
)
from tinydcs.simulator import ExposureProfile, ornstein_uhlenbeck_vo2  # noqa: E402
from tinydcs.surrogate import TrainConfig, train_surrogate  # noqa: E402


# Published VO2 ranges by activity level, from Webb 2010 (ASEM 81:987-92)
# and the ICASM 2017 slide deck summary.
_EXERCISE_VO2_LOOKUP = {
    "Rest":  {"mean": 0.10, "sd": 0.05},   # L/min whole-body (I_ex above rest)
    "Mild":  {"mean": 0.45, "sd": 0.10},
    "Heavy": {"mean": 1.10, "sd": 0.15},
}


def _augment_with_vo2(df: pd.DataFrame, *, seed: int = 42) -> pd.DataFrame:
    """Synthesize a Conkin-style VO2 trajectory consistent with the
    categorical exercise level of each grid row.

    This is necessary because the shipped ADRAC grid only has a 3-level
    exercise indicator; the TinyDCS feature vector requires continuous
    VO2 summaries. We sample a plausible mean (per Webb 2010 ranges)
    and generate an Ornstein-Uhlenbeck trajectory to populate the
    altitude_vo2_* features. Prebreathe VO2 is assumed resting.

    The synthesis is deterministic given ``seed`` and is documented as a
    modelling assumption in docs/methods.md §M2.
    """
    rng = np.random.default_rng(seed)
    records = []
    for _, row in df.iterrows():
        level = str(row["exercise_level"])
        vo2_params = _EXERCISE_VO2_LOOKUP.get(level, _EXERCISE_VO2_LOOKUP["Rest"])
        mean_i_ex = max(0.0, rng.normal(loc=vo2_params["mean"], scale=vo2_params["sd"]))

        alt_time = float(row["time_at_altitude"])
        alt_traj = ornstein_uhlenbeck_vo2(
            duration_min=alt_time,
            dt_min=5.0,
            mean_i_ex=mean_i_ex,
            rng=rng,
        )

        profile = ExposureProfile(
            target_altitude_ft=float(row["altitude"]),
            prebreathe_duration_min=float(row["prebreathing_time"]),
            prebreathe_fio2=1.0,
            prebreathe_fin2=0.0,
            prebreathe_i_ex_trajectory=0.0,
            ascent_rate_fpm=5000.0,
            altitude_duration_min=alt_time,
            altitude_fio2=0.21,
            altitude_fin2=0.79,
            altitude_i_ex_trajectory=alt_traj,
            vo2_dt_min=5.0,
        )
        feats = extract_features(profile)
        rec = asdict(feats)
        # Attach the original target and categorical exercise for reference.
        rec["exercise_level"] = level
        rec["pdcs_adrac_target"] = float(row["risk_of_decompression_sickness"]) / 100.0
        records.append(rec)
    return pd.DataFrame(records)


def _leave_one_altitude_out_splits(df: pd.DataFrame, band_ft: int = 5000) -> list[dict]:
    """Partition by altitude band so each fold's test set is an unseen band.

    Gives a strict extrapolation test — the surrogate never sees altitudes
    in the held-out band during training.
    """
    alt = df["altitude_ft"].to_numpy(dtype=float)
    band_lo = (alt // band_ft).astype(int)
    bands = sorted(np.unique(band_lo).tolist())
    splits = []
    for b in bands:
        mask = band_lo == b
        splits.append({
            "band_lo_ft": int(b * band_ft),
            "band_hi_ft": int(b * band_ft + band_ft),
            "train": df.loc[~mask].reset_index(drop=True),
            "test": df.loc[mask].reset_index(drop=True),
        })
    return splits


def _evaluate_baseline(
    baseline: AdracModel, df_raw: pd.DataFrame, target_in_percent: bool = True
) -> tuple[np.ndarray, np.ndarray]:
    """Run the ADRAC baseline on raw-grid rows (not augmented)."""
    y_pred = baseline.predict(
        altitude_ft=df_raw["altitude"].to_numpy(dtype=float),
        prebreathe_min=df_raw["prebreathing_time"].to_numpy(dtype=float),
        exercise_level=df_raw["exercise_level"].to_numpy(),
        time_at_altitude_min=df_raw["time_at_altitude"].to_numpy(dtype=float),
    )
    y_true = df_raw["risk_of_decompression_sickness"].to_numpy(dtype=float)
    if target_in_percent:
        y_true = y_true / 100.0
    return y_true, y_pred


def _plot_reliability(rbin, path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    ax.plot([0, 1], [0, 1], "k--", alpha=0.6, label="perfect")
    mask = np.isfinite(rbin.bin_mean_pred)
    ax.plot(rbin.bin_mean_pred[mask], rbin.bin_mean_true[mask], "o-", label=title)
    ax.set_xlabel("Predicted P(DCS)")
    ax.set_ylabel("Observed P(DCS) (ADRAC grid)")
    ax.set_title("Reliability diagram — " + title)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _plot_bland_altman(y_ref: np.ndarray, y_pred: np.ndarray, path: Path, title: str) -> None:
    diff = y_pred - y_ref
    mean = (y_pred + y_ref) / 2
    bias = float(diff.mean())
    sd = float(diff.std(ddof=1)) if diff.size > 1 else 0.0
    fig, ax = plt.subplots(figsize=(5.0, 4.0))
    ax.scatter(mean, diff, s=3, alpha=0.3)
    ax.axhline(bias, color="k", linestyle="-", label=f"bias = {bias:+.3f}")
    ax.axhline(bias + 1.96 * sd, color="gray", linestyle="--", label=f"+1.96 SD = {bias + 1.96 * sd:+.3f}")
    ax.axhline(bias - 1.96 * sd, color="gray", linestyle="--", label=f"-1.96 SD = {bias - 1.96 * sd:+.3f}")
    ax.set_xlabel("Mean of prediction + ADRAC grid P(DCS)")
    ax.set_ylabel("Prediction − ADRAC grid P(DCS)")
    ax.set_title("Bland–Altman — " + title)
    ax.legend(loc="best", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _metrics_blob(y_true: np.ndarray, y_pred: np.ndarray, *, tag: str) -> dict:
    """Compute the standard per-model metrics blob."""
    pe = point_errors(y_true, y_pred)
    slope, intercept = calibration_slope_intercept(y_true, y_pred)
    return {
        "tag": tag,
        "n": int(len(y_true)),
        "point": pe,
        "brier": brier_score(y_true, y_pred),
        "roc_auc_at_0.10": binarized_roc_auc(y_true, y_pred, threshold=0.10),
        "calibration": {"slope": slope, "intercept": intercept},
        "bland_altman": bland_altman(y_true, y_pred),
    }


@click.command()
@click.option("--training", type=click.Path(exists=True, dir_okay=False), required=True,
              help="Cleaned ADRAC parquet from scripts/01_clean_data.py")
@click.option("--output-surrogate", type=click.Path(dir_okay=False), required=True)
@click.option("--output-baseline", type=click.Path(dir_okay=False), required=True)
@click.option("--output-metrics", type=click.Path(dir_okay=False), required=True)
@click.option("--output-figures", type=click.Path(file_okay=False), required=True)
@click.option("--seed", type=int, default=42, show_default=True)
@click.option("--run-leave-one-altitude-out/--no-run-leave-one-altitude-out",
              default=True, show_default=True)
@click.option("--cqr/--no-cqr", default=False, show_default=True,
              help="Use Conformalized Quantile Regression (Romano 2019) for calibration")
def main(
    training: str,
    output_surrogate: str,
    output_baseline: str,
    output_metrics: str,
    output_figures: str,
    seed: int,
    run_leave_one_altitude_out: bool,
    cqr: bool,
) -> None:
    training_path = Path(training)
    if training_path.suffix.lower() == ".parquet":
        df_raw = pd.read_parquet(training_path)
    else:
        df_raw = pd.read_csv(training_path)

    # 1. ADRAC baseline.
    click.echo(f"Fitting ADRAC baseline on {len(df_raw)} rows ...")
    baseline = fit_adrac(df_raw)
    y_true_all, y_pred_baseline_all = _evaluate_baseline(baseline, df_raw)
    metrics_baseline_all = _metrics_blob(y_true_all, y_pred_baseline_all, tag="adrac_baseline_inbag")

    # 2. Augment with synthesized VO2 and extract features.
    click.echo(f"Augmenting with VO2 features ...")
    df_aug = _augment_with_vo2(df_raw, seed=seed)
    df_aug["pdcs_3rut_mbe1"] = df_aug["pdcs_adrac_target"]  # rename so train_surrogate finds it

    # 3. TinyDCS surrogate on random split. Calibration mode is either
    # Mondrian (altitude-band stratified) or CQR (Conformalized Quantile
    # Regression, Romano 2019), which additionally handles the bias-driven
    # shortfall at the boundary-mass low-altitude band.
    if cqr:
        click.echo(
            "Training TinyDCS surrogate on augmented grid (Mondrian-CQR calibration) ..."
        )
        surrogate, splits = train_surrogate(
            df_aug,
            feature_names=FEATURE_COLUMNS,
            target_col="pdcs_3rut_mbe1",
            test_fraction=0.15,
            calibration_fraction=0.20,
            config=TrainConfig(random_state=seed),
            use_cqr=True,
            cqr_band_feature="altitude_ft",
            cqr_band_width=5000.0,
            cqr_band_origin=18000.0,
        )
    else:
        click.echo("Training TinyDCS surrogate on augmented grid (Mondrian conformal) ...")
        surrogate, splits = train_surrogate(
            df_aug,
            feature_names=FEATURE_COLUMNS,
            target_col="pdcs_3rut_mbe1",
            test_fraction=0.15,
            calibration_fraction=0.20,
            config=TrainConfig(random_state=seed),
            mondrian_feature="altitude_ft",
            mondrian_band_width=5000.0,
            mondrian_band_origin=18000.0,
        )
    test_df = splits["test"]
    y_true_rand = test_df["pdcs_3rut_mbe1"].to_numpy(dtype=float)
    pred_rand = surrogate.predict(test_df)
    metrics_surrogate_rand = _metrics_blob(y_true_rand, pred_rand["point"], tag="tinydcs_random_test")
    metrics_surrogate_rand["conformal_coverage"] = empirical_coverage(
        y_true_rand, pred_rand["lower"], pred_rand["upper"], nominal=surrogate.conformal.confidence
    )

    # Per-altitude-band coverage — the key check that Mondrian / CQR restore.
    # Report per-band for both calibration modes so the comparison is direct.
    from tinydcs.surrogate import (
        CQRCalibration,
        MondrianConformalCalibration,
    )
    per_band_cov: dict[str, dict[str, float]] = {}
    alt_vals = test_df["altitude_ft"].to_numpy(dtype=float)
    BAND_WIDTH = 5000.0
    BAND_ORIGIN = 18000.0
    bands_test = np.floor((alt_vals - BAND_ORIGIN) / BAND_WIDTH).astype(int)
    for b in np.unique(bands_test):
        mask = bands_test == b
        if int(mask.sum()) < 10:
            continue
        band_cov = empirical_coverage(
            y_true_rand[mask], pred_rand["lower"][mask], pred_rand["upper"][mask],
            nominal=surrogate.conformal.confidence,
        )
        key = f"{int(b) * int(BAND_WIDTH) + int(BAND_ORIGIN)}-{int(b) * int(BAND_WIDTH) + int(BAND_ORIGIN) + int(BAND_WIDTH)}_ft"
        per_band_cov[key] = band_cov
    metrics_surrogate_rand["per_band_coverage"] = per_band_cov
    metrics_surrogate_rand["calibration_mode"] = (
        "cqr" if isinstance(surrogate.conformal, CQRCalibration)
        else ("mondrian" if isinstance(surrogate.conformal, MondrianConformalCalibration)
              else "global")
    )

    # Also evaluate the baseline on the same test fold (row-for-row) for apples-to-apples.
    # We need to trace back to the raw df via the index.
    # The augmented df preserves row order (iterrows() is ordered), so splits index back to raw.
    # For simplicity we rebuild the raw-aligned test fold by index.
    idx_test = test_df.index.to_numpy()  # these are 0..N-1 reset indices in the augmented df
    # Since df_aug was built in the same row order as df_raw, we can align using positional index:
    df_raw_reset = df_raw.reset_index(drop=True)
    df_aug_reset = df_aug.reset_index(drop=True)
    # Map aug-test rows back to raw via shared positional index before the shuffle.
    # Reconstruct by matching on altitude/PB/ex/time.
    df_raw_test = df_raw_reset.merge(
        test_df[["altitude_ft", "prebreathe_time_min", "exercise_level", "altitude_time_min"]]
        .rename(columns={
            "altitude_ft": "altitude", "prebreathe_time_min": "prebreathing_time",
            "altitude_time_min": "time_at_altitude",
        }),
        on=["altitude", "prebreathing_time", "exercise_level", "time_at_altitude"],
        how="inner",
    )
    y_true_rand_raw, y_pred_baseline_rand = _evaluate_baseline(baseline, df_raw_test)
    metrics_baseline_rand = _metrics_blob(
        y_true_rand_raw, y_pred_baseline_rand, tag="adrac_baseline_random_test"
    )

    # 4. Leave-one-altitude-out (optional; slower).
    metrics_loao_surrogate = []
    metrics_loao_baseline = []
    if run_leave_one_altitude_out:
        click.echo("Running leave-one-altitude-out folds ...")
        loao_splits = _leave_one_altitude_out_splits(df_aug_reset, band_ft=5000)
        for s in loao_splits:
            train_fold = s["train"]
            test_fold = s["test"]
            if len(train_fold) < 100 or len(test_fold) < 20:
                continue
            fold_surrogate, fold_splits = train_surrogate(
                train_fold,
                feature_names=FEATURE_COLUMNS,
                target_col="pdcs_3rut_mbe1",
                test_fraction=0.10,  # tiny in-train test to size train/cal
                calibration_fraction=0.15,
                config=TrainConfig(random_state=seed),
            )
            fold_pred = fold_surrogate.predict(test_fold)
            y_fold = test_fold["pdcs_3rut_mbe1"].to_numpy(dtype=float)
            fold_metrics = _metrics_blob(
                y_fold, fold_pred["point"],
                tag=f"tinydcs_LOAO_{s['band_lo_ft']}_{s['band_hi_ft']}",
            )
            fold_metrics["band_lo_ft"] = s["band_lo_ft"]
            fold_metrics["band_hi_ft"] = s["band_hi_ft"]
            metrics_loao_surrogate.append(fold_metrics)

            # Baseline on the same test band.
            df_raw_band = df_raw_reset.loc[
                (df_raw_reset["altitude"] >= s["band_lo_ft"])
                & (df_raw_reset["altitude"] < s["band_hi_ft"])
            ]
            if len(df_raw_band) < 20:
                continue
            y_b, y_bp = _evaluate_baseline(baseline, df_raw_band)
            base_metrics = _metrics_blob(
                y_b, y_bp, tag=f"adrac_baseline_LOAO_{s['band_lo_ft']}_{s['band_hi_ft']}"
            )
            base_metrics["band_lo_ft"] = s["band_lo_ft"]
            base_metrics["band_hi_ft"] = s["band_hi_ft"]
            metrics_loao_baseline.append(base_metrics)

    # 5. Save artifacts.
    Path(output_surrogate).parent.mkdir(parents=True, exist_ok=True)
    Path(output_baseline).parent.mkdir(parents=True, exist_ok=True)
    Path(output_metrics).parent.mkdir(parents=True, exist_ok=True)
    Path(output_figures).mkdir(parents=True, exist_ok=True)
    surrogate.save(output_surrogate)
    joblib.dump(
        {
            "beta_1": baseline.beta_1,
            "beta_2": baseline.beta_2,
            "beta": baseline.beta.tolist(),
            "feature_names": list(baseline.feature_names),
            "version": "0.2.0",
        },
        output_baseline,
    )

    metrics_blob = {
        "n_raw_rows": int(len(df_raw)),
        "n_augmented_rows": int(len(df_aug)),
        "features_used": list(FEATURE_COLUMNS),
        "adrac_baseline_full_inbag": metrics_baseline_all,
        "adrac_baseline_random_test": metrics_baseline_rand,
        "tinydcs_random_test": metrics_surrogate_rand,
        "leave_one_altitude_out_surrogate": metrics_loao_surrogate,
        "leave_one_altitude_out_baseline": metrics_loao_baseline,
    }
    Path(output_metrics).write_text(json.dumps(metrics_blob, indent=2), encoding="utf-8")

    fig_dir = Path(output_figures)
    _plot_reliability(
        reliability_bins(y_true_rand, pred_rand["point"], n_bins=10),
        fig_dir / "reliability_tinydcs_random.png",
        "TinyDCS (random split)",
    )
    _plot_reliability(
        reliability_bins(y_true_rand_raw, y_pred_baseline_rand, n_bins=10),
        fig_dir / "reliability_adrac_random.png",
        "ADRAC baseline (random split)",
    )
    _plot_bland_altman(
        y_true_rand, pred_rand["point"],
        fig_dir / "bland_altman_tinydcs_random.png",
        "TinyDCS (random split)",
    )
    _plot_bland_altman(
        y_true_rand_raw, y_pred_baseline_rand,
        fig_dir / "bland_altman_adrac_random.png",
        "ADRAC baseline (random split)",
    )

    click.echo(
        "\nRandom split results (apples-to-apples on the same test fold):\n"
        "  ADRAC baseline: MAE={adrac_mae:.4f}, R²={adrac_r2:.4f}, Brier={adrac_br:.4f}\n"
        "  TinyDCS:        MAE={td_mae:.4f}, R²={td_r2:.4f}, Brier={td_br:.4f}, "
        "coverage={td_cov:.3f}\n".format(
            adrac_mae=metrics_baseline_rand["point"]["mae"],
            adrac_r2=metrics_baseline_rand["point"]["r2"],
            adrac_br=metrics_baseline_rand["brier"],
            td_mae=metrics_surrogate_rand["point"]["mae"],
            td_r2=metrics_surrogate_rand["point"]["r2"],
            td_br=metrics_surrogate_rand["brier"],
            td_cov=metrics_surrogate_rand["conformal_coverage"]["coverage"],
        )
    )
    if metrics_loao_surrogate:
        td_maes = [m["point"]["mae"] for m in metrics_loao_surrogate]
        base_maes = [m["point"]["mae"] for m in metrics_loao_baseline]
        click.echo(
            "Leave-one-altitude-out (mean over bands):\n"
            f"  ADRAC baseline MAE: {float(np.mean(base_maes)):.4f} ± {float(np.std(base_maes)):.4f}\n"
            f"  TinyDCS MAE:        {float(np.mean(td_maes)):.4f} ± {float(np.std(td_maes)):.4f}"
        )


if __name__ == "__main__":
    main()
