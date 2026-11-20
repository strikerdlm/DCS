# NASA, AFRL and Russian clinical chamber series

Release 1.13 adds 15 clinical and ultrasound outcome rows from three primary reports. The source register includes earlier or later publications that use the same cohorts or address different endpoints. The searches and verification cover 106 retrieval records across 19 operations. [Observations](../data/chamber/v1.13/observations.csv) · [Source registry](../data/chamber/v1.13/sources.csv) · [Search runs](../data/chamber/v1.13/search_runs.csv) · [Search hits](../data/chamber/v1.13/search_hits.csv)

| Source | Recorded outcomes | Analysis scope |
| --- | --- | --- |
| NASA 2024 ground programme | Altitude refresher tests since 2015 had **6 Type I and 6 Type II cases in 1,650 exposures**. The exploration-atmosphere tests through 2023 reported **5 cases in 126 exposures**, including one Type II. Research and hardware development reported three Type I and one Type II case. | The refresher aggregate potentially reuses Johnson Space Center exposures from 2015–2016. The exploration aggregate likely includes separately reported Garbino campaigns. NASA gives approximately 225 hardware or research exposures, so the exact denominator field is blank. [Section 6.0, pp. 12–13](https://www.nasa.gov/wp-content/uploads/2026/01/pfo-dcs-summary-report-august-2024.pdf#page=12) |
| Balldin et al. 2002 | In the prospective supine arm at 4.3 psia, **17/39** had clinical DCS, **20/39** had any VGE and **13/39** had Spencer Grade III–IV VGE. | The paper identifies its 26-exposure ambulatory control as previously published by Webb et al. The intake adds the supine arm and links the earlier control. [Methods and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/73/8/article-p773.pdf) · [Original control](https://pubmed.ncbi.nlm.nih.gov/8830940/) |
| Skedina et al. 1997 | The Russian chamber abstract reports **7 DCS episodes and 27 VGE detections in 32 experiments**. Two DCS episodes occurred at 308 mmHg and five at 263 mmHg. | The same abstract names ten men and describes each as having two exposures. The pooled rows retain the reported 32 and carry a denominator conflict. Pressure-specific denominators are unavailable. [Original abstract, PDF p. 6](https://ntrs.nasa.gov/api/citations/19980024361/downloads/19980024361.pdf?attachment=true#page=6) |

The 2024 NASA report gives 677 legacy exposures in its introductory tally, while the three historical subgroups it lists sum to 678 before the additional 126 exploration exposures. The legacy counts remain linked to their earlier protocol data. The September 2026 executive summary provides a newer interpretation without an additional observed risk denominator. [2024 report](https://ntrs.nasa.gov/citations/20240010473) · [2026 report](https://ntrs.nasa.gov/citations/20260009389) · [Overlap register](../data/chamber/v1.13/overlap.csv)

```powershell
python -m scripts.build_chamber_database --clinical-series-supplement
```

The command writes `artifacts/chamber-v1.13/observed.sqlite`. The `--fac-official` option includes the official Colombian Air Force aggregates. [Input digests](../data/chamber/v1.13/manifest.json)
