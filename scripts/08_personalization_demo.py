#!/usr/bin/env python3
"""Paper 2 prototype demo: hierarchical Bayesian personalization of TinyDCS.

Synthesizes a cohort with known per-subject susceptibilities ``log lambda_i``,
runs the conjugate Gaussian personalization layer on top of a trained
TinyDCS base surrogate, and reports:

  * Recovery of ``log lambda_i`` (Pearson r, Spearman rho, RMSE).
  * Information-gain curve: calibration / log-likelihood vs number of
    exposures per subject (k = 1, 2, 5, 10, 20).
  * Personalized vs population-average Brier score on a held-out exposure
    per subject.

The numbers produced here are the headline figures for Paper 2's synthetic
validation section.

Usage
-----
    python scripts/08_personalization_demo.py \\
        --base-surrogate artifacts/tinydcs_adrac_zi.joblib \\
        --exposure-template artifacts/DCS_Risk_DB_2025_clean.parquet \\
        --output-metrics artifacts/personalization_demo.json \\
        --n-subjects 200 --sigma-lambda 1.0 --seed 42
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
from tinydcs.metrics import brier_score  # noqa: E402
from tinydcs.personalization import (  # noqa: E402
    PersonalizedSurrogate,
    PopulationPrior,
    generate_synthetic_cohort,
)
from tinydcs.simulator import ExposureProfile, ornstein_uhlenbeck_vo2  # noqa: E402
from tinydcs.surrogate import TinyDcsSurrogate  # noqa: E402


_EXERCISE_VO2 = {
    "Rest": {"mean": 0.10, "sd": 0.05},
    "Mild": {"mean": 0.45, "sd": 0.10},
    "Heavy": {"mean": 1.10, "sd": 0.15},
}


def _augment_with_vo2(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records = []
    for _, row in df.iterrows():
        v = _EXERCISE_VO2.get(str(row["exercise_level"]), _EXERCISE_VO2["Rest"])
        m = max(0.0, rng.normal(v["mean"], v["sd"]))
        t = float(row["time_at_altitude"])
        traj = ornstein_uhlenbeck_vo2(duration_min=t, dt_min=5.0, mean_i_ex=m, rng=rng)
        p = ExposureProfile(
            target_altitude_ft=float(row["altitude"]),
            prebreathe_duration_min=float(row["prebreathing_time"]),
            prebreathe_fio2=1.0, prebreathe_fin2=0.0,
            prebreathe_i_ex_trajectory=0.0,
            ascent_rate_fpm=5000.0, altitude_duration_min=t,
            altitude_fio2=0.21, altitude_fin2=0.79,
            altitude_i_ex_trajectory=traj,
            vo2_dt_min=5.0,
        )
        rec = asdict(extract_features(p))
        records.append(rec)
    return pd.DataFrame(records)


def _recovery_metrics(truths: np.ndarray, estimates: np.ndarray) -> dict:
    truths = np.asarray(truths, dtype=float)
    estimates = np.asarray(estimates, dtype=float)
    pearson = float(np.corrcoef(truths, estimates)[0, 1])
    spearman = float(np.corrcoef(pd.Series(truths).rank(), pd.Series(estimates).rank())[0, 1])
    return {
        "pearson_r": pearson,
        "spearman_rho": spearman,
        "rmse_log_lambda": float(np.sqrt(np.mean((truths - estimates) ** 2))),
        "mean_abs_error_log_lambda": float(np.mean(np.abs(truths - estimates))),
        "n_subjects": int(truths.size),
    }


def _info_gain_sweep(
    base: TinyDcsSurrogate,
    exposure_template: pd.DataFrame,
    n_subjects: int,
    sigma_lambda: float,
    seed: int,
    k_values: tuple[int, ...],
) -> dict:
    """Train / evaluate the personalized surrogate at several per-subject k."""
    results = {}
    for k in k_values:
        cohort = generate_synthetic_cohort(
            base, exposure_template,
            n_subjects=n_subjects, exposures_per_subject=k + 1,  # +1 for a held-out test exposure
            sigma_lambda=sigma_lambda, seed=seed,
        )
        # Split: first k exposures per subject → training, last → held-out test.
        train_parts = []
        test_parts = []
        for sid, grp in cohort.groupby("subject_id"):
            train_parts.append(grp.iloc[:k])
            test_parts.append(grp.iloc[k:])
        train_df = pd.concat(train_parts, ignore_index=True)
        test_df = pd.concat(test_parts, ignore_index=True)

        prior = PopulationPrior(mu_lambda=0.0, sigma_lambda_sq=sigma_lambda**2, sigma_lik_sq=4.0)
        ps = PersonalizedSurrogate(base=base, prior=prior)
        truths = []
        estimates = []
        for sid, grp in train_df.groupby("subject_id"):
            ps.observe(sid, grp[list(FEATURE_COLUMNS)], grp["y"].to_numpy())
            truths.append(float(grp["log_lambda_true"].iloc[0]))
            estimates.append(ps.subjects[sid].mean)

        rec = _recovery_metrics(np.asarray(truths), np.asarray(estimates))

        # Held-out exposure: compare personalized point estimate vs population
        # baseline vs true P(DCS).
        per_preds = []
        pop_preds = []
        trues = []
        for _, row in test_df.iterrows():
            sid = int(row["subject_id"])
            feats = pd.DataFrame([row[list(FEATURE_COLUMNS)]])
            p_personal = float(ps.predict(sid, feats)["point"][0])
            p_pop = float(base.predict(feats)["point"][0])
            per_preds.append(p_personal)
            pop_preds.append(p_pop)
            trues.append(float(row["y_prob_true"]))

        rec["brier_population"] = brier_score(np.asarray(trues), np.asarray(pop_preds))
        rec["brier_personalized"] = brier_score(np.asarray(trues), np.asarray(per_preds))
        rec["brier_reduction"] = rec["brier_population"] - rec["brier_personalized"]
        results[f"k_{k}"] = rec
    return results


@click.command()
@click.option("--base-surrogate", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--exposure-template", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--output-metrics", type=click.Path(dir_okay=False), required=True)
@click.option("--n-subjects", type=int, default=200, show_default=True)
@click.option("--sigma-lambda", type=float, default=1.0, show_default=True)
@click.option("--seed", type=int, default=42, show_default=True)
def main(
    base_surrogate: str,
    exposure_template: str,
    output_metrics: str,
    n_subjects: int,
    sigma_lambda: float,
    seed: int,
) -> None:
    click.echo(f"Loading base surrogate from {base_surrogate} ...")
    base = TinyDcsSurrogate.load(base_surrogate)

    click.echo(f"Building exposure template from {exposure_template} ...")
    raw = (
        pd.read_parquet(exposure_template)
        if exposure_template.endswith(".parquet")
        else pd.read_csv(exposure_template)
    )
    template = _augment_with_vo2(raw, seed=seed)

    click.echo(f"Running personalization sweep with {n_subjects} subjects, sigma_lambda={sigma_lambda:.2f} ...")
    results = _info_gain_sweep(
        base=base,
        exposure_template=template,
        n_subjects=n_subjects,
        sigma_lambda=sigma_lambda,
        seed=seed,
        k_values=(1, 2, 5, 10, 20),
    )

    blob = {
        "n_subjects": n_subjects,
        "sigma_lambda": sigma_lambda,
        "seed": seed,
        "results_by_k": results,
    }
    Path(output_metrics).parent.mkdir(parents=True, exist_ok=True)
    Path(output_metrics).write_text(json.dumps(blob, indent=2), encoding="utf-8")

    click.echo("\nInformation-gain summary (per-subject exposures k):")
    click.echo(f"  {'k':<5}  {'Pearson r':<11}  {'Spearman':<10}  {'RMSE(logλ)':<12}  {'Brier pop':<11}  {'Brier pers':<12}  {'Δ Brier':<10}")
    for key, r in results.items():
        click.echo(
            f"  {key:<5}  {r['pearson_r']:>8.3f}     {r['spearman_rho']:>8.3f}    "
            f"{r['rmse_log_lambda']:>10.3f}  {r['brier_population']:>10.4f}  "
            f"{r['brier_personalized']:>11.4f}  {r['brier_reduction']:>+8.4f}"
        )
    click.echo(f"\nSummary written to {output_metrics}")


if __name__ == "__main__":
    main()
