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
