CREATE TABLE publication_fraser_ascent_run_score (
    source_id TEXT NOT NULL,
    stratum TEXT NOT NULL,
    subject_number INTEGER NOT NULL,
    printed_row_number INTEGER NOT NULL CHECK(printed_row_number > 0),
    pdf_page INTEGER NOT NULL CHECK(pdf_page BETWEEN 19 AND 23),
    date_as_printed TEXT NOT NULL CHECK(length(date_as_printed) BETWEEN 3 AND 5),
    symptom_score INTEGER CHECK(symptom_score >= 0),
    ambiguous_score_reading TEXT CHECK(instr(ambiguous_score_reading, '?') > 0),
    date_note TEXT,
    PRIMARY KEY(source_id,stratum,subject_number,printed_row_number),
    FOREIGN KEY(source_id,stratum,subject_number)
        REFERENCES publication_fraser_ascent_score(source_id,stratum,subject_number),
    CHECK((symptom_score IS NULL) != (ambiguous_score_reading IS NULL))
) STRICT;

CREATE VIEW publication_fraser_ascent_score_coverage AS
SELECT s.source_id, s.stratum, s.subject_number, s.reported_runs,
       count(d.printed_row_number) AS dated_rows,
       count(d.symptom_score) AS readable_scores
FROM publication_fraser_ascent_score AS s
LEFT JOIN publication_fraser_ascent_run_score AS d USING (source_id,stratum,subject_number)
GROUP BY s.source_id, s.stratum, s.subject_number, s.reported_runs;
