# Chamber publication register and review protocol

**19 November 2026 · Investigator approved the role-comparison protocol and development of search strategies.** The register covers human hypobaric decompression literature. The review examines symptomatic decompression sickness (DCS) among staff and trainees in operational altitude chambers. The team had already seen several role-specific results when it formulated the question. Registration is undecided and no registration identifier has been issued. Date amendments and document prior access to results in any registration. [PRISMA-P](https://www.prisma-statement.org/protocols)

## What the existing evidence contributes

The chamber releases document source identity, acquisition details, table and page locators, extraction decisions, and known cohort overlap. The Mahon bibliography includes reference and citing-paper records. Earlier searches also provide leads from technical reports and Spanish-language publications. Their search totals include ranked results beyond the records actually retrieved. A reproducible review needs the retrieved records, their search routes, and a disposition for each report. [Chamber dictionary](chamber-benchmark.md) · [Mahon citation register](chamber-mahon-citations.md) · [Prior search coverage](chamber-literature-supplement.md)

The best initial audit cases are the U.S. Army, U.S. Navy, NASA Johnson Space Center and Turkish programs. Each reports counts by role. In the Conkin paper, the original NASA cohort and the cross-program meta-analysis have distinct uses. The Colombian register reports DCS cases by role, while its training workbook counts activities. Estimating a FAC role-specific risk requires person-exposure denominators for both roles. [U.S. Army and Turkish source extractions](chamber-zotero-supplement.md) · [U.S. Navy data](chamber-benchmark.md) · [NASA original cohort](chamber-cohort-supplement.md) · [FAC reconciliation](chamber-fac-official.md)

Releases 1.6–1.11 also cover historical training, controlled chamber experiments, pressure-suit protocols, expeditions and cadet exposures. Two original reports extend the role evidence beyond the six PMIDs used for search calibration. Furry reported 35 DCS cases in an estimated 60,000 observer exposures and 266 in 252,564 trainee exposures in the U.S. Navy during 1959–1968. Retain the reconstructed observer denominator when assessing precision. Baumgartner’s 1985–1987 USAF table reports 54 cases in 46,261 observer exposures and 228 in 192,623 student exposures. The role denominators leave 459 of the 239,343 total exposures unassigned, and the archive carries an overlap flag. [Original Furry table and extraction notes](2026-11-19_ebsco_altitude-dcs.md) · [USAF adjudications](chamber-discovery-supplement.md)

Releases 1.7–1.11 document 72 earlier search and verification operations with 473 logged results and retrieval attempts. The logs preserve ranks, dispositions, source checks and repeat hits. The six-PDF and Zotero collection reviews also identify byte-identical attachments, alternative PDF copies and repeated cohorts. The Rojas supplement links a second copy of one occupational case-control study whose sampled controls have a different denominator from chamber person-exposures. Retain these links when counting distinct published reports and eligible cohorts. [Technical intake](2026-11-19_ebsco_altitude-dcs.md) · [Historical studies](chamber-historical-supplement.md) · [Pressure and crossover studies](chamber-protocol-supplement.md) · [Expeditions](chamber-expedition-supplement.md) · [Cadets](chamber-cadet-supplement.md) · [Six-PDF intake](chamber-six-pdfs.md) · [Zotero attachment crosswalks](chamber-zotero-dcs.md) · [Rojas report](chamber-rojas-2015.md)

## Publication inventory

The 19 November build contains 1,059 source occurrences. Of these, 993 came from archived inputs and 66 from new bibliographic retrievals. They resolve provisionally to 799 identities, including publications, administrative records and access pages. The identity queue flags 316 distinct pairs of occurrences for adjudication. Formal screening has yet to establish an eligible study count.

The register draws on release source inventories, bibliographies, citing records, staged outcome rows, attachment catalogues, and documented literature searches. Its scope includes FAC administrative workbooks, scientific publications and technical reports. Each occurrence retains its input key and can be traced through to a provisional report identity. Among the six seed cohorts, three cover different U.S. Navy periods. The 1976 Navy report gives 57 DCS cases in 14,959 observer exposures and 22 in 73,561 trainee exposures. The 1991 publication also summarizes earlier surveillance. Each report's own ascertainment period identifies which counts it can contribute. [1976 primary report](https://pubmed.ncbi.nlm.nih.gov/971183/) · [1991 primary report](https://pubmed.ncbi.nlm.nih.gov/1755801/)

### Building and querying the register

Consensus returned 20 ranked records and SciSpace returned 12. The OpenAlex connector returned all eight matches to the targeted role query, ten forward citations of Conkin and colleagues, and the seed record itself. Europe PMC verified 15 specified MED records. The local OpenAlex CLI requested a key; the connector supplied the metadata. The [retrieval snapshots](../data/chamber/publication-review/retrievals-2026-11-19.json) retain the exact queries, source IDs and rank. The [quality log](../data/chamber/publication-review/quality.json) records seven DOI-level Scite checks affected by the account quota, with a provider-reported reset on 27 November 2026. Available Europe PMC and Crossref metadata are recorded separately. Smart Citation context and editorial verification remain pending.

Run `python -m scripts.build_chamber_database --publication-review` from the repository root. This builds `artifacts/chamber-publication-review/observed.sqlite` from versioned inputs with SHA-256 verification. Use `--output PATH` to build a different release alongside an existing database. Each release also contains the public outcome tables and their source locators.

```sql
-- Programs and cohort periods with a primary source identified for protocol development.
SELECT s.label, p.display_title, l.report_id, l.locator
FROM review_study_report AS l
JOIN review_study AS s USING (study_id)
JOIN review_report AS p USING (report_id)
WHERE l.role = 'primary'
ORDER BY s.period;

-- Trace each bibliographic route to the original NASA JSC publication.
SELECT stream, source_key, title, url
FROM review_record
WHERE report_id = 'pmid:30352646'
ORDER BY stream, source_key;

-- Inspect the original role-specific cells used to identify the six seed cohorts.
SELECT study_id, chamber_role, cases, exposures, source_table, source_cell, locator
FROM review_seed_role_cell ORDER BY study_id, chamber_role, source_cell;
```

`review_supplementary_role_cell` gives cases, exposures, locators and denominator notes for Furry, Baumgartner and the Shaw FY2004 outbreak investigated by Brandt. The outbreak report questions two trainee diagnoses. These three periods require eligibility and sensitivity assessment. `review_historical_search_record` traces each archived search hit to its original query, rank and disposition. [Shaw extraction](chamber-six-pdfs.md)

`review_publication_catalog` lists report identities with their indexed identifiers. Each `review_record` links to its input file and retains the source metadata in JSON. New snapshots preserve bibliographic fields and retrieval order. Author abstracts and provider-generated summaries are available through the original services. `review_run_counts` distinguishes the provider's stated total from actual retrievals. `review_report_relation` describes evidence for links such as overlapping study periods or correspondence about a primary report. The reviewed assignments and their supporting URLs are in `review_identity_assignment`. Similar titles and conflicting identifiers are available in `review_identity_candidate` and `review_identifier_disagreement`. For example, Europe PMC indexed two comments about Cheok's paper under one DOI and two distinct PMIDs. [First indexed comment](https://pubmed.ncbi.nlm.nih.gov/34642007/) · [Second indexed comment](https://pubmed.ncbi.nlm.nih.gov/34642008/)

To extend the register, add a dated retrieval snapshot using the existing run and record fields. Preserve provider IDs, returned order, exact parameters, date and coverage limitations. Add verified record-to-report or report-to-study links with evidence in `curation.json`. Record each reviewer's decision as a new revision in `screening.csv`; the full-text stage requires a locator and exclusions require a reason. Update the manifest for the files changed and build to a fresh path. The SQLite output is reproducible from those inputs. Clinical risk-of-bias assessments and adjudicated review inclusion require separately documented reviewer judgments. [Versioned register inputs](../data/chamber/publication-review/) · [Database schema](../data/chamber/publication-review/schema.sql)

## Eligibility for the role comparison

**Among people undergoing operational hypobaric chamber training, how does the risk of symptomatic DCS per person-exposure compare between staff inside the chamber and trainees in the same program?**

| Component | Proposed rule |
| --- | --- |
| Population | Human military or civilian altitude physiology training. Record site, calendar period, eligibility and whether each group experienced routine training. |
| Exposure and comparator | Inside observer, technician, or instructor versus trainee. Verify physical presence in the chamber and retain each program's role definition. |
| Primary outcome | Clinically diagnosed symptomatic DCS during training or the reported post-return follow-up. Record the diagnostic criteria, ascertainment method, endpoint window, and completeness of surveillance for each group. |
| Secondary outcomes | (1) Study-defined neurological or serious DCS. (2) DCS first presenting after return, through a stated window. Each requires its own eligible denominator to estimate absolute risk. |
| Designs and reports | Primary cohort and surveillance records, including original data within a mixed review/report. Seek journal articles, government reports, theses, and conference records from database inception. Retain all languages at identification and arrange translation when needed. Link successive reports about the same population. |
| Quantitative eligibility | For the role comparison require a compatible staff and trainee risk set within the same program and period, with cases and evaluable person-exposures for both groups or an adequately documented equivalent effect estimate. Count a person once per exposure. Retain incomplete denominators for narrative description. |

Decompression illness (DCI) may include arterial gas embolism. Record DCI as defined by the authors and assess eligibility for DCS only when the component is separable. The broader register also retains experimental exposures, flight after diving, Doppler venous gas emboli (VGE), and prediction models for their own questions. Simulations, pressure profiles without observed clinical outcomes, isolated cases and VGE-only records cannot estimate the staff-to-trainee DCS contrast.

## Identification and review decisions

1. **Search design.** Search pressure and setting terms with disease terms. Include *altitude chamber*, *low-pressure chamber*, *hypobaric training*, *decompression sickness*, *bends*, *cámara hipobárica*, *cámara de altura*, *enfermedad descompresiva* and *enfermedad por descompresión*. Use role terms for supplementary searches because many titles omit role. Plan PubMed/MEDLINE, OpenAlex, CINAHL, Cochrane Library, LILACS/SciELO, NASA NTRS and FAA technical repositories, with backward and forward citation searching. Review the translated strings, known-paper recovery, access limitations and coverage before execution. [Cochrane search guidance](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)
2. **Search audit.** Preserve the database, platform, exact query, filters, date, pagination, total hits reported by the service, actual exported identifiers, export file, and updates. Classify seed lookups and exploratory ranked searches separately. Preserve every retrieval route to a report and flag conflicting metadata for adjudication. [PRISMA-S](https://www.prisma-statement.org/prisma-search)
3. **Screening.** Two reviewers should independently assess eligibility and record stage, decision, date and reviewer ID. Retain disagreements and their resolution. At full text, record a source locator and one primary exclusion reason. Track unavailable reports and translation needs as retrieval statuses. For included reports, record correction, withdrawal and retraction checks, source, date and unresolved coverage. A zero citation count leaves editorial status unresolved. [Cochrane study selection](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)
4. **Cohort reconciliation.** Give distinct IDs to search records, reports and underlying studies. Compare site, personnel, dates, protocol, cases and denominators across reports. Record overlap as confirmed, possible or unresolved. Prefer the original table with the clearest matching numerator and denominator. Preserve alternative reported values and the reason for each choice. Count each cohort once per analysis and retain complementary reports. Reconcile PRISMA flow counts from actual retrieval and reviewer events. [PRISMA 2020](https://www.prisma-statement.org/prisma-2020)

## Analysis and appraisal

Estimate the association under each program's actual procedures. Report cases, exposures, risk per 1,000 and the staff-to-trainee risk ratio, with intervals and assumptions. Extract altitude, oxygen prebreathe, activity, repeated attendance, and follow-up by role. Consider a separate contrast restricted to matched protocols when data permit. Workload and prebreathe can be components of the occupational exposure itself.

Record explicitly reported zeros and distinguish missing case counts. Prefer analyses that account for participants making repeated exposures. With aggregate counts, document the clustering information available, show sensitivity to repeated participation where feasible, and label any intervals calculated under independence. If cohorts are sufficiently comparable, consider a study-stratified sparse-event model over the original counts. Evaluate a random role effect only if the data support it. Summarize double-zero cohorts' absolute risks separately. Examine sensitivity to clinical definitions, surveillance windows, unresolved overlap and one-cohort omissions. Sparse or incompatible evidence can support cohort-specific reporting even when a pooled estimate is unstable. [Cochrane guidance on rare events](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-10)

For follow-up studies addressing a causal exposure contrast, specify the target effect and apply ROBINS-E to the individual result. For descriptive surveillance, document denominator validity, selection, ascertainment, missing follow-up and dependencies directly. Have a second reviewer verify source numbers, interpretations and appraisal judgments. Assess certainty per outcome after the eligible evidence set and any synthesis are agreed. [ROBINS-E](https://www.riskofbias.info/welcome/robins-e-tool)

**Search strategy checkpoint.** The dated search development record contains the proposed platform-specific queries, verified seed reports and pilot yields. Investigator approval of these queries precedes the formal identification searches. Registration remains a separate investigator decision. [Search strategy and pilot results](chamber-review-search.md)
