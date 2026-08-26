# KJAsEM-26-0013 major-revision analysis

This note documents the analysis added in response to the first review of
“TinyDCS as a calibrated surrogate for hypobaric decompression-sickness risk
estimation in aerospace medicine.” It describes surrogate fidelity to a cleaned
ADRAC-derived planning grid. It does not evaluate observed decompression
sickness, operational impairment, or flight safety.

## Locked design

- Source grid: 15,908 unique cells after the versioned cleaner repairs 1,221
  fraction/percent entries and collapses duplicate cell keys to their median.
- Random development split: 70% training, 15% calibration, 15% test; seed 42.
- Structured seeds: 17, 42, 73, 101, and 2026.
- Structured test regions: five contiguous altitude bands (18–<23, 23–<28,
  28–<33, 33–<38, and 38–40 kft), each of five source prebreathe levels, four
  contiguous duration ranges, each exercise category, and all 20
  altitude-by-duration regions.
- For every structured fold, the complete test region is removed first. The
  remaining cells are split 80/20 into model-training and conformal-calibration
  sets. Test cells never enter either set.
- Interval comparison: global split conformal, altitude-Mondrian conformal,
  global conformalized quantile regression (CQR), altitude-Mondrian CQR, and
  the zero-inflated two-stage model.
- Altitude-specific coverage is a descriptive post hoc analysis. It is not a
  claim of simultaneous or distribution-free group-conditional coverage.
- Coverage confidence intervals use 10,000 cluster-bootstrap replicates (seed
  2026). The resampling unit is `(altitude, prebreathe, exercise)` so the
  duration cells belonging to one source-grid trajectory remain together.

## Main findings

The random split continues to show high interpolation fidelity. The final
zero-inflated model had MAE 0.019744 and R² 0.98658. Its empirical coverage was
0.95767 with mean width 0.18109. Altitude-band coverage ranged from 0.95098 to
0.96642, but the cluster-bootstrap confidence intervals include values below
0.95 in every band. The subgroup estimates must therefore be reported with
their numerators, denominators, and uncertainty—not as guaranteed coverage.

The interval comparison shows that coverage was not obtained solely by making
all intervals arbitrarily wider. The global conformal variant was widest on
average (0.43555) and still covered only 0.88223 overall because it failed in
the zero-heavy 18–<23-kft band. The zero-inflated model was narrower on average
(0.18109) while restoring overall and descriptive altitude-band coverage.

The structured tests materially change the interpretation. With an entire
altitude band held out, fold-mean MAE ranged from 0.03315 to 0.12467 and the
minimum seed-specific coverage was 0.16523. Holding out an exercise category
produced fold-mean MAE from 0.08969 to 0.12846 and minimum coverage 0.36194.
These failures show that random cell splitting mainly assesses interpolation
among nearby grid cells. They do not support reliable extrapolation across a
missing exposure region.

## Evidence files

- `artifacts/repro/metrics_zi.json`: compatibility summary used by the
  manuscript source verifier.
- `artifacts/repro/kjasem_26_0013/metrics.json`: complete machine-readable
  summary.
- `random_split_predictions.csv.gz`: cell-level test predictions for all five
  interval variants.
- `interval_efficiency_overall.csv`, `interval_efficiency_by_altitude.csv`, and
  `interval_efficiency_by_source_risk.csv`: coverage and width analyses.
- `structured_validation_by_seed.csv` and
  `structured_validation_summary.csv`: all 185 structured fits and summaries.
- `safety_error_analysis.csv`: signed-error and underprediction summaries.
- `provenance.json`: source hashes, code revision, package versions, and the
  complete locked configuration.

Reproduce from the repository root with:

```bash
python scripts/04_kjasem_revision_analysis.py \
  --config configs/kjasem_26_0013.toml \
  --out artifacts/repro/kjasem_26_0013
```
