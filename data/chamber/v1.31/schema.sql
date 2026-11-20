CREATE TABLE publication_observation_superseded (
    source_id TEXT NOT NULL REFERENCES publication_source,
    stratum TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    numerator INTEGER NOT NULL CHECK(numerator >= 0),
    denominator INTEGER NOT NULL CHECK(denominator >= numerator AND denominator > 0),
    retained_source_id TEXT NOT NULL,
    retained_stratum TEXT NOT NULL,
    retained_endpoint TEXT NOT NULL,
    reason TEXT NOT NULL,
    PRIMARY KEY(source_id,stratum,endpoint),
    FOREIGN KEY(retained_source_id,retained_stratum,retained_endpoint)
        REFERENCES publication_observation
) STRICT;

INSERT INTO publication_observation_superseded VALUES
    ('houston47_low_altitude','staff-ever-affected','aeroembolism_author_attributed',6,20,
     'houston46_navy','operating-staff','aeroembolism_symptomatic_person_source',
     'Same six of 20 staff in the 1946 Navy report and 1947 journal article.'),
    ('houston47_low_altitude','staff-ever-scotoma','scintillating_temporal_scotoma',3,20,
     'houston46_navy','operating-staff','scotoma_person_source',
     'Same three staff with temporal scotomata in both publications.'),
    ('houston47_low_altitude','staff-scotoma-temporal-blindness','unilateral_temporal_blindness',2,3,
     'houston46_navy','operating-staff','persistent_unilateral_temporal_blindness_source',
     'Same two staff with blindness. The journal denominator of three is the conditional scotoma subset recorded in the retained report.');

DELETE FROM publication_observation
WHERE (source_id,stratum,endpoint,numerator,denominator) IN (
    SELECT source_id,stratum,endpoint,numerator,denominator
    FROM publication_observation_superseded
);

UPDATE publication_overlap
SET relationship = 'same_cohort',
    evidence = 'Original Navy report and journal article match on 387 lock ascents, 20 operating staff, six affected people, three scotomas, and two persistent visual losses. Their case descriptions describe the same episodes.'
WHERE source_id = 'houston46_navy' AND related_source = 'houston47_low_altitude';

UPDATE publication_source
SET disposition = 'crosswalk',
    note = 'Publisher PDF confirms the same 20-person cohort as Houston 1946 Navy report AD0622164. The journal remains the source of the incapacitating-bends margin. Three overlapping journal rows are documented in publication_observation_superseded. The exact episode count and linked flight denominator remain unavailable.'
WHERE source_id = 'houston47_low_altitude';
