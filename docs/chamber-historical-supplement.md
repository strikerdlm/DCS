# Historical human hypobaric chamber studies

Release 1.8 adds 12 aggregate rows from four primary publications to the v1.7 publication tables. The search used Tavily and Firecrawl, then verified exact counts against three publisher PDFs and one NASA-hosted author abstract. The intake records 16 search or verification operations and 96 screened retrieval records. [Queries](../data/chamber/v1.8/search_runs.csv) · [Screening log](../data/chamber/v1.8/search_hits.csv) · [Source registry](../data/chamber/v1.8/sources.csv)

| Source | Extracted observation | Cohort and endpoint scope |
| --- | --- | --- |
| Maio et al. 1969 | Source-reported bends in 7/29 staged chamber flights. The three direct-decompression groups had 8/11, 5/10 and 1/10 affected flights. | The four rows total 21/60 affected exposures in 22 men. The paper also counts 28 symptom sites across the affected exposures. The staged arm had 29 flights by 18 men. [Table III and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/aeme/40/10/article-p1114.pdf) |
| Maio et al. 1970 | During measured-work simulated Apollo flights, 6/19, 4/19, 3/15 and 3/17 exposures had source-reported bends at 3.5 psia. | Some volunteers match the earlier study by subject code and anthropometric values. The current measured rowing exposures are distinct. The copy of the 1969 result in the Discussion is excluded. [Table III and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/aeme/41/10/article-p1162.pdf) |
| Beard et al. 1967 | 24/106 helium-diluent flights and 21/119 nitrogen-diluent flights had first bends during the Work EVA stage. | The figure covers a subset of the 334 man-flights across mixed profiles. Related paired analyses and earlier-stage events share this underlying experiment. [Figure 3 and Methods](https://asma.kglmeridian.com/downloadpdf/view/journals/aeme/38/4/article-p331.pdf) |
| Cooke and Robertson 1974 | In Apollo–Soyuz simulation, 6/20 and 5/21 subjects had DCS symptoms in the 30- and 60-minute oxygen arms, respectively. | The abstract supplies the denominators as people by arm. Cross-arm participant linkage and delayed follow-up remain unavailable. The archived full-text request returned an unavailable response. [NASA NTRS author abstract](https://ntrs.nasa.gov/citations/19740041935) |

The 2001 NASA report incorporates the two Maio publications at a different serious-DCS endpoint. The crosswalk records the reused flights for later analyses. Meader 1967 was verified as a selected subset of 958 operational flights by 11 affected crew members and remains outside the chamber observation tables. Skinner's Point Cook cases overlap the calendar period of the published Australian Defence Force surveillance series and remain a linkage lead. [Cohort crosswalk](../data/chamber/v1.8/overlap.csv) · [NASA compilation](https://ntrs.nasa.gov/api/citations/20010020946/downloads/20010020946.pdf)

```powershell
python -m scripts.build_chamber_database --historical-supplement
```

The command writes `artifacts/chamber-v1.8/observed.sqlite`. The v1.8 inputs append to the existing publication tables, where a matching source or observation key fails the build. The endpoint and denominator fields preserve the source-defined unit and scope. [Observation rows](../data/chamber/v1.8/observations.csv) · [Input hashes](../data/chamber/v1.8/manifest.json)
