# Chamber evidence release v1.42

## Ryabtsev repeat-exposure study

The 1996 Russian author synopsis reports **one disputed DCS case in 540 simulated exposures among 18 men**. The event occurred on the first exposure day. The exposure margin uses the author's denominator of 540. The companion person-level margin records the same event in 18 volunteers who contributed repeated exposures. The case remains labeled suspected DCS. The synopsis gives no fixed post-exposure follow-up window. [Original Russian synopsis](https://medical-diss.com/medicina/psihofiziologicheskoe-sostoyanie-cheloveka-pri-modelirovanii-nekotoryh-faktorov-sistematicheskoy-vnekorabelnoy-deyatelnos)

The main series involved 28 days at 493 mmHg in a normoxic chamber environment. The first simulated exposure followed 24 hours of residence. Each participant completed 30 simulated exposures at 195 mmHg on a schedule of four- and eight-hour sessions. The synopsis lists an ultrasound method and says that gas formation was detected only during the first two exposures. It gives no number of positive scans or tested denominator by exposure order. The complete programme's 572 simulated exposures include two preliminary series whose clinical counts are unavailable. [Methods, Tables 1–2 and decompression safety section](https://medical-diss.com/medicina/psihofiziologicheskoe-sostoyanie-cheloveka-pri-modelirovanii-nekotoryh-faktorov-sistematicheskoy-vnekorabelnoy-deyatelnos)

The earlier Chadov publications describe other target pressures or a different number of experiments. They share investigators or a chamber facility with Ryabtsev. The database records the source links and unresolved participant overlap. The 1991 conference item in Ryabtsev's bibliography is a separate report lead with no additional outcome rows. [Chadov 1997 abstract](https://ntrs.nasa.gov/api/citations/19980024361/downloads/19980024361.pdf#page=2) · [Chadov 2001 abstract](https://pubmed.ncbi.nlm.nih.gov/11496423/) · [Overlap records](../data/chamber/v1.42/overlap.csv)

## Kazakova and Poleshchuk translation

The later v1.44 release recovered the tables and added counts and symptom timing. [JPRS translation and extraction](chamber-jprs-translation-supplement.md)

The recovered citation identifies 38 investigations in 13 men, with five, six or eight hours of oxygen breathing and a six-hour chamber exposure at 11,000 m. The author abstract gives a qualitative comparison and lacks exact DCS counts by arm. NASA's index identifies the English translation as JPRS-71096, pp. 34–38, accession N78-23713. The case tables remain unavailable. [Author abstract](https://pubmed.ncbi.nlm.nih.gov/642418/) · [NASA bibliography](https://ntrs.nasa.gov/api/citations/19780023769/downloads/19780023769.pdf)

Tavily and Firecrawl located and extracted the author synopsis. A direct download of the Russian HTML provides the source fingerprint. The scan viewer returned HTTP 404. The recorded counts come from the synopsis's narrative text. [Search queries](../data/chamber/v1.42/search_runs.csv) · [Search results](../data/chamber/v1.42/search_hits.csv) · [Frozen input checksums](../data/chamber/v1.42/manifest.json)

```sh
python -m scripts.build_chamber_database --chamber-repeated-eva-supplement
python -m scripts.build_chamber_database --chamber-repeated-eva-supplement --fac-official
```

The public and combined outputs are `artifacts/chamber-v1.42/observed.sqlite` and `artifacts/chamber-fac-official/observed-v1.42.sqlite`.

Both databases passed SQLite integrity and foreign-key checks. Comparison with v1.41 verified that every existing row was retained. The public rebuild matched the original SHA-256, and all 34 benchmark tests passed.
