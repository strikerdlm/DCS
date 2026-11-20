ALTER TABLE publication_validation_snapshot ADD COLUMN reported_actual_dcs_plus_minus_pp
    REAL CHECK(reported_actual_dcs_plus_minus_pp BETWEEN 0 AND 100);
