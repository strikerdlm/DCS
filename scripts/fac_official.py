"""Read the two frozen FAC workbooks and verify their public aggregates before local use."""

from __future__ import annotations

import re
from collections import Counter

from scripts.build_chamber_database import FAC_DATA, read_csv, sha256


CASE_SCHEMA = """
CREATE TABLE fac_official_case (
    source_id TEXT NOT NULL REFERENCES fac_official_source,
    source_row INTEGER PRIMARY KEY,
    event_number INTEGER UNIQUE NOT NULL,
    annual_number INTEGER NOT NULL,
    quarter_number INTEGER,
    document_group INTEGER,
    year INTEGER NOT NULL REFERENCES fac_official_annual(year),
    flight_date TEXT,
    invalid_source_date TEXT,
    age_years INTEGER,
    sex TEXT NOT NULL,
    entity TEXT NOT NULL,
    specialty_source TEXT,
    role TEXT NOT NULL,
    performed_spn_mark INTEGER,
    performed_iva_mark INTEGER,
    performed_rd_mark INTEGER,
    injury_source TEXT NOT NULL,
    dcs INTEGER NOT NULL CHECK(dcs = 1),
    dcs_subtype TEXT NOT NULL,
    affected_site_source TEXT,
    event_profile TEXT NOT NULL,
    event_segment TEXT NOT NULL,
    event_altitude_source TEXT NOT NULL,
    hypoxia_25000_time_source TEXT,
    hypoxia_18000_time_source TEXT,
    spn_detail_source TEXT,
    iva_detail_source TEXT,
    rd_18000_detail_source TEXT,
    rd_15000_detail_source TEXT,
    helmet_source TEXT,
    mask_source TEXT,
    seat_source TEXT,
    aviation_oxygen_source TEXT,
    medical_oxygen_source TEXT,
    history_source TEXT,
    inflight_action_source TEXT,
    treatment_source TEXT,
    incapacity_source TEXT,
    sequelae_source TEXT,
    program_action_source TEXT,
    CHECK((flight_date IS NULL) != (invalid_source_date IS NULL))
) STRICT
"""

SUBTYPES = {
    "ENF POR DESCOMPRESION": "unspecified",
    "ENF. DESCOMPRESION T1": "I",
    "ENF. DESCOMPRESION T2": "II",
}
CASE_DIMENSIONS = {
    "sex": "I:J",
    "role": "POSICION T:U",
    "dcs_subtype": "Q",
    "entity": "K",
    "event_profile": "V",
    "event_segment": "W",
}


def read_cases(book):
    import xlrd

    sheet = book.sheet_by_name("DCS")
    groups = {}
    events = []
    for row in range(4, 58):
        values = [v if v != "" else None for v in sheet.row_values(row)]
        if values[0] != row - 3 or values[17] != 1:
            raise ValueError(f"Unexpected DCS register row {row + 1}")
        date = None
        invalid_date = None
        if sheet.cell_type(row, 3) == xlrd.XL_CELL_DATE:
            date = xlrd.xldate_as_datetime(values[3], book.datemode).date()
            year = date.year
        else:
            invalid_date = values[3]
            match = re.fullmatch(r"\d{2}/\d{2}/(\d{4})", invalid_date)
            if not match:
                raise ValueError(f"Unresolved register year in row {row + 1}")
            year = int(match.group(1))
        if values[8:10] not in ([1, None], [None, 1]) or values[19:21] not in (
            [1, None],
            [None, 1],
        ):
            raise ValueError(f"Ambiguous sex or role markers in row {row + 1}")
        # Only equal nonblank document numbers share a local group. No name matching.
        group = None
        if values[6] is not None:
            group = groups.setdefault(values[6], len(groups) + 1)
        altitude = values[23]
        events.append(
            dict(
                source_id="fac_cases",
                source_row=row + 1,
                event_number=int(values[0]),
                annual_number=int(values[1]),
                quarter_number=values[2],
                document_group=group,
                year=year,
                flight_date=date.isoformat() if date else None,
                invalid_source_date=invalid_date,
                age_years=values[7],
                sex="MAS" if values[8] else "FEM",
                entity=values[10],
                specialty_source=values[12],
                role="ALUMNO" if values[19] else "INSTRUCTOR",
                performed_spn_mark=values[13],
                performed_iva_mark=values[14],
                performed_rd_mark=values[15],
                injury_source=values[16],
                dcs=int(values[17]),
                dcs_subtype=SUBTYPES[values[16]],
                affected_site_source=values[18],
                event_profile=values[21],
                event_segment=values[22],
                event_altitude_source=str(int(altitude))
                if isinstance(altitude, float)
                else altitude,
                hypoxia_25000_time_source=values[24],
                hypoxia_18000_time_source=values[25],
                spn_detail_source=values[26],
                iva_detail_source=values[27],
                rd_18000_detail_source=values[28],
                rd_15000_detail_source=values[29],
                helmet_source=values[30],
                mask_source=values[31],
                seat_source=values[32],
                aviation_oxygen_source=values[33],
                medical_oxygen_source=values[34],
                history_source=values[35],
                inflight_action_source=values[36],
                treatment_source=values[37],
                incapacity_source=values[38],
                sequelae_source=values[39],
                program_action_source=values[40],
            )
        )
    for index in (8, 9, 13, 14, 15, 17, 19, 20):
        if sum(sheet.cell_value(i, index) == 1 for i in range(4, 58)) != sheet.cell_value(
            58, index
        ):
            raise ValueError(f"Case footer mismatch in column {index + 1}")
    return events


TRAINING_FIELDS = (
    "trained_crew",
    "fac_crew",
    "army_crew",
    "navy_crew",
    "police_crew",
    "other_crew",
    "deb",
    "dea",
    "nvt",
    "nvg",
    "hypoxia",
    "rapid_decompression",
    "ejection",
    "total_training_activities",
    "courses",
    "course_attendees",
)


def extract(case_path, training_path):
    import openpyxl
    import xlrd

    sources = {s["source_id"]: s["sha256"] for s in read_csv("sources.csv", directory=FAC_DATA)}
    for path, key in ((case_path, "fac_cases"), (training_path, "fac_training")):
        if sha256(path) != sources[key]:
            raise ValueError(f"Input differs from the registered {key} workbook")
    with xlrd.open_workbook(case_path) as book:
        events = read_cases(book)
    yearly_cases = Counter(e["year"] for e in events)
    yearly_roles = Counter((e["year"], e["role"]) for e in events)
    annual = []
    book = openpyxl.load_workbook(training_path, data_only=True, read_only=True)
    try:
        sheet = book["consolidado"]
        cells = list(sheet.values)
        for row in range(13, 30):
            raw = cells[row - 1]
            year = int(str(raw[0]).rstrip("*"))
            covered = 2010 <= year <= 2020
            data = dict(zip(TRAINING_FIELDS, raw[1:17], strict=True))
            if data["ejection"] == "?":
                data["ejection"] = None
            annual.append(
                dict(
                    source_id="fac_training",
                    year=year,
                    source_row=row,
                    partial_through="2021-03-31" if year == 2021 else None,
                    **data,
                    registered_dcs_events=yearly_cases[year] if covered else None,
                    student_dcs_events=yearly_roles[year, "ALUMNO"] if covered else None,
                    instructor_dcs_events=yearly_roles[year, "INSTRUCTOR"] if covered else None,
                    case_source_id="fac_cases" if covered else None,
                )
            )
            if covered and tuple(cells[row + 18][:3]) != (
                year,
                data["hypoxia"],
                data["rapid_decompression"],
            ):
                raise ValueError(f"Training cross-tab mismatch for {year}")
        for i, field in enumerate(TRAINING_FIELDS, start=1):
            if sum(r[field] for r in annual if r[field] is not None) != cells[29][i]:
                raise ValueError(f"Training total mismatch for {field}")
        chamber_years = [r for r in annual if r["case_source_id"]]
        h = sum(r["hypoxia"] for r in chamber_years)
        rd = sum(r["rapid_decompression"] for r in chamber_years)
        if (h, rd, h + rd) != tuple(cells[50][1:4]):
            raise ValueError("Chamber activity total differs from B51:D51")
    finally:
        book.close()
    counts = []
    for dimension, columns in CASE_DIMENSIONS.items():
        for category, n in sorted(Counter(e[dimension] for e in events).items()):
            counts.append(
                dict(
                    source_id="fac_cases",
                    dimension=dimension,
                    category=category,
                    events=n,
                    locator=f"DCS rows 5–58, {columns}",
                )
            )
    return events, annual, counts


def ingest_workbooks(db, case_path, training_path):
    events, annual, counts = extract(case_path, training_path)
    for table, rows in (("fac_official_annual", annual), ("fac_official_observation", counts)):
        columns = ",".join(rows[0])
        stored = db.execute(f"SELECT {columns} FROM {table}").fetchall()
        if Counter(map(tuple, stored)) != Counter(tuple(r.values()) for r in rows):
            raise ValueError(f"Workbook extraction differs from {table}")
    db.execute(CASE_SCHEMA)
    columns = ",".join(events[0])
    params = ",".join("?" for _ in events[0])
    db.executemany(
        f"INSERT INTO fac_official_case ({columns}) VALUES ({params})",
        [tuple(e.values()) for e in events],
    )
