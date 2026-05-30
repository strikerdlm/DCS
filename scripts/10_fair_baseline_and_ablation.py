"""Reviewer-requested robustness analyses for the TinyDCS reframe.

Addresses two peer-review concerns (PEER_REVIEW_2026-05-29.md):

  A-M1  The headline 4x/10x gain is measured against a *global* (non-stratified)
        log-logistic AFT, but the ADRAC generator is stratified. Fit a FAIR
        per-altitude-band stratified AFT baseline and recompute the honest
        multiplier on the same random test fold.

  A-M3  The continuous-VO2 features are synthesised from the 3-level exercise
        category, so they cannot add predictive information. Quantify this with
        (i) a drop-column ablation (train surrogate with vs without the 5 VO2
        features on the identical fold) and (ii) LightGBM gain importances.

Run:
    ~/.venvs/tinydcs/bin/python scripts/10_fair_baseline_and_ablation.py \
        --training artifacts/repro/clean.parquet \
        --output artifacts/repro/fair_baseline_ablation.json

The train/test split in train_surrogate is a deterministic permutation seeded
only by random_state and len(df); it does NOT depend on the feature set, so the
ablated model lands on the identical test fold.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import click
import numpy as np
import pandas as pd

from mechanistic.adrac import AdracModel, fit_adrac
from tinydcs.metrics import (
    brier_score,
    calibration_slope_intercept,
    empirical_coverage,
    point_errors,
)
from tinydcs.surrogate import TrainConfig, train_surrogate

ROOT = Path(__file__).resolve().parent.parent

# Import _augment_with_vo2 + FEATURE_COLUMNS from script 04 (same augmentation).
_spec = importlib.util.spec_from_file_location(
    "_train04", ROOT / "scripts" / "04_train_adrac_surrogate.py"
)
_train04 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_train04)
_augment_with_vo2 = _train04._augment_with_vo2
FEATURE_COLUMNS = list(_train04.FEATURE_COLUMNS)

VO2_FEATURES = [
    "prebreathe_vo2_mean_lmin",
    "prebreathe_vo2_peak_lmin",
    "altitude_vo2_mean_lmin",
    "altitude_vo2_peak_1min_lmin",
    "altitude_vo2_integral_lmin_min",
]
FEATURES_NO_VO2 = [c for c in FEATURE_COLUMNS if c not in VO2_FEATURES]

BAND_WIDTH = 5000.0
BAND_ORIGIN = 18000.0
SEED = 42
TEST_FRAC = 0.15
CAL_FRAC = 0.20


def _band_index(alt_ft: np.ndarray) -> np.ndarray:
    return np.floor((np.asarray(alt_ft, dtype=float) - BAND_ORIGIN) / BAND_WIDTH).astype(int)


def _replicate_split(n: int) -> dict[str, np.ndarray]:
    """Reproduce the train_surrogate permutation split exactly."""
    rng = np.random.default_rng(SEED)
    idx = rng.permutation(n)
    n_test = int(round(n * TEST_FRAC))
    n_cal = int(round(n * CAL_FRAC))
    n_train = n - n_test - n_cal
    return {
        "train": idx[:n_train],
        "cal": idx[n_train:n_train + n_cal],
        "test": idx[n_train + n_cal:],
    }


def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    pe = point_errors(y_true, y_pred)
    slope, intercept = calibration_slope_intercept(y_true, y_pred)
    return {
        "n": int(len(y_true)),
        "mae": float(pe["mae"]),
        "rmse": float(pe["rmse"]),
        "r2": float(pe["r2"]),
        "brier": float(brier_score(y_true, y_pred)),
        "calibration_slope": float(slope),
        "calibration_intercept": float(intercept),
    }


# --------------------------------------------------------------------------- #
# A-M1: fair stratified-by-altitude-band AFT baseline                          #
# --------------------------------------------------------------------------- #
def _predict_aft(model: AdracModel, df_raw: pd.DataFrame) -> np.ndarray:
    return model.predict(
        df_raw["altitude"].to_numpy(dtype=float),
        df_raw["prebreathing_time"].to_numpy(dtype=float),
        df_raw["exercise_level"].to_numpy(),
        df_raw["time_at_altitude"].to_numpy(dtype=float),
    )


def fit_stratified_by(df_raw: pd.DataFrame, group: np.ndarray, global_model: AdracModel) -> dict:
    """Fit one ADRAC AFT per stratum (in-bag). Returns {key: AdracModel}."""
    models: dict = {}
    for g in np.unique(group):
        sub = df_raw.loc[group == g]
        if len(sub) < 30:
            models[g] = global_model
            continue
        try:
            models[g] = fit_adrac(sub)
        except RuntimeError:
            models[g] = global_model
    return models


def _predict_grouped(models: dict, group: np.ndarray, global_model: AdracModel, df_raw: pd.DataFrame) -> np.ndarray:
    out = np.zeros(len(df_raw), dtype=float)
    alt = df_raw["altitude"].to_numpy(dtype=float)
    pb = df_raw["prebreathing_time"].to_numpy(dtype=float)
    ex = df_raw["exercise_level"].to_numpy()
    t = df_raw["time_at_altitude"].to_numpy(dtype=float)
    for i in range(len(df_raw)):
        m = models.get(group[i], global_model)
        out[i] = float(m.predict(alt[i], pb[i], ex[i], t[i])[0])
    return out


def run_fair_baseline(df_raw: pd.DataFrame, test_idx: np.ndarray) -> dict:
    """Try three parametric baselines, all fit in-bag (every advantage given):
      - global AFT (the manuscript's current baseline)
      - AFT stratified by EXERCISE level (3 strata, full altitude range each —
        the faithful reading of 'ADRAC is stratified', preserves the pressure
        covariate)
      - AFT stratified by 5,000-ft ALTITUDE band (starves the pressure
        covariate; reported to show stratification choice matters)
    """
    df_raw = df_raw.reset_index(drop=True)
    y_true = df_raw["risk_of_decompression_sickness"].to_numpy(dtype=float) / 100.0

    global_model = fit_adrac(df_raw)
    ex_group = df_raw["exercise_level"].to_numpy()
    alt_group = _band_index(df_raw["altitude"].to_numpy(dtype=float))

    ex_models = fit_stratified_by(df_raw, ex_group, global_model)
    alt_models = fit_stratified_by(df_raw, alt_group, global_model)

    y_global = _predict_aft(global_model, df_raw)
    y_ex = _predict_grouped(ex_models, ex_group, global_model, df_raw)
    y_alt = _predict_grouped(alt_models, alt_group, global_model, df_raw)

    return {
        "n_exercise_strata": len(ex_models),
        "n_altitude_strata": len(alt_models),
        "global_aft_test": _metrics(y_true[test_idx], y_global[test_idx]),
        "exercise_stratified_aft_test": _metrics(y_true[test_idx], y_ex[test_idx]),
        "altitude_stratified_aft_test": _metrics(y_true[test_idx], y_alt[test_idx]),
        "best_aft_mae": min(
            _metrics(y_true[test_idx], y_global[test_idx])["mae"],
            _metrics(y_true[test_idx], y_ex[test_idx])["mae"],
            _metrics(y_true[test_idx], y_alt[test_idx])["mae"],
        ),
    }


# --------------------------------------------------------------------------- #
# A-M3: VO2 drop-column ablation + gain importances                           #
# --------------------------------------------------------------------------- #
def _eval_surrogate_on_test(surrogate, test_df) -> dict:
    pred = surrogate.predict(test_df)
    y = test_df["pdcs_3rut_mbe1"].to_numpy(dtype=float)
    out = _metrics(y, pred["point"])
    cov = empirical_coverage(y, pred["lower"], pred["upper"], nominal=surrogate.conformal.confidence)
    out["coverage"] = float(cov["coverage"])
    return out


def run_ablation(df_aug: pd.DataFrame) -> dict:
    """Test the circularity claim correctly.

    The model has NO direct exercise feature; the 3-level exercise category
    enters ONLY through the 5 synthesised VO2 features. So 'drop VO2' also
    drops all exercise information and is uninformative about circularity.
    The right comparison is:
      - full:       8 non-VO2 features + 5 synthesised VO2 features
      - ordinal-ex: 8 non-VO2 features + 1 ordinal exercise feature (0/1/2)
      - no-exercise: 8 non-VO2 features only (exercise removed entirely)
    If full ~= ordinal-ex, the continuous VO2 synthesis adds nothing beyond the
    category it was generated from (circular). no-exercise shows how much the
    category is worth at all.
    """
    df_aug = df_aug.copy()
    ex_map = {"Rest": 0.0, "Mild": 1.0, "Heavy": 2.0}
    df_aug["exercise_ordinal"] = df_aug["exercise_level"].map(ex_map).astype(float)
    features_ordinal = FEATURES_NO_VO2 + ["exercise_ordinal"]

    common = dict(
        target_col="pdcs_3rut_mbe1",
        test_fraction=TEST_FRAC,
        calibration_fraction=CAL_FRAC,
        config=TrainConfig(random_state=SEED),
        use_zero_inflated=True,
    )
    full_surr, full_splits = train_surrogate(df_aug, feature_names=FEATURE_COLUMNS, **common)
    ord_surr, ord_splits = train_surrogate(df_aug, feature_names=features_ordinal, **common)
    novo_surr, novo_splits = train_surrogate(df_aug, feature_names=FEATURES_NO_VO2, **common)

    same = (
        np.array_equal(full_splits["test"].index.to_numpy(), ord_splits["test"].index.to_numpy())
        and np.array_equal(full_splits["test"].index.to_numpy(), novo_splits["test"].index.to_numpy())
    )

    res = {
        "identical_test_fold": bool(same),
        "n_features_full": len(FEATURE_COLUMNS),
        "vo2_features": VO2_FEATURES,
        "note": "exercise enters the full model ONLY via the 5 synthesised VO2 features",
        "full_vo2_test": _eval_surrogate_on_test(full_surr, full_splits["test"]),
        "ordinal_exercise_test": _eval_surrogate_on_test(ord_surr, ord_splits["test"]),
        "no_exercise_test": _eval_surrogate_on_test(novo_surr, novo_splits["test"]),
    }

    # Gain importances from the full ZI continuous regressor + zero classifier.
    zi = full_surr.conformal
    importances = {}
    for name, mdl in (("continuous_regressor", zi.continuous_model),
                      ("zero_classifier", zi.zero_classifier)):
        try:
            booster = mdl.booster_
            gain = np.asarray(booster.feature_importance(importance_type="gain"), dtype=float)
            total = float(gain.sum()) or 1.0
            share = {f: float(g) / total for f, g in zip(FEATURE_COLUMNS, gain)}
            vo2_share = float(sum(share[f] for f in VO2_FEATURES))
            importances[name] = {
                "per_feature_gain_share": dict(sorted(share.items(), key=lambda kv: -kv[1])),
                "vo2_block_gain_share": vo2_share,
            }
        except Exception as exc:  # pragma: no cover
            importances[name] = {"error": str(exc)}
    res["gain_importance"] = importances
    return res


@click.command()
@click.option("--training", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--output", required=True, type=click.Path(dir_okay=False))
def main(training: str, output: str) -> None:
    df_raw = pd.read_parquet(training) if training.endswith(".parquet") else pd.read_csv(training)
    df_raw = df_raw.reset_index(drop=True)

    df_aug = _augment_with_vo2(df_raw, seed=SEED)
    df_aug["pdcs_3rut_mbe1"] = df_aug["pdcs_adrac_target"]

    split = _replicate_split(len(df_raw))

    click.echo("== A-M1: fair parametric baselines (global vs stratified AFT) ==")
    fair = run_fair_baseline(df_raw, split["test"])
    for key, label in (("global_aft_test", "global AFT          "),
                       ("exercise_stratified_aft_test", "exercise-stratified "),
                       ("altitude_stratified_aft_test", "altitude-stratified ")):
        m = fair[key]
        click.echo(f"  {label} MAE = {m['mae']:.4f}  R2 = {m['r2']:.4f}  slope = {m['calibration_slope']:.3f}")

    click.echo("== A-M3: circularity test (VO2 block vs ordinal exercise) ==")
    abl = run_ablation(df_aug)
    for key, label in (("full_vo2_test", "full + 5 VO2 feats   "),
                       ("ordinal_exercise_test", "+ 1 ordinal exercise "),
                       ("no_exercise_test", "no exercise feature  ")):
        m = abl[key]
        click.echo(f"  {label} MAE = {m['mae']:.4f}  R2 = {m['r2']:.4f}  cov = {m['coverage']:.3f}")
    click.echo(f"  VO2 gain share (continuous regressor) = {abl['gain_importance']['continuous_regressor']['vo2_block_gain_share']*100:.2f}%")

    tinydcs_mae = abl["full_vo2_test"]["mae"]
    best_aft = fair["best_aft_mae"]
    blob = {
        "seed": SEED,
        "tinydcs_full_mae": tinydcs_mae,
        "fair_baseline": fair,
        "ablation": abl,
        "honest_multipliers": {
            "vs_global_aft": fair["global_aft_test"]["mae"] / tinydcs_mae,
            "vs_best_aft": best_aft / tinydcs_mae,
        },
        "circularity_verdict": {
            "full_vo2_mae": abl["full_vo2_test"]["mae"],
            "ordinal_exercise_mae": abl["ordinal_exercise_test"]["mae"],
            "vo2_minus_ordinal_mae_delta": abl["full_vo2_test"]["mae"] - abl["ordinal_exercise_test"]["mae"],
            "interpretation": "if delta ~ 0 or positive, the synthesised continuous-VO2 features add nothing beyond the 3-level category they were generated from",
        },
    }
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(blob, indent=2), encoding="utf-8")
    click.echo(f"\nHonest multipliers: vs global AFT = {blob['honest_multipliers']['vs_global_aft']:.2f}x, "
               f"vs BEST AFT = {blob['honest_multipliers']['vs_best_aft']:.2f}x")
    cv = blob["circularity_verdict"]
    click.echo(f"Circularity: full-VO2 MAE {cv['full_vo2_mae']:.4f} vs ordinal-exercise MAE {cv['ordinal_exercise_mae']:.4f} "
               f"(delta {cv['vo2_minus_ordinal_mae_delta']:+.4f})")
    click.echo(f"Wrote {output}")


if __name__ == "__main__":
    main()
