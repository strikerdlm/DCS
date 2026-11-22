CREATE TABLE publication_doppler_vibration_protocol (
    source_id TEXT PRIMARY KEY NOT NULL REFERENCES publication_source,
    participants INTEGER NOT NULL CHECK(participants > 0),
    dive_pressure_kpa REAL NOT NULL CHECK(dive_pressure_kpa > 0),
    dive_duration_min INTEGER NOT NULL CHECK(dive_duration_min > 0),
    dive_cycle_work_watts REAL NOT NULL CHECK(dive_cycle_work_watts >= 0),
    max_surface_interval_min INTEGER NOT NULL CHECK(max_surface_interval_min >= 0),
    exposure_pressure_kpa REAL NOT NULL CHECK(exposure_pressure_kpa > 0),
    exposure_altitude_m INTEGER NOT NULL CHECK(exposure_altitude_m > 0),
    exposure_duration_min INTEGER NOT NULL CHECK(exposure_duration_min > 0),
    interval_duration_min INTEGER NOT NULL CHECK(interval_duration_min > 0),
    primary_vibration_hz REAL NOT NULL CHECK(primary_vibration_hz > 0),
    primary_peak_acceleration_g REAL NOT NULL CHECK(primary_peak_acceleration_g > 0),
    prophylaxis_duration_min INTEGER NOT NULL CHECK(prophylaxis_duration_min > 0),
    prophylaxis_pressure_methods_kpa REAL NOT NULL CHECK(prophylaxis_pressure_methods_kpa > 0),
    prophylaxis_pressure_figure_kpa REAL NOT NULL CHECK(prophylaxis_pressure_figure_kpa > 0),
    prophylaxis_pressure_adjudicated_kpa REAL CHECK(prophylaxis_pressure_adjudicated_kpa > 0),
    locator TEXT NOT NULL
) STRICT;

CREATE TABLE publication_doppler_vibration_pair (
    source_id TEXT NOT NULL REFERENCES publication_doppler_vibration_protocol,
    subject_number INTEGER NOT NULL CHECK(subject_number > 0),
    starting_condition TEXT NOT NULL CHECK(starting_condition IN ('vibration','non_vibration')),
    vibration_signal_seconds INTEGER NOT NULL CHECK(vibration_signal_seconds >= 0),
    non_vibration_signal_seconds INTEGER NOT NULL CHECK(non_vibration_signal_seconds >= 0),
    locator TEXT NOT NULL,
    PRIMARY KEY(source_id,subject_number)
) STRICT;
