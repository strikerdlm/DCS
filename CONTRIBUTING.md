# Contributing & Authorship

This is a single-author research artifact maintained by **Dr. Diego Malpica
(`@strikerdlm`)**, Direction of Aerospace Medicine, Colombian Aerospace Force
(FAC). External contributions are welcome via issues and pull requests.

## Author's note on AI tooling

I use large language models (LLMs) and AI-assisted IDE tooling the same way I
use a compiler, a formatter, or a stack-overflow answer: as a tool to help me
work faster. Specifically, I have used Claude (Anthropic), Cursor, ChatGPT, and
related tools at various stages of this repository.

What that does *not* mean:

- It does not mean an AI designed the underlying scientific or engineering
  system. The choice of model family (ADRAC log-logistic, Conkin RM/NM, 3RUT-
  MBe1), the validity envelope, the calibration approach, the publication
  roadmap, the IRB / chamber validation plan — all of those are decisions I
  made and own as the author.
- It does not mean an AI is a coauthor. Coauthorship is reserved for humans
  who contribute substantively to the design, analysis, or interpretation of
  the work, per ICMJE-style criteria. Tools do not meet those criteria.

What that *does* mean:

- The repository contains code that was edited or scaffolded with AI
  assistance (refactors, frontend boilerplate, documentation polish). Where
  the substantive math is concerned (`mechanistic/adrac.py`,
  `mechanistic/conkin_nasa.py`, `tinydcs/*`), every equation is traceable to
  its primary source listed in `docs/scientific-background.md`, and the
  TypeScript ports in `frontend/src/utils/models.ts` are bit-exact to those
  Python references on a fixed test grid.

If you ever spot a place where the science *appears* to have been outsourced
to a model — e.g. an unsourced equation, a hallucinated citation, a
parameter without an upstream reference — please open an issue. That is a bug
and I want it fixed.

## How to contribute

1. Open an issue describing the change you'd like to discuss.
2. Fork, branch (`feature/<short-name>`), and submit a PR.
3. PR commits should follow the existing convention: `area: short imperative
   subject`, then a body explaining the *why*. No AI co-author trailers.
4. For code in `tinydcs/`, `mechanistic/`, or `scripts/`, please run
   `pytest tests/ -q` and report the result in the PR description.
5. Manuscript and figure work belongs in `docs/papers/` and
   `artifacts/paper_figures/` — please cross-link the relevant Methods
   section if your change affects a figure or a reported number.

## Chamber review workflow

For source placement, identity reconciliation, updates to historical cases and building the two linked databases, follow the [repository agent rules](AGENTS.md) and [database guide](docs/chamber-linked-databases.md).

Start with the [publication register](docs/chamber-publication-review.md) and
the [search log](docs/chamber-review-search.md). Keep operational chamber
outcomes, research exposures and model results distinct.

### Evidence and reproducibility

- Use Tavily, Firecrawl, OpenAlex and Undermind for supplementary discovery.
  Check Consensus and UNAL EBSCO when full text is missing. Load
  `OPENALEX_API_KEY` from `openalex-research/.env` in the `SKILLS.md` checkout
  without printing it or adding it to Git.
- Preserve the exact query, filters, returned order, source identifiers and
  retrieval outcome in a dated snapshot under `data/chamber/publication-review/`.
  Record source locators and documented report or cohort links in the register.
  Formal search and inclusion follow the review protocol and its recorded decisions.
- Verify cases, endpoints, roles, study window and denominator units against
  the original source. Preserve discrepant values and unresolved overlap. A
  missing case count is unknown. Repeated reports of the same event or cohort
  count once in each analysis.
- Update the manifest when changing frozen inputs. Build the register with
  `python -m scripts.build_chamber_database --publication-review --output PATH`
  using a fresh output path. Check the new evidence and relevant tests before
  publishing. SQLite builds are generated artifacts.

### Full-text archive

- Validate recovered PDFs and preserve their source bytes. Organize originals
  by report type. Put PDFs with verified public redistribution rights in the
  [full-text archive](data/chamber/publication-review/full-text/README.md).
  Update `index.csv` with the citation, source URL, reuse basis and locator,
  page count, size and SHA-256.
- Keep subscription copies and originals with unresolved redistribution rights
  in the Git-ignored `artifacts/chamber-publication-review/full-text-working/`
  folder. Index them there and record stable source links and access status in
  the public register. Keep credentials, private material and signed download
  URLs out of commits and pull requests.

### Sync and publication checkpoints

- Fetch `origin` before starting or resuming work. Check upstream divergence
  and worktree collisions before fast-forwarding local branches. Preserve
  existing edits and untracked files. Verify the base of an open review branch
  against GitHub before continuing it.
- During the active chamber review, publish material progress at 30-minute
  checkpoints as requested by the maintainer. Stage the task files and any
  verified redistributable PDFs, commit, push the branch, open a pull request
  and verify its head on GitHub. Stack a checkpoint on an open predecessor
  when it depends on that work. Skip empty checkpoints.

## Reporting issues

- Scientific / methodological concerns: open an issue with the `science` label
  and cite the relevant primary source.
- Frontend / dashboard bugs: open an issue with `frontend` label, include
  browser, OS, and console output.
- Reproducibility issues: please paste the exact command and the diff between
  expected and observed output.

## License

Research-use-only, MIT-adjacent for the code (see `LICENSE`). Vendored NASA /
USAFSAM / NEDU reference documents retain their original public-domain status.
