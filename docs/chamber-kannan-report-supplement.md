# Armstrong survival analysis and the journal subset

Kannan and Raychaudhuri's January 1998 technical report tabulates **518 symptomatic DCS events in 1,426 chamber exposures**. Tables 3.1, 3.3 and 3.4 each give 908 right-censored exposures. The prose on p. 9 gives 906. The model database uses the matching table totals and records the conflicting prose in the source note. [Original report, Tables 3.1 and 3.3–3.5](https://archive.org/download/DTIC_ADA338089/DTIC_ADA338089.pdf#page=18) · [Outcome record](../data/chamber/v1.47/observations.csv)

| Reported outcome breakdown | Rows | DCS from rows | Right-censored from rows | Total from rows |
| --- | ---: | ---: | ---: | ---: |
| Prebreathe duration | 7 | 518 | 908 | 1,426 |
| Activity code | 3 | 518 | 908 | 1,426 |
| Final pressure | 21 | 518 | 908 | 1,426 |
| Maximum Spencer grade | 5 | 516 | 907 | 1,423 |

These are four separate summaries of the same archive. Table 3.5's printed footer gives 518 events and 1,425 exposures, two more than the grade rows. The authors also state that one of the 1,426 exposures lacked a bubble measurement. The database preserves the five printed grade rows and the disagreement in the source note. The two unresolved events have no assigned grade. Table 3.2 summarizes prebreathe duration by planned exposure time without DCS counts. [Source tables](https://archive.org/download/DTIC_ADA338089/DTIC_ADA338089.pdf#page=20) · [Extracted counts](../data/chamber/v1.47/outcome_margins.csv)

Table 3.3 gives 47/129 DCS events with no exercise and 467/1,292 with mild exercise. The accompanying prose describes about 63.5% as the DCS percentage, closer to the censored fractions of 63.6% and 63.9%. The database uses the labeled count columns. [Exercise table and narrative](https://archive.org/download/DTIC_ADA338089/DTIC_ADA338089.pdf#page=19)

## One archive, two publications

The 1998 journal article analyzes the 975-exposure subset at final pressures of 314 mmHg or less. Table 3.4 yields 506 events and 469 censored observations for the subset, matching the journal article. Section 4.2 of the technical report instead describes a 48% DCS rate, close to the 48.1% censored fraction and different from the 51.9% event fraction. The 451 higher-pressure exposures account for the remaining 12 events. Both publications are linked to one study in the literature review. The technical report's aggregate is held for overlap in the model database. [Technical report, §4.2](https://archive.org/download/DTIC_ADA338089/DTIC_ADA338089.pdf#page=23) · [Journal article](https://pubmed.ncbi.nlm.nih.gov/9773897/) · [Overlap register](../data/chamber/v1.47/overlap.csv)

The report provides historical model-development evidence and no role-specific counts for chamber trainees and observers. Its analysis assigns two delayed symptom reports to the planned time at altitude and a pre-plateau symptom report to minute 1. Participant linkage, individual symptom times and consistent postexposure follow-up are unavailable for the archive. Maximum bubble grade was observed during the exposure, after baseline. [Technical report, §3](https://archive.org/download/DTIC_ADA338089/DTIC_ADA338089.pdf#page=16)

Tavily located the indexed report and Firecrawl located the public archive copy. LlamaParse extracted the scan, and the tabulated counts were checked against the original page images. The UNAL sign-in stayed on the proxy page, so the institutional queries and PDF retrieval did not run. The same search pass traced the 1999 Krause validation abstract to citation records. An original copy remains unverified. [Search and retrieval log](../data/chamber/publication-review/retrievals-2026-11-20-kannan-report.json) · [Original PDF index](../data/chamber/publication-review/full-text/index.csv)

```sh
python -m scripts.chamber_products --output-dir artifacts/chamber-products/2026-11-20-v1.47
```

Both databases passed SQLite integrity and foreign-key checks. The 52 linked-database, publication-review, identity and benchmark tests passed. The benchmark reproduced the v1.46 results, and the 26 role-specific groups and 105 catalogued cases were identical across releases.
