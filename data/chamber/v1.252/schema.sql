UPDATE publication_source
SET url='https://archive.org/details/sim_jama_1944-02-19_124_8_0/page/499',
    access='full_text',
    disposition='extracted',
    locator='Tables 1–3, printed pp. 499–501',
    source_sha256='d430ffe70e0360b36b80c0283ad5bc57098d162a52cbf83de87e489a8ead9644',
    note='Original Greenville Army Air Base chamber series. Nine flights were reported in Table 1. Tables 2 and 3 describe overlapping subsets. Participant IDs in the extraction are Table 2 row ordinals. Retain discrepancies between tables and the subsequent Kumar compilation.'
WHERE source_id='mackenzie44';

CREATE TABLE publication_mackenzie_flight (
    source_id TEXT NOT NULL REFERENCES publication_source,
    flight_number INTEGER NOT NULL CHECK(flight_number BETWEEN 1 AND 9),
    flight_label TEXT NOT NULL CHECK(flight_label IN ('Ex.','C.')),
    pressure_altitude_ft INTEGER NOT NULL CHECK(pressure_altitude_ft > 0),
    regulator_connection_altitude_ft INTEGER NOT NULL CHECK(
        regulator_connection_altitude_ft BETWEEN 0 AND pressure_altitude_ft
    ),
    automix TEXT NOT NULL CHECK(automix IN ('on','off')),
    exercise INTEGER NOT NULL CHECK(exercise IN (0,1)),
    ascent_rate_ft_min INTEGER NOT NULL CHECK(ascent_rate_ft_min > 0),
    chokes_grade_3_count INTEGER NOT NULL CHECK(chokes_grade_3_count >= 0),
    chokes_grade_4_count INTEGER NOT NULL CHECK(chokes_grade_4_count >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,flight_number)
) STRICT;

CREATE TABLE publication_mackenzie_susceptibility (
    source_id TEXT NOT NULL REFERENCES publication_source,
    table_2_row INTEGER NOT NULL CHECK(table_2_row BETWEEN 1 AND 18),
    flight_1_outcome TEXT CHECK(flight_1_outcome IN ('0','2','3','chokes_3','chokes_4')),
    flight_3_outcome TEXT CHECK(flight_3_outcome IN ('0','2','3','chokes_3','chokes_4')),
    flight_4_outcome TEXT CHECK(flight_4_outcome IN ('0','2','3','chokes_3','chokes_4')),
    flight_6_outcome TEXT CHECK(flight_6_outcome IN ('0','2','3','chokes_3','chokes_4')),
    flight_9_outcome TEXT CHECK(flight_9_outcome IN ('0','2','3','chokes_3','chokes_4')),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,table_2_row)
) STRICT;

CREATE TABLE publication_mackenzie_later_flights (
    source_id TEXT NOT NULL,
    table_2_row INTEGER NOT NULL,
    initial_symptomatic_flights INTEGER NOT NULL CHECK(initial_symptomatic_flights BETWEEN 0 AND 2),
    later_flights INTEGER NOT NULL CHECK(later_flights BETWEEN 1 AND 3),
    later_symptomatic_flights INTEGER NOT NULL CHECK(later_symptomatic_flights BETWEEN 0 AND later_flights),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,table_2_row),
    FOREIGN KEY(source_id,table_2_row) REFERENCES publication_mackenzie_susceptibility(source_id,table_2_row)
) STRICT;
