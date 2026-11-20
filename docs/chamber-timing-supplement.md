# Participant-linked chamber trial timing

Release 1.26 adds 96 trial timing records linked to 15 published participant identifiers, four aggregate or referral observations, two source records and two cohort links. The search ledger records 44 search or retrieval operations and 187 result screenings. [Sources](../data/chamber/v1.26/sources.csv) · [Participants](../data/chamber/v1.26/participants.csv) · [Trial times](../data/chamber/v1.26/trial_times.csv) · [Observations](../data/chamber/v1.26/observations.csv) · [Overlap](../data/chamber/v1.26/overlap.csv) · [Search operations](../data/chamber/v1.26/search_runs.csv) · [Search hits](../data/chamber/v1.26/search_hits.csv)

**Marotta et al., 1961.** Tables I and II identify 15 male volunteers, their reported anthropometrics, two direct-ascent trials and six planned durations at 12,000 ft before ascent to 38,000 ft. The 96 observed cells contain 89 times below the 60-minute limit, six symptom-free completions identified by the authors and a seventh value of 100% for participant 13 after the six-hour intermediate stage. The paper's summary gives six symptom-free trials and reports early termination for bends in all other trials. The participant-13 cell preserves 100% with unresolved event status. The source summary corresponds to 90 of 96 trials affected. The participant-linked classification supports 89 event rows, six right-censored rows and one unresolved row. The 24 blank table cells are absent from the trial table. Table II reports whole percentages of the 60-minute limit, so the original timing precision is retained. Participants 14 and 15 were unable to complete the planned series, which limits comparisons across stage durations. [Original Methods, Table II, Results and Summary](https://asma.kglmeridian.com/downloadpdf/view/journals/aeme/32/4/article-p289.pdf#page=2)

**AFRL staged chamber profile.** Kannan and Kundu report seven symptomatic events among 40 subjects during the first 240 minutes at 18,000 ft and 31 cumulative events among the same 40 through a further 180-minute stage at 35,000 ft. Nine subjects remained asymptomatic through study end. The two counts are nested. The later reanalysis gives no individual onset table, AFRL test code, actual gas delivery or workload for the profile. Both rows are held pending linkage to the earlier AFRL collections. A different Webb et al. staged profile used a 29,500-ft final stage. [Kannan and Kundu, section 5.1](https://arxiv.org/pdf/1807.01137#page=16) · [Webb et al., Table II](https://asma.kglmeridian.com/downloadpdf/view/journals/asem/71/7/article-p692.pdf)

**Spanish Navy referral.** The official issue confirms one DCS diagnosis before an operational HALO–HAHO jump. The three chamber referrals in the same table are already in release 1.7. The new operational row has no exposure denominator. [Ministry of Defence journal, Table 4 and Results](https://publicaciones.defensa.gob.es/media/downloadable/files/links/r/s/rsm_74-3-.pdf)

```sh
python -m scripts.build_chamber_database --chamber-timing-supplement
python -m scripts.build_chamber_database --chamber-timing-supplement --fac-official
```

```sql
SELECT exposure_label, event_status, COUNT(*) AS trials
FROM publication_chamber_trial_time
WHERE source_id = 'marotta61_partial'
GROUP BY exposure_label, event_status;
```

The public build writes `artifacts/chamber-v1.26/observed.sqlite`. The combined FAC build writes `artifacts/chamber-fac-official/observed-v1.26.sqlite`. [Input checksums](../data/chamber/v1.26/manifest.json)

Both builds passed integrity and foreign-key checks. The audit verified the published source digests, all eight trial-column totals, the unresolved cell, both AFRL counts, the new Spanish referral and the search ledger. Comparison with release 1.25 confirmed that every prior row was retained, including the locked external evaluation rows. The independent public rebuild was byte-identical, and all 23 benchmark tests passed.
