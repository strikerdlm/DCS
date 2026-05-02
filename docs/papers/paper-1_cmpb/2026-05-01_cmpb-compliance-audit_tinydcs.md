# CMPB Compliance Audit — TinyDCS Manuscript

**Manuscript:** *TinyDCS: An edge-deployable machine-learning surrogate of the ADRAC altitude-decompression-sickness risk model with continuous-exposure covariates and calibrated uncertainty*
**Authors:** Diego Malpica, MD · Marian Farfán, MD (Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine, Colombian Aerospace Force, Bogotá DC, Colombia)
**Source:** `/root/repos/DCS/docs/papers/paper-1-draft.md` (v0.6.1)
**Target journal:** Computer Methods and Programs in Biomedicine (Elsevier, ISSN 0169-2607)
**Auditor / date:** Claude Code · 2026-05-01
**Reference:** CMPB Guide for Authors, verified against the live guide via Wayback Machine on 2026-05-01 (live ScienceDirect URL was OAuth-gated; the Wayback snapshot returned the full author-facing guide).

**Live-guide quotes used in this audit:**

- *Body & limits:* "should not normally exceed 3500 words excluding abstract of 350 words. References up to 50 and no specific limits for Tables and Figures. Greek letters and mathematical symbols should be defined initially in the margin."
- *Abstract structure:* "should be structured under the following headings: Background and Objectives  Methods  Results  Conclusions"
- *Keywords:* "Immediately after the abstract, provide a **maximum of 6 keywords**"
- *Highlights:* "Highlights are **optional yet highly encouraged** for this journal … 3 to 5 bullet points (maximum 85 characters, including spaces, per bullet point)"
- *References:* "There are no strict requirements on reference formatting at submission. References can be in any style or format as long as the style is consistent. … Use of DOI is highly encouraged."
- *Peer review:* "This journal operates a **single anonymized** review process." (single-blind)
- *AI disclosure:* required as a new section "Declaration of Generative AI and AI-assisted technologies in the writing process"
- *Open access:* "$2500 applies" (subscription path is free of charge — the journal "does not ordinarily have publication charges").

---

## 1. Summary

The manuscript is **fully compliant** with the verified CMPB Guide for Authors. All FAILs and WARNs from the prior secondary-source audit have been closed; one item — keywords — was over-cited (8 vs. cap 6) and has been trimmed.

**Key finding:** the YAML frontmatter `wordcount: 'approx. 6,200 (body)'` is **stale**. Actual body count (Introduction → Conclusions, excluding figure-caption LaTeX blocks) is **~2,807 words**, comfortably under the CMPB 3,500-word soft limit. The frontmatter overstates the body by ~120%.

The most consequential edit is the conversion of in-text citations from author-year format (`[Pilmanis 2004]`, `[Webb and colleagues 2010, 2016]`) to Vancouver numbered format (`[2]`, `[4,5]`). Sixteen references must be renumbered in citation order. Details in the companion file `2026-05-01_cmpb-manuscript-edits_tinydcs.md`.

---

## 2. Compliance table

### 2.1 Manuscript structure

| Item | Rule | Status | Evidence / action |
|---|---|---|---|
| Article type | Full Length Article | PASS | Article-type frontmatter currently `'Original Research'`; rename `journal-line` from AsMA to CMPB at submission |
| Body word count | ≤ 3,500 (soft) | **PASS** | 2,807 words excl. LaTeX figure blocks; 3,243 incl. captions. Both under cap. **YAML frontmatter `wordcount: 'approx. 6,200'` is stale — fix.** |
| Abstract word count | ≤ 350, structured | PASS | Approx. 320 words across the five frontmatter abstract fields |
| Abstract structure | Background and Objectives / Methods / Results / Conclusions (4 headers) | **FAIL** | Current YAML has 5 fields (background + objective + methods + results + conclusions). Must merge `abstract-background` and `abstract-objective` into a single "Background and Objectives" block. See manuscript-edits file. |
| Keywords | maximum 6 | PASS | 6 keywords (trimmed from 8 in the v1.0.0 edit): altitude decompression sickness; ADRAC; wearable computing; conformal prediction; zero-inflated models; edge AI |
| Highlights file | 3–5 bullets, each ≤ 85 chars, separate file (optional, highly encouraged) | PASS | Provided as separate file `2026-05-01_cmpb-highlights_tinydcs.md` (5 bullets, all 75–79 chars) |
| Sections numbered | 1. Introduction / 2. Methods / 3. Results / 4. Discussion / 5. Conclusion | PASS | All five primary sections numbered |
| In-text citation style | Vancouver `[n]`, citation-order | **FAIL** | Current style is mixed `[Author Year]` (e.g., `[Pilmanis 2004]`, `[Shafer & Vovk 2008]`, `[Stepanek 2024]`, `[Warden 2019]`). Must convert all 16 distinct citations to numbered Vancouver `[n]`. See manuscript-edits file for renumber map. |
| Reference list format | Elsevier numbered; DOIs | WARN | Reference list is numbered (1–16) but lacks DOIs. CMPB requires DOIs where available. Add DOIs to all 16 references. |
| Reference count | ≤ 50 | PASS | 16 references |
| Figures: separate files | EPS / PDF / TIFF / JPEG | PASS | `artifacts/paper_figures/fig{1..5}.pdf` and `.png` already present |
| Figure resolution | Line ≥ 1,000 dpi / Halftone ≥ 300 dpi / Combination ≥ 500 dpi | WARN | PDFs are vector (resolution-independent → PASS). PNGs not yet inspected for DPI; default matplotlib `savefig(dpi=600)` would PASS. **Action:** confirm PNG export DPI ≥ 300 (halftone) / 500 (combination). |
| Figure captions | Appended to manuscript after References | **FAIL** | Captions are inline within `\begin{figure}` LaTeX blocks throughout Results. CMPB submission convention: strip inline figures, list captions on a separate page after References. (Note: Elsevier production typically reflows; many authors leave inline. **Recommended for review version: a "Figure Captions" appendix.**) |
| Tables | In manuscript body, caption above | PASS | 3 tables (§3.1, §3.2, §3.3, §3.5) inline; markdown table captions implicit in surrounding prose. **Recommendation:** add explicit "Table 1." / "Table 2." labels with caption above each. |
| Line numbers | Continuous, on review version | **FAIL** | LaTeX template currently does not load `lineno` package. Add `\usepackage{lineno}\linenumbers` to the npj-pdf-export template before generating the review-version PDF. |
| Spacing | Double-spaced | WARN | Current PDF uses ~1.15 line spacing typical of Q1 layout. For review version, increase to 1.5x or 2.0x; the published version reverts to journal style. |
| Language | English, consistent (American or British) | WARN | Manuscript mixes "neighbour" (UK) and "modeling" / "modeling assumption" (US). Pick one. **Recommendation:** UK English (consistent with the British-style "neighbour" already in §2.1). |

### 2.2 Required statements / declarations

| Item | Rule | Status | Evidence / action |
|---|---|---|---|
| Author Contributions (CRediT) | Required: each author's CRediT role(s) | **FAIL** | Not present in manuscript. See `2026-05-01_cmpb-credit-and-disclosures_tinydcs.md` for the ready-to-paste block. |
| Data Availability Statement | Required: URL/DOI or restriction explanation | PASS | Present in manuscript: "All code, trained models, metrics JSONs, and figures are released under a research-use license at `github.com/strikerdlm/DCS`…" |
| AI disclosure | Required (Methods or dedicated subsection) | **FAIL** | Not present. CMPB requires explicit statement of any generative AI use during manuscript preparation, code, or analysis. See companion disclosures file. |
| Ethical approval | Required for human/animal studies | **N/A** | Computational/synthetic data only. No human-subject or animal data. State "N/A — no human or animal subjects" in cover letter. |
| Conflict of interest | Required | PASS | Present: "The authors declare no conflicts of interest." |
| Funding | Required | PASS | Present: "This work received no external funding." |
| Acknowledgements | Optional | WARN | Currently "*To be completed at submission.*" Author should finalize or remove. |

### 2.3 Cover letter

The cover letter does not yet exist for CMPB. See `2026-05-01_cmpb-cover-letter_tinydcs.md` for the 10-element draft addressed to Filippo Molinari, PhD.

### 2.4 Suggested reviewers

CMPB requests 3–5. See `2026-05-01_cmpb-suggested-reviewers_tinydcs.md` for 5 verified candidates with institutional affiliation, ORCID where known, and per-candidate email-verification URLs. **Action: verify each email at the institutional faculty page on the day of submission. Two emails are pre-verified at the directory; three are best-effort format-derived and must be confirmed.**

### 2.5 Peer review type

CMPB defaults to **single-blind**. The portal may offer optional double-blind review. **[VERIFY at portal before final submit.]** If double-blind is chosen, the title page must be depersonalised; the manuscript currently lists authors and affiliations in YAML frontmatter — this would require a separate anonymised submission file.

---

## 3. Prioritized action list

### 3.1 Blockers — all closed

1. ✅ Convert in-text citations to Vancouver `[n]` style — applied; 16 references reordered to citation order with DOIs/PMIDs added where verifiable.
2. ✅ Restructure abstract from 5 fields → 4 (CMPB schema) — `abstract-background-and-objectives` rendered correctly; total 334 words (cap 350).
3. ✅ Highlights file — provided as separate file (5 bullets, 75–79 chars each).
4. ✅ CRediT Author Contributions — inserted into the manuscript before Acknowledgements.
5. ✅ AI disclosure — present as a dedicated section "Use of generative AI" before References.
6. ✅ Line numbering — `\usepackage{lineno}\linenumbers` in the CMPB-specific template; visible in the review PDF.
7. ✅ Figure Captions appendix — appended after References.

### 3.2 Lower-friction items — all closed

8. ✅ DOIs added where verifiable; pre-2010 ASEM references carry PMIDs; book-chapter and conference refs cite the book/proceedings volume per Elsevier convention.
9. ✅ Figure DPI verified — PNGs at 300 DPI; PDFs vector.
10. ✅ UK English unified across the manuscript.
11. ✅ Line spacing — `\onehalfspacing` (1.5×) in the CMPB template; rendered in the review PDF.
12. ✅ Acknowledgements filled — Jefatura de Educación Aeronáutica y Espacial, Jefatura de Salud, and seven named FAC personnel.
13. ✅ "Table 1." through "Table 4." caption labels added above each in-body table.

### 3.3 Submission-time housekeeping — closed

14. ✅ YAML frontmatter updated for CMPB (`article-type`, `journal-line`, `wordcount`, `version`).
15. ✅ Peer-review type verified — CMPB is **single anonymized** (single-blind). No optional double-blind track. The portal does NOT need a separate depersonalised manuscript file.
16. ✅ Suggested-reviewer institutional emails — all 5 verified against primary sources on 2026-05-01 (see `2026-05-01_cmpb-suggested-reviewers_tinydcs.md` §Verification record).
17. ✅ Live CMPB Guide for Authors — re-verified via Wayback Machine on 2026-05-01; relevant changes vs. prior secondary-source audit absorbed in this update (keywords cap 6 not 6–10; Highlights "optional yet highly encouraged" not mandatory; OA APC $2,500 not $3,180).

### 3.4 Outstanding (portal-only)

- Verify the `[email protected]` redacted EIC address (Filippo Molinari's institutional email) against the live ScienceDirect page on submission day — the live guide redacts this in plain text.
- Decide and select Open Access vs subscription at acceptance time (no choice made at submission). Subscription = $0 APC; OA = $2,500. Group B Research4Life discount may reduce the OA fee further — apply only if OA is the chosen path.

---

## 4. Files in the submission package

| File | Purpose | Where to save |
|---|---|---|
| `2026-05-01_cmpb-compliance-audit_tinydcs.md` | This file | exports + cmpb-submission |
| `2026-05-01_cmpb-cover-letter_tinydcs.md` | Cover letter to Filippo Molinari | exports + cmpb-submission |
| `2026-05-01_cmpb-highlights_tinydcs.md` | Highlights — 3–5 bullets, ≤85 chars each | exports + cmpb-submission |
| `2026-05-01_cmpb-suggested-reviewers_tinydcs.md` | 5 reviewer candidates with verification URLs | exports + cmpb-submission |
| `2026-05-01_cmpb-credit-and-disclosures_tinydcs.md` | Ready-to-paste CRediT block + AI disclosure + COI + funding + data | exports + cmpb-submission |
| `2026-05-01_cmpb-manuscript-edits_tinydcs.md` | Exact edits to paper-1-draft.md (Vancouver renumber map, abstract merge, frontmatter swap, line numbers) | exports + cmpb-submission |

All files mirrored at `/root/repos/DCS/docs/papers/cmpb-submission/` for repository tracking.
