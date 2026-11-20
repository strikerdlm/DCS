-- Upgrade the indexed abstract lead in place once the original article is available.
UPDATE publication_source
SET url = 'https://asma.kglmeridian.com/downloadpdf/view/journals/joam/18/2/article-p165.pdf',
    access = 'full_text',
    disposition = 'extracted',
    locator = 'Program description p. 165, Cases 1–6 pp. 166–167, discussion and summary pp. 167–168',
    source_sha256 = 'a5ce682ecad1aa8eafabc0646a9f42bc65a8dc9bf0db66131c2a8e233bdce278',
    note = 'Primary PDF recovered. The 20 staff made all but a few of the 387 program lock ascents over the reported 28-day period. The summary assigns all 387 ascents to those staff and approximates 15 episodes. Ascents are program context. Six of the 20 staff had symptoms attributed to aeroembolism. Visual symptoms have source-specific clinical attribution.'
WHERE source_id = 'houston47_low_altitude';
