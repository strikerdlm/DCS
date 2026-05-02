# CRediT, AI Disclosure, COI, Funding, Data Availability — TinyDCS

> **Purpose.** This file is a *ready-to-paste* block for the manuscript and the Editorial Manager declaration fields. CMPB requires each item explicitly. Insert the manuscript-bound text immediately before the existing **Acknowledgements** section in `docs/papers/paper-1-draft.md`.

---

## 1. CRediT Author Contributions

CRediT taxonomy (https://credit.niso.org) defines 14 contributor roles. The author should confirm or amend the role assignments below before submission.

> **Diego Malpica:** Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing — original draft, Writing — review and editing, Visualization, Supervision, Project administration.
>
> **Marian Farfán:** Conceptualization, Methodology, Investigation, Writing — review and editing, Resources.

**Manuscript-paste form** (place under a new heading `## Author contributions` before `## Acknowledgements`):

```markdown
## Author contributions (CRediT)

**Diego Malpica:** Conceptualization, Methodology, Software, Validation, Formal
analysis, Investigation, Data curation, Writing — original draft, Writing —
review and editing, Visualization, Supervision, Project administration.

**Marian Farfán:** Conceptualization, Methodology, Investigation, Writing —
review and editing, Resources.

All authors read and approved the final version of the manuscript.
```

---

## 2. AI Disclosure

CMPB and Elsevier require explicit disclosure of any generative-AI tool used in manuscript preparation, code, or analysis. AI cannot be listed as an author. Reviewers and editors are instructed not to use AI tools.

**Manuscript-paste form** (recommended location: end of `§2.5 Edge deployment` as a new subsection `### 2.6 Use of generative AI`, OR within the existing data-availability section):

```markdown
## Use of generative AI

During the preparation of this work, the authors used Claude Code (Anthropic
Claude Opus 4.7) as a coding and prose-revision assistant under direct human
supervision. AI tools were used to (i) accelerate boilerplate code (e.g.,
ONNX export wrappers, plotting scripts), (ii) suggest manuscript phrasing on
non-scientific passages, and (iii) cross-check formatting against journal
guidelines. AI tools were not used to generate scientific content, design
experiments, fabricate or alter data, draft results or interpretation, or
produce figures, tables, or citations without manual verification. All
scientific claims and numerical results were derived from the released code
base and verified by the authors. After using these tools, the authors
reviewed and edited the content as needed and take full responsibility for
the content of the publication.
```

---

## 3. Conflicts of Interest

**Manuscript-paste form** (already present as `## Conflicts of interest and funding`; CMPB prefers separation):

```markdown
## Declaration of competing interests

The authors declare that they have no known competing financial interests or
personal relationships that could have appeared to influence the work
reported in this paper.
```

---

## 4. Funding

**Manuscript-paste form:**

```markdown
## Funding

This work received no external funding. The work was conducted as part of the
authors' duties at the Colombian Aerospace Force, Direction of Aerospace
Medicine.
```

---

## 5. Data and Code Availability

CMPB requires a Data Availability Statement with explicit URL/DOI or restriction explanation. The current manuscript text is acceptable but can be tightened to use the Elsevier-preferred wording.

**Manuscript-paste form:**

```markdown
## Data and code availability

All code, the cleaned ADRAC-derived dataset, trained model bundles (joblib),
ONNX artifacts at four size tiers, metrics JSONs, paper figures, the
TRIPOD+AI checklist, and a command-by-command reproduction guide are
released under a research-use license at https://github.com/strikerdlm/DCS
(default branch `main`, tagged release at the time of submission). All
training runs are reproducible from the shipped raw CSV with `seed = 42` in
under three minutes on CPU via `docs/runbook.md`. No restricted data are
involved.
```

---

## 6. Editorial Manager declaration fields — pre-filled values

When the EM portal prompts for these declarations (CMPB Step 8), enter the corresponding values verbatim:

| Portal field | Value |
|---|---|
| CRediT contributions | (see §1 above; enter per author) |
| Data Availability Statement | "All data and code are publicly available at https://github.com/strikerdlm/DCS under a research-use license." |
| Funding sources | "No external funding. Conducted as part of the authors' duties at the Colombian Aerospace Force." |
| Conflict of interest statement | "The authors declare no competing financial interests or personal relationships that could have influenced this work." |
| Ethical approval | "Not applicable — the study uses a published computational grid (ADRAC) and synthetic VO₂ trajectories; no human or animal subjects were involved." |
| AI disclosure | (paste §2 verbatim into the AI-tools field) |

---

## 7. ORCID

Include each author's ORCID at submission:

- **Diego Malpica, MD** — ORCID: `[VERIFY at https://orcid.org/`...`]` (corresponding author)
- **Marian Farfán, MD** — ORCID: `[VERIFY at https://orcid.org/`...`]`

If neither author has an ORCID, register one before submission at https://orcid.org/register. CMPB single-blind review still requires ORCID for the corresponding author.
