# Calculation and evidence architecture

- `mechanistic/`: source-reference NASA equations, shared layered atmosphere, ADRAC-form fit and experimental gated 3RUT.
- `tinydcs/`: input validation, sequential EVA calculations, unit/freshness-checked telemetry, API/report contracts, feature extraction, surrogate/calibration/support and Bernoulli personalization.
- `scripts/`: primary cleaning/training, stronger baselines and ablations, grouped/sensitivity evidence, ONNX parity, browser contract/data export and artifact manifest.
- `frontend/src/utils/eva*.ts`: offline reference calculations with the same generated schema, rules and synthetic Python golden cases. EVA state keys include scenario, rules and telemetry context; obsolete responses cannot be selected.
- `frontend/src/data/adrac_*.json`: training-only browser baseline and the full frozen held-out validation set. The LightGBM/ONNX surrogate is not executed by this browser panel.
- `artifacts/accuracy-v3/`: generated models and detailed evidence, intentionally ignored by git. The compact versioned evidence is `docs/evidence/accuracy-v3.json`.

Version-2 EVA responses use nullable unsupported outputs. Reports recompute from supplied inputs and retain provenance; callers cannot submit arbitrary displayed risk as authoritative output. v1 routes are deprecated aliases and are not backwards-compatible numeric contracts.

No deployment, hardware bridge or clinical approval follows from successful software verification.
