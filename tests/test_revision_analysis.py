"""Tests for the KJAsEM-26-0013 reviewer-analysis utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from tinydcs.kjasem_revision import run_revision_analysis
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
from tinydcs.surrogate import TrainConfig, ZeroInflatedCalibration


@pytest.fixture
def miniature_grid() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cell_id = 0
    for altitude in (18000, 22500, 23000, 27500, 28000, 32500, 33000, 37500, 40000):
        for prebreathe in (0, 15, 30, 45, 60):
            for exercise in ("Rest", "Mild", "Heavy"):
                for duration in (10, 60, 70, 120, 130, 180, 190, 240):
                    rows.append(
                        {
                            "cell_id": cell_id,
                            "altitude": altitude,
                            "prebreathing_time": prebreathe,
                            "exercise_level": exercise,
                            "time_at_altitude": duration,
                            "risk": max(0.0, (altitude - 22000) / 22000 + duration / 500 - prebreathe / 200),
                        }
                    )
                    cell_id += 1
    return pd.DataFrame(rows)


def test_structured_holdouts_cover_locked_families(miniature_grid: pd.DataFrame) -> None:
    folds = build_structured_holdouts(miniature_grid)
    by_family = {}
    for fold in folds:
        by_family.setdefault(fold.family, []).append(fold)

    assert len(by_family["altitude_band"]) == 5
    assert len(by_family["prebreathe_level"]) == 5
    assert len(by_family["duration_band"]) == 4
    assert len(by_family["exercise_level"]) == 3
    assert len(by_family["altitude_x_duration"]) == 20

    for family, family_folds in by_family.items():
        held_out = np.concatenate([f.test_indices for f in family_folds])
        assert sorted(held_out.tolist()) == sorted(miniature_grid.index.tolist()), family

    altitude_labels = [f.label for f in by_family["altitude_band"]]
    assert altitude_labels == ["18-<23 kft", "23-<28 kft", "28-<33 kft", "33-<38 kft", "38-40 kft"]


def test_train_calibration_split_is_deterministic_and_leak_free(miniature_grid: pd.DataFrame) -> None:
    test_idx = build_structured_holdouts(miniature_grid)[0].test_indices
    train_a, cal_a = split_train_calibration(miniature_grid.index.to_numpy(), test_idx, seed=42)
    train_b, cal_b = split_train_calibration(miniature_grid.index.to_numpy(), test_idx, seed=42)

    assert np.array_equal(train_a, train_b)
    assert np.array_equal(cal_a, cal_b)
    assert set(train_a).isdisjoint(cal_a)
    assert set(train_a).isdisjoint(test_idx)
    assert set(cal_a).isdisjoint(test_idx)
    assert set(train_a) | set(cal_a) | set(test_idx) == set(miniature_grid.index)
    remaining = len(miniature_grid) - len(test_idx)
    assert len(cal_a) == round(remaining * 0.20)


def test_random_split_uses_locked_70_15_15_partition(miniature_grid: pd.DataFrame) -> None:
    train, calibration, test = random_train_cal_test_split(
        miniature_grid.index.to_numpy(), seed=42
    )
    n = len(miniature_grid)
    assert len(test) == round(n * 0.15)
    assert len(calibration) == round(n * 0.15)
    assert len(train) == n - len(test) - len(calibration)
    assert set(train) | set(calibration) | set(test) == set(miniature_grid.index)
    assert set(train).isdisjoint(calibration)
    assert set(train).isdisjoint(test)
    assert set(calibration).isdisjoint(test)


def test_interval_efficiency_reports_coverage_and_width_distribution() -> None:
    y = np.array([0.0, 0.2, 0.5, 0.9])
    lower = np.array([0.0, 0.0, 0.4, 0.7])
    upper = np.array([0.1, 0.3, 0.6, 0.8])
    result = interval_efficiency(y, lower, upper, nominal=0.95)

    assert result["n"] == 4
    assert result["n_covered"] == 3
    assert result["coverage"] == pytest.approx(0.75)
    assert result["mean_width"] == pytest.approx(0.175)
    assert result["median_width"] == pytest.approx(0.15)
    assert result["p90_width"] == pytest.approx(0.27)


def test_cluster_bootstrap_coverage_ci_is_deterministic() -> None:
    covered = np.array([1, 1, 0, 1, 0, 0, 1, 1], dtype=bool)
    clusters = np.array(["a", "a", "b", "b", "c", "c", "d", "d"])
    first = cluster_bootstrap_coverage_ci(covered, clusters, n_boot=500, seed=2026)
    second = cluster_bootstrap_coverage_ci(covered, clusters, n_boot=500, seed=2026)

    assert first == second
    assert first["n_clusters"] == 4
    assert first["lower"] <= covered.mean() <= first["upper"]


def test_source_risk_strata_separate_zero_then_nonzero_quartiles() -> None:
    risk = np.array([0.0, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    labels, cutpoints = assign_source_risk_strata(risk)

    assert labels.tolist()[:2] == ["exact zero", "exact zero"]
    assert set(labels[2:]) == {"nonzero Q1", "nonzero Q2", "nonzero Q3", "nonzero Q4"}
    assert len(cutpoints) == 3


def test_boundary_shell_marks_supported_envelope_edges(miniature_grid: pd.DataFrame) -> None:
    mask = boundary_shell_mask(miniature_grid)
    middle = miniature_grid.loc[
        (miniature_grid.altitude == 28000)
        & (miniature_grid.prebreathing_time == 30)
        & (miniature_grid.time_at_altitude == 120)
    ]
    edge = miniature_grid.loc[miniature_grid.altitude == 18000]

    assert not mask.loc[middle.index].any()
    assert mask.loc[edge.index].all()


def test_fixed_split_zero_inflated_fit_does_not_repartition() -> None:
    rng = np.random.default_rng(7)
    n = 500
    x = rng.uniform(-1.0, 1.0, size=n)
    z = rng.uniform(0.0, 1.0, size=n)
    target = np.where(x < -0.25, 0.0, np.clip(0.05 + 0.4 * x + 0.1 * z, 0.01, 0.9))
    frame = pd.DataFrame({"x": x, "z": z, "target": target})
    train = np.arange(0, 300)
    calibration = np.arange(300, 400)
    test = np.arange(400, 500)

    surrogate = fit_variant_on_split(
        frame,
        feature_names=["x", "z"],
        target_col="target",
        train_indices=train,
        calibration_indices=calibration,
        variant="zero_inflated",
        config=TrainConfig(
            n_estimators=30,
            num_leaves=7,
            min_data_in_leaf=5,
            monotonic_constraints={},
        ),
    )
    prediction = surrogate.predict(frame.loc[test, ["x", "z"]])
    assert isinstance(surrogate.conformal, ZeroInflatedCalibration)
    assert prediction["point"].shape == (len(test),)
    assert np.all((prediction["lower"] >= 0.0) & (prediction["upper"] <= 1.0))


def test_adrac_augmentation_is_deterministic_and_keeps_cell_keys() -> None:
    raw = pd.DataFrame(
        {
            "altitude": [18000, 30000, 40000],
            "prebreathing_time": [0, 30, 60],
            "exercise_level": ["Rest", "Mild", "Heavy"],
            "time_at_altitude": [10, 120, 240],
            "risk_of_decompression_sickness": [0.0, 20.0, 80.0],
        }
    )
    first = augment_adrac_grid(raw, seed=42)
    second = augment_adrac_grid(raw, seed=42)

    pd.testing.assert_frame_equal(first, second)
    assert first["source_cell_id"].tolist() == [0, 1, 2]
    assert first["pdcs_adrac_target"].tolist() == [0.0, 0.2, 0.8]
    assert first["altitude"].tolist() == raw["altitude"].tolist()
    assert first["exercise_level"].tolist() == raw["exercise_level"].tolist()


def test_revision_pipeline_emits_reviewer_artifacts(
    miniature_grid: pd.DataFrame, tmp_path
) -> None:
    raw = miniature_grid.rename(
        columns={"risk": "risk_of_decompression_sickness"}
    ).drop(columns="cell_id")
    exercise_add = raw["exercise_level"].map({"Rest": 0.0, "Mild": 8.0, "Heavy": 16.0})
    raw["risk_of_decompression_sickness"] = np.clip(
        (raw["altitude"] - 22000) / 400
        + raw["time_at_altitude"] / 12
        - raw["prebreathing_time"] / 4
        + exercise_add,
        0.0,
        98.0,
    )
    raw_path = tmp_path / "grid.csv"
    raw.to_csv(raw_path, index=False)
    out = tmp_path / "reviewer"
    compatibility = tmp_path / "metrics_zi.json"
    config = {
        "input": {"raw_csv": str(raw_path)},
        "analysis": {
            "baseline_seed": 42,
            "augmentation_seed": 42,
            "structured_seeds": [17],
            "structured_families": ["altitude_band"],
            "confidence": 0.95,
            "bootstrap_replicates": 100,
            "bootstrap_seed": 2026,
        },
        "model": {"n_estimators": 10, "num_leaves": 7, "min_data_in_leaf": 5},
        "output": {"compatibility_metrics": str(compatibility)},
    }

    summary = run_revision_analysis(config, out)

    assert summary["n_source_cells"] == len(raw)
    assert compatibility.exists()
    assert (out / "random_split_predictions.csv.gz").exists()
    assert (out / "structured_validation_by_seed.csv").exists()
    assert (out / "interval_efficiency_by_altitude.csv").exists()
    assert (out / "provenance.json").exists()
