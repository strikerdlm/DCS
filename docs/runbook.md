# Runbook — step-by-step reproduction of TinyDCS

This is the **command-by-command** guide to reproduce every headline number in the current release from a clean checkout. It is written so that if a development session is interrupted mid-work, the next session (human or agent) can resume cleanly by running the steps below in order.

Tested on Python 3.13 on Linux x86_64. All commands are relative to the repo root.

---

## 0. Setup

```bash
git clone https://github.com/strikerdlm/DCS
cd DCS
pip install -r requirements.txt
pytest tests/ -q
```

**Expected output**: `25 passed` in ~3 seconds, a handful of benign LightGBM feature-name warnings. If a test fails, stop and fix before going further — every downstream step depends on correct calibration / OOD / personalization behaviour.

ONNX tooling is only needed for Step 4:

```bash
pip install onnx onnxruntime onnxmltools skl2onnx onnxconverter_common
```

---

## 1. Clean the ADRAC grid

```bash
mkdir -p artifacts
python scripts/01_clean_data.py \
    --input legacy/Model_Rel_Candidate/DCS_Risk_DB_2025.csv \
    --output artifacts/DCS_Risk_DB_2025_clean.parquet \
    --report artifacts/data_quality_report.md
```

**Expected output**:

```
Cleaned 16295 → 15908 rows. Rescaled fraction→percent: 1221. Cells with disagreement: 26. Rows removed by dedup: 387.
```

**Artifacts produced**:
- `artifacts/DCS_Risk_DB_2025_clean.parquet` (≈ 14 KB) — 15,908 unique grid cells on the percent scale.
- `artifacts/data_quality_report.md` — markdown audit describing what was changed.

**Sanity check**: the cleaned parquet target should be in `[0, 100]` with the same altitude / PB / exercise / time grid as the raw CSV minus duplicates and NaNs.

---

## 2. Fit the ADRAC baseline + train the zero-inflated surrogate

This is the Paper-1 primary training pipeline.

```bash
python scripts/04_train_adrac_surrogate.py \
    --training artifacts/DCS_Risk_DB_2025_clean.parquet \
    --output-surrogate artifacts/tinydcs_adrac_zi.joblib \
    --output-baseline artifacts/adrac_baseline_zi.joblib \
    --output-metrics artifacts/metrics_adrac_zi.json \
    --output-figures artifacts/figures_adrac_zi \
    --no-run-leave-one-altitude-out --zi
```

**Expected headline output**:

```
Random split results (apples-to-apples on the same test fold):
  ADRAC baseline: MAE=0.0860, R²=0.8693, Brier=0.0150
  TinyDCS:        MAE=0.0200, R²=0.9864, Brier=0.0016, coverage=0.960
```

**Artifacts produced**:
- `artifacts/tinydcs_adrac_zi.joblib` — trained zero-inflated surrogate bundle (base + classifier + continuous sub-models + conformal + OOD + feature names).
- `artifacts/adrac_baseline_zi.joblib` — closed-form ADRAC coefficients.
- `artifacts/metrics_adrac_zi.json` — all metrics (point, Brier, per-altitude-band coverage, calibration mode).
- `artifacts/figures_adrac_zi/*.png` — reliability and Bland–Altman diagnostic plots.

**Sanity check**:

```bash
python -c "
import json
m = json.load(open('artifacts/metrics_adrac_zi.json'))
td = m['tinydcs_random_test']
print(f'Mode: {td[\"calibration_mode\"]}')
print(f'Overall coverage: {td[\"conformal_coverage\"][\"coverage\"]:.3f} (nominal 0.95)')
for k, v in sorted(td['per_band_coverage'].items()):
    print(f'  {k}: {v[\"coverage\"]:.3f}')
"
```

All five altitude bands should report coverage ≥ 0.95.

---

## 3. Train the compact edge-deployable variant

```bash
python scripts/06_train_compact_surrogate.py \
    --training artifacts/DCS_Risk_DB_2025_clean.parquet \
    --output-metrics artifacts/compact_vs_full.json
```

**Expected output**: a four-row table showing `full / medium / compact / tiny` with MAE, R², Brier, ONNX size. The **compact** row should show ≈ 47 KB with MAE ≈ 0.028.

---

## 4. Export the zero-inflated surrogate to ONNX

### 4.1 Full (1.8 MB) variant

```bash
python scripts/07_export_zero_inflated_onnx.py \
    --input-model artifacts/tinydcs_adrac_zi.joblib \
    --output-dir artifacts/zi_onnx \
    --benchmark-n 10000 --tolerance 1e-4
```

**Expected tail**:

```
Combined:   1786.8 KB, per-row p50 = 16.52 us
```

### 4.2 Compact (95 KB) variant

Train a compact zero-inflated surrogate first (inline one-liner; see `scripts/06_train_compact_surrogate.py` for the full pattern):

```bash
python -c "
import sys; sys.path.insert(0, '.')
import pandas as pd, numpy as np
from dataclasses import asdict
from tinydcs.features import FEATURE_COLUMNS, extract_features
from tinydcs.simulator import ExposureProfile, ornstein_uhlenbeck_vo2
from tinydcs.surrogate import TrainConfig, train_surrogate

VO2 = {'Rest':{'mean':0.10,'sd':0.05},'Mild':{'mean':0.45,'sd':0.10},'Heavy':{'mean':1.10,'sd':0.15}}
df = pd.read_parquet('artifacts/DCS_Risk_DB_2025_clean.parquet')
rng = np.random.default_rng(42); rows = []
for _, row in df.iterrows():
    vp = VO2.get(row['exercise_level'], VO2['Rest'])
    m = max(0.0, rng.normal(vp['mean'], vp['sd']))
    t = float(row['time_at_altitude'])
    traj = ornstein_uhlenbeck_vo2(duration_min=t, dt_min=5.0, mean_i_ex=m, rng=rng)
    p = ExposureProfile(target_altitude_ft=float(row['altitude']),
        prebreathe_duration_min=float(row['prebreathing_time']),
        prebreathe_fio2=1.0, prebreathe_fin2=0.0,
        prebreathe_i_ex_trajectory=0.0, ascent_rate_fpm=5000.0,
        altitude_duration_min=t, altitude_fio2=0.21, altitude_fin2=0.79,
        altitude_i_ex_trajectory=traj, vo2_dt_min=5.0)
    r = asdict(extract_features(p))
    r['pdcs_3rut_mbe1'] = float(row['risk_of_decompression_sickness']) / 100.0
    rows.append(r)
s, _ = train_surrogate(pd.DataFrame(rows), feature_names=FEATURE_COLUMNS,
    target_col='pdcs_3rut_mbe1', test_fraction=0.15, calibration_fraction=0.20,
    config=TrainConfig(n_estimators=100, learning_rate=0.10, num_leaves=7, random_state=42),
    use_zero_inflated=True)
s.save('artifacts/tinydcs_adrac_zi_compact.joblib')
print('Saved compact ZI surrogate.')
"
```

Then export:

```bash
python scripts/07_export_zero_inflated_onnx.py \
    --input-model artifacts/tinydcs_adrac_zi_compact.joblib \
    --output-dir artifacts/zi_onnx_compact \
    --benchmark-n 10000 --tolerance 1e-4
```

**Expected tail**:

```
Combined:   94.6 KB, per-row p50 = 2.44 us
```

---

## 5. Personalization demo (Paper 2 prototype)

```bash
python scripts/08_personalization_demo.py \
    --base-surrogate artifacts/tinydcs_adrac_zi.joblib \
    --exposure-template artifacts/DCS_Risk_DB_2025_clean.parquet \
    --output-metrics artifacts/personalization_demo.json \
    --n-subjects 100 --sigma-lambda 1.0 --seed 42
```

**Expected output**: Pearson r on log(λ) recovery grows from ~0.10 at k=1 to ~0.63 at k=20. Personalized vs population Brier score is approximately at parity at k ≈ 10–20.

---

## 6. Quick parity check (optional but recommended before any PR)

```bash
pytest tests/ -q
python -c "
from tinydcs.surrogate import TinyDcsSurrogate
s = TinyDcsSurrogate.load('artifacts/tinydcs_adrac_zi.joblib')
print(f'Loaded surrogate with {len(s.feature_names)} features, calibration: {type(s.conformal).__name__}')
"
```

---

## If the session disconnects mid-work

1. Read the last `## Session log` entry in `AGENTS.md`. It names the git range and the last substantive state.
2. Run steps 0–2 above to regenerate the core artifacts from a clean checkout. These artifacts are git-ignored and always reproducible.
3. If steps 0–2 differ from the published metrics numbers (§2 above), report the divergence before going further — something has drifted.
4. Continue from the first incomplete task listed in AGENTS.md §7 "Open problems, ranked."

The runbook is the first file new agents should open. Keep it current whenever a step changes.

---

## Known benign warnings that can be ignored

- `UserWarning: X does not have valid feature names, but LGBMRegressor was fitted with feature names` — fires in some edge cases around `predict()`; numeric outputs are correct.
- `[W:onnxruntime:...] Expected shape from model of {1} does not match actual shape of {N} for output label` — legacy LightGBM-classifier-ONNX artifact; the probability tensor has correct shape and is what we consume.
- `InconsistentVersionWarning` from any pre-1.1 joblib files — indicates the file is from the `legacy/` directory and is not load-bearing.

All other warnings deserve investigation before release.
