# Public altitude chamber outcomes, release 1.2

The 19 November 2026 search used Tavily and Firecrawl to find primary publications and retrieve tables. Release 1.2 adds 57 aggregate endpoint rows from nine publications, two source leads and eight relationships to the chamber SQLite database. The release keeps the locked operational benchmark and NASA development data from release 1.0 and the Zotero supplement from release 1.1. The new rows support descriptive comparisons and protocol reconstruction. Their inclusion in a future calibration or validation set requires endpoint and observation-window review. [Source registry](../data/chamber/v1.2/sources.csv) · [Outcome rows](../data/chamber/v1.2/observations.csv) · [Overlap register](../data/chamber/v1.2/overlap.csv)

| Primary study | Observed outcomes and denominators | Scope |
| --- | --- | --- |
| Colombian DIMAE-FAC, Olaya Santamaria | 15 confirmed neurological Type II DCS events in 10,280 person-exposures, January 2013 through December 2023. Eleven annual counts and two reported severity subclasses are available. | Candidate operational benchmark for neurological Type II DCS. Chamber profiles, role-specific exact denominators and a uniform diagnosis window are unavailable in the published tables. [Methods and Tables 2–3](https://esdeglibros.edu.co/index.php/editorial/catalog/download/371/277/4828?inline=1) |
| Swedish parachute jumpmasters, Eiken et al. | DCS 2/10 after hypobaric preoxygenation and 0/10 after sea-level preoxygenation. Any VGE 9/10 and 4/10, respectively. DCS onsets were 40 and 55 min after arrival at 28,000 ft. | The same ten jumpmasters took part in both conditions. [Methods and Results](https://pmc.ncbi.nlm.nih.gov/articles/PMC10363086/) |
| Swedish moderate-altitude excursion, Ånell et al. | DCS 0/10 in each condition. Each condition planned 90 min at 24,000 ft. One inserted a 30-min dwell at 15,000 ft. | The same ten men completed both sessions. The VGE data available in the text are summarized as medians and ranges. [Methods and Results](https://pmc.ncbi.nlm.nih.gov/articles/PMC8505281/) |
| Swedish hyperoxic crossover, Ånell et al. | DCS 3/13 with 54% oxygen, 2/13 with 90% oxygen and 1/13 with 90% oxygen plus 18,000-ft excursions. | The trial enrolled 13 men across three paired conditions. The case in the excursion arm remains in the clinical denominator even though the VGE comparison excluded that session. [Results and Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/92/4/article-p223.pdf) |
| USAF repeated altitude, Pilmanis et al. | DCS 19/32, 7/32 and 2/32 at 25,000 ft across a continuous protocol, a segmented protocol and a segmented protocol with hour-long air breaks at ground level. Any VGE, Spencer Grade III–IV VGE, and serious respiratory or neurological DCS signs have their own rows. | The same 32 people took part in all three arms. Hold for unresolved participant links to historical USAF data. [Methods and Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/73/6/article-p525.pdf) |
| UK gas mixtures, Connolly et al. 2010 | Type I DCS 3/10 with 56% oxygen and 2/10 with 75% oxygen at 21,500 ft. Table III gives diagnosis times. | The paired total of 5/20 duplicates the earlier intake. The separately reported case outside the paired sample is flagged. [Results and Table III](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/81/12/article-p1069.pdf) |
| UK frequent ascents, Connolly et al. 2026 | One DCS event across 43 chamber decompressions at 25,000 ft. The case occurred on the third ascent and the authors report 53 min at 25,000 ft. | The public abstract gives the aggregate count for 11 participants. The paper's full text and the ascent-specific risk sets were unavailable. [Publisher abstract](https://doi.org/10.3357/AMHP.6973.2026) |
| U.S. Navy training, Davenport | 12 suspected DCS cases in 5,851 trainee records, including 11 Type II cases. | Hold for likely overlap with the Rice Navy series and differences in adjudication and ascertainment. The report gives postflight onset as late as 60 h. [Table I and Results](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/68/1/article-p61.pdf) |
| Operation Everest II, Malconian et al. | 28 DCS episodes across 274 investigator-flights above 15,000 ft. Sixteen of 23 investigators had at least one episode. | Repeat staff flights in a simulated expedition. The database preserves the flight counts by altitude band and sequential flight number and keeps the person-level margin separate. [Results and Tables I–II](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/58/7/article-p679.pdf) |

## Source discrepancies and eligibility

- The FAC narrative on p. 312 lists 2015 among years without cases. The visually checked Table 2 gives 1/828 and its 11 years sum to 15/10,280, identical to Table 3. The database preserves the 2015 table count with a row-level flag. The two PSI subclasses are overlapping margins for incidence calculations because each uses the full denominator. [FAC chapter, pp. 312–315](https://esdeglibros.edu.co/index.php/editorial/catalog/download/371/277/4828?inline=1)
- The Swedish hyperoxic crossover Table I gives 80 min for the excursion case, while the Results prose gives 30 min before the first recompression. The exact clinical count is usable for chamber-protocol incidence. The event time is unresolved. [Results and Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/amhp/92/4/article-p223.pdf)
- The Everest II detailed flight cells sum to 28/274 and match the text. The bottom subtotal for 15,000–20,000 ft gives 4/146 while its component cells sum to 4/148. One cell pairs 2/23 with a printed 87%. The database preserves exact cells and the reconciled study total. The high-altitude rate of 29.7% belongs to 11/37 at 26,000–29,000 ft. DeGroot et al. explicitly omit these same 28 cases from their analysis of adverse reactions. Their 23,656 exposures provide no new DCS numerator–denominator pair. [Everest II Table II](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/58/7/article-p679.pdf) · [DeGroot et al., p. 996](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/74/9/article-p994.pdf)

## Rebuild and query

```sh
python -m scripts.build_chamber_database --web-supplement
```

The builder writes `artifacts/chamber-v1.2/observed.sqlite` and verifies the curated input manifest before loading. `web_source.source_sha256` records the bytes of cached public PDFs where acquired. The publisher abstract and the abstract-only 2019 lead have a null digest. Publisher access watermarks may change PDF bytes on a later download. [Frozen input checksums](../data/chamber/v1.2/manifest.json)

```sql
SELECT period, cases, denominator, ROUND(1000.0 * cases / denominator, 3) AS per_1000
FROM web_observation
WHERE source_id = 'olaya25' AND analysis_role = 'descriptive_stratum'
ORDER BY period;
```

`planned_target_min` is the nominal total time at the target altitude. Protocol text gives intervening dwells at other pressures. `cases` counts occurrences of the named endpoint, including VGE endpoints. `analysis_role` identifies descriptive cells, overall totals, overlapping margins and rows held for review. Use one coherent set of strata per endpoint and retain the documented repeated-measures structure when comparing protocols. The database stores no individual records for these sources.
