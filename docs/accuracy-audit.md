# Scientific accuracy correction record

Implementation of the accepted September 2026 accuracy plan. Source code and
generated model-emulation evidence are the deliverables; published clinical
validation is not inferred from software agreement.

## Work ledger

- [x] Reference mathematics: NASA Eq. 6 / Table 17; ADRAC boundaries; atmosphere.
- [x] 3RUT source-equation audit and quantitative gate (full reconciliation unresolved).
- [x] Data provenance, shared partitions, metrics and conformal calibration.
- [x] Bernoulli personalization and uncertainty semantics.
- [x] EVA physiology, applicability, telemetry and reports.
- [x] Frontend contracts, offline parity and supported quantities.
- [x] Regenerated evidence and model/ONNX artifacts.
- [x] Full tests, build/lint, browser checks and final review.

## Confirmed starting defects

- NASA implementation used candidate Eq. 7 with coefficients fitted to Eq. 6.
  Table 17 NM nitrogen was 5.110921 psia instead of approximately 6.62 psia.
- EVA workload was reused as prebreathe exercise; endpoint risk was increased
  with arbitrary penalties, then interpolated into an invented risk curve.
- EVA interval widths and non-DCS hazard percentages were heuristic.
- Some baseline evaluation reused training rows; zero-inflated intervals were
  changed after calibration and used a fixed 2% upper bound on one branch.
- Personalization shrank binary targets according to observation batch size.
- Frontend fallback ignored selected mission rules, and stale API results
  could remain visible after the inputs changed.

## Evidence and defaults

- NASA: https://www.nasa.gov/wp-content/uploads/2023/03/conkin-dcs-exercise-tp-213158-2004.pdf
  Eq. 6, Eq. 14/15, Table 17; RM lambda 0.025, NM lambda 0.030. Dry ambient
  nitrogen is the source-model convention, distinct from humidified inspired O2.
- Conformal: https://papers.nips.cc/paper/2019/file/5103c3584b063c431bd1268e9b5e76fb-Paper.pdf
  Split calibration must evaluate the final predictor and requires exchangeability.
- User choices: all active models; retain dashboard design and offline use;
  suppress unsupported quantities.
- Shared random split: training 65%, calibration 20%, test 15%, seed 42.
- Surrogate targets: MAE <= 0.03 probability units, empirical coverage >= 0.94
  for nominal 0.95 intervals. A failing artifact is not released for quantitative use.
- 3RUT absolute risk remains disabled unless source reconciliation and benchmarks pass.

## Baseline checks

Frontend build and lint passed. Fourteen core Python tests passed. Full tests
could not collect in the initial environment because dependencies were missing;
the implementation uses a dedicated Python 3.12 virtual environment.

## Corrections and regression evidence

- NASA reference regressions cover source Eq. 6, RM/NM coefficient selection,
  Table 17 and sequential segments. Shared layered standard-atmosphere pressure
  is continuous at 11 km. ADRAC returns exactly zero at zero exposure time.
- 3RUT recruitment gain and perfusion units, initial recruitment and alveolar
  CO2 were corrected. Adaptive rollback prevents invalid numerical states from
  being clipped into plausible output. Absolute risk remains disabled because
  the gain/volume convention and complete source-profile benchmarks are unresolved.
- Primary cleaning retains 14,683 of 16,295 raw rows, preserving a raw ledger and
  separate raw/rescaled sensitivity policies. The frozen train/cal/test split
  is 9,544/2,937/2,202 cells; no baseline is fitted on evaluation rows.
- The final zero-inflated mixture is calibrated directly in probability units.
  Finite-sample conformal ranks, target-transform inversion, ordered CQR bounds,
  standardized support checking and unavailable metric handling have regressions.
  Quantitative release requires both passing evidence and accepted input support;
  unreleased raw predictions are retained only for diagnostic model evaluation.
- Personalization now accumulates binary outcomes under a Bernoulli likelihood;
  batch-order invariance and posterior quadrature are tested. Its intervals are
  posterior credible intervals, not conformal intervals.
- EVA validates finite inputs and exact segment coverage, separating PB exercise
  from EVA workload. Accepted floating-point roundoff is normalized at the final
  segment. Inspired O2 checks all pressure stages. Endpoint probabilities are
  unavailable except under explicitly declared NASA reference conditions; all
  invented EVA bands, risk curves and non-DCS event percentages were removed.
- Rule thresholds and stop flags are separate from applicability. Telemetry is
  unit/freshness checked and does not invent VO2 or cooling from sensor proxies.
  Counterfactual alternatives use a common observed state without reapplying a
  pressure snapshot to overwrite future hypotheses. Shortening cannot lengthen
  a short or zero-duration EVA.
- Generated schema/rules and 13 synthetic golden cases check Python/browser
  parity. Responses are keyed to current inputs; HTTP/schema/rule mismatches do
  not silently fall back. Reports recompute and validate the same model and rule
  context, retaining inputs, telemetry, replay clock and source provenance.
- Browser ADRAC is labelled a training-only closed-form baseline, not deployed
  ML. Its 2,202 held-out pairs are exported together with real residuals. Grid
  support uses PB 0–60 min. Unsupported plots and empty validation subsets are
  unavailable, not zero or a favorable category.

## Rebuilt evidence

The [versioned evidence manifest](evidence/accuracy-v3.json) and
[runbook](runbook.md) record exact commands, environment and hashes.

- Primary surrogate MAE 0.021932 probability units; nominal 95% interval coverage
  2095/2202 (95.14%). Profile-grouped holdout MAE 0.026344, coverage 97.21%.
- Global ADRAC baseline MAE 0.084972; calibration-selected altitude-stratified
  baseline MAE 0.033773. Ordinal exercise outperforms synthetic continuous VO2:
  independently measured continuous-workload predictive value is unestablished.
- Cleaning sensitivity, altitude holdouts and all compact variants remain
  separate from the prespecified primary model. No post-test model replacement.
- Two ONNX graphs total 1780.1 KiB. Final point/bound parity maximum error is
  3.22e-7 on 10,000 feasible profiles, with matching support gating. Benchmarks
  are desktop CPU inference, not wearable or hardware-in-the-loop evidence.
- A constant-workload duration sweep found zero decreases in 25,875 adjacent
  comparisons over 1,125 profiles. This finite audit is not a mathematical proof
  for arbitrary changing workload schedules.

None of these checks is clinical validation, individual risk accuracy,
certification or operational clearance. Raw-grid scale ambiguities, external
outcome validation, full 3RUT reconciliation and hardware evaluation remain open.

## Final software verification

Verified on Python 3.12 / Node 22 with the current accuracy-v3 working tree:

- `pytest -q`: 109 passed; two third-party test-client deprecation warnings.
- `npm test`: 97 passed, including Python/browser golden parity and unsupported
  output, segment-boundary, rule-context and stale-response regressions.
- `npm run build` and `npm run lint`: passed. Vite reports a large chart/data
  bundle warning; bundle optimization is not evidence of model accuracy.
- `npm audit --audit-level=low`: zero reported vulnerabilities at verification.
- Ruff Pyflakes checks passed across scientific modules/scripts/tests except
  excluded unchanged `scripts/02_simulate_training.py` (existing unused import).
  The broader inherited style rules still report legacy formatting/type-style
  findings; they were not represented as a passing full Python style check.
- Manifest validation: 52 artifact links/hashes checked; frozen IDs, release
  criteria, final ONNX parity and frontend residual arithmetic verified.
- Chrome/Playwright: correct title/route, meaningful content, no framework
  overlay, no application runtime errors in clean sessions. Desktop 1440×1000
  and mobile 390×844 checked; mobile page width is 390 px after fixing implicit
  chart-grid overflow, header wrapping and axis-label placement. Switches,
  sliders and EVA selectors expose accessible names.
  Range filters render both bounds and display the full selected interval;
  selecting an empty altitude subset yields unavailable statistics and plots.
- Exercised all EVA presets, mission rules, independent PB exercise, explicit
  pressure stages, synthetic telemetry and symptom-stop behavior. JSON/HTML/PDF
  downloads retain the tested inputs; offline JSON records the browser engine
  and identical rule/telemetry context. Intentional network failures and HTTP422
  were tested separately; expected failed-request console entries were explained.
- A delayed scenario-A response followed by B then C never replaced the current
  C result, during synchronization or after the old response completed. ADRAC,
  NASA, 3RUT profile generation and empty validation-subset states were exercised.
- Independent code review's short-EVA, telemetry counterfactual, roundoff and
  server/browser rule/export-context findings were corrected and re-reviewed.

Browser plugin was unavailable; existing Playwright/Chrome tooling was used.
Screenshots and temporary browser scripts are outside the repository. Other
browsers, device hardware and clinical outcomes were not tested.
