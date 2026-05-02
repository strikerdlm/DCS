# Manuscript Edits — paper-1-draft.md → CMPB Submission

> **Purpose.** Concrete, line-numbered edits the corresponding author must approve and apply to `/root/repos/DCS/docs/papers/paper-1-draft.md` before submission to *Computer Methods and Programs in Biomedicine*. No edits applied unilaterally — this file is the **action list**, not the diff.
>
> Source manuscript: `paper-1-draft.md` v0.6.1 (2026-04-18).
> Targets the same numbering as the file at `git show HEAD:docs/papers/paper-1-draft.md` on 2026-05-01.

---

## 1. Frontmatter (YAML, lines 1–35)

| Line | Current | New |
|---|---|---|
| 7 | `article-type: 'Original Research'` | `article-type: 'Full Length Article'` |
| 8 | `journal-line: '\textit{Aerospace Medicine and Human Performance} (AsMA) --- in preparation'` | `journal-line: '\textit{Computer Methods and Programs in Biomedicine} (Elsevier) --- under review'` |
| 18 | `wordcount: 'approx. 6,200 (body) --- 250 (abstract)'` | `wordcount: 'approx. 2,800 (body) --- 320 (abstract) --- 16 references'` |
| 19 | `version: '0.6.0 --- 2026-04-18'` | `version: '1.0.0 --- 2026-05-01 (CMPB submission)'` |

---

## 2. Abstract restructure (5 fields → 4 fields)

CMPB requires the structured abstract in **four** sections: *Background and Objectives / Methods / Results / Conclusions*. The current YAML has five fields. **Merge `abstract-background` and `abstract-objective` into one block.**

### Edit (replace lines 23–25 with a single field)

```yaml
abstract-background-and-objectives: 'The US Air Force Altitude DCS Risk Assessment Computer (ADRAC; Pilmanis 2004) is the operational standard for planning hypobaric exposures in aviation and extravehicular activity. Two limitations constrain modern use: ADRAC''s three-level exercise covariate cannot accommodate continuous wearable-derived VO\textsubscript{2} trajectories, and the model returns point estimates without calibrated uncertainty. Our objective was to build and benchmark a wearable-grade machine-learning surrogate of the ADRAC grid that (i) accepts continuous-VO\textsubscript{2} exposure covariates, (ii) ships calibrated 95\% prediction intervals with uniform altitude-band coverage, (iii) abstains outside the validated input envelope, and (iv) meets an edge-deployment footprint below 100 KB and a per-inference latency below 10 \textmu{}s.'
```

The `npj-pdf-export` template renders abstract fields by name. **Update the template** at `scripts/render_pdf.sh` (or wherever the abstract layout is defined) to read `background-and-objectives` instead of separate `background` and `objective` fields.

After merge, run a word count on the four resulting blocks and confirm total ≤ 350. Current counts (approximate):
- background-and-objectives (merged): ≈ 145 words
- methods: ≈ 130 words
- results: ≈ 110 words
- conclusions: ≈ 65 words
- **Total: ≈ 450** → **WARN: trim ~100 words from `methods` to get under 350.**

---

## 3. In-text citation conversion: author-year → Vancouver `[n]`

The current manuscript uses inline author-year citations (e.g. `[Pilmanis 2004]`, `[Shafer & Vovk 2008]`, `Webb and colleagues (2010, 2016)`, `[Stepanek 2024]`). CMPB requires Vancouver numbered citations in **first-appearance order** in the body.

### 3.1 Final reference list — re-ordered to citation order

The existing reference list (lines 277–292, 16 entries) is in a topical order that no longer matches first-appearance order. Renumber the reference list to the order below. Each entry then has its new Vancouver number; subsequent inline citations use that number.

| New # | Old # | Citation (short form) | Reference (use full Elsevier-numbered format with DOI) |
|---|---|---|---|
| **[1]** | 2 | Pilmanis 2004 | Pilmanis AA, Petropoulos L, Kannan N, Webb JT. *Decompression sickness risk model: development and validation by 150 prospective hypobaric exposures.* Aviat Space Environ Med 2004; 75:749–59. **DOI: [add]** |
| **[2]** | 4 | Webb 2010 | Webb JT, Krock LP, Gernhardt ML. *Oxygen consumption at altitude as a risk factor for altitude decompression sickness.* Aviat Space Environ Med 2010; 81:987–92. **DOI: [add]** |
| **[3]** | 5 | Webb 2016 | Webb JT, Morgan TR, Sarsfield SD. *Altitude decompression sickness risk and physical activity during exposure.* Aerosp Med Hum Perform 2016; 87:516–20. **DOI: [add]** |
| **[4]** | 6 | Gerth 2018 | Gerth WA, Doolette DJ, Gault KA. *A Probabilistic Model of Altitude Decompression Sickness Based on the 3RUT-MB Model.* NEDU TR 18-01, 2018 (DTIC AD1101527). |
| **[5]** | 16 | Han 2023 | Han et al. *Machine Learning Methods to Predict Incidence Risk of Altitude Decompression Sickness.* IEEE CACRE 2023. **DOI: [add]** |
| **[6]** | 3 | Conkin 2004 | Conkin J, Gernhardt ML. *A probability model of decompression sickness at 4.3 psia after exercise prebreathe.* NASA TP-2004-213158, 2004. |
| **[7]** | 14 | Ke 2017 (LightGBM) | Ke G, Meng Q, Finley T, et al. *LightGBM: A highly efficient gradient boosting decision tree.* NeurIPS 2017. |
| **[8]** | 10 | Smithson 2006 | Smithson M, Verkuilen J. *A better lemon squeezer? Maximum-likelihood regression with beta-distributed dependent variables.* Psychol Methods 2006; 11(1):54–71. **DOI: 10.1037/1082-989X.11.1.54** |
| **[9]** | 7 | Shafer & Vovk 2008 | Shafer G, Vovk V. *A tutorial on conformal prediction.* J Mach Learn Res 2008; 9:371–421. |
| **[10]** | 8 | Vovk 2022 (Mondrian) | Vovk V, Gammerman A, Shafer G. *Algorithmic Learning in a Random World.* 2nd ed., Springer, 2022 (Mondrian conformal, Chapter 4). |
| **[11]** | 9 | Romano 2019 (CQR) | Romano Y, Patterson E, Candès EJ. *Conformalized quantile regression.* NeurIPS 2019. |
| **[12]** | 1 | Kannan 1998 | Kannan N, Raychaudhuri A, Pilmanis AA. *A loglogistic model for altitude decompression sickness.* Aviat Space Environ Med 1998; 69:965–70. |
| **[13]** | 11 | Van Calster 2019 | Van Calster B, McLernon DJ, van Smeden M, et al. *Calibration: the Achilles heel of predictive analytics.* BMC Med 2019; 17:230. **DOI: 10.1186/s12916-019-1466-7** |
| **[14]** | 15 | Warden 2019 | Warden P, Situnayake D. *TinyML.* O'Reilly, 2019. |
| **[15]** | 13 | Stepanek 2024 | Stepanek J et al. *Decompression sickness risk assessment and awareness in general aviation.* Aerosp Med Hum Perform 2024. **DOI: [add]** |
| **[16]** | 12 | Collins 2024 (TRIPOD+AI) | Collins GS, Moons KGM, et al. *TRIPOD+AI statement.* BMJ 2024; 385:e078378. **DOI: 10.1136/bmj-2023-078378** |

### 3.2 In-text citation insertion / replacement (line-by-line)

| Line | Current text (excerpt) | Edit |
|---|---|---|
| 44 | `since the late 1990s [Pilmanis 2004].` | `since the late 1990s [1].` |
| 46 | `Webb and colleagues (2010, 2016) demonstrated…` | `Webb and colleagues [2,3] demonstrated…` |
| 48 | `Gerth and coauthors (NEDU TR 18-01, 2018) developed the 3RUT-MBe1…` | `Gerth and coauthors [4] developed the 3RUT-MBe1…` |
| 56 (Contrib #3) | `Mondrian (altitude-stratified) split-conformal prediction intervals…` | Add `[9,10]` after "split-conformal prediction intervals" |
| 81 (table cell) | `Conkin / Webb 1999` | **WARN: "Webb 1999" is not in the reference list.** Either (a) add the missing reference (likely Webb JT, Pilmanis AA, Krock LP, Olson RM. *Altitude DCS risk during a 1-hour prebreathe followed by exposure to 9.1 psia.* Aviat Space Environ Med 1999; 70:435–7), or (b) reduce to `Conkin [6]`. **Author decision required.** |
| 84 (table cell) | `Conkin 2004 prebreathe-exercise effect` | `Conkin 2004 [6] prebreathe-exercise effect` |
| 85 (table cell) | `Webb 2010, 2016 (1-min peak…)` | `Webb 2010, 2016 [2,3] (1-min peak…)` |
| 86 (table cell) | `Conkin single-compartment tissue N_2…` | `Conkin [6] single-compartment tissue N_2…` |
| 88 | `consistent with the published ranges for Rest / Mild / Heavy (Webb 2010).` | `consistent with the published ranges for Rest / Mild / Heavy [2].` |
| 96 | `following Smithson and Verkuilen (2006).` | `following Smithson and Verkuilen [8].` |
| 98 | `A LightGBM gradient-boosting regressor fit η…` | `A LightGBM [7] gradient-boosting regressor fit η…` |
| 100 | `[Shafer & Vovk 2008]` and `Mondrian conformal stratified…` | `[9]` and `Mondrian conformal [10] stratified…` |
| 115 | `(Kannan 1998 / Pilmanis 2004) fit the log-logistic AFT…` | `[12,1] fit the log-logistic AFT…` |
| 117 | `(Van Calster 2019 weighted logistic recalibration)` | `[13]` |
| 187 | `[Warden 2019]` | `[14]` |
| 196–198 (calibration table) | `Mondrian` / `CQR (global q)` / `Mondrian-CQR` | Add `[10]` / `[11]` / `[10,11]` to the first occurrence in the surrounding prose (e.g. line 195 introductory sentence) |
| 255 | `[Stepanek 2024]` | `[15]` |
| 296 (Appendix A) | `## Appendix A — TRIPOD+AI checklist coverage` | Cite `[16]` after "TRIPOD+AI" — e.g. `## Appendix A — TRIPOD+AI [16] checklist coverage` |

### 3.3 Sanity check after conversion

After applying §3.2, run:

```bash
grep -c -E '\[[0-9]+(,[0-9]+|–[0-9]+)*\]' docs/papers/paper-1-draft.md
```

Expected: ≥ 18 distinct `[n]` insertions in the body. Cross-check that **every reference [1]–[16] appears at least once in the body** (including Refs [10] Vovk-Mondrian, [11] Romano-CQR, [16] Collins-TRIPOD which are currently uncited):

```bash
for n in {1..16}; do
  echo "Ref [$n]: $(grep -c "\[$n[],-]" docs/papers/paper-1-draft.md) inline mentions"
done
```

---

## 4. Add CRediT, AI disclosure, COI, Funding

Insert before existing `## Acknowledgements` (line 261) and after existing `## 5. Conclusion` (line 257):

Source: `2026-05-01_cmpb-credit-and-disclosures_tinydcs.md` (this submission package). Paste the four code blocks (`Author contributions (CRediT)`, `Use of generative AI`, `Declaration of competing interests`, `Funding`) verbatim.

Existing `## Conflicts of interest and funding` heading (line 269) is then redundant — replace with `## Funding` only.

---

## 5. Append a Figure Captions page

CMPB convention: a "Figure Captions" section after References. Currently captions are inline within `\begin{figure}…\end{figure}` LaTeX blocks (lines 105–110, 138–144, 171–177, 203–209, 216–222).

Add after the existing References section (after line 292):

```markdown
## Figure captions

**Figure 1. TinyDCS system architecture.** Block diagram of the three-layer
inference stack: (1) wearable sensor input layer producing a 13-feature vector
from altitude telemetry and accelerometer-derived VO₂; (2) LightGBM logit
core with monotonicity constraints and Mahalanobis OOD gate; (3) zero-
inflated conformal calibration layer returning a point estimate plus a
calibrated 95 % interval. ONNX artifacts are shown at the edge-deployment
node.

**Figure 2. Reliability diagram — TinyDCS vs. closed-form ADRAC baseline.**
Predicted P(DCS) bins (x-axis) versus empirical observed fraction (y-axis)
on the held-out test fold (n = 2,386). Perfect calibration lies on the
diagonal. TinyDCS (zero-inflated two-stage) tracks the diagonal closely
across the full probability range; the closed-form AFT baseline shows
systematic overestimation at low probabilities.

**Figure 3. ONNX model size versus MAE — Pareto frontier across the size
ladder.** Log-scale x-axis (ONNX file size in KB) versus MAE on the held-out
test fold. Four TinyDCS variants (Tiny, Compact, Medium, Full) and the
closed-form ADRAC baseline are plotted. The Compact variant achieves the
target edge-deployment footprint while dominating the baseline by 3× on MAE.

**Figure 4. Per-altitude-band 95 % conformal coverage — five calibration
strategies.** Grouped bars showing empirical coverage in each 5,000-ft
altitude band for five calibration methods on the same test fold. Four
conformal-only methods (global, Mondrian, CQR, Mondrian-CQR) are invariant
at 0.58–0.59 in the 18,000–23,000 ft band. The zero-inflated two-stage
method achieves ≥ 0.95 coverage in all five bands.

**Figure 5. Personalisation information gain — per-subject susceptibility
recovery.** Left y-axis: Pearson r between true and posterior-mean log-
susceptibility (synthetic 200-subject cohort) as a function of observed
exposures k per subject. Right y-axis: Brier score for population-level
(flat prior) versus personalised predictions. Crossover near k = 10
indicates the exposure count at which personalisation begins to outperform
the population model.
```

**Note.** The numbering above also corrects an inconsistency: the current LaTeX captions reference `\label{fig:reliability}`, `\label{fig:size-accuracy}`, `\label{fig:coverage}`, `\label{fig:personalization}`, `\label{fig:architecture}` with cross-references like "Figure 1" used for the architecture (line 102) but "Figure 2" for the reliability diagram (line 136) — verify that the renumbering matches the document order:

- Line 102: schematized in **Figure 1** → Architecture (matches `fig5_architecture.pdf`)
- Line 136: shown in **Figure 2** → Reliability diagram (matches `fig1_reliability_diagram.pdf`)
- Line 169: shown in **Figure 3** → Size vs accuracy (matches `fig3_size_vs_accuracy.pdf`)
- Line 201: shown in **Figure 4** → Per-band coverage (matches `fig2_per_band_coverage.pdf`)
- Line 214: shown in **Figure 5** → Personalisation (matches `fig4_personalization_info_gain.pdf`)

The figure-file numbering (`fig1_*` through `fig5_*`) does not match the manuscript figure number — `fig5_architecture` is referenced as Figure 1 in the manuscript. **Action**: rename the figure files to match manuscript order before final upload, OR retain the existing names and ensure the production figure-upload step explicitly maps each file to its journal figure number.

---

## 6. Enable line numbering for review version

Add to the LaTeX preamble (in `npj-pdf-export` template):

```latex
\usepackage{lineno}
\linenumbers
```

This adds continuous line numbers throughout the manuscript body. Required for the review version; remove for the final production version.

---

## 7. Increase line spacing for review version

Current: ~1.15× (Q1 layout). Recommended for review: 1.5× or 2.0×.

In LaTeX template:

```latex
\usepackage{setspace}
\onehalfspacing   % or \doublespacing
```

---

## 8. UK-vs-US English consistency

Manuscript currently mixes:

- UK: `neighbour-median` (line 67), `neighbour-consistently` (frontmatter), `centred` (line 88), `randomly partitioned` (line 115)
- US: `unpressurized` (line 44), `synthesized` (line 88), `categorical` (line 88), `quantized` (line 123), `prioritize`, `optimize`, `recognize`, `categorized`, `personalization`, `synthesized`

**Recommendation:** convert to **UK English** (matches `neighbour-median` already in §2.1 — the more distinctive choice). Find/replace pairs:

| US → UK |
|---|
| `unpressurized` → `unpressurised` |
| `synthesized` → `synthesised` |
| `recognized` → `recognised` |
| `categorical` → `categorical` (unchanged) |
| `quantized` → `quantised` |
| `optimize` / `optimization` → `optimise` / `optimisation` |
| `personalization` → `personalisation` |
| `prioritize` → `prioritise` |
| `analyze` → `analyse` |
| `behavior` → `behaviour` |
| `modeling` → `modelling` |

After find/replace, **re-run** the spell-checker with the UK locale (`hunspell -d en_GB`).

---

## 9. Add DOIs to all references

Verify each DOI on the publisher page; add to the reference entry. Prefer the canonical Elsevier numbered format:

```
[n] Author1 A, Author2 B, et al. *Title.* Journal abbrev Year; vol(issue):pages. https://doi.org/10.xxxx/yyyy
```

DOIs needed (best-effort starting points; verify):

- [1] Pilmanis 2004 — verify in Aviat Space Environ Med archive
- [2] Webb 2010 — verify
- [3] Webb 2016 — `https://doi.org/10.3357/AMHP.4477.2016` **[VERIFY]**
- [5] Han 2023 — IEEE Xplore
- [8] Smithson 2006 — `https://doi.org/10.1037/1082-989X.11.1.54`
- [13] Van Calster 2019 — `https://doi.org/10.1186/s12916-019-1466-7`
- [16] Collins 2024 — `https://doi.org/10.1136/bmj-2023-078378`
- [4] Gerth 2018 — DTIC reference; no DOI; cite the DTIC accession number AD1101527 in the entry
- [6] Conkin 2004 — NASA TP-2004-213158; no DOI; cite NTRS document ID
- [9, 10, 11, 12, 14] — book chapters / NeurIPS / proceedings; cite as published

---

## 10. Optional: explicit "Table N." labels

Add `**Table 1.**` / `**Table 2.**` / `**Table 3.**` / `**Table 4.**` / `**Table 5.**` above each table:

| Line | Add caption |
|---|---|
| 131 (before §3.1 table) | **Table 1.** Head-to-head accuracy on the random held-out test fold (n = 2,386). |
| 151 (before §3.2 table) | **Table 2.** Leave-one-altitude-out cross-validation MAE (mean ± SD across five 5,000-ft bands). |
| 162 (before §3.3 table) | **Table 3.** TinyDCS size-ladder variants and inference latency. |
| 193 (before §3.5 table) | **Table 4.** Per-altitude-band 95 % conformal coverage across five calibration strategies. |

(Optionally: a Table 5 summarising Appendix A TRIPOD+AI checklist locations, if the appendix is retained as in-body table.)

---

## 11. Repository tag for submission

After all edits land, tag the repository with the submission version:

```bash
git -C /root/repos/DCS commit -am "v1.0.0 — CMPB submission package"
git -C /root/repos/DCS tag -a v1.0.0-cmpb-submission -m "TinyDCS CMPB submission, 2026-05-01"
git -C /root/repos/DCS push origin main --tags  # (only if user authorizes push)
```

The cover letter and Data Availability Statement reference the GitHub repository; freezing a tag aligns the public artefact with what the reviewers will see.

---

## 12. Edit checklist (compact)

```
[ ] §1 — frontmatter: article-type, journal-line, wordcount, version
[ ] §2 — abstract: merge background+objective; trim to ≤350 words
[ ] §3 — citations: convert all to Vancouver [n]; renumber refs to citation order
[ ] §4 — insert CRediT + AI disclosure + COI + Funding before Acknowledgements
[ ] §5 — append Figure Captions page after References
[ ] §6 — add \usepackage{lineno}\linenumbers to LaTeX preamble
[ ] §7 — set \onehalfspacing or \doublespacing for review version
[ ] §8 — find/replace US → UK English; re-spell-check with en_GB
[ ] §9 — add DOIs to all 16 references
[ ] §10 — add explicit Table N. caption labels (optional but recommended)
[ ] §11 — git tag v1.0.0-cmpb-submission
[ ] §12 — re-render PDF with new frontmatter and template; visually inspect line numbers
[ ] §13 — verify peer-review type (single- vs double-blind) at EM portal
```

After every box is ticked, the manuscript is ready for upload.
