-- Program-owner account accompanying the official FAC workbooks, clarified 2026-11-19.
CREATE TABLE fac_protocol_calendar (
    period TEXT PRIMARY KEY,
    relation_to_2022_change TEXT NOT NULL,
    facility_rd_exercises_per_week INTEGER NOT NULL,
    facility_25000_ft_flights_per_week INTEGER NOT NULL,
    combined_sessions_per_week INTEGER,
    individual_flights_per_week_cap INTEGER,
    source TEXT NOT NULL
) STRICT;
INSERT INTO fac_protocol_calendar VALUES
    ('historical', 'Before the change in 2022', 2, 3, NULL, NULL, 'Program owner'),
    ('revised', 'From the change in 2022, month and day unknown', 1, 1, 1, 1, 'Program owner');

CREATE TABLE fac_reported_profile (
    profile TEXT PRIMARY KEY,
    facility_altitude_ft INTEGER NOT NULL,
    preoxygenation_min INTEGER NOT NULL,
    preoxygenation_o2_fraction REAL NOT NULL,
    routine_ascent_ft_min INTEGER NOT NULL,
    routine_descent_ft_min INTEGER NOT NULL,
    source TEXT NOT NULL
) STRICT;
INSERT INTO fac_reported_profile VALUES
    ('Bogotá 25000 ft', 8360, 30, 1.0, 2500, 2500, 'Program owner, protocol unchanged across the schedule change');

CREATE TABLE fac_profile_phase (
    phase INTEGER PRIMARY KEY,
    profile TEXT NOT NULL REFERENCES fac_reported_profile,
    activity TEXT NOT NULL,
    from_ft INTEGER NOT NULL,
    to_ft INTEGER NOT NULL,
    stated_hold_min REAL,
    interpretation TEXT NOT NULL
) STRICT;
INSERT INTO fac_profile_phase VALUES
    (1,'Bogotá 25000 ft','Ascent to ear and sinus check',8360,13000,NULL,'Routine ascent'),
    (2,'Bogotá 25000 ft','Ear and sinus check',13000,13000,NULL,'Check duration unspecified'),
    (3,'Bogotá 25000 ft','Descent after check',13000,8360,NULL,'Assumed return to facility altitude'),
    (4,'Bogotá 25000 ft','Complete preoxygenation',8360,8360,NULL,'Complete 30 min total on 100% oxygen. Remaining time after check unspecified'),
    (5,'Bogotá 25000 ft','Ascent to upper plateau',8360,25000,NULL,'Routine ascent from assumed facility altitude'),
    (6,'Bogotá 25000 ft','Upper plateau',25000,25000,10,'Plateau time. Individual mask-off time unknown'),
    (7,'Bogotá 25000 ft','Descent to lower plateau',25000,18000,NULL,'Routine descent'),
    (8,'Bogotá 25000 ft','Lower plateau',18000,18000,10,'Plateau time. Individual mask-off time unknown'),
    (9,'Bogotá 25000 ft','Final descent',18000,8360,NULL,'Assumed return to facility altitude');

CREATE VIEW fac_nominal_profile_phase AS
    SELECT p.*, CASE WHEN to_ft>from_ft THEN round(1.0*(to_ft-from_ft)/routine_ascent_ft_min,3)
                     WHEN from_ft>to_ft THEN round(1.0*(from_ft-to_ft)/routine_descent_ft_min,3)
                END AS calculated_transit_min
    FROM fac_profile_phase p JOIN fac_reported_profile USING(profile);

-- All dates are chamber-flight calendar dates. The register contains cases only.
CREATE VIEW fac_dated_case AS
    SELECT source_row, role, document_group, flight_date,
           date(flight_date,'-6 days','weekday 1') AS week_start_monday,
           (CAST(strftime('%w',flight_date) AS INTEGER)+6)%7+1 AS iso_weekday
    FROM fac_official_case WHERE flight_date IS NOT NULL;

CREATE VIEW fac_instructor_case_week AS
    SELECT week_start_monday, count(*) AS case_records,
           count(DISTINCT flight_date) AS case_dates,
           count(DISTINCT document_group) AS documented_groups,
           count(*)-count(document_group) AS missing_document_records
    FROM fac_dated_case WHERE role='INSTRUCTOR' GROUP BY week_start_monday;

CREATE VIEW fac_instructor_case_intervals AS
    WITH ordered AS (
        SELECT *, lag(flight_date) OVER w AS prior_dated_case_flight,
               lag(week_start_monday) OVER w AS prior_case_week
        FROM fac_dated_case WHERE role='INSTRUCTOR' AND document_group IS NOT NULL
        WINDOW w AS (PARTITION BY document_group ORDER BY flight_date,source_row)
    )
    SELECT *, CAST(julianday(flight_date)-julianday(prior_dated_case_flight) AS INTEGER)
               AS days_since_prior_dated_case_flight,
           week_start_monday=prior_case_week AS same_iso_week
    FROM ordered;
