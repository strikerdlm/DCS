# Berry’s Air Force chamber surveillance

Berry’s 1957 Stockholm presentation and 1958 journal article each report **48 chamber reactors in 1956**. Both give an annual rate of **110 Grade IV reactions per 100,000 trainees**. The exact 1956 denominator is unavailable. The 51,580 reported training exposures apply to 1955. Grade IV is the author’s hospitalization-based classification for severe dysbarism reactions. It includes symptoms with several possible mechanisms. [Journal pp. 939–940](https://babel.hathitrust.org/cgi/ssd?id=uiug.30112104084048;seq=10) · [1956 count, journal p. 946](https://babel.hathitrust.org/cgi/ssd?id=uiug.30112104084048;seq=16) · [Stockholm presentation, PDF p. 11](https://utmb-ir.tdl.org/bitstreams/36358400-9c6c-4bc1-b94f-7146c4bd442f/download#page=11)

| Period | Count reported | Denominator reported | Grade IV rate per 100,000 trainees |
| --- | ---: | ---: | ---: |
| 1950–1955 combined | 125 | Unavailable | Unavailable |
| 1954 | Unavailable | Unavailable | 49 |
| 1955 | Unavailable | 51,580 | 85 |
| 1956 | 48 | Unavailable | 110 |

The model database adds the 1956 count under the existing journal source. The review links the article and its conference version to the same studies. The 1954 and 1956 rates remain in their reported units. No counts were reconstructed from percentages. The GAO records a trainee’s decompression injury in the same program in November 1956. Its diagnostic details and membership in the 48 reports remain unverified. It contributes no additional DCS case. [Outcome record](../data/chamber/v1.49/observations.csv) · [GAO decision B-133537](https://www.gao.gov/products/b-133537)

Table 4 contributes **62 printed symptom percentages** across the five reported subgroups of the 125 hospitalized reactors. The subgroup sizes are 65, 4, 4, 5 and 47. The extracted percentages are conditional on subgroup membership, and symptoms can co-occur. Blank source cells were left unassigned. In the neurological group, the source reports 61.7% each for abnormal vision, paralysis or paresis, dizziness, and loss of consciousness. The treatment paragraph uses 45 for that group, so its 58% estimate has a different reported denominator and was left out of this table. [Table 4 and treatment paragraph, p. 943](https://babel.hathitrust.org/cgi/ssd?id=uiug.30112104084048;seq=13) · [Extracted rates](../data/chamber/v1.49/reported_rates.csv)

Tavily located the university-held manuscript and Firecrawl located the HathiTrust issue. LlamaParse transcribed the manuscript. The journal’s printed table and 1956 count were checked against original page images. The search also documented Korean chamber dysbarism citations from 1974 and 1975 as two reports with possible overlap. Clinical outcomes and risk sets await full text. [Retrieval register](../data/chamber/publication-review/retrievals-2026-11-20-berry-training.json) · [1974 reference](https://koreascience.kr/article/JAKO201231434069438.pub?&lang=ko&orgId=ksafo) · [1975 catalogue](https://kiss.kstudy.com/Detail/Ar?key=4019953)

```sh
python -m scripts.chamber_products --output-dir artifacts/chamber-products/2026-11-20-v1.49
```

Both databases passed integrity and foreign-key checks. All 54 linked-database, review, identity and benchmark tests passed. The benchmark reproduced v1.48, and the 105 catalogued cases and 26 role-specific groups were identical between releases.
