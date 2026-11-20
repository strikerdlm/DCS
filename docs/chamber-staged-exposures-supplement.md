# Archived post-dive chamber flights and staged symptom records

Release 1.35 adds 47 printed participant records and 27 grouped outcomes from two original Edel studies. The study profiles differ and participant linkage is unavailable. The source files retain publication, table, phase, and conflict information. [Participant rows](../data/chamber/v1.35/staged_symptoms.csv) · [Grouped outcomes](../data/chamber/v1.35/observations.csv) · [Cohort links](../data/chamber/v1.35/overlap.csv)

## Edel and colleagues, 1969

Eleven volunteers were described in the participant table. Tables III–VI provide 47 participant rows across the three test conditions. The intended simulated flight included 112 minutes at 8,000 ft and a later excursion to 16,000 ft. Individual rows preserve reported joint pain, cutaneous itch, the source's symptom grades and stated follow-up. Blank cells remain null. Nominal altitude labels identify the scheduled profile stage. Several flights ended early or had symptoms during ascent. [Publisher PDF, pp. 1105–1110](https://asma.kglmeridian.com/downloadpdf/view/journals/aeme/40/10/article-p1105.pdf)

| Original source discrepancy | Database handling |
| --- | --- |
| Working 40 FSW dive with a five-minute surface interval | Detailed Table V has six rows and one bends case at the first stage. Table VII has four subjects and one case. The first-stage outcome stores 1/6 from the detailed table and carries a denominator conflict flag. |
| Working 120 FSW dive with a five-minute surface interval | Results and Table VII give one case during the later excursion. The five matching detailed rows in Table III print zero symptoms in that phase. The aggregate 1/5 is held, and the original individual zero cells are preserved without assigning the positive case to an individual. |

Table III prints the same participant code twice in the five-minute group. The published rows have separate table-row keys and no session dates. Test condition 3 also includes a case with symptoms at surface and termination at 5,000 ft. The database preserves it as a narrative-marked record and omits the ambiguous 33 FSW five-hour group from the fixed 8,000 ft outcome counts.

## Edel NASA report, 1970

Eleven arms account for 48 chamber exposures after simulated dives at 47 FSW. Tables II, III and V report five cases during the initial simulated flight. Two other participants stopped after one developed symptoms at surface earlier in the dive sequence. These two contribute no altitude exposures. [NASA report, Tables I–V and Results](https://ntrs.nasa.gov/api/citations/19700031843/downloads/19700031843.pdf#page=32)

| Series | Initial exposure groups | Participants exposed | Clinical cases in the initial stage |
| --- | ---: | ---: | ---: |
| A, one simulated dive | 3 | 16 | 0 |
| B, two simulated dives | 4 | 16 | 2 |
| C, four simulated dives | 4 | 16 | 3 |

Four separately recorded later-excursion counts preserve the figures as printed in Table V. The cohort assignment at the initial altitude does not identify how many were assessed at each later altitude. These rows keep the numerator, a null denominator and the nominal maximum in the protocol description. The reported C-5 count represents the printed column, while the narrative describes both new and recurrent symptoms during multiple excursion patterns.

## Source screening and rebuild

Tavily extracted the 1969 publisher PDF and found the NASA archive source. Firecrawl verified the reprint metadata and found an archival record for Furry. The publisher PDF confirms that Furry's chamber experiment used dogs. Its cited Duffner human study is indexed as a lead pending original exact outcomes. [Searches](../data/chamber/v1.35/search_runs.csv) · [Results](../data/chamber/v1.35/search_hits.csv) · [Source register](../data/chamber/v1.35/sources.csv) · [Input checksums](../data/chamber/v1.35/manifest.json)

```sh
python -m scripts.build_chamber_database --chamber-staged-exposures-supplement
python -m scripts.build_chamber_database --chamber-staged-exposures-supplement --fac-official
```

The public and combined outputs are `artifacts/chamber-v1.35/observed.sqlite` and `artifacts/chamber-fac-official/observed-v1.35.sqlite`.

Both builds passed SQLite integrity and foreign-key checks. All prior rows and five locked external strata were preserved. The three archived PDF digests matched the registry. The independent public rebuild was byte-identical, and all 27 benchmark tests passed.
