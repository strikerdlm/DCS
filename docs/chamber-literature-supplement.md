# Altitude chamber literature supplement, release 1.3

This search used Tavily, Firecrawl, Undermind and the OpenAlex CLI. OpenAlex returned 2,304 indexed matches for `altitude decompression sickness` and 205 for `hypobaric chamber training decompression sickness incidence`. The first 30 results from each search were available for screening. Undermind supplied two semantic searches for experimental and training datasets. The counts below come from primary reports, tables and abstracts. [Source registry](../data/chamber/v1.3/sources.csv) · [Extracted observations](../data/chamber/v1.3/observations.csv) · [Published case timelines](../data/chamber/v1.3/cases.csv) · [Overlap register](../data/chamber/v1.3/overlap.csv)

Release 1.3 adds 89 aggregate rows from eight publications, including 16 exact numerator–denominator pairs, one count-only observation and 72 reported percentages. It also adds six case timelines and four acquisition or methods leads. Some rows are strata, endpoints or checkpoints from the same exposures. Each source keeps its own denominator, reported precision and outcome definition.

| Source | Data extracted and scope |
| --- | --- |
| FAA training, Valdez | **Three suspected DCS reactions among 12,759 trainees** in the 1965–1989 report. Table 2 separates the three trainees from inside observers. The report gives 10 suspected reactions overall and a student-only denominator, so the overall count has a blank denominator. Records for 1972 and 1985 were unavailable. The series overlaps the earlier FAA report. [Tables 1 and 2, pp. 4–5](https://www.govinfo.gov/content/pkg/GOVPUB-TD4_200-PURL-LPS83855/pdf/GOVPUB-TD4_200-PURL-LPS83855.pdf) |
| NASA, Conkin et al. | **15 Type I cases in 219 Doppler-technician exposures**, explicitly outside the 731 research exposures. The research series yielded **103 DCS diagnoses in 731 exposures**, including six historical Type II cases. The six timelines record first symptom report, VGE timing where available and the presenting features. Historical Type II includes skin mottling, so it differs from the Colombian neurological endpoint. [NASA report, Purpose and case descriptions](https://ntrs.nasa.gov/citations/20030063917) |
| NASA, Waligora et al. | Four DCS symptom reports and 18 VGE detections in 38 exposures after 6 h of oxygen prebreathe. After 8 h, the authors observed zero DCS symptoms and zero VGE in eight exposures. Both protocols used six hours of exertion at 4.3 psia. Participant linkage to the historical NASA archives remains unresolved. [NASA abstract](https://ntrs.nasa.gov/citations/19880025744) |
| USAF, Webb and Pilmanis | DCS, any VGE and Grade IV VGE at 4 and 8 h for four altitudes between 22,500 and 30,000 ft. The 27,500-ft group has an explicit 27/33 DCS count by 8 h, with 22/33 having both DCS and VGE. Other tabulated percentages retain their published values. The two time points measure the same exposure sessions. [Results and Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/76/1/article-p34.pdf) |
| USAF, Webb et al. | Three preoxygenation conditions at 30,000 ft with sex-specific and combined results, plus a separate 29,500-ft staged-decompression study with ten original groups. In the staged study, the pre-target period yielded 1 DCS event and 12 any-VGE events across 173 exposures. The two papers have likely corresponding groups in NEDU PE2 and DNT. Their group sizes differ, so the original source values are retained. [Exercise Table II](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/73/12/article-p1161.pdf) · [Staged decompression Table II and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/71/7/article-p692.pdf) |
| Sweden, Gottschalk et al. | VGE in **10/13** sessions after eccentric arm exercise and **9/13** control sessions. Early termination occurred in **2/13** and **1/13** sessions, respectively. The stopping rule combined DCS-related symptoms and high bubble scores, so those counts use a composite endpoint. [Results and Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC10460726/) |
| France, Operation Everest III | The abstract reports DCS symptoms in **15.6% of 32 investigator-flights overall** and **50% of eight flights above 8,000 m**. The high-altitude subset overlaps the overall series. The exact numerators remain blank because the primary abstract reports percentages. [Primary abstract](https://pubmed.ncbi.nlm.nih.gov/11796447/) |

The NASA case timelines cover the six cases classified as Type II in the report. First symptom report can precede the finding that led to the Type II classification. These six diagnoses and the 32 selected symptomatic noncases lack a complete individual exposure and follow-up roster. Keep the case table for clinical timeline review, and use the aggregate tables for their documented denominators. [Format of case descriptions and narratives](https://ntrs.nasa.gov/api/citations/20030063917/downloads/20030063917.pdf)

## Rebuild and query

```sh
python -m scripts.build_chamber_database --literature-supplement
```

This writes `artifacts/chamber-v1.3/observed.sqlite` with all prior supplements. The outcome and case tables sit outside the frozen development and external-evaluation views. The manifest pins the exact CSV and schema bytes. Where a local PDF was retrieved, its digest is recorded in the source registry. [Release manifest](../data/chamber/v1.3/manifest.json)

```sql
SELECT source_id, stratum, endpoint, denominator, denominator_unit,
       cases, reported_percent, analysis_role
FROM literature_observation
WHERE endpoint IN ('dcs', 'suspected_dcs', 'dcs_type_i', 'dcs_type_ii_historical')
ORDER BY source_id, stratum, endpoint;
```

The 1992 NASA computerized hypobaric databank describes 378 grouped records compiled from 80 publications. Its catalogue entry offers no download. Access to the original files and the source crosswalk would allow a broader deduplication audit. [NASA catalogue](https://ntrs.nasa.gov/citations/19920072110)
