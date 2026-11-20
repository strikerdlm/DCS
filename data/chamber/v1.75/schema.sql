CREATE TABLE publication_argo_phase_i_arm (
    source_id TEXT NOT NULL REFERENCES publication_source,
    arm TEXT NOT NULL CHECK(arm IN ('ambulatory','bed_rest')),
    nasa_test_id TEXT NOT NULL REFERENCES nasa_test(test_id),
    reported_doppler_n INTEGER NOT NULL CHECK(reported_doppler_n > 0),
    reported_any_vge INTEGER NOT NULL CHECK(reported_any_vge BETWEEN 0 AND reported_doppler_n),
    reported_grade_iv INTEGER NOT NULL CHECK(reported_grade_iv BETWEEN 0 AND reported_any_vge),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,arm),
    UNIQUE(source_id,nasa_test_id)
) STRICT;

CREATE TABLE publication_argo_phase_i_doppler (
    source_id TEXT NOT NULL REFERENCES publication_source,
    roster_row INTEGER NOT NULL CHECK(roster_row BETWEEN 1 AND 27),
    ambulatory_grade INTEGER CHECK(ambulatory_grade BETWEEN 0 AND 4),
    ambulatory_status TEXT NOT NULL CHECK(ambulatory_status IN ('graded','lost','withdrawn','outside_grade_roster')),
    bed_rest_grade INTEGER CHECK(bed_rest_grade BETWEEN 0 AND 4),
    bed_rest_status TEXT NOT NULL CHECK(bed_rest_status IN ('graded','lost','withdrawn','atypical_signal','outside_grade_roster')),
    ambulatory_tcd_bubbles INTEGER CHECK(ambulatory_tcd_bubbles IN (0,1)),
    bed_rest_tcd_bubbles INTEGER CHECK(bed_rest_tcd_bubbles IN (0,1)),
    saline_contrast_status TEXT NOT NULL CHECK(saline_contrast_status IN (
        'resting_arterialization','no_arterialization','not_tested','lost'
    )),
    CHECK((ambulatory_grade IS NOT NULL) = (ambulatory_status = 'graded')),
    CHECK((bed_rest_grade IS NOT NULL) = (bed_rest_status = 'graded')),
    CHECK(ambulatory_tcd_bubbles IS NULL OR ambulatory_status = 'graded'),
    CHECK(bed_rest_tcd_bubbles IS NULL OR bed_rest_status = 'graded'),
    CHECK((roster_row = 27) = (ambulatory_status = 'outside_grade_roster')),
    CHECK((roster_row = 27) = (bed_rest_status = 'outside_grade_roster')),
    PRIMARY KEY(source_id,roster_row)
) STRICT;

CREATE TABLE publication_argo_phase_i_clinical (
    source_id TEXT NOT NULL,
    arm TEXT NOT NULL,
    finding TEXT NOT NULL CHECK(finding IN ('source_type_ii_dcs','mild_joint_pain_dcs','rash_and_orthostatic_instability')),
    roster_row INTEGER,
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,arm,finding),
    UNIQUE(source_id,arm,roster_row),
    FOREIGN KEY(source_id,arm) REFERENCES publication_argo_phase_i_arm,
    FOREIGN KEY(source_id,roster_row) REFERENCES publication_argo_phase_i_doppler
) STRICT;
