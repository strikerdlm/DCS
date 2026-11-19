# Mahon and Regis citation and chamber evidence database

Release 1.5 traces **243 printed references** in *Decompression and Decompression Sickness* (2014) and **50 later works** that OpenAlex indexed as citing the review on 19 November 2026. Ten cited primary publications contribute 68 aggregate observations. One also provides a published participant-by-protocol table. The records include clinical DCS, DCI, VGE, and outcomes conditional on diagnosis or treatment. [Review record](https://pubmed.ncbi.nlm.nih.gov/24944033/) · [References](../data/chamber/v1.5/references.csv) · [Forward citations](../data/chamber/v1.5/citers.csv) · [Sources and access](../data/chamber/v1.5/sources.csv)

## Reference and access checks

LlamaParse Agentic returned 19 pages from the supplied PDF, printed pages 1157–1175. All 243 numbered entries were matched in order against a second extraction from the PDF text layer and the publisher's 243 Crossref reference keys. Each entry retains its printed bibliography page. The supplied PDF has SHA-256 `c7de4c2d049c516bb96aee3e2382d4f534ca9b26661d1b603430be88e1084939`. The local LlamaParse Markdown has SHA-256 `5d24e2c8d99c01e4fab7f09bb74119b26448d597baf68e0779abc97464de5fe6`. [Crossref deposit](https://api.crossref.org/works/10.1002/cphy.c130039)

| Access status of a cited reference | Entries | Interpretation |
| --- | ---: | --- |
| Full text inspected | 12 | Original paper or report available locally or from the publisher or archive. |
| Primary abstract inspected | 5 | Eligible outcomes use only quantities explicitly stated by the authors. |
| Additional indexed full-text link | 51 | OpenAlex or Europe PMC supplies an access route. A link alone does not establish the contents of the paper. |
| No verified copy | 175 | The search did not establish a free full-text route or a reviewed copy. These entries remain searchable. |

OpenAlex resolved the printed DOI to work W1491023115 under an alternate DOI. Its 220 outgoing IDs are an unordered index. The batch metadata lookup returned 215 work records. DOI, title, year, and targeted identifier checks linked 200 printed entries to OpenAlex. The forward-citation lookup returned all 50 records in its result set. Europe PMC returned 183 matched PubMed records for the bulk availability check. Links classified as free abstract only were excluded from full-text availability. [OpenAlex review record](https://openalex.org/W1491023115) · [Forward citation query](https://api.openalex.org/works?filter=cites:W1491023115)

Consensus and SciSpace each returned 20 candidates for searches on the cited chamber experiments. The 1996 preoxygenation and 2001 altitude papers were retrieved from Consensus, and four matching original papers were identified in SciSpace. Outcomes were checked against primary tables, report images, or the authors' abstracts. Scite’s outgoing citation graph request reached its monthly account limit and supplied no edges.

A read-only snapshot of the configured Zotero desktop library, including its write-ahead log, showed **no matching review item** by title or either DOI in the personal or two locally stored group libraries. No matching attachment filename or byte-identical stored PDF was found. Three cited papers had verified matching attachments in the personal library, references 221, 224, and 225. The Zotero connector was unavailable for a separate cloud check.

## What the original papers add

| Printed reference | Data in the release | Interpretation and overlap |
| --- | --- | --- |
| 8 · Bassett | During 1973–1977, USAFSAM recorded 29 DCS cases in 12,465 student exposures. Other training units, excluding USAFSAM and Academy cadets, reported 60/222,425. Academy cadets had 12/1,654 and inside observers had 61/59,925. | The USAFSAM and Academy sex strata are nested in their respective totals. USAFSAM included course-specific altitude changes. [Original report, p. 12](https://archive.org/download/DTIC_ADA360821/DTIC_ADA360821.pdf) |
| 32 · Butler, Wolf and Krock | Chamber origin in 131/145, 507/528 and 437/480 hyperbaric-treated altitude cases across three periods. | The denominators count treated cases. Two earlier periods reproduce older case series. The first two counts differ from the prose percentages. [Original report, p. 1-3](https://archive.org/download/DTIC_ADP011059/DTIC_ADP011059.pdf) |
| 50, 124, 163 · Dervay, Krause, Pilmanis | Dervay reported no DCI among 20 crossover participants. Krause reported 801 DCS diagnoses in 2,001 research exposures and complete resolution after ground-level oxygen in 739/749 treated cases. Pilmanis reported DCS in 50%, 38%, 41% and 31% of 32 participants across four exercise conditions. | Dervay retains the DCI label. The Krause treatment denominator is conditional. Pilmanis tested each participant at an individually selected altitude. [Dervay](https://pubmed.ncbi.nlm.nih.gov/11817616/) · [Krause](https://pubmed.ncbi.nlm.nih.gov/10685583/) · [Pilmanis](https://pubmed.ncbi.nlm.nih.gov/9895017/) |
| 221 · Webb et al., 1996 | DCS in 11/26 after 10 min exercise plus 50 min rest during oxygen prebreathe, 20/26 after 60 min resting prebreathe, and 14/22 after 10 min exercise plus 5 min rest. | Table VI identifies 26 study participants, 74 completed sessions, and four unperformed sessions. The fields preserve symptoms, severe-VGE markings, and the postflight and HBO footnotes. All three published paired comparisons reconcile with these cells. NEDU PE1-A repeats the 11/26 result. [Primary publication](https://pubmed.ncbi.nlm.nih.gov/8830940/) · [Participant cells](../data/chamber/v1.5/participant_cells.csv) · [Paired counts](../data/chamber/v1.5/paired_dcs.csv) |
| 222, 225 · Webb et al., 2003 and 2005 | The 2003 sex comparison uses 550 male and 309 female exposures from 859 eligible exposures. The full study had 961. The 2005 archive has 47.5% DCS in 2,210 exposures and 46.5% in a repeat-volunteer subset of 1,879. | The SharePoint source register corroborates six of the 2003 percentages and the 1,879-exposure margin. The combined build stores these seven rows once in the citation tables. Ref. 225 also illustrates the need to check the review's wording. Its Results describe 35/240 in a low relative-susceptibility index bin, while the review gives 14%. That index is not a count of clinical events. [2003 report, pp. 3–5](https://archive.org/download/DTIC_ADA408816/DTIC_ADA408816.pdf) · [2005 paper](https://pubmed.ncbi.nlm.nih.gov/15945398/) |
| 223 · Webb et al., 2001 | At 35,000 ft, Table I gives DCS in 57% of 60 resting sessions, 91% of 32 mild-exercise sessions, and 97% of 60 strenuous-exercise sessions. | The 60 participants crossed over between rest and strenuous exercise. The mild-exercise arm had different participants, prebreathe, and ascent rate. The Discussion says 94% for mild exercise. The database retains Table I's 91% with that discrepancy. [Primary report, Table I](https://archive.org/download/DTIC_ADA426860/DTIC_ADA426860.pdf) |
| 226 · Webb et al., 2002 | Figure 1 reports 36 DCS cases among 67 exposed volunteers. Of the 60 eligible for post-exposure randomization, 29 had experienced DCS that resolved on descent. No delayed or recurrent DCS was reported among the 31 assigned post-exposure exercise. | The review's approximately 48% corresponds to 29/60 in the selected group. Seven volunteers were removed before randomization. The experiment does not supply a standardized 48-hour event-free endpoint. [Primary report, Figure 1 and Tables II–III](https://archive.org/download/DTIC_ADA426862/DTIC_ADA426862.pdf) |

References 53 and 84 give the same NEDU report number 09-03 and title with different author ordering. Reference 62's Crossref DOI points to a land-reclamation paper. Its deposited DOI is preserved for audit and its verified-work fields are empty. Reference 186's printed title omits the word *decompression*. The primary paper and PubMed identifier resolve it to the existing Sulaiman record. [Citation register](../data/chamber/v1.5/references.csv) · [Overlap register](../data/chamber/v1.5/overlap.csv)

## Build and query

```sh
python -m scripts.build_chamber_database --citation-supplement
```

The command builds `artifacts/chamber-v1.5/observed.sqlite` from the pinned inputs and earlier releases through 1.4. To inspect the primary evidence for a printed citation, join the reference's `source_id` to its observations. The forward-citation table uses `cited_source_id` for the review. The combined build includes the deduplicated reference and observation views. [Manifest](../data/chamber/v1.5/manifest.json) · [Combined build and deduplication rules](chamber-sharepoint-review.md#deduplicated-database)

```sql
SELECT r.ref_no, o.stratum, o.endpoint, o.numerator, o.denominator,
       o.denominator_unit, o.reported_percent, o.outcome_window, o.locator
FROM citation_reference AS r
JOIN citation_observation AS o USING (source_id)
WHERE r.citing_source_id = 'mahon2014' AND r.ref_no = 226
ORDER BY o.endpoint, o.stratum;
```

The 68 aggregate rows include 31 exact numerator–denominator pairs and 37 source-reported percentages. Many reuse the same exposures. A null numerator preserves the published reporting precision. Participant IDs in Table VI are local to the 1996 study, and zero in a marking field means the mark was absent in a completed table cell. Unperformed profiles have null outcomes. The new observations are descriptive and outside the frozen development and external evaluation views.
