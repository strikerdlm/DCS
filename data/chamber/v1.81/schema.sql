CREATE TABLE publication_allan_chamber_plateau (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    study_day INTEGER NOT NULL CHECK(study_day BETWEEN 1 AND 3),
    order_in_description INTEGER NOT NULL CHECK(order_in_description > 0),
    altitude_ft INTEGER NOT NULL CHECK(altitude_ft > 0),
    duration_min INTEGER NOT NULL CHECK(duration_min > 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,order_in_description),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;

CREATE TABLE publication_allan_dci_case (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    patient_label TEXT NOT NULL CHECK(patient_label IN ('A','B','C')),
    reported_age_years INTEGER NOT NULL CHECK(reported_age_years > 0),
    pain_sites TEXT NOT NULL,
    self_reported_pain_score TEXT NOT NULL,
    other_symptoms TEXT NOT NULL,
    exam_findings TEXT NOT NULL,
    self_reported_resolution_min_from_hbot_start INTEGER NOT NULL
        CHECK(self_reported_resolution_min_from_hbot_start > 0),
    possible_oxygen_toxicity_during_hbot TEXT NOT NULL,
    followup TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint,patient_label),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation
) STRICT;

UPDATE publication_observation
SET altitude=26000,
    protocol='Winnipeg high-altitude indoctrination over three days. The cases spent 33 minutes at 26,000 ft and 18 minutes at 18,000 ft on day 1. Day 2 had no training. Day 3 included 24 minutes at 26,000 ft. The cases took a commercial flight about six hours after training ended.',
    outcome_window='The cases first noticed symptoms during the first commercial flight after training. The report gives no exact case-specific onset times from departure.',
    locator='Allan and Kenny, Case, pp. 803–804, and Table 1, p. 804',
    note='The peak altitude in the case histories is 26,000 ft. The same article describes approximately 25,000 ft for typical training. Three DCI cases were already recorded for this group. Seventeen trainees attended the course. The number taking the later flight with comparable follow-up is unavailable.'
WHERE source_id='allan03' AND stratum='after-chamber-and-commercial-flight'
  AND endpoint='dci' AND numerator=3 AND denominator IS NULL AND altitude=25000;
