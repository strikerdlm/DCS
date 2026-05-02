# CMPB Submission Package — TinyDCS

Submission-preparation artefacts for *TinyDCS* targeted at **Computer Methods and Programs in Biomedicine** (Elsevier, ISSN 0169-2607). The journal-specific edited manuscript lives in this folder; the canonical pre-CMPB draft remains at `docs/papers/paper-1-draft.md` (untouched).

Generated 2026-05-01 by the `/cmpb-submit` skill.

## Files

| File | Purpose |
|---|---|
| [`paper-1-draft_cmpb.md`](paper-1-draft_cmpb.md) | **The CMPB-edited manuscript.** All applied edits: frontmatter (article-type, journal-line, wordcount, version), abstract merged 5→4 fields ≤ 350 words, Vancouver `[n]` citations throughout, reference list reordered to citation order with DOIs, CRediT + AI disclosure + COI + Funding + Data Availability blocks before Acknowledgements, Figure Captions appendix after References, UK English unified. Body: 2,952 words (under 3,500 cap). |
| [`2026-05-01_cmpb-compliance-audit_tinydcs.md`](2026-05-01_cmpb-compliance-audit_tinydcs.md) | Full PASS/FAIL/WARN audit against the CMPB Guide for Authors. |
| [`2026-05-01_cmpb-manuscript-edits_tinydcs.md`](2026-05-01_cmpb-manuscript-edits_tinydcs.md) | The edit recipe that was applied to produce `paper-1-draft_cmpb.md`. Retained as a record. |
| [`2026-05-01_cmpb-cover-letter_tinydcs.md`](2026-05-01_cmpb-cover-letter_tinydcs.md) | 10-element cover letter to Filippo Molinari, PhD, EIC. Methods-and-software framing. |
| [`2026-05-01_cmpb-highlights_tinydcs.md`](2026-05-01_cmpb-highlights_tinydcs.md) | 5 bullets, each ≤ 85 chars, character-count-verified. Separate file for portal upload. |
| [`2026-05-01_cmpb-suggested-reviewers_tinydcs.md`](2026-05-01_cmpb-suggested-reviewers_tinydcs.md) | 5 candidates with verification URLs. Two emails directly verified at faculty pages; three best-effort format-derived — verify before portal entry. |
| [`2026-05-01_cmpb-credit-and-disclosures_tinydcs.md`](2026-05-01_cmpb-credit-and-disclosures_tinydcs.md) | Reference for the CRediT, AI, COI, Funding, Data-availability blocks already pasted into the edited manuscript. |

## Submission-day checklist (compact)

1. Re-verify the live CMPB Guide for Authors at https://www.elsevier.com/journals/computer-methods-and-programs-in-biomedicine/0169-2607/guide-for-authors
2. Re-render the manuscript PDF with line numbers and 1.5–2.0× spacing — the LaTeX template at `npj-pdf-export` needs `\usepackage{lineno}\linenumbers` and `\onehalfspacing` added for the review version
3. Verify each suggested-reviewer email at the institutional faculty page on the day of submission
4. Confirm peer-review type (single-blind default vs. optional double-blind) at the Editorial Manager portal
5. Tag the repo: `git tag v1.0.0-cmpb-submission`
6. Upload via https://www.editorialmanager.com/cmpb/

## Provenance

- Original source: `docs/papers/paper-1-draft.md` v0.6.1 (2026-04-18, commit `1feca11`)
- Edited copy: `paper-1-draft_cmpb.md` v1.0.0 (2026-05-01, this submission)
- Body word count after edits: 2,952 (Intro → Conclusion, excluding LaTeX figure blocks)
- Abstract: 334 words across 4 CMPB-required fields (Background and Objectives / Methods / Results / Conclusions)
- Reference count: 16, all cited at least once in body, in Vancouver `[n]` style
- CMPB Guide for Authors version referenced: secondary-source verified 2026-05-01 — re-verify before submission
