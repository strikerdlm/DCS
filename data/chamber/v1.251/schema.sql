CREATE TABLE publication_threshold_profile_revision (
    source_id TEXT NOT NULL,
    printed_row INTEGER NOT NULL,
    related_source_id TEXT NOT NULL,
    related_stratum TEXT NOT NULL,
    related_endpoint TEXT NOT NULL,
    reconciliation_status TEXT NOT NULL CHECK(reconciliation_status IN (
        'counts_concordant', 'scope_discrepancy'
    )),
    reconciliation_note TEXT NOT NULL,
    PRIMARY KEY(source_id, printed_row),
    FOREIGN KEY(source_id, printed_row)
        REFERENCES publication_threshold_profile(source_id, printed_row),
    FOREIGN KEY(related_source_id, related_stratum, related_endpoint)
        REFERENCES publication_observation(source_id, stratum, endpoint)
) STRICT;

CREATE VIEW publication_threshold_profile_reconciled AS
SELECT p.source_id, p.printed_row, p.altitude_ft, p.exposure_count,
    p.duration_h_min, p.duration_h_max, p.denitrogenation_h, p.exercise_schedule,
    p.ascent_ft_per_min, p.symptom_count, p.printed_reference,
    COALESCE(r.related_source_id, p.related_source_id) AS related_source_id,
    r.related_stratum, r.related_endpoint, o.locator AS related_locator,
    COALESCE(r.reconciliation_status, p.reconciliation_status) AS reconciliation_status,
    COALESCE(r.reconciliation_note, p.reconciliation_note) AS reconciliation_note
FROM publication_threshold_profile p
LEFT JOIN publication_threshold_profile_revision r USING(source_id, printed_row)
LEFT JOIN publication_observation o
    ON o.source_id=r.related_source_id AND o.stratum=r.related_stratum AND o.endpoint=r.related_endpoint;
