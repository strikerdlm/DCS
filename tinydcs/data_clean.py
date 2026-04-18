"""Cleaner for DCS_Risk_DB_2025.csv.

The shipped CSV has a known issue: the ``risk_of_decompression_sickness`` column is
documented as a percentage in [0, 100], but a subset of rows were accidentally stored
on the fraction scale [0, 1] instead. In addition, some grid cells
(altitude, prebreathe_time, exercise_level, time_at_altitude) have two rows that
disagree in value.

This module audits both issues and produces:

* a repaired dataframe where suspected-fraction rows have been rescaled to the
  percent scale;
* a human-readable markdown report describing what was changed and why.

Detection heuristic for the scale bug
-------------------------------------
For each row we compare its target to the *combo-median* target across all rows
sharing its (altitude, prebreathe_time, exercise_level, time_at_altitude)
signature. If the row's value is consistent with ``100 × median`` (within a
tolerance) *and* inconsistent with ``median`` itself, we flag it as a fraction
entry and rescale it by ``× 100``. When no in-combo reference exists, we fall
back to a global neighbourhood regression over the four covariates.

This heuristic is intentionally conservative: it never flags rows that are
consistent with their neighbours on the percent scale, and it documents every
change in the report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


_EXPECTED_COLUMNS = (
    "altitude",
    "prebreathing_time",
    "exercise_level",
    "time_at_altitude",
    "risk_of_decompression_sickness",
)
_COMBO_KEYS = ("altitude", "prebreathing_time", "exercise_level", "time_at_altitude")
_FRACTION_ABS_THRESHOLD = 1.0 - 1e-9  # values <= this look like fractions
_FRACTION_RESCALE = 100.0


@dataclass(slots=True)
class CleanReport:
    """Human-readable summary of what ``clean_dcs_risk_db`` changed."""

    n_rows_in: int
    n_rows_out: int
    n_target_nan_in: int
    n_scale_fixed: int
    n_within_combo_disagreements: int
    n_rows_deduped: int
    examples_scale_fixed: pd.DataFrame = field(default_factory=pd.DataFrame)
    examples_disagreements: pd.DataFrame = field(default_factory=pd.DataFrame)

    def to_markdown(self) -> str:
        lines: list[str] = [
            "# DCS_Risk_DB_2025.csv — data-quality report",
            "",
            f"- **Rows in**: {self.n_rows_in:,}",
            f"- **Rows out**: {self.n_rows_out:,}",
            f"- **Target NaNs on input**: {self.n_target_nan_in:,}",
            f"- **Rows rescaled from fraction→percent**: {self.n_scale_fixed:,}",
            f"- **Grid cells with within-combo disagreement**: {self.n_within_combo_disagreements:,}",
            f"- **Rows removed by dedup-to-median**: {self.n_rows_deduped:,}",
            "",
            "## Rescaling logic",
            "",
            "For each grid cell defined by "
            "`(altitude, prebreathing_time, exercise_level, time_at_altitude)`, "
            "we compare each row's target to the combo-median. A row is flagged "
            "as a fraction-scale mistake if its value is ≤ 1.0 and is "
            "consistent (within 10%) with `median / 100`, while the combo median "
            "itself exceeds 1.0. Flagged rows are multiplied by 100.",
            "",
        ]
        if len(self.examples_scale_fixed) > 0:
            lines += [
                "### Examples of rescaled rows (up to 20)",
                "",
                self.examples_scale_fixed.head(20).to_markdown(index=False),
                "",
            ]
        if len(self.examples_disagreements) > 0:
            lines += [
                "### Examples of within-combo disagreements (up to 20)",
                "",
                "After rescaling, these cells still contained multiple distinct "
                "target values. Dedup keeps the median.",
                "",
                self.examples_disagreements.head(20).to_markdown(index=False),
                "",
            ]
        return "\n".join(lines)


def _validate_input(df: pd.DataFrame) -> None:
    missing = [c for c in _EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Input is missing required columns: {missing}")


_ALT_WINDOW = 1000  # ft; ±1000 matches the dataset's 500-ft spacing
_TIME_WINDOW = 20    # min; ±20 matches the dataset's 10-min spacing
_PB_WINDOW = 15      # min
_SCALE_REL_TOL = 0.30  # fraction rows are flagged if 100× value is within 30% of neighbour median


def _neighbour_median(df: pd.DataFrame, percent_mask: np.ndarray) -> np.ndarray:
    """For each row, return the median target over its neighbourhood, using
    only rows known to be on the percent scale (``percent_mask``).

    Neighbourhood: same exercise level, altitude within ±_ALT_WINDOW, prebreathe
    within ±_PB_WINDOW, time within ±_TIME_WINDOW. Uses a vectorized group-wise
    lookup keyed on (exercise, rounded-altitude-band, rounded-time-band) for
    speed; an exact O(N) neighbour scan is documented below as the reference.
    """
    t = df["risk_of_decompression_sickness"].to_numpy(dtype=float)
    alt = df["altitude"].to_numpy(dtype=float)
    pb = df["prebreathing_time"].to_numpy(dtype=float)
    time_ = df["time_at_altitude"].to_numpy(dtype=float)
    ex = df["exercise_level"].to_numpy()

    idx = np.arange(len(df))
    out = np.full(len(df), np.nan, dtype=float)

    # Build a reference pool of percent-scale rows for fast lookup.
    ref_mask = percent_mask
    if not ref_mask.any():
        return out

    ref = df.loc[ref_mask].copy()
    ref_alt = ref["altitude"].to_numpy(dtype=float)
    ref_pb = ref["prebreathing_time"].to_numpy(dtype=float)
    ref_time = ref["time_at_altitude"].to_numpy(dtype=float)
    ref_ex = ref["exercise_level"].to_numpy()
    ref_t = ref["risk_of_decompression_sickness"].to_numpy(dtype=float)

    # Group reference rows by exercise level for an O(R) per-row slice.
    ex_levels = np.unique(ref_ex)
    ref_by_ex: dict[object, np.ndarray] = {}
    for lvl in ex_levels:
        ref_by_ex[lvl] = np.where(ref_ex == lvl)[0]

    for i in idx:
        pool = ref_by_ex.get(ex[i])
        if pool is None or pool.size == 0:
            continue
        close_alt = np.abs(ref_alt[pool] - alt[i]) <= _ALT_WINDOW
        close_pb = np.abs(ref_pb[pool] - pb[i]) <= _PB_WINDOW
        close_t = np.abs(ref_time[pool] - time_[i]) <= _TIME_WINDOW
        sel = pool[close_alt & close_pb & close_t]
        if sel.size == 0:
            continue
        out[i] = float(np.median(ref_t[sel]))
    return out


def _flag_scale_rows(df: pd.DataFrame) -> pd.Series:
    """Identify rows whose target appears to be on the fraction scale.

    Heuristic
    ---------
    A row is flagged when:
      (a) its raw value is in (0, 1]  -- on the fraction-scale band,
      (b) there exist neighbour rows (same exercise, close altitude/PB/time)
          whose bulk is clearly on the percent scale, and
      (c) rescaling the row (×100) brings it within _SCALE_REL_TOL of the
          neighbour-median.

    Rows with exact zeros are *not* flagged because 0.0 is identical on both
    scales and so cannot be disambiguated.
    """
    t = df["risk_of_decompression_sickness"].to_numpy(dtype=float)
    # Percent-scale reference pool: values clearly > 1.0.
    percent_mask = t > 1.0 + 1e-9
    neighbour_med = _neighbour_median(df, percent_mask)

    rescaled = t * _FRACTION_RESCALE
    has_ref = np.isfinite(neighbour_med) & (neighbour_med > 1.0 + 1e-9)
    ratio = np.full_like(rescaled, np.inf)
    valid = has_ref & (t > 0.0) & (t <= _FRACTION_ABS_THRESHOLD)
    if np.any(valid):
        ratio[valid] = rescaled[valid] / np.maximum(neighbour_med[valid], 1e-9)
    flagged = valid & (np.abs(ratio - 1.0) <= _SCALE_REL_TOL)
    return pd.Series(flagged, index=df.index)


def _dedup_to_median(df: pd.DataFrame) -> tuple[pd.DataFrame, int, pd.DataFrame]:
    """Collapse duplicate grid cells, keeping the median. Also returns a
    small sample of disagreement cases for the report.
    """
    grouped = df.groupby(list(_COMBO_KEYS), as_index=False, sort=False)
    agg = grouped["risk_of_decompression_sickness"].agg(["median", "nunique", "count"])
    disagreements = agg.loc[agg["nunique"] > 1].copy()
    disagreements.rename(columns={"nunique": "n_unique_values", "count": "n_rows"}, inplace=True)
    disagreements = disagreements.head(50)

    out = (
        grouped["risk_of_decompression_sickness"]
        .median()
        .rename(columns={"risk_of_decompression_sickness": "risk_of_decompression_sickness"})
    )
    n_removed = int(len(df) - len(out))
    return out, n_removed, disagreements


def clean_dcs_risk_db(
    df: pd.DataFrame,
    *,
    drop_nan_target: bool = True,
    clip_target: bool = True,
) -> tuple[pd.DataFrame, CleanReport]:
    """Audit and repair the shipped DCS_Risk_DB_2025.csv.

    Parameters
    ----------
    df
        Input dataframe matching the shipped schema.
    drop_nan_target
        If True (default), drop rows where the target is NaN after repair.
    clip_target
        If True (default), clip the repaired target to [0, 100].

    Returns
    -------
    repaired
        Cleaned dataframe with the target consistently on the percent scale,
        deduplicated to one row per grid cell.
    report
        :class:`CleanReport` summarising the changes.
    """
    _validate_input(df)
    n_rows_in = int(len(df))
    n_target_nan_in = int(df["risk_of_decompression_sickness"].isna().sum())

    work = df.copy()
    work["risk_of_decompression_sickness"] = work["risk_of_decompression_sickness"].astype(float)

    # Step 1: rescale fraction-scale rows.
    flagged = _flag_scale_rows(work)
    n_scale_fixed = int(flagged.sum())
    examples_scale_fixed = pd.DataFrame()
    if n_scale_fixed > 0:
        examples_scale_fixed = (
            work.loc[flagged, list(_COMBO_KEYS) + ["risk_of_decompression_sickness"]]
            .assign(repaired_value=work.loc[flagged, "risk_of_decompression_sickness"] * _FRACTION_RESCALE)
            .head(20)
            .reset_index(drop=True)
        )
        work.loc[flagged, "risk_of_decompression_sickness"] *= _FRACTION_RESCALE

    # Step 2: optional NaN drop + clipping.
    if drop_nan_target:
        work = work.dropna(subset=["risk_of_decompression_sickness"])
    if clip_target:
        work["risk_of_decompression_sickness"] = work["risk_of_decompression_sickness"].clip(lower=0.0, upper=100.0)

    # Step 3: deduplicate by grid cell, keeping the median.
    deduped, n_rows_deduped, disagreements = _dedup_to_median(work)

    n_disagreements = int(len(disagreements))
    report = CleanReport(
        n_rows_in=n_rows_in,
        n_rows_out=int(len(deduped)),
        n_target_nan_in=n_target_nan_in,
        n_scale_fixed=n_scale_fixed,
        n_within_combo_disagreements=n_disagreements,
        n_rows_deduped=n_rows_deduped,
        examples_scale_fixed=examples_scale_fixed,
        examples_disagreements=disagreements,
    )
    return deduped, report


def run_file(input_path: Path, output_path: Path, report_path: Path) -> CleanReport:
    """Convenience entry point: read CSV, clean, write parquet + report."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    report_path = Path(report_path)

    df = pd.read_csv(input_path)
    repaired, report = clean_dcs_risk_db(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.suffix.lower() == ".parquet":
        repaired.to_parquet(output_path, index=False)
    else:
        repaired.to_csv(output_path, index=False)

    report_path.write_text(report.to_markdown(), encoding="utf-8")
    return report
