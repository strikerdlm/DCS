"""Unit tests for tinydcs.data_clean."""

from __future__ import annotations

import pandas as pd
import pytest

from tinydcs.data_clean import clean_dcs_risk_db


@pytest.fixture
def mixed_scale_df() -> pd.DataFrame:
    # Grid cell A: majority of rows in percent (50, 52), one mis-entered as 0.51.
    # Grid cell B: majority of rows in percent (10, 11), one mis-entered as 0.10.
    # Grid cell C: pure percent, no errors.
    rows = [
        # altitude, prebreathing_time, exercise_level, time_at_altitude, target
        (30000, 0, "Rest", 240, 50.0),
        (30000, 0, "Rest", 240, 52.0),
        (30000, 0, "Rest", 240, 0.51),   # ← fraction mistake
        (25000, 0, "Rest", 240, 10.0),
        (25000, 0, "Rest", 240, 11.0),
        (25000, 0, "Rest", 240, 0.10),   # ← fraction mistake
        (20000, 0, "Rest", 240, 2.0),
        (20000, 0, "Rest", 240, 2.5),
    ]
    return pd.DataFrame(rows, columns=[
        "altitude", "prebreathing_time", "exercise_level", "time_at_altitude",
        "risk_of_decompression_sickness",
    ])


def test_scale_fix_flags_and_rescales(mixed_scale_df: pd.DataFrame) -> None:
    cleaned, report = clean_dcs_risk_db(mixed_scale_df)

    assert report.n_scale_fixed == 2, "expected exactly the two seeded fraction rows to be flagged"
    # After cleaning, every cell should have values on the percent scale.
    for _, row in cleaned.iterrows():
        tgt = row["risk_of_decompression_sickness"]
        assert 0.0 <= tgt <= 100.0
    # Cell A median should now be ~ median(50, 52, 51) = 51.
    a_val = cleaned.loc[
        (cleaned.altitude == 30000) & (cleaned.time_at_altitude == 240),
        "risk_of_decompression_sickness",
    ].iloc[0]
    assert 50.0 <= a_val <= 52.0


def test_dedup_collapses_cells(mixed_scale_df: pd.DataFrame) -> None:
    cleaned, _ = clean_dcs_risk_db(mixed_scale_df)
    # Three input cells → three output rows.
    assert len(cleaned) == 3


def test_nan_target_dropped() -> None:
    df = pd.DataFrame({
        "altitude": [20000, 20000],
        "prebreathing_time": [0, 0],
        "exercise_level": ["Rest", "Rest"],
        "time_at_altitude": [60, 60],
        "risk_of_decompression_sickness": [3.0, float("nan")],
    })
    cleaned, report = clean_dcs_risk_db(df)
    assert report.n_target_nan_in == 1
    assert len(cleaned) == 1


def test_consistent_percent_untouched() -> None:
    # A clean dataset must come out unchanged (modulo dedup-to-median collapsing duplicates).
    df = pd.DataFrame({
        "altitude": [25000, 25000, 30000],
        "prebreathing_time": [0, 0, 30],
        "exercise_level": ["Rest", "Rest", "Mild"],
        "time_at_altitude": [120, 120, 60],
        "risk_of_decompression_sickness": [12.0, 13.0, 5.0],
    })
    cleaned, report = clean_dcs_risk_db(df)
    assert report.n_scale_fixed == 0
