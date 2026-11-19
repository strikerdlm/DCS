# Chamber outcome database v1.6

The 19 November 2026 search added 90 observation rows from 13 sources, plus two research references. The database has 18 source crosswalks and 13 documented adjudications. Rows can represent overlapping strata, alternative reports of the same outcome, or repeated exposures from the same cohort. The row count measures extraction coverage.

```powershell
python -m scripts.build_chamber_database --discovery-supplement
```

The command builds `artifacts/chamber-v1.6/observed.sqlite` from the [hash-pinned inputs](../data/chamber/v1.6/manifest.json). It includes the earlier public supplements and the SharePoint deduplication views. With `--fac-official`, it also includes the Colombian aggregate supplement in a distinct output file. The existing development partition and its locked external evaluation retain their original study membership.

## Extracted outcomes

| Source | Evidence in SQLite |
| --- | --- |
| Royal Malaysian Air Force | Four diagnosed Type I DCI cases among 395 people across 23 sessions. The abstract gives no matching denominator for its separately printed per-exposure percentage. [ICASM abstract 176](https://icasm2025.com/assets/pdf/Abstracts%20Booklet.pdf) |
| USAF 1985–1987 | 282 DCS cases in 239,343 exposures, with role, sex and nine named flight-profile strata. Role- and sex-specific denominators each fall short of the reported total. Historical archive overlap is flagged. [Workshop Tables 3 and 5](https://archive.org/download/DTIC_ADA257612/DTIC_ADA257612.pdf#page=375) |
| RAF AMTC 1983–1987 | Five reported simple DCS cases across more than 12,000 student exposures. The exact denominator is unavailable. [Harding, printed p. 468](https://archive.org/download/DTIC_ADA257612/DTIC_ADA257612.pdf#page=479) |
| RAF Henlow, reported in October 2000 | One case during the preceding year. The report gives a rate of one per 1,000 exposures and a three-month count of 497 trained aircrew. The exact annual denominator is unavailable. [McLoughlin, printed p. 12-3](https://citeseerx.ist.psu.edu/document?doi=42f5ea06ef915db7d858019fe6003fd0b1fda564&repid=rep1&type=pdf) |
| NASA Exploration Atmosphere Tests 1–2 | Two Type I and zero Type II cases in 50 evaluable volunteer EVA exposures. The chart supports the 50-exposure analysis. The raw participation bullets sum to 52. The measured chamber plots corroborate the 4.3 psia target, recorded as 29.6 kPa. Separate VGE grade fields preserve the campaign result, the conflicting earlier label and the Eftedal–Brubakk grade 7 result. Two technician cases have an unavailable exposure denominator. [NASA presentation, slides 21, 23–25 and 29–31](https://ntrs.nasa.gov/citations/20240005151) · [Companion physiological study](https://doi.org/10.3389/fphys.2025.1637834) |
| NASA Tests 3–4 | Two source-classified cases and one zero-event protocol. Arm denominators are unavailable. The 20-minute arm has a disputed pressure in the published abstract. [NASA abstract](https://ntrs.nasa.gov/citations/20240013238) |
| NASA Test 6 | Three DCS cases. The ten daily exposure cells sum to 61 and the cumulative column reaches 62. The one-exposure discrepancy begins on test day 15. Both counts are available in the database. [NASA slides 14–17](https://ntrs.nasa.gov/api/citations/20260003261/downloads/2026_05_18_AsMA_Garbino_EA_v2.pdf#page=14) |
| Webb et al. 2004 | The 60-minute exercise-enhanced prebreathe arm had 10 symptomatic participants in 40 exposures. For the 30-minute arm, the Results, Table II and Figure 1 support 43% DCS at four hours. The 40% abstract value remains documented. The historical 30-minute resting control cites the ADRAC validation study and is cross-linked to NEDU MV-B. [Table II and Figure 1](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/75/10/article-p859.pdf#page=3) · [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/15497365/) |
| Chadov et al. 2001 | One symptomatic event and nine VGE-positive exposures among 27 experiments starting at 93 kPa. Three lower starting-pressure arms have zero reported DCS and published VGE percentages. Their exact denominators are unavailable. [Primary abstract](https://pubmed.ncbi.nlm.nih.gov/11496423/) |
| Rice and Moore 2005 | 97 cases across 50,355 exposures. Of 58 source-classified Type II cases, 29 had only non-dermatomal paresthesia. The surveillance series overlaps Rice et al. 2003. [Primary abstract](https://pubmed.ncbi.nlm.nih.gov/16173680/) |
| Demir and Ata 2022 | Five Type I cases among 18 people in an outcome-selected cluster. Table II assigns three and two cases to the two nine-person flights. All five symptom reports occurred the following day. [Publisher issue, pp. 712–714](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/93/10/article-p1.pdf) |
| Connolly et al. 2023 | Five ascent counts moved from the staged CSV to SQLite. The risk sets changed after DCS events and withdrawal. The two 22,000-ft risk sets were counted from Figure 3A. [Original paper](https://kclpure.kcl.ac.uk/portal/files/233430858/DCS_2023.pdf) |
| Conkin et al. 2017 | Table II distinguishes 11/41 with any VGE from 6/41 with Spencer Grade III or IV in Nuc-3. The any-grade count is already in NASA F1. This release adds the three published combined Grade III–IV counts. [Primary paper, Table II and onset results](https://www.nasa.gov/wp-content/uploads/2023/03/conkin-dcs-vge-ambulation-2017.pdf#page=4) |

## Database fields and checks

- `discovery_source` records the source location, access level, extraction disposition and available PDF hash.
- `discovery_observation` records the outcome, numerator or reported percentage, applicable denominator and its unit, exposure descriptors, observation window, locator and analysis role. A missing denominator is SQL `NULL`. A recorded zero reflects a source statement. Cumulative exposure counts retain the values printed in the source.
- `discovery_overlap` records confirmed or unresolved relationships. The Furry report is a bibliographic lead, pending verification of its original numerator and denominator.
- `discovery_adjudication` preserves published variants, the source evidence for the preferred value, and any evidence still needed. `supported` marks a value corroborated for its stated scope. `reported_only` retains an author's summary with unresolved source details. `unresolved` leaves the chosen value empty. `distinct_scope` documents differences in the included observations or publication versions. [Adjudication register](../data/chamber/v1.6/adjudications.csv)

Tavily, Firecrawl, Consensus and Undermind informed source discovery. Reviewed measurements come from primary reports, presentations or author abstracts. The NASA Tests 1–2 deck was verified through NASA's public copy after the Firecrawl request timed out. [Source registry](../data/chamber/v1.6/sources.csv)
