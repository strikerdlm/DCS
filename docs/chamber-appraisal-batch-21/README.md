# Batch 21 chamber DCS expert appraisal

Review four descriptive incidence estimates and two crude staff–trainee comparisons from operational hypobaric chamber training. Each result traces to the source cells already selected in the review register. The two forms contain the same 32 domain checks so each expert can submit an independent appraisal.

| Reviewer resources | What they contain |
| --- | --- |
| [Reviewer 1 form](human-reviewer-1.csv) · [Reviewer 2 form](human-reviewer-2.csv) | Blank fields for each reviewer’s judgment, rationale and verified locator |
| [Draft cohort incidence](cohort-incidence.csv) · [Draft staff–trainee comparisons](staff-trainee-contrasts.csv) | Source-linked counts, denominators, outcome windows, draft estimates and intervals |
| [Accepted source selections](../../data/chamber/publication-review/analysis-selection-batch-20.json) | Original table or page references, selection scope, overlapping strata and holds |
| [Navy follow-up source audit](../../data/chamber/v1.275/adjudications.csv) | Unresolved Rice and Moore denominator, figure-window and timing discrepancies |

## Complete the assigned form

1. Open the original source using the link in each row. Verify the source cell, counting unit, case definition and follow-up before entering a judgment.
2. Fill in the reviewer ID, review date, judgment, rationale, verified source locator and verification status. Use few concerns, some concerns, substantial concerns, or insufficient information for the domain judgment. Record missing evidence explicitly.
3. Return the completed CSV privately to the study coordinator. This repository is public. The coordinator will reconcile the forms after both independent appraisals are received.

## How to read the draft tables

Incidence is expressed per 1,000 source-defined exposures. The role ratio divides staff cases per exposure by trainee cases per exposure within the same program. The draft intervals assume independence and leave uncertainty from repeat attendance, follow-up and case ascertainment unresolved. Incidence intervals use the exact binomial method. Role intervals use the conditional Poisson method. Both tables are descriptive drafts for source appraisal. [Exact binomial interval](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html) · [Conditional Poisson interval](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/poisson.test.html)

The Rice (2003) overall estimate is retained. The Type IIA role cells remain restricted to descriptive sensitivity because the printed tables disagree. Furry’s staff estimate remains on hold. Ercan’s male-only odds ratio is an overlapping sensitivity result. The eventual pooling decision depends on verified comparability of risk sets, outcome windows and repeat attendance. [Dated review protocol](../chamber-publication-review.md#analysis-and-appraisal)
