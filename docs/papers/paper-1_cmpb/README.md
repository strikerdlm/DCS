# CMPB Submission Package — TinyDCS

Submission-preparation artefacts for *TinyDCS* targeted at **Computer Methods and Programs in Biomedicine** (Elsevier, ISSN 0169-2607). The journal-specific edited manuscript lives in this folder; the canonical pre-CMPB draft remains at `docs/papers/paper-1-draft.md` (untouched).

Generated 2026-05-01 by the `/cmpb-submit` skill.

## Files

| File | Purpose |
|---|---|
| [`paper-1-draft_cmpb.md`](paper-1-draft_cmpb.md) | **The CMPB-edited manuscript.** All applied edits: frontmatter (article-type, journal-line, wordcount, version), abstract merged 5→4 fields ≤ 350 words, Vancouver `[n]` citations throughout, reference list reordered to citation order with DOIs/PMIDs added, explicit "Table 1." through "Table 4." caption labels, CRediT + AI disclosure + COI + Funding + Data Availability blocks before Acknowledgements (filled), Figure Captions appendix after References, UK English unified. Body: 2,952 words (under 3,500 cap). |
| [`paper-1-draft_cmpb.pdf`](paper-1-draft_cmpb.pdf) | **Review-version PDF (16 pages).** Built with the CMPB-specific template — continuous line numbers, 1.5× line spacing, structured abstract box with the four CMPB-required headers. |
| [`cmpb_template.latex`](cmpb_template.latex) | xelatex template for the review-version build. Adds `\usepackage{lineno}\linenumbers`, `\onehalfspacing`, and renders `abstract-background-and-objectives` as the merged CMPB abstract header. Derived from the npj-pdf-export base template. |
| [`2026-05-01_cmpb-compliance-audit_tinydcs.md`](2026-05-01_cmpb-compliance-audit_tinydcs.md) | Full PASS/FAIL/WARN audit against the CMPB Guide for Authors. |
| [`2026-05-01_cmpb-manuscript-edits_tinydcs.md`](2026-05-01_cmpb-manuscript-edits_tinydcs.md) | The edit recipe that was applied to produce `paper-1-draft_cmpb.md`. Retained as a record. |
| [`2026-05-01_cmpb-cover-letter_tinydcs.md`](2026-05-01_cmpb-cover-letter_tinydcs.md) | 10-element cover letter to Filippo Molinari, PhD, EIC. Methods-and-software framing. |
| [`2026-05-01_cmpb-highlights_tinydcs.md`](2026-05-01_cmpb-highlights_tinydcs.md) | 5 bullets, each ≤ 85 chars, character-count-verified. Separate file for portal upload. |
| [`2026-05-01_cmpb-suggested-reviewers_tinydcs.md`](2026-05-01_cmpb-suggested-reviewers_tinydcs.md) | 5 candidates with verification URLs. Two emails directly verified at faculty pages; three best-effort format-derived — verify before portal entry. |
| [`2026-05-01_cmpb-credit-and-disclosures_tinydcs.md`](2026-05-01_cmpb-credit-and-disclosures_tinydcs.md) | Reference for the CRediT, AI, COI, Funding, Data-availability blocks already pasted into the edited manuscript. |

## Build the review PDF

```bash
/root/.claude/skills/npj-pdf-export/bin/npj-export \
  --template docs/papers/paper-1_cmpb/cmpb_template.latex \
  docs/papers/paper-1_cmpb/paper-1-draft_cmpb.md \
  docs/papers/paper-1_cmpb/paper-1-draft_cmpb.pdf
```

## Submission-day checklist (compact)

1. ✅ CMPB Guide for Authors verified against the live source on 2026-05-01 (Wayback snapshot of the OAuth-gated ScienceDirect page); audit table reflects the live rules.
2. ✅ Review PDF (`paper-1-draft_cmpb.pdf`) is already produced. Rebuild only if the markdown changes.
3. ✅ All 5 suggested-reviewer institutional emails verified on 2026-05-01 (see suggested-reviewers file §Verification record).
4. ✅ Peer-review type confirmed — **CMPB operates a single-anonymised review** (= single-blind). No double-blind option. No depersonalisation needed.
5. Tag the repo: `git tag v1.0.0-cmpb-submission`
6. Upload via https://www.editorialmanager.com/cmpb/

**Open Access decision** (post-acceptance, not now): subscription path = $0 APC; gold OA = $2,500 (down from earlier $3,180 estimate; verified 2026-05-01). Authors may apply for the Research4Life Group B discount only if gold OA is chosen.

## Provenance

- Original source: `docs/papers/paper-1-draft.md` v0.6.1 (2026-04-18, commit `1feca11`)
- Edited copy: `paper-1-draft_cmpb.md` v1.0.0 (2026-05-01, this submission)
- Body word count after edits: 2,952 (Intro → Conclusion, excluding LaTeX figure blocks)
- Abstract: 334 words across 4 CMPB-required fields (Background and Objectives / Methods / Results / Conclusions)
- Reference count: 16, all cited at least once in body, in Vancouver `[n]` style
- CMPB Guide for Authors version referenced: secondary-source verified 2026-05-01 — re-verify before submission
