CREATE TABLE web_chamber_stage_vge_summary (
    source_id TEXT NOT NULL REFERENCES web_chamber_source_extract,
    condition TEXT NOT NULL,
    measurement_context TEXT NOT NULL CHECK(measurement_context IN ('rest','after_knee_bends')),
    phase TEXT NOT NULL CHECK(phase IN ('ascent','descent')),
    column_in_phase INTEGER NOT NULL CHECK(column_in_phase > 0),
    altitude_label_as_printed TEXT NOT NULL,
    altitude_ft_as_printed INTEGER NOT NULL CHECK(altitude_ft_as_printed >= 0),
    altitude_ft_per_methods INTEGER NOT NULL CHECK(altitude_ft_per_methods >= 0),
    resolved_altitude_ft INTEGER CHECK(resolved_altitude_ft >= 0),
    altitude_status TEXT NOT NULL CHECK(altitude_status IN ('as_printed','unresolved_source_conflict')),
    participants_as_reported INTEGER NOT NULL CHECK(participants_as_reported > 0),
    grade_scale TEXT NOT NULL,
    minimum_grade INTEGER NOT NULL CHECK(minimum_grade BETWEEN 0 AND 5),
    median_grade REAL NOT NULL CHECK(median_grade BETWEEN minimum_grade AND maximum_grade),
    maximum_grade INTEGER NOT NULL CHECK(maximum_grade BETWEEN minimum_grade AND 5),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,condition,measurement_context,phase,column_in_phase),
    CHECK((altitude_status='as_printed' AND altitude_ft_as_printed=altitude_ft_per_methods
            AND resolved_altitude_ft IS NOT NULL AND resolved_altitude_ft=altitude_ft_as_printed)
       OR (altitude_status='unresolved_source_conflict' AND altitude_ft_as_printed<>altitude_ft_per_methods
            AND resolved_altitude_ft IS NULL))
) STRICT;

CREATE TABLE web_chamber_hemodynamic_summary (
    source_id TEXT NOT NULL REFERENCES web_chamber_source_extract,
    condition TEXT NOT NULL,
    measure TEXT NOT NULL,
    unit TEXT NOT NULL,
    source_elapsed_min INTEGER NOT NULL CHECK(source_elapsed_min >= 0),
    availability TEXT NOT NULL CHECK(availability IN ('summary_as_printed','dash_as_printed')),
    participants_as_reported INTEGER CHECK(participants_as_reported > 0),
    mean REAL CHECK(mean > 0),
    standard_deviation REAL CHECK(standard_deviation >= 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id,condition,measure,source_elapsed_min),
    CHECK((measure='cardiac_output' AND unit='L_per_min') OR (measure='heart_rate' AND unit='beats_per_min')),
    CHECK((availability='summary_as_printed' AND mean IS NOT NULL AND standard_deviation IS NOT NULL
            AND participants_as_reported IS NOT NULL)
       OR (availability='dash_as_printed' AND mean IS NULL AND standard_deviation IS NULL
            AND participants_as_reported IS NULL))
) STRICT;
