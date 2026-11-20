-- Promote two earlier catalogue records to verified primary sources.
UPDATE publication_source
SET access='full_text',
    disposition='extracted',
    locator='Abstract, Tables II–VI and Results, pp. 1327–1330',
    source_sha256='df6b3beb6510a7cf32a21029ad65e09489b93fde0368f5669f96f44a0dc17fad',
    note='Original four sequential protocols in 16 men. Table III gives marginal bends counts at 5 psia and among those reaching 3.5 psia. Table IV gives 45 of 102 man-flights affected by bends. The Allen 1971 body-fat subgroups share protocol lineage and do not provide independent observations.'
WHERE source_id='allen_beard69_2h' AND access='metadata' AND disposition='crosswalk';

UPDATE publication_source
SET citation='Meader WL. Decompression sickness in high-altitude flight. Aerosp Med. 1967;38(3):301–303.',
    identifier='AEME:38:3:301',
    access='full_text',
    disposition='extracted',
    locator='Methods pp. 301–302, Table I p. 302 and Results p. 303',
    source_sha256='a1041abff6c0dda1c9652256330e01b9dfd9168a4c24af0d194e2cbd6280ed53',
    note='The 958 flights are from crewmembers with a recorded case. This is a selected operational aircraft risk set. Squadron-wide counts are not enumerated.'
WHERE source_id='meade67' AND access='metadata' AND disposition='lead';

-- Original source review resolves the direction and scope of earlier links.
UPDATE publication_overlap
SET relationship='partial_overlap',
    evidence='Allen 1971 Table I lines 9 and 13 cite Allen and Beard for the third-hour cabin results. The oxygen comparator denominator is 58 in both via 32+26 in the 1969 two-hour trials. The mixed-gas denominators differ: 47 in the 1971 three-hour table and 36 for the 1969 nine-hour 5 psia arm. The stage views cannot be pooled.'
WHERE source_id='allen71_body_fat' AND related_source='allen_beard69_2h';

UPDATE publication_overlap
SET related_source='mciver67_eva',
    relationship='partial_overlap',
    evidence='Allen 1971 Table I line 2 cites this paper (ref. 38) and has the same 18 exposures. The original used two denitrogenation durations and presented symptoms including paresthesia. The different endpoint tally prevents treating the two rows as identical.'
WHERE source_id='allen71_body_fat' AND related_source='McIver et al. 1967, Aerosp Med 38:1034–1036';
