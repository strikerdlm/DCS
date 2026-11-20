# Simulated spaceflight and air interruptions, release 1.16

Release 1.16 adds 36 outcome rows and two source revisions. The intake records 45 retrieval results across nine operations. [Sources](../data/chamber/v1.16/sources.csv) · [Observations](../data/chamber/v1.16/observations.csv) · [Revisions](../data/chamber/v1.16/observation_revisions.csv) · [Overlap](../data/chamber/v1.16/overlap.csv) · [Search runs](../data/chamber/v1.16/search_runs.csv) · [Search hits](../data/chamber/v1.16/search_hits.csv)

| Study | Observation and scope |
| --- | --- |
| Cooke and Robertson (1974), 3.7 psia suit challenge | After 30 minutes of oxygen prebreathe, **6/22** had bends, including four Grade I and two Grade II cases as defined by the authors. Methods, Results and the exposed rows in Table II agree on 22. The abstracts print 20. The new build updates the existing v1.8 outcome through a revision that retains both denominators. After 60 minutes, **5/21** had Grade I bends. Nineteen of the 24 men completed both profiles. [Journal Table II](https://asma.kglmeridian.com/downloadpdf/view/journals/aeme/45/3/article-p297.pdf#page=2) · [NASA abstract](https://ntrs.nasa.gov/citations/19740041935) |
| Cooke, Bollinger and Richardson (1975), repeated docking transfer | **0/11** evaluable 24-hour sessions in **seven** men who completed simulated transfers between the two spacecraft atmospheres. The 33 transfers are stages within the sessions. The authors excluded one additional person who left early with sinus pain. [Journal Methods and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/46/7/article-p930.pdf#page=2) |
| Cooke (1976), interrupted prebreathe | **0/17** bends cases in the uninterrupted control and **7/71** across six 5- or 10-minute interruption schedules. Four volunteers had all seven Grade I cases. Table IV preserves the six schedule denominators separately. The 1975 technical-report abstract is linked to the same likely cohort. [Journal Tables II–IV](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/47/11/article-p1205.pdf#page=2) |
| Degner et al. (1965), multistage orbital profiles | Flight 1a had **13/22** tabulated people with bends. Counts of people with any positive pain grade and cases first appearing by stage were read from Table III. For flights 2a, 2b and 2c, the printed denominators of 31, 24 and 30 disagree with the counts implied by displayed participation and the footnote. Those rows retain the printed values under denominator conflict. [Journal Table III and footnote](https://asma.kglmeridian.com/downloadpdf/view/journals/aeme/36/5/article-p418.pdf#page=3) |

The 1963 journal article and 1965 NASA appendix describe the same 136 ACEL ascents in 17 people. The 1991 AGARD chapter attributes its incidence table to an earlier Armstrong Laboratory database. Both records were linked without a second intake of the underlying outcomes. Firecrawl identified the Cooke interruption PDF and the original table was verified from the downloaded publisher file. [ACEL journal article](https://asma.kglmeridian.com/downloadpdf/view/journals/aeme/34/11/article-p1037.pdf) · [AGARD proceedings](https://archive.org/download/DTIC_ADA244158/DTIC_ADA244158.pdf)

```powershell
python -m scripts.build_chamber_database --spaceflight-supplement
```

The builder writes `artifacts/chamber-v1.16/observed.sqlite`. Add `--fac-official` for the combined release. The separate revision table links the changed denominator to the full-text evidence. [Input digests](../data/chamber/v1.16/manifest.json)
