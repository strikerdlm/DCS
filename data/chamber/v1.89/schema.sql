CREATE TABLE publication_flinn63_exposure (
    source_id TEXT NOT NULL REFERENCES publication_source(source_id),
    sequence_number INTEGER NOT NULL CHECK(sequence_number > 0),
    exposure_setting TEXT NOT NULL CHECK(exposure_setting IN (
        'aircraft','chamber','pressure_suit_chamber','sham_chamber'
    )),
    source_phase TEXT NOT NULL CHECK(source_phase IN ('antecedent_history','medical_evaluation')),
    exposure_date TEXT,
    reported_altitude_ft INTEGER NOT NULL CHECK(reported_altitude_ft > 0),
    altitude_description TEXT NOT NULL CHECK(altitude_description IN (
        'cabin','flight_altitude_unspecified','chamber','outer_chamber','chamber_upper_bound','cabin_lower_bound'
    )),
    inside_suit_equivalent_ft INTEGER CHECK(inside_suit_equivalent_ft > 0),
    altitude_stated_to_subject_ft INTEGER CHECK(altitude_stated_to_subject_ft > 0),
    prebreathe_min INTEGER CHECK(prebreathe_min >= 0),
    first_subjective_symptom_min INTEGER CHECK(first_subjective_symptom_min >= 0),
    first_symptom_phase TEXT CHECK(first_symptom_phase IN ('at_altitude','after_chamber')),
    symptom_free_observation_min INTEGER CHECK(symptom_free_observation_min > 0),
    visual_symptom_status TEXT NOT NULL CHECK(visual_symptom_status IN ('reported','explicitly_absent','unreported')),
    antecedent_neurologic_episode INTEGER CHECK(antecedent_neurologic_episode IN (0,1)),
    clinical_course TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,sequence_number),
    CHECK(inside_suit_equivalent_ft IS NULL OR exposure_setting='pressure_suit_chamber'),
    CHECK(altitude_stated_to_subject_ft IS NULL OR exposure_setting='sham_chamber'),
    CHECK(first_subjective_symptom_min IS NULL OR first_symptom_phase IS NOT NULL),
    CHECK(symptom_free_observation_min IS NULL OR first_symptom_phase IS NULL),
    CHECK(antecedent_neurologic_episode IS NULL OR source_phase='antecedent_history')
) STRICT;

CREATE TABLE publication_flinn63_milestone (
    source_id TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    finding TEXT NOT NULL,
    elapsed_min INTEGER CHECK(elapsed_min >= 0),
    elapsed_reference TEXT CHECK(elapsed_reference IN (
        'at_altitude','after_first_symptom','at_ground','after_descent','postflight'
    )),
    precision TEXT CHECK(precision IN ('source_value','approximate','upper_bound','derived_from_source_timing')),
    altitude_ft INTEGER CHECK(altitude_ft >= 0),
    note TEXT NOT NULL,
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,sequence_number,finding),
    FOREIGN KEY(source_id,sequence_number) REFERENCES publication_flinn63_exposure(source_id,sequence_number),
    CHECK((elapsed_min IS NULL) = (elapsed_reference IS NULL)),
    CHECK((elapsed_min IS NULL) = (precision IS NULL)),
    CHECK(altitude_ft IS NOT NULL OR elapsed_min IS NOT NULL)
) STRICT;
