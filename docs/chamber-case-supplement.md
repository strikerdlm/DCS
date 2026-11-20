# Hypobaric chamber case reports and training cluster

Release 1.25 adds five observation rows from three original publications. The rows describe one selected flight cluster, its two case subtype counts, and two individual case reports. The search ledger records 27 operations and 135 result screenings or retrievals, including repeat appearances of the same publication. [Sources](../data/chamber/v1.25/sources.csv) · [Observations](../data/chamber/v1.25/observations.csv) · [Cohort links](../data/chamber/v1.25/overlap.csv) · [Search operations](../data/chamber/v1.25/search_runs.csv) · [Screened results](../data/chamber/v1.25/search_hits.csv)

| Publication | Extracted observation | Denominator and overlap |
| --- | --- | --- |
| Piwinski et al., United States, 1986 | Four DCS cases in a single HALO training flight that reached 32,500 ft. The authors classified one case as Type I and three as Type II. | Nine trainees on that flight. The same institution's 63-month routine training report excludes HALO. A later literature table cites these same four cases. [Original abstract](https://pubmed.ncbi.nlm.nih.gov/3718386/) · [Routine program report](https://pubmed.ncbi.nlm.nih.gov/3790029/) |
| Gentry et al., United States, 2017 | One DCS case. First symptoms were reported three hours after chamber training. The initial assessment occurred about 48 hours after exposure. Recurrent symptoms belong to the same case. | The original report supplies no trainee denominator. The release reuses the SharePoint source identifier and links to the existing bibliography entry. [Publisher PDF, pp. 427–429](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/88/4/article-p427.pdf) |
| Qi et al., China, 2002 | The original title documents one DCS case during a hypobaric chamber altitude tolerance test. | The publisher record supplies no abstract. The PDF was unavailable through the public routes checked, so precise timing, pressure history, diagnostic details and a trainee denominator remain missing. [Publisher record, p. 13](https://cs.medjournals.cn/article/doi/full/10.3760/cma.j.issn.1007-6239.2002.01.020) |

The 4-of-9 count describes the selected flight. The two subtype rows use the four clinical cases as their denominator. All five rows are designated as selected cases, a selected cluster, or case-conditional evidence. The 919-pilot Wang study reported hypoxia symptoms and physiological outcomes, with no verified clinical DCS count in the public text screened. The historical NASA databank remains a catalogued lead, with no outcome download in its repository record. [Wang et al., publisher record](https://cs.medjournals.cn/article/doi/full/10.3760/cma.j.cn113854-20230920-00092) · [NASA catalogue](https://ntrs.nasa.gov/citations/19920072110)

The sources table records the SHA-256 digests of the PubMed XML, publisher PDF and publisher HTML used for this extraction. The release manifest records the digests of the portable input files. [Input manifest](../data/chamber/v1.25/manifest.json)

```sh
python -m scripts.build_chamber_database --chamber-case-supplement
python -m scripts.build_chamber_database --chamber-case-supplement --fac-official
```

The public build writes `artifacts/chamber-v1.25/observed.sqlite`. The build with the official Colombian aggregates writes `artifacts/chamber-fac-official/observed-v1.25.sqlite`.

Both SQLite builds passed integrity, foreign-key and source-digest checks. Row-by-row comparisons against 1.24 confirmed the five additions and preserved all earlier data, including the locked evaluation rows. The public rebuild was byte-identical. The 23 benchmark tests passed.
