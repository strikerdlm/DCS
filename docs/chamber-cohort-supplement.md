# Altitude chamber cohorts, release 1.4

This cut adds **73 aggregate observations from six primary studies**, comprising 61 exact numerator–denominator pairs and 12 reported percentages. Twenty-one observations describe timing among treated DCS cases. Three additional publications are registered as leads. The previous releases remain reproducible, including the frozen development and external evaluation views. [Source inventory](../data/chamber/v1.4/sources.csv) · [Outcome observations](../data/chamber/v1.4/observations.csv) · [Overlap register](../data/chamber/v1.4/overlap.csv)

## Search strategy

The 19 November 2026 search focused on human hypobaric chamber studies with an explicit DCS definition, a usable denominator or a clearly defined selected case population, and verifiable pressure history. Searches covered operational training, controlled oxygen and ascent-rate experiments, and flight after an earlier dive or chamber exposure. Records were screened against releases 1.0–1.3 and the previously staged intake by publication identity, role, profile, dates and institution. Occupational diving without subsequent simulated altitude and model-generated probabilities were excluded from the outcome tables.

| Service | Search and result |
| --- | --- |
| Consensus Research | Three single-page queries covered ascent rate and oxygen experiments, operational training incidence before 1993, and onset after repeated or prior-dive exposures. Human and peer-reviewed filters applied. Multi-query and simpler single-query submissions returned execution errors on the requested personal connector. The hosted Consensus connector returned ten results for original chamber studies of training incidence and early signs, including previously staged cohorts. |
| Tavily | Advanced searches for the NASA training review and primary historical citations, and for flying-after-diving exposure counts. Full-text extraction and the Duke record helped verify Vann 2004 and trace Pollock 2003. |
| Elicit | Two semantic searches covered human chamber trials and operational incidence. A keyword retry in the PubMed corpus used `"decompression sickness" AND ("altitude chamber" OR "hypobaric")`. The connector returned `INVALID_ARGUMENT` on all three calls. |
| SciSpace | Searched for exact symptomatic DCS outcomes by profile or operational cohort over 15,000–40,000 ft. Ten hits included the Conkin training review and the Pilmanis ascent-rate trial. |
| Firecrawl | Searched for original RAF and USAF historical training reports and tried the RAF and Czech report PDFs. The RAF scrape returned a redirect. The RAF chapter was inspected through the public PDF index. |

## Extracted evidence

| Primary source | Observations added | Use and scope |
| --- | --- | --- |
| NASA JSC aerospace physiological training | **4/8,694, 1/718 and 1/148** student exposures in three profiles. **1/3,612** inside-observer exposures across profiles. The six student cases in 9,560 exposures are also retained as a margin. | The earlier intake already held the four strata. Release 1.4 brings them into SQLite with profile periods, pressure, prebreathe and source notes. The paper’s case review includes during- and post-training diagnoses with a variable or unreported follow-up window. [Methods and Tables I–II](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/89/11/article-p941.pdf) |
| Duke high-altitude trial, Pollock et al. | Confirmed DCS in **1/35** and **0/24** flight-only sessions at 25,000 ft for two and three hours. After a simulated dive, three-hour arms yielded **0/23, 1/37 and 1/36** with 24-, 18- and 12-hour surface intervals. | The five arms total 3/155. Some participants completed multiple profiles. Assessments continued through 48 h. The in-flight VGE Results report 31/155, the Table II peak-grade cells sum to 32/155, and the abstract reports 19%. The 18-hour arm’s case narrative and summary disagree on onset time. [Tables I–II and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/74/11/article-p1163.pdf) |
| Duke commercial-cabin trial, Vann et al. | **40 DCS incidents in 802 completed simulated flights at 8,000 ft after diving**. The 17-hour surface-interval subset had **0/52**. | Follow-up through 24 h. The 52 sessions are included in the 802. This is a prior-hyperbaric-exposure cohort. [Primary publication record and abstract](https://scholars.duke.edu/publication/679117) |
| USAF zero-preoxygenation series, Webb et al. | No symptoms diagnosed as DCS in the five reprinted groups at or below 19,800 ft. The primary results report **5% of 20** at 21,200 ft and **55% of 20** at 22,500 ft. | The observed percentages preserve the original reporting precision. The paper’s modeled thresholds remain outside the outcome table. Historical groups and potentially overlapping USAF archive records are flagged. [Abstract, Table I and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/69/4/article-p335.pdf) |
| USAF 40,000-ft ascent-rate trial, Pilmanis et al. | Two 40-session arms with DCS symptom rates of **47.5%** and **55.0%**. The paired subset has **5/17** slow-ascent and **9/17** fast-ascent DCS symptom observations. VGE and symptom subtype counts occupy separate rows. | Seventeen participants undertook both rates. The slow arm’s profile matches NEDU 40K-A, whose printed 18/40 requires reconciliation with the paper. The groups stay outside pooled fitting. [Tables II–IV](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/74/10/article-p1052.pdf) |
| USAF post-chamber air travel, Rush and Wirjosemito | Among **292 hyperbaric-treated chamber DCS cases**, 151 had onset within two hours and 141 had later onset. Seven delayed cases were first symptomatic during or after subsequent aircraft travel. Year-specific counts are included. | The population is conditional on a treated diagnosis. The number of trainees who flew afterward is unavailable, so the data support onset description only. [Tables I–II](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/61/11/article-p1028.pdf) |

## Source decisions

- The RAF reports one recent case with a rate of one per 1,000 and five cases during 1983–1987 with a rate of 0.4 per 1,000. Both rates are rounded, and the inspected RAF chapter gives no exact denominator. The report remains a lead. [RAF symposium paper](https://citeseerx.ist.psu.edu/document?doi=42f5ea06ef915db7d858019fe6003fd0b1fda564&repid=rep1&type=pdf)
- The 1985–1987 USAF cohort is cited in the Conkin review. Its two tables differ on the Type V student denominator, 53,185 versus 53,239. The primary workshop chapter tables remain unverified. The 1965–1967 Watson report also remains a lead pending primary verification. [Conkin Tables I–II and references](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/89/11/article-p941.pdf)
- NASA training Profile II and clinical Type II DCS are separate concepts. The cohort numerator counts diagnoses of DCS. Use of the table for specific Type II outcomes requires the source’s separate diagnoses and matching denominator. [NASA Profile Review and Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/89/11/article-p941.pdf)

## Build and query

```sh
python -m scripts.build_chamber_database --cohort-supplement
```

This writes `artifacts/chamber-v1.4/observed.sqlite`. The manifest pins the database inputs. The source table records original PDF hashes for extracted studies. Use `exposure_context` and `denominator_unit` to select eligible records. `cases` is null for source percentages. `overlapping_margin` marks summaries and subsets that share exposures with other rows. [Manifest](../data/chamber/v1.4/manifest.json)

```sql
SELECT source_id, stratum, cases, denominator, denominator_unit,
       reported_percent, exposure_context, analysis_role
FROM cohort_observation
WHERE endpoint = 'dcs'
ORDER BY source_id, stratum;
```
