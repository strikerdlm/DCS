# Chamber evidence release v1.39

## USAF 8.3-psia Doppler study

Webb and colleagues reported grade 3 or 4 venous gas emboli in **5 of 20 men** and **3 of 10 women** in a blood-analysis subset. Ultrasound showed grade 0 in the other 22 participants in that subset. The USAF protocol report places this publication and the Smead conference paper under the same study. The full study had 31 participants, comprising 20 men and 11 women. The missing blood-subset participant’s bubble grade was unavailable. [Webb author abstract](https://pubmed.ncbi.nlm.nih.gov/3363750/) · [USAFSAM-TP-88-10, study 6](https://archive.org/download/DTIC_ADA201274/DTIC_ADA201274.pdf)

The Smead abstract gives **25.8%** significant intravascular bubbling in the full sample. The database preserves that percentage under the authors’ endpoint and links it to the exact subset counts. NEDU already records the same experiment’s clinical outcomes, 1/20 for men and 0/11 for women. Webb and Pilmanis also reused the male VGE margin as a historical comparator. These reports represent one experiment. [Smead author abstract](https://ntrs.nasa.gov/citations/19880026174) · [Curated NEDU Appendix E](../data/chamber/v1/nedu_appendix_e.csv) · [Webb and Pilmanis, Table I](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/64/9/article-p808.pdf)

## Altitude training case

Studer and colleagues describe one presumptive Type II DCS case after training that included rapid decompression from 5,000 to 25,000 ft. The trainee associated symptom onset with removing the oxygen mask at altitude and sought emergency care 48 hours after training. The case provides a clinical account and symptom timing. A population denominator is unavailable. [Publisher PDF, pp. 11 and 14](https://jsomonline.org/wp-content/uploads/2024/02/2015111Studer.pdf)

## Source tracking

Tavily and Firecrawl found the 8.3-psia abstracts and the training case. Searches also rediscovered the Polish chamber cohort, the Russian Filipenkov Doppler series and the Israeli Ben-Ari cohort. Their records already appear in the database. The 1975 and 1977 Cherniakov papers are registered as linked leads. The 1977 abstract reports 40 experiments in 18 people. Study-level totals and the abstract's symptom summary cannot establish arm-specific event counts. [Search queries](../data/chamber/v1.39/search_runs.csv) · [Search results](../data/chamber/v1.39/search_hits.csv) · [1977 author abstract](https://pubmed.ncbi.nlm.nih.gov/839713/) · [1975 record](https://pubmed.ncbi.nlm.nih.gov/1162923/)

```sh
python -m scripts.build_chamber_database --chamber-bubble-outcomes-supplement
python -m scripts.build_chamber_database --chamber-bubble-outcomes-supplement --fac-official
```

The public and Colombian aggregate builds are `artifacts/chamber-v1.39/observed.sqlite` and `artifacts/chamber-fac-official/observed-v1.39.sqlite`. [Frozen input checksums](../data/chamber/v1.39/manifest.json)

Both builds passed SQLite integrity and foreign-key checks. Comparison to v1.38 verified all prior rows, including the five locked external strata. The public rebuild was byte-identical. All 31 benchmark tests passed.
