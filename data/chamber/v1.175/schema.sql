-- Profile counts describe reported students and chamber flights. The report
-- supplies no observer risk set that can be paired with mixed-role reactions.
CREATE TABLE publication_faa90_profile (
    source_id TEXT NOT NULL REFERENCES literature_source(source_id),
    profile TEXT NOT NULL CHECK(profile IN ('A', 'B')),
    year_first INTEGER NOT NULL,
    year_last INTEGER NOT NULL CHECK(year_last >= year_first),
    student_count_as_reported INTEGER NOT NULL CHECK(student_count_as_reported > 0),
    chamber_flight_count INTEGER NOT NULL CHECK(chamber_flight_count > 0),
    locator TEXT NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY(source_id, profile)
) STRICT;

-- Table 1 counts recorded reactions. These can overlap within people and
-- include inside observers. Profile totals are retained in the profiles table.
CREATE TABLE publication_faa90_reaction (
    source_id TEXT NOT NULL,
    profile TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    reaction_count INTEGER NOT NULL CHECK(reaction_count >= 0),
    role_basis TEXT NOT NULL CHECK(role_basis IN (
        'unresolved', 'mixed_series', 'known_student'
    )),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id, profile, endpoint),
    FOREIGN KEY(source_id, profile) REFERENCES publication_faa90_profile
) STRICT;
