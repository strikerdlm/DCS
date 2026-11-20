# Armstrong Laboratory chamber archive and treatment follow-up

The 1994 proceedings report describes 1,163 experimental chamber exposures at Brooks AFB from 1983 through 1993. Constant pain or more severe DCS signs or symptoms ended 309 exposures. The full archive total is on overlap hold because these experiments likely recur in other Armstrong analyses. Ryles and Pilmanis report 447 cases in 1,132 exposures for a partly shared period. The individual exposures cannot be matched from the publications. [Demboski and Pilmanis, pp. 532 and 536](https://ntrs.nasa.gov/api/citations/19940029137/downloads/19940029137.pdf) · [Ryles and Pilmanis, p. 984](https://pubmed.ncbi.nlm.nih.gov/9025822/) · [Overlap register](../data/chamber/v1.43/overlap.csv)

| Original observation | Cases / denominator | Denominator basis |
| --- | ---: | --- |
| DCS during chamber exposure | 309 / 1,163 | Research exposures |
| Pain-only DCS | 265 / 309 | DCS cases |
| Pain-only symptoms resolved during descent and met study treatment criteria | 261 / 265 | Pain-only DCS cases |
| Study-reported success after ground-level oxygen | 259 / 261 | Selected treated cases |
| Recurrence after treatment | 2 / 261 | Same treated cases |
| Reported post-treatment sequelae | 0 / 261 | Same treated cases |

The proceedings abstract prints 98.5% beside 259 successes. The integer fraction is 99.23%, which agrees with the chart. AsMA abstract 91 reports 99.2%, the same integer counts and the outcome after rescue recompression for both patients with recurring symptoms. All three printed percentages are retained with their locators. The two abstracts describe the same cohort. Both lack a standardized follow-up interval, and the treatment observations concern people whose initial pain resolved during descent. [Proceedings pp. 532 and 537](https://ntrs.nasa.gov/api/citations/19940029137/downloads/19940029137.pdf#page=6) · [AsMA abstract 91, p. 454](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/65/5/article-p439-s.pdf#page=16) · [Published percentage register](../data/chamber/v1.43/reported_rates.csv)

Firecrawl and Tavily recovered the NASA report. Tavily also identified the alternate meeting abstract, which was checked in the publisher's PDF. The NASA copy is archived with its public-use declaration and checksum. The search also recovered a declassified index entry identifying the Kazakova translation by title and page count. The entry supplies bibliographic confirmation. Outcome counts for Kazakova and Poleshchuk remain unavailable. [Search and retrieval log](../data/chamber/publication-review/retrievals-2026-11-20-armstrong-archive.json) · [Full-text index](../data/chamber/publication-review/full-text/index.csv) · [Translation index](https://www.cia.gov/readingroom/document/cia-rdp91-00403r000201100005-8)

Build the paired release using the existing publication workflow. It includes the earlier Doppler and repeated-exposure supplements and their source links.

```sh
python -m scripts.chamber_products --output-dir artifacts/chamber-products/2026-11-20-v1.43-r2
```

Both SQLite files passed integrity and foreign-key checks. The paired audit found one Armstrong incidence row linked to the two reports through their shared study. The prior NASA development, AFRL, Grade IV, external and chamber-group rows matched exactly. The benchmark evaluation reproduced the prior result apart from the evidence release ID. All 48 tests in the linked database, publication review, report identity and observed benchmark suites passed.
