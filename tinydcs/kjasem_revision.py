"""End-to-end reviewer analysis for manuscript KJAsEM-26-0013."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import lightgbm
import numpy as np
import pandas as pd
import sklearn

from tinydcs.data_clean import clean_dcs_risk_db
from tinydcs.features import FEATURE_COLUMNS
from tinydcs.metrics import point_errors
from tinydcs.revision_analysis import (
    assign_source_risk_strata,
    augment_adrac_grid,
    boundary_shell_mask,
    build_structured_holdouts,
    cluster_bootstrap_coverage_ci,
    fit_variant_on_split,
    interval_efficiency,
    random_train_cal_test_split,
    split_train_calibration,
)
from tinydcs.surrogate import TrainConfig

VARIANTS = (
    "global_conformal",
    "mondrian_conformal",
    "global_cqr",
    "mondrian_cqr",
    "zero_inflated",
)


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, np.ndarray):
        return [_json_ready(item) for item in value.tolist()]
    if isinstance(value, np.generic):
        return _json_ready(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_ready(value), indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dataframe_sha256(df: pd.DataFrame) -> str:
    hashed = pd.util.hash_pandas_object(df, index=True).to_numpy(dtype=np.uint64)
    return hashlib.sha256(hashed.tobytes()).hexdigest()


def _git_value(args: list[str], root: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def _altitude_band(values: pd.Series) -> pd.Series:
    altitude = values.to_numpy(dtype=float)
    labels = np.select(
        [
            (altitude >= 18000) & (altitude < 23000),
            (altitude >= 23000) & (altitude < 28000),
            (altitude >= 28000) & (altitude < 33000),
            (altitude >= 33000) & (altitude < 38000),
            (altitude >= 38000) & (altitude <= 40000),
        ],
        ["18-<23 kft", "23-<28 kft", "28-<33 kft", "33-<38 kft", "38-40 kft"],
        default="outside envelope",
    )
    return pd.Series(labels, index=values.index, dtype=str)


def _cluster_ids(frame: pd.DataFrame) -> np.ndarray:
    return (
        frame["altitude"].astype(str)
        + "|"
        + frame["prebreathing_time"].astype(str)
        + "|"
        + frame["exercise_level"].astype(str)
    ).to_numpy(dtype=object)


def _prediction_frame(
    test: pd.DataFrame,
    prediction: dict[str, np.ndarray],
    *,
    variant: str,
) -> pd.DataFrame:
    y = test["pdcs_adrac_target"].to_numpy(dtype=float)
    result = test[
        [
            "source_cell_id",
            "altitude",
            "prebreathing_time",
            "exercise_level",
            "time_at_altitude",
            "source_risk_stratum",
            "boundary_shell",
        ]
    ].copy()
    result["altitude_band"] = _altitude_band(test["altitude"])
    result["variant"] = variant
    result["source_risk"] = y
    result["point"] = prediction["point"]
    result["lower"] = prediction["lower"]
    result["upper"] = prediction["upper"]
    result["error"] = result["point"] - result["source_risk"]
    result["absolute_error"] = result["error"].abs()
    result["interval_width"] = result["upper"] - result["lower"]
    result["covered"] = (
        (result["source_risk"] >= result["lower"])
        & (result["source_risk"] <= result["upper"])
    )
    result["in_envelope"] = prediction["in_envelope"]
    if "p_zero" in prediction:
        result["p_zero"] = prediction["p_zero"]
        result["is_gated_zero"] = prediction["is_gated_zero"]
    return result


def _point_and_interval_metrics(frame: pd.DataFrame, nominal: float) -> dict[str, Any]:
    return {
        "point": point_errors(frame["source_risk"].to_numpy(), frame["point"].to_numpy()),
        "interval": interval_efficiency(
            frame["source_risk"].to_numpy(),
            frame["lower"].to_numpy(),
            frame["upper"].to_numpy(),
            nominal=nominal,
        ),
        "ood_abstention_fraction": float((~frame["in_envelope"]).mean()),
    }


def _group_interval_table(
    predictions: pd.DataFrame,
    *,
    group_column: str,
    nominal: float,
    n_boot: int,
    bootstrap_seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (variant, group), subset in predictions.groupby(["variant", group_column], sort=False):
        efficiency = interval_efficiency(
            subset["source_risk"].to_numpy(),
            subset["lower"].to_numpy(),
            subset["upper"].to_numpy(),
            nominal=nominal,
        )
        row: dict[str, Any] = {
            "variant": variant,
            group_column: group,
            **efficiency,
            "coverage_interpretation": "descriptive post hoc subgroup estimate",
        }
        if variant == "zero_inflated":
            ci = cluster_bootstrap_coverage_ci(
                subset["covered"].to_numpy(),
                _cluster_ids(subset),
                n_boot=n_boot,
                seed=bootstrap_seed,
            )
            row.update(
                coverage_ci_lower=ci["lower"],
                coverage_ci_upper=ci["upper"],
                n_clusters=ci["n_clusters"],
                bootstrap_replicates=ci["n_boot"],
            )
        rows.append(row)
    return pd.DataFrame(rows)


def _safety_error_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    groups: list[tuple[str, pd.DataFrame]] = [("overall", frame)]
    groups.extend((f"risk: {name}", subset) for name, subset in frame.groupby("source_risk_stratum"))
    groups.extend((f"altitude: {name}", subset) for name, subset in frame.groupby("altitude_band"))
    groups.append(("boundary shell", frame.loc[frame["boundary_shell"]]))
    groups.append(("source risk >=0.10", frame.loc[frame["source_risk"] >= 0.10]))
    groups.append(("source risk >=0.20", frame.loc[frame["source_risk"] >= 0.20]))
    for label, subset in groups:
        if subset.empty:
            continue
        under = subset["source_risk"] - subset["point"]
        rows.append(
            {
                "stratum": label,
                "n": len(subset),
                "mae": float(subset["absolute_error"].mean()),
                "mean_signed_error": float(subset["error"].mean()),
                "max_underprediction": float(max(0.0, under.max())),
                "fraction_underpredicted": float((under > 0.0).mean()),
                "fraction_underpredicted_gt_0.01": float((under > 0.01).mean()),
                "fraction_underpredicted_gt_0.02": float((under > 0.02).mean()),
                "fraction_underpredicted_gt_0.05": float((under > 0.05).mean()),
            }
        )
    return rows


def _train_config(config: dict[str, Any], seed: int) -> TrainConfig:
    model = config.get("model", {})
    return TrainConfig(
        n_estimators=int(model.get("n_estimators", 400)),
        learning_rate=float(model.get("learning_rate", 0.05)),
        num_leaves=int(model.get("num_leaves", 31)),
        max_depth=int(model.get("max_depth", -1)),
        min_data_in_leaf=int(model.get("min_data_in_leaf", 20)),
        subsample=float(model.get("subsample", 0.9)),
        subsample_freq=int(model.get("subsample_freq", 1)),
        colsample_bytree=float(model.get("colsample_bytree", 0.9)),
        reg_alpha=float(model.get("reg_alpha", 0.0)),
        reg_lambda=float(model.get("reg_lambda", 0.0)),
        random_state=int(seed),
    )


def _structured_validation(
    augmented: pd.DataFrame,
    config: dict[str, Any],
    *,
    confidence: float,
) -> pd.DataFrame:
    analysis = config.get("analysis", {})
    seeds = [int(seed) for seed in analysis.get("structured_seeds", [17, 42, 73, 101, 2026])]
    selected_families = set(
        analysis.get(
            "structured_families",
            [
                "altitude_band",
                "prebreathe_level",
                "duration_band",
                "exercise_level",
                "altitude_x_duration",
            ],
        )
    )
    folds = [fold for fold in build_structured_holdouts(augmented) if fold.family in selected_families]
    all_indices = augmented.index.to_numpy(dtype=int)
    rows: list[dict[str, Any]] = []
    for seed in seeds:
        for fold in folds:
            train, calibration = split_train_calibration(
                all_indices,
                fold.test_indices,
                seed=seed,
                calibration_fraction=0.20,
            )
            surrogate = fit_variant_on_split(
                augmented,
                feature_names=list(FEATURE_COLUMNS),
                target_col="pdcs_adrac_target",
                train_indices=train,
                calibration_indices=calibration,
                variant="zero_inflated",
                config=_train_config(config, seed),
                confidence=confidence,
            )
            test = augmented.loc[fold.test_indices]
            prediction = surrogate.predict(test[list(FEATURE_COLUMNS)])
            frame = _prediction_frame(test, prediction, variant="zero_inflated")
            metrics = _point_and_interval_metrics(frame, confidence)
            safety = _safety_error_rows(frame)[0]
            rows.append(
                {
                    "family": fold.family,
                    "holdout": fold.label,
                    "seed": seed,
                    "n_train": len(train),
                    "n_calibration": len(calibration),
                    "n_test": len(fold.test_indices),
                    **metrics["point"],
                    **metrics["interval"],
                    "ood_abstention_fraction": metrics["ood_abstention_fraction"],
                    "mean_signed_error": safety["mean_signed_error"],
                    "max_underprediction": safety["max_underprediction"],
                    "fraction_underpredicted_gt_0.02": safety[
                        "fraction_underpredicted_gt_0.02"
                    ],
                }
            )
    return pd.DataFrame(rows)


def run_revision_analysis(config: dict[str, Any], output_dir: Path | str) -> dict[str, Any]:
    """Run the locked KJAsEM revision analysis and write auditable artifacts."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    analysis = config.get("analysis", {})
    confidence = float(analysis.get("confidence", 0.95))
    baseline_seed = int(analysis.get("baseline_seed", 42))
    augmentation_seed = int(analysis.get("augmentation_seed", 42))
    n_boot = int(analysis.get("bootstrap_replicates", 10_000))
    bootstrap_seed = int(analysis.get("bootstrap_seed", 2026))

    raw_path = Path(config["input"]["raw_csv"]).resolve()
    raw = pd.read_csv(raw_path)
    clean, clean_report = clean_dcs_risk_db(raw)
    clean = clean.reset_index(drop=True)
    augmented = augment_adrac_grid(clean, seed=augmentation_seed)
    strata, risk_cutpoints = assign_source_risk_strata(
        augmented["pdcs_adrac_target"].to_numpy()
    )
    augmented["source_risk_stratum"] = strata
    augmented["boundary_shell"] = boundary_shell_mask(augmented)

    train, calibration, test_indices = random_train_cal_test_split(
        augmented.index.to_numpy(), seed=baseline_seed
    )
    predictions: list[pd.DataFrame] = []
    random_metrics: dict[str, Any] = {}
    for variant in VARIANTS:
        surrogate = fit_variant_on_split(
            augmented,
            feature_names=list(FEATURE_COLUMNS),
            target_col="pdcs_adrac_target",
            train_indices=train,
            calibration_indices=calibration,
            variant=variant,
            config=_train_config(config, baseline_seed),
            confidence=confidence,
        )
        test = augmented.loc[test_indices]
        prediction = surrogate.predict(test[list(FEATURE_COLUMNS)])
        frame = _prediction_frame(test, prediction, variant=variant)
        predictions.append(frame)
        random_metrics[variant] = _point_and_interval_metrics(frame, confidence)

    prediction_table = pd.concat(predictions, ignore_index=True)
    altitude_table = _group_interval_table(
        prediction_table,
        group_column="altitude_band",
        nominal=confidence,
        n_boot=n_boot,
        bootstrap_seed=bootstrap_seed,
    )
    risk_table = _group_interval_table(
        prediction_table,
        group_column="source_risk_stratum",
        nominal=confidence,
        n_boot=n_boot,
        bootstrap_seed=bootstrap_seed,
    )
    overall_table = pd.DataFrame(
        [
            {"variant": variant, **metrics["point"], **metrics["interval"]}
            for variant, metrics in random_metrics.items()
        ]
    )
    final_prediction = prediction_table.loc[prediction_table["variant"] == "zero_inflated"]
    safety_table = pd.DataFrame(_safety_error_rows(final_prediction))

    structured = _structured_validation(augmented, config, confidence=confidence)
    structured_summary = (
        structured.groupby(["family", "holdout"], sort=False)
        .agg(
            seeds=("seed", "nunique"),
            n_test=("n_test", "first"),
            mae_mean=("mae", "mean"),
            mae_sd=("mae", "std"),
            mae_worst=("mae", "max"),
            rmse_mean=("rmse", "mean"),
            r2_mean=("r2", "mean"),
            coverage_mean=("coverage", "mean"),
            coverage_min=("coverage", "min"),
            mean_width_mean=("mean_width", "mean"),
            median_width_mean=("median_width", "mean"),
            max_underprediction_worst=("max_underprediction", "max"),
        )
        .reset_index()
    )

    prediction_table.to_csv(output / "random_split_predictions.csv.gz", index=False)
    overall_table.to_csv(output / "interval_efficiency_overall.csv", index=False)
    altitude_table.to_csv(output / "interval_efficiency_by_altitude.csv", index=False)
    risk_table.to_csv(output / "interval_efficiency_by_source_risk.csv", index=False)
    safety_table.to_csv(output / "safety_error_analysis.csv", index=False)
    structured.to_csv(output / "structured_validation_by_seed.csv", index=False)
    structured_summary.to_csv(output / "structured_validation_summary.csv", index=False)

    repository_root = Path(__file__).resolve().parent.parent
    provenance = {
        "manuscript_id": "KJAsEM-26-0013",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_code_commit": _git_value(["rev-parse", "HEAD"], repository_root),
        "analysis_worktree_status": _git_value(["status", "--short"], repository_root),
        "raw_source_path": str(raw_path),
        "raw_source_sha256": _sha256_file(raw_path),
        "cleaned_grid_sha256": _dataframe_sha256(clean),
        "augmented_grid_sha256": _dataframe_sha256(augmented[list(FEATURE_COLUMNS)]),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__,
        "lightgbm": lightgbm.__version__,
        "config": config,
        "cleaning_report": asdict(clean_report),
    }
    # Dataframe examples in CleanReport are useful interactively but are not
    # suitable for the machine-readable provenance JSON.
    provenance["cleaning_report"].pop("examples_scale_fixed", None)
    provenance["cleaning_report"].pop("examples_disagreements", None)
    _write_json(output / "provenance.json", provenance)

    summary: dict[str, Any] = {
        "schema_version": 1,
        "manuscript_id": "KJAsEM-26-0013",
        "source_target": "cleaned ADRAC-derived planning-grid probability",
        "clinical_outcome_validation": False,
        "n_source_cells": len(augmented),
        "random_split": {
            "seed": baseline_seed,
            "n_train": len(train),
            "n_calibration": len(calibration),
            "n_test": len(test_indices),
            "variants": random_metrics,
        },
        "source_risk_nonzero_quartile_cutpoints": risk_cutpoints,
        "altitude_subgroup_coverage_interpretation": (
            "descriptive post hoc estimates; calibration does not provide a simultaneous "
            "group-conditional coverage guarantee"
        ),
        "zero_inflated_altitude_bands": altitude_table.loc[
            altitude_table["variant"] == "zero_inflated"
        ].to_dict(orient="records"),
        "structured_validation": {
            "seeds": sorted(structured["seed"].unique().astype(int).tolist()),
            "n_fits": len(structured),
            "families": structured_summary.to_dict(orient="records"),
        },
        "artifacts": {
            "random_split_predictions": "random_split_predictions.csv.gz",
            "interval_efficiency_overall": "interval_efficiency_overall.csv",
            "interval_efficiency_by_altitude": "interval_efficiency_by_altitude.csv",
            "interval_efficiency_by_source_risk": "interval_efficiency_by_source_risk.csv",
            "safety_error_analysis": "safety_error_analysis.csv",
            "structured_validation_by_seed": "structured_validation_by_seed.csv",
            "structured_validation_summary": "structured_validation_summary.csv",
            "provenance": "provenance.json",
        },
    }
    _write_json(output / "metrics.json", summary)
    compatibility_path = Path(
        config.get("output", {}).get(
            "compatibility_metrics", output.parent / "metrics_zi.json"
        )
    )
    if not compatibility_path.is_absolute():
        compatibility_path = repository_root / compatibility_path
    _write_json(compatibility_path, summary)
    return _json_ready(summary)
