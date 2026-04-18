# legacy/

This directory preserves earlier iterations of the project for **provenance and auditability**, not for active development. Nothing in `legacy/` is imported by the current codebase; nothing here should be relied on.

## What is here, and why

| Subdirectory | Original purpose | Why it's in legacy/ |
|---|---|---|
| `BU_Model_2025/` | First-generation ML + mechanistic pipeline (early 2025) | Superseded by `tinydcs/` + `mechanistic/` split |
| `BU_3RUT/` | Earlier 3RUT experiments with calibration scripts | Superseded by `mechanistic/rut_mbe1.py`; the calibration work is folded into the reconciliation issue in `docs/methods.md` §M7 |
| `3RTU_BU_2025_02_02/` | 3RUT theory snapshot from Feb 2025 | Theory reference superseded by `docs/scientific-background.md` |
| `3RUT_MBe1/` | Development scratch directory (run_simulations.py, duplicate model) | Superseded by `scripts/02_simulate_training.py` + `mechanistic/rut_mbe1.py` |
| `DCS_Python_Project_old/` | Oldest iteration; pre-ML experimentation | Historical reference only |
| `Dive_DCS/` | Buhlmann diving-decompression library | Out of scope for altitude-DCS surrogate work |
| `ML_model/` | First-generation ML experiments | Superseded by `tinydcs.surrogate` |
| `Model_Rel_Candidate/` | Release-candidate area with the ADRAC grid CSV, legacy script, and metrics snapshot | The CSV is still used (via `scripts/01_clean_data.py`); the rest is preserved for provenance |
| `dcs_validation.py` | Ad-hoc validation script | Replaced by `tests/` suite |
| `test_rut_mbe1_model.py` | Legacy test script | Replaced by `tests/test_simulator.py` |
| `DCS.code-workspace` | VS Code workspace file | Editor-specific, not portable |

## What lives outside legacy/ but is still reference material

Primary-source scientific documents are kept out of `legacy/` because they are the citation backbone of the active methods and publication plans:

- `docs/nasa_model_references/` — Conkin 2004 exercise-prebreathe paper, NASA BiP 2024 report, NASA evidence reviews.
- `docs/scientific-background.md` — curated bibliography.

## Can I delete `legacy/`?

No — not without losing the audit trail of how the project evolved. The whole directory survives the `.gitignore` and is part of the repo by design. If disk space ever becomes an issue, the correct fix is `git filter-repo` to rewrite history, not a working-tree delete.

## How do I actually *run* a legacy script?

You usually can't, cleanly. The legacy scripts frequently assumed a different package layout, imported from the old `NASA_model/` or `DCS_Python_Project_old/BU_project/` directories, and carried dependencies on older scikit-learn versions. Treat them as archival reading. If you need the functionality, use the current code in `mechanistic/`, `tinydcs/`, or `scripts/`.
