# The 19 March 1954 chamber case

Halbouty and Heisler's 1955 report and Berry and King's 1959 Case 1 describe the same chamber episode. The match uses the March 1954 date, age, body measurements, ascent rate, 43,000-ft peak, timing of visible signs, loss of consciousness during descent and the hospital course. The model database retains the existing `berry59_king:case-01` observation and adds the exact date. The literature review links the original and follow-up to one episode. [1955 original, p. 1364](https://babel.hathitrust.org/cgi/ssd?id=uiug.30112104083990;seq=452) · [1959 follow-up, Case 1](https://archive.org/details/in.ernet.dli.2015.71422/page/n6/mode/1up)

| Observation | Reported timing or stage | Source |
| --- | --- | --- |
| Patient-reported abdominal pain | During ascent at 35,000 ft | 1959, p. 2 |
| Chamber team's first observed signs | 30 seconds after reaching 43,000 ft | 1955, p. 1365 · 1959, p. 2 |
| Loss of consciousness | On descent at 30,000 ft | 1955, p. 1365 · 1959, p. 2 |
| Ground arrival and immediate clinical attention | 14:07 | 1955, p. 1365 |
| Transfer to hospital ward | 15:00 | 1955, p. 1365 |
| Re-examination | 1958, with neurologic findings reported within normal limits | 1959, p. 3 |

The 11 recorded milestones preserve their original clocks, anchors and sources. The 35,000-ft discomfort has no stated elapsed time or confirmed attribution. The 30-second interval starts at peak arrival, while the hospital timestamp records a later transfer. The catalog therefore leaves the standardized DCS-onset time blank. The case supplies no exposure denominator. Its membership in Berry’s overlapping 1950–1955 surveillance series remains unverified. [1955 chronology, p. 1365](https://archive.org/download/in.ernet.dli.2015.71418/page/n1139_large.jpg) · [Model milestones](../data/chamber/v1.50/case_milestones.csv)

The Internet Archive scan has a misplaced page at the location of printed p. 1364. The HathiTrust copy supplies that page. LlamaParse reached its credit limit, so the chronology was verified directly from the original page images and their public text views. A follow-up search also matched Donnell and Norton’s 1960 chamber case to its existing database record. [Retrieval log](../data/chamber/publication-review/retrievals-2026-11-20-halbouty.json)

Cannon and Gould identify Cotes’s 1953 paper as FPRC Report 825. The UK National Archives lists Report 825’s number within the range covered by undigitized folder **AIR 57/28**. The earlier 793 and 794 reports on the 610-person series fall within the range of undigitized folder **AIR 57/22**. The catalogue gives folder ranges, and the original reports await retrieval. [Cannon and Gould, references p. 282](https://www.bmj.com/content/bmj/1/5378/282.full.pdf) · [AIR 57/28](https://discovery.nationalarchives.gov.uk/details/r/C2151737) · [AIR 57/22](https://discovery.nationalarchives.gov.uk/details/r/C2151735)

```sh
python -m scripts.chamber_products --output-dir artifacts/chamber-products/2026-11-20-v1.50
```

Both SQLite databases passed integrity and foreign-key checks. All 55 linked-database, review, identity and benchmark tests passed. The case catalog contains one row for this episode linked to both reports. Existing outcome totals, role-specific groups and benchmark evaluation matched v1.49.
