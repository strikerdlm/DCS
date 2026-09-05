"""Auditable ADRAC-grid cleaning; heuristic guesses are never primary labels.

The raw source is retained. Suspected scale errors and disagreeing duplicate
cells are excluded from the primary analysis, and available only in explicitly
labelled sensitivity datasets. No clinical outcomes are present in this grid.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

_COMBO_KEYS = ("altitude", "prebreathing_time", "exercise_level", "time_at_altitude")
_TARGET = "risk_of_decompression_sickness"
_EXPECTED_COLUMNS = (*_COMBO_KEYS, _TARGET)
_FRACTION_ABS_THRESHOLD = 1.0 - 1e-9
_FRACTION_RESCALE = 100.0


@dataclass(slots=True)
class CleanReport:
    n_rows_in: int
    n_rows_out: int
    n_target_nan_in: int
    n_scale_fixed: int
    n_within_combo_disagreements: int
    n_rows_deduped: int
    examples_scale_fixed: pd.DataFrame = field(default_factory=pd.DataFrame)
    examples_disagreements: pd.DataFrame = field(default_factory=pd.DataFrame)
    ledger: pd.DataFrame = field(default_factory=pd.DataFrame)
    policy: str = "primary"

    def to_markdown(self):
        return "\n".join([
            "# ADRAC grid data-quality record", "",
            f"- Policy: {self.policy}",
            f"- Raw rows: {self.n_rows_in}; output cells: {self.n_rows_out}",
            f"- Missing targets: {self.n_target_nan_in}",
            f"- Unresolved scale flags: {int(self.ledger['scale_suspected'].sum())}",
            f"- Disagreeing cells (full count): {self.n_within_combo_disagreements}",
            f"- Sensitivity-only rescalings: {self.n_scale_fixed}",
            f"- Identical/median duplicate rows collapsed: {self.n_rows_deduped}", "",
            "Primary labels exclude scale-flagged rows and every disagreeing cell.",
            "The scale flag compares 100 × a value in (0,1) with the same-exercise",
            "neighbour median (>1), within 30%; altitude ±1000 ft, PB ±15 min,",
            "time ±20 min. This is a heuristic, not verified correction evidence.",
            "The complete row-level ledger is saved beside the output as .ledger.csv.",
            "Sensitivity datasets retain raw medians or use heuristic-rescaled medians.",
            "These are model-generated probabilities, not observed clinical outcomes.", "",
        ])


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


def clean_dcs_risk_db(df, *, drop_nan_target=True, clip_target=False, policy="primary"):
    """Return one row per cell and a complete, untruncated source-row ledger."""
    missing = [c for c in _EXPECTED_COLUMNS if c not in df]
    if missing:
        raise ValueError(f"Input is missing required columns: {missing}")
    if policy not in ("primary", "sensitivity_raw", "sensitivity_rescaled"):
        raise ValueError("unknown cleaning policy")
    if clip_target:
        raise ValueError("Clipping invalid labels is not supported; inspect the ledger")
    work = df[list(_EXPECTED_COLUMNS)].copy().reset_index(drop=True)
    for col in ("altitude", "prebreathing_time", "time_at_altitude", _TARGET):
        work[col] = pd.to_numeric(work[col], errors="coerce")
    target = work[_TARGET]
    valid = np.isfinite(work[["altitude", "prebreathing_time", "time_at_altitude", _TARGET]]).all(axis=1)
    valid &= target.between(0, 100) & work.altitude.between(0, 20000/0.3048)
    valid &= (work.prebreathing_time >= 0) & (work.time_at_altitude >= 0)
    valid &= work.exercise_level.isin(["Rest", "Mild", "Heavy"])
    if not drop_nan_target and not valid.all():
        raise ValueError("invalid records require exclusion; see source data")
    flagged = pd.Series(False, index=work.index)
    flagged.loc[valid] = _flag_scale_rows(work.loc[valid])
    counts = work.loc[valid].groupby(list(_COMBO_KEYS))[_TARGET].nunique()
    disagreements = counts[counts > 1].reset_index(name="n_unique_values")
    cell_keys = work[list(_COMBO_KEYS)].apply(lambda r: "|".join(map(str, r)), axis=1)
    ambiguous = work[list(_COMBO_KEYS)].merge(disagreements.assign(disagreement=True), how="left", on=list(_COMBO_KEYS))["disagreement"].eq(True)
    primary = valid & ~flagged & ~ambiguous
    ledger = work.copy()
    ledger.insert(0, "source_row", np.arange(len(work)) + 2)
    ledger["cell_id"] = cell_keys.map(lambda key: hashlib.sha256(key.encode()).hexdigest()[:20])
    ledger["raw_target_percent"] = df[_TARGET].to_numpy()
    ledger["suggested_target_percent"] = np.where(flagged, target * 100, target)
    ledger["scale_suspected"] = flagged
    ledger["duplicate_disagreement"] = ambiguous
    ledger["valid_input"] = valid
    ledger["included_primary"] = primary
    ledger["correction_status"] = np.select([~valid, flagged, ambiguous], ["invalid_excluded", "heuristic_unresolved", "disagreement_unresolved"], default="unchanged")
    selected = work.loc[primary if policy == "primary" else valid].copy()
    if policy == "sensitivity_rescaled":
        selected.loc[flagged.loc[selected.index], _TARGET] *= 100
    grouped = selected.groupby(list(_COMBO_KEYS), as_index=False, sort=True)[_TARGET].median()
    grouped["cell_id"] = grouped[list(_COMBO_KEYS)].apply(lambda r: hashlib.sha256("|".join(map(str, r)).encode()).hexdigest()[:20], axis=1)
    grouped["target_provenance"] = policy
    report = CleanReport(
        len(df), len(grouped), int(target.isna().sum()),
        int(flagged.sum()) if policy == "sensitivity_rescaled" else 0,
        len(disagreements), len(selected)-len(grouped),
        ledger.loc[flagged].copy(), disagreements, ledger, policy,
    )
    return grouped, report


def run_file(input_path: Path, output_path: Path, report_path: Path) -> CleanReport:
    df = pd.read_csv(input_path)
    primary, report = clean_dcs_risk_db(df)
    output_path, report_path = Path(output_path), Path(report_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() == ".parquet":
        primary.to_parquet(output_path, index=False)
    else:
        primary.to_csv(output_path, index=False)
    report.ledger.to_csv(output_path.with_suffix(".ledger.csv"), index=False)
    for policy in ("sensitivity_raw", "sensitivity_rescaled"):
        sensitivity, _ = clean_dcs_risk_db(df, policy=policy)
        sensitivity.to_parquet(output_path.with_name(output_path.stem + "_" + policy + ".parquet"), index=False)
    report_path.write_text(report.to_markdown(), encoding="utf-8")
    return report
