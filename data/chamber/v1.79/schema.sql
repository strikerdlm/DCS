CREATE TABLE publication_u2_episode (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    report_pilot_key TEXT NOT NULL,
    episode_sequence INTEGER NOT NULL CHECK(episode_sequence > 0),
    reported_year INTEGER CHECK(reported_year >= 1955),
    approximate_interval_from_prior_episode_months INTEGER
        CHECK(approximate_interval_from_prior_episode_months IS NULL OR
              (episode_sequence > 1 AND approximate_interval_from_prior_episode_months > 0)),
    first_symptom_phase TEXT NOT NULL CHECK(first_symptom_phase IN ('in_flight','unknown')),
    approximate_onset_min_low INTEGER CHECK(approximate_onset_min_low >= 0),
    approximate_onset_min_high INTEGER CHECK(approximate_onset_min_high >= approximate_onset_min_low),
    onset_reference TEXT CHECK(onset_reference = 'from_flight_start' AND first_symptom_phase = 'in_flight'),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    UNIQUE(source_id,report_pilot_key,episode_sequence),
    FOREIGN KEY(source_id,stratum,endpoint) REFERENCES publication_observation,
    CHECK((approximate_onset_min_low IS NULL) = (approximate_onset_min_high IS NULL)),
    CHECK((approximate_onset_min_low IS NULL) = (onset_reference IS NULL))
) STRICT;
