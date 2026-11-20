# Kazakova and Poleshchuk chamber outcomes from JPRS-71096

The English translation of the 1978 article is available in the University of California copy of *Space Biology and Aerospace Medicine*, volume 12. The issue cover and bibliographic sheet identify report JPRS-71096, dated 11 May 1978. Pages 34–38 correspond to HathiTrust scan sequences 190–194. The Russian article and English translation describe one study. The earlier PubMed abstract record remains linked to the full-text extraction. [Volume catalogue](https://catalog.hathitrust.org/Record/102453231) · [Issue cover](https://babel.hathitrust.org/cgi/ssd?id=uc1.c2960236&seq=149) · [Original article citation](https://pubmed.ncbi.nlm.nih.gov/642418/)

The 13 volunteers completed 38 chamber tests at 11,000 m. Seven took part in both experimental conditions. Planned time at altitude was six hours, and exercise was repeated every 15 minutes. The event is the authors’ altitude decompression disorder, reported by the subject and described mainly as joint or muscle pain. Severe pain or deterioration could end the test. The report gives no standardized post-exposure follow-up. [Methods and Results, translated pp. 35–36](https://babel.hathitrust.org/cgi/ssd?id=uc1.c2960236&seq=191)

| Prebreathe condition | Prebreathe duration | Affected tests / all tests |
| --- | --- | ---: |
| Oxygen-filled suit | 5 or 6 h combined | 8 / 11 |
| Oxygen-filled suit | 8 h | 3 / 4 |
| Ordinary control | 5 h | 4 / 6 |
| Ordinary control | 6 h | 9 / 15 |
| Ordinary control | 8 h | 1 / 2 |

The five strata sum to 25 affected tests across 38 exposures. The suit and control totals of 11/15 and 14/23 each repeat their duration-specific rows. The database labels them as overlapping margins. The groups share some participants, and the 5- and 6-hour suit tests are published together. No individual exposure duration is assigned to that combined prebreathe stratum. [Table 1, translated p. 36](https://babel.hathitrust.org/cgi/ssd?id=uc1.c2960236&seq=192) · [Table 2, translated p. 37](https://babel.hathitrust.org/cgi/ssd?id=uc1.c2960236&seq=193) · [Observation register](../data/chamber/v1.44/observations.csv)

The linked `publication_chamber_reported_onset` table retains the 25 symptomatic rows, including published subject codes, onset and actual time at high altitude, converted from hours and minutes. These timings describe the affected tests already counted above. The report lacks test-level durations for the other 13 exposures. Repeat attendance, the published outcome definition and missing censoring information constrain use of the timing data. [Onset transcription](../data/chamber/v1.44/reported_onsets.csv) · [Overlap register](../data/chamber/v1.44/overlap.csv)

Firecrawl recovered the HathiTrust source-provided text, including both tables. The counts were checked against the narrative and against the number of symptomatic rows in each table. The page viewer did not return readable table images in the available retrievals. Participant codes and times retain their status as transcriptions of the archive OCR. Tavily identified the University of Pennsylvania catalogue route to the earlier JPRS series and helped check related literature. The Webb workshop report was logged for overlap reconciliation before numeric intake. [Search and retrieval log](../data/chamber/publication-review/retrievals-2026-11-20-jprs71096.json) · [Webb chapter citation](https://catalog.nlm.nih.gov/nde/fulldisplay/alma999346563406676/01NLM_INST:NDE/en)

```sh
python -m scripts.chamber_products --output-dir artifacts/chamber-products/2026-11-20-v1.44
```

Both databases passed integrity and foreign-key checks. The release retained every prior observation, and the benchmark reproduced the previous evaluation. All 49 tests in the linked database, publication review, report identity and observed benchmark suites passed.
