UPDATE publication_ascent_reference
SET related_source_id='bridge44_38000'
WHERE source_id='kumar89_ascent' AND reference_number=12;

UPDATE publication_ascent_reference
SET related_source_id='degner65_orbital'
WHERE source_id='kumar89_ascent' AND reference_number=22;

INSERT INTO publication_overlap (source_id, related_source, relationship, evidence)
VALUES ('kumar89_ascent','waligora87','partial_overlap',
        'Appendix B p. 57 rows 27–29 cite Waligora et al. The two 19-person, six-hour-prebreathe groups and one 8-person, eight-hour-prebreathe group match the publication totals and pressure. The appendix does not label a sex for each 19-person row. Existing VGE correction is documented separately.');
