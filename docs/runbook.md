# Reproduction runbook — accuracy-v3

All commands run from the repository root unless noted. Tested with Python 3.12, Node 22, CPU execution. Model artifacts are ignored by git; do not load legacy joblib files as accuracy-v3 bundles.

## Setup and checks

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev,edge]'
.venv/bin/pytest -q
cd frontend
npm ci
npm test
npm run build
npm run lint
```

Return to the repository root for the following commands.

## Primary data and model

```bash
.venv/bin/python scripts/01_clean_data.py --input legacy/Model_Rel_Candidate/DCS_Risk_DB_2025.csv --output artifacts/accuracy-v3/clean.parquet --report artifacts/accuracy-v3/data_quality.md

env MPLCONFIGDIR=/tmp/dcs-matplotlib .venv/bin/python scripts/04_train_adrac_surrogate.py --training artifacts/accuracy-v3/clean.parquet --output-surrogate artifacts/accuracy-v3/surrogate.joblib --output-baseline artifacts/accuracy-v3/adrac.joblib --output-metrics artifacts/accuracy-v3/metrics.json --output-figures artifacts/accuracy-v3/figures --zi
```

Default primary cleaning excludes unresolved scaling/duplicate disagreements. It also writes the raw-row ledger and raw/rescaled sensitivity datasets. Expect 14,683 primary cells; 9,544/2,937/2,202 train/calibration/test cells. The training command records frozen cell IDs, dataset SHA, configuration and model ID. Use its default altitude holdouts for the robustness evidence; do not suppress them in a full reproduction.

Expected primary MAE is approximately 0.021932 probability units and coverage 2095/2202. A release check requires MAE ≤0.03 and empirical coverage ≥0.94 at nominal 0.95. This is model-grid emulation only.

## Comparisons and export

```bash
.venv/bin/python scripts/06_train_compact_surrogate.py --help
.venv/bin/python scripts/10_fair_baseline_and_ablation.py --help
.venv/bin/python scripts/11_grouped_cleaning_validation.py --help
.venv/bin/python scripts/07_export_zero_inflated_onnx.py --input-model artifacts/accuracy-v3/surrogate.joblib --output-dir artifacts/accuracy-v3/onnx --benchmark-n 10000 --tolerance 1e-4
.venv/bin/python scripts/12_export_frontend_evidence.py --help
.venv/bin/python scripts/13_build_evidence_manifest.py --help
```

The [evidence manifest](evidence/accuracy-v3.json) records exact commands and environment for compact/fair/profile-grouped/cleaning-sensitivity reproduction. It also inventories source and artifact hashes. Do not choose a different architecture based on its test-set result.

Use script 07 for the primary zero-inflated model: both classifier and continuous graphs plus probability-mixture/conformal/OOD sidecar are required. Generic script 05 accepts supported non-ZI bundles and explicitly rejects unsupported interval export. ONNX parity checks final probabilities, bounds and support on feasible recomputed profiles. CPU batch/per-row timings are not wearable or hardware-in-the-loop benchmarks.

## Browser contract and API

```bash
.venv/bin/python scripts/12_export_eva_browser_contract.py
.venv/bin/uvicorn tinydcs.api:app --host 127.0.0.1 --port 8180
```

The generator exports Pydantic's scenario schema, all merged mission rules, and synthetic Python golden cases. Run browser tests again after any equation/schema/rule change. Its fixtures are software-parity checks, not observed clinical data.

The browser compares the server's full mission-rule snapshot and model version with its bundle, including report exports. A mismatch is an explicit error, not an offline fallback. Regenerate the bundle after customizing server rules.

With the frontend running on 127.0.0.1:5173, check all EVA presets, PB exercise, schedule edits, rule profiles, unavailable quantities, stop conditions, synthetic replay, online/offline JSON and API PDF/HTML export. Test rapid input changes while a delayed response is outstanding. API validation errors must not show an older result or offline success.

Desktop and mobile screenshots belong outside the repository. Record console issues, route identity and export input provenance before claiming UI success.

## Notes

Numerical support checks are not evidence of clinical applicability. Outside-support surrogate results and unresolved 3RUT computations must not be used quantitatively. The zero-inflated model's intervals are calibrated on the final mixture point; personalization instead returns posterior credible intervals.

The primary grid's uncertain raw cells remain unresolved; sensitivity rescaling is a hypothesis, not a verified correction. Legacy metrics, old README snapshots and manuscripts do not supersede accuracy-v3 evidence.
