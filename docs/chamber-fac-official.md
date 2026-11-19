# Colombian Air Force chamber records

The two FAC workbooks supplied by the program are the primary sources for DCS registrations and training activity in 2010–2020. The numbered case register covers all participating organizations. Column K identifies 50 of the 54 events as FAC, two as SATENA, one as Ejército and one as Perú. The training workbook reports annual totals across organizations from 2005 through 31 March 2021. [Source hashes, sheet names and locators](../data/chamber/fac-official/sources.csv)

## Cases and chamber activity

Each numbered row on the `DCS` sheet represents one registered event. Under the merged header `POSICION`, T is `ALUMNO` and U is `INSTRUCTOR`. Exactly one column is marked on every case row. Independently summing rows 5–58 reproduces both footer cells, T59 = 35 and U59 = 19. Columns I:J encode sex separately. The year is the year of the chamber flight.

| Flight year | Student DCS | Instructor DCS | All DCS | Hypoxia activities | Rapid-decompression activities |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2010 | 0 | 0 | 0 | 154 | 85 |
| 2011 | 0 | 0 | 0 | 345 | 206 |
| 2012 | 2 | 0 | 2 | 560 | 327 |
| 2013 | 0 | 1 | 1 | 703 | 33 |
| 2014 | 8 | 5 | 13 | 541 | 254 |
| 2015 | 2 | 4 | 6 | 437 | 184 |
| 2016 | 9 | 3 | 12 | 460 | 153 |
| 2017 | 5 | 3 | 8 | 636 | 215 |
| 2018 | 3 | 1 | 4 | 520 | 156 |
| 2019 | 5 | 1 | 6 | 584 | 102 |
| 2020 | 1 | 1 | 2 | 90 | 0 |
| **Total** | **35** | **19** | **54** | **5,030** | **1,715** |

On the `consolidado` sheet, L and M count hypoxia and rapid-decompression training. B51:D51 sum those categories to **6,745 activities**. Separately, B18:B28 sum to **7,599 trained crewmember entries** across the physiological training program. Both activities can occur in one profile. E51 subtracts an unexplained 247 from D51 to give 6,498. The workbook provides no counting rule for that adjustment. The 2021 row is partial and its ejection count is marked `?`. Outside 2010–2020, case counts are stored as missing. [Full annual extraction](../data/chamber/fac-official/annual.csv)

The student and instructor percentages among registered events are 64.8% and 35.2%. Role-specific incidence needs the number of monitored student and instructor exposures. These workbooks provide annual activity totals without a person-by-session roster, exposure histories for event-free participants, a common follow-up window, or Doppler grades. They support case descriptions and annual activity comparisons. Individual DCS risk, instructor-versus-student risk and VGE model fitting require additional observations.

## Instructor flight dates and the 2022 schedule change

`FECHA VUELO CAMARA DE ALTURA` (D) dates the chamber flight associated with a registered DCS event. `POSICION` (T:U) identifies the occupant's role on that flight. Instructor cases fall between 2013 and 2020. Of 19 instructor case records, 18 have a valid flight date, 17 have a document number, and 16 have both. D28 contains `15/93/2016`. The printed year is usable for annual counts. Its exact date remains unknown.

| Dated case flights | Monday | Tuesday | Wednesday | Thursday | Friday | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Instructor | 2 | 5 | 5 | 3 | 3 | 18 |
| Student | 6 | 6 | 12 | 9 | 2 | 35 |

The 18 dated instructor events occurred on 17 dates in 16 Monday–Sunday weeks. Fourteen weeks contained one instructor case and two weeks contained two. In one week the two records share a Friday. In the other they fall on a Wednesday and Thursday. The names recorded on the two rows differ in each week. Same-day records alone cannot establish how many chamber sessions took place.

Exact document-number matching identifies five groups with repeat instructor DCS records. Four groups have at least two valid dates, giving five intervals between consecutive dated case flights of **97, 362, 800, 862 and 923 days** in ascending order. In the fifth group, one flight was in 2014 and the other has only a usable year of 2016. No linked instructor had two dated **case flights** in the same calendar week or in a rolling window of seven calendar dates (a difference of 0–6 days). Two instructor records have no document number. A spelling shared by two different recorded document numbers was left unresolved. The linkage uses exact numbers and preserves all case rows.

An instructor could have flown earlier in the week without developing DCS on that flight. Such flights leave no row in the case register. The Tuesday–Friday count of 16 therefore describes when registered cases flew. Testing cumulative exposure requires the occupant roster for every session, including event-free flights, and its date or time. That would allow calculation of time since the previous flight, flights and RD exercises in the preceding seven days, and comparable follow-up for each occupant. In a combined session, one attendance can contribute one flight and one RD component.

### Program-owner protocol history

| Operating period | Facility schedule per week | Per-person attendance |
| --- | --- | --- |
| Before the change in 2022 | Two rapid-decompression (RD) exercises and three 25,000-ft flights | An instructor could fly more than once. Individual assignments and timing are unavailable. |
| From the change in 2022 | One combined session containing one RD exercise and one 25,000-ft flight | Each person flies at most once per week. The effective month and day are unspecified. |

The program owner reports the same Bogotá 25,000-ft profile in both periods. The chamber starts at **8,360 ft**, ascends to **13,000 ft** for an ear and sinus check, then descends to complete **30 minutes total of preoxygenation on 100% oxygen**. The main ascent reaches **25,000 ft for 10 minutes**, followed by **18,000 ft for 10 minutes** and final descent. Routine ascent and descent use **2,500 ft/min**. The reconstructed profile assumes the two returns are to 8,360 ft. At the stated rate, the main ascent takes 6.656 minutes, descent between plateaus takes 2.800 minutes and the final return takes 3.856 minutes. These are calculated transit times. Individual breathing-gas switches, ear-check duration, and the RD pressure step and timing are undocumented. All registered cases predate the policy change, so its effect on DCS incidence cannot be estimated from these workbooks. [Protocol tables and chronology definitions](../data/chamber/fac-flight-history/analysis.sql)

## Reconciliation with the publications

- The 11 thesis annual DCS counts match the official register. The thesis figure reports 8,993 trained, and its main Results and the conference abstract give 6,745. The official activity columns explain the latter figure. For 2020, the official file gives 90 hypoxia activities and zero rapid-decompression activities. The thesis lists 120 trained and the Olaya chapter lists 117 exposures.
- The register's 35 student and 19 instructor events take precedence over the thesis table's 34 students and 20 instructors and the abstract's 34 instructors or inside observers.
- Column Q explicitly labels two Type I events and one Type II event. The other 51 rows record DCS without a subtype. A program note confirms the same Type II event. The published subtype splits remain available as secondary classifications. Column W records 2 cruise, 2 descent, 14 ground, 5 postflight and 31 delayed presentations without numeric onset times.
- Olaya reports a neurological endpoint during 2013–2023. The two sources overlap during 2013–2020. The official case register ends in 2020 and therefore cannot revise the later years. [Publication versions](chamber-sharepoint-review.md#colombian-training-records) · [Source relationships](../data/chamber/fac-official/overlap.csv)

## Build and query

The aggregate database builds from the versioned extractions using the Python standard library.

```sh
python -m scripts.build_chamber_database --fac-official
```

To reproduce the extraction and load the 54 individual event records locally, install the FAC Excel readers and supply the two original files in this order.

```sh
python -m pip install -e ".[fac]"
python -m scripts.build_chamber_database --fac-workbooks "PATH/TO/CASE_REGISTER.xls" "PATH/TO/TRAINING_TOTALS.xlsx"
python -m scripts.analyze_fac_flight_dates
```

The first command to build the database creates `artifacts/chamber-fac-official/observed.sqlite`. The workbook build creates `case-records.local.sqlite` beside it. It verifies both source hashes, footer totals, duplicate annual activity tables and all frozen aggregate rows before publishing the database. The table `fac_official_case` is local to the workbook build. It preserves the source row, role, age, sex, flight date, recorded profiles, clinical labels, presentation segment and available clinical notes. Source blanks remain null. One invalid flight date in D28 preserves the source text and year 2016, with the date field left null. Neither hypoxia-duration column contains a recorded value.

Names, document numbers, ranks and units remain in the originals. A local document group links exact nonblank document numbers within the register. There are 47 events with a document number, representing 41 distinct recorded numbers, and seven events without one. A group denotes a matching recorded number. Repeat events and missing identifiers preclude treating 54 as a count of distinct people.

The flight-date command creates `flight-history.local.sqlite` beside the case database. It contains the case records, `fac_instructor_case_week`, `fac_instructor_case_intervals`, the reported weekly schedules and the nominal altitude phases. In the intervals view, a missing previous date means there is no earlier **dated case** in that document group. Personal flights in the previous week remain unknown.

```sql
SELECT year, student_dcs_events, instructor_dcs_events, registered_dcs_events,
       hypoxia, rapid_decompression, chamber_activities
FROM fac_official_chamber_year
ORDER BY year;
```
