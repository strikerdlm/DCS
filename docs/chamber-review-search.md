# Search strategy for symptomatic DCS during altitude chamber training

**19 November 2026 · Pilot searches completed. Full identification searches await investigator approval.** The investigator approved protocol development for the within-program comparison of inside staff and trainees. Search the disease and exposure setting together. Review titles and abstracts for the role comparison because either role may appear only in the full text. The proposed search period runs from database inception through the execution date, without language or study-design filters. [Review protocol](chamber-publication-review.md) · [PRISMA-S reporting items](https://www.prisma-statement.org/prisma-search)

## Calibration

Six reports with role-specific primary observations were selected from the earlier inventory. Their susceptibility to discovery was already known. Recovery measures sensitivity to this seed set only. The two Bason reports cover different periods, and Conkin also summarizes previous reports. Each of these features requires adjudication during cohort reconciliation.

| Report | Program and contribution | Verified PMID |
| --- | --- | --- |
| Bason, 1976 | U.S. Navy low-pressure chambers, 1972–1975 | [971183](https://pubmed.ncbi.nlm.nih.gov/971183/) |
| Piwinski et al., 1986 | U.S. Army students and technicians | [3790029](https://pubmed.ncbi.nlm.nih.gov/3790029/) |
| Bason and Yacavone, 1991 | U.S. Navy, 1981–1988 | [1755801](https://pubmed.ncbi.nlm.nih.gov/1755801/) |
| Rice et al., 2003 | U.S. Navy, role and oxygen prebreathe | [12546299](https://pubmed.ncbi.nlm.nih.gov/12546299/) |
| Conkin et al., 2018 | Original NASA JSC cohort within a systematic review | [30352646](https://pubmed.ncbi.nlm.nih.gov/30352646/) |
| Ercan et al., 2020 | Turkish trainees and inside observers | [32574436](https://pubmed.ncbi.nlm.nih.gov/32574436/) |

The count request queried the entire index and returned at most one record or identifier. A separate request intersected the same query with the six seed PMIDs. All three bibliographic APIs exceeded the proposed 80% known-item recovery threshold. Counts are platform-specific and may overlap extensively. No records from these calibration requests entered the formal review's identification or screening counts. [Exact parameters, seeds and responses](../data/chamber/publication-review/search-pilots.json)

| Database and platform | Hits reported on 19 November | Seed recovery | Interpretation |
| --- | ---: | ---: | --- |
| PubMed, NCBI ESearch | 869 | 6/6 | Disease MeSH plus title/abstract terms. Includes PubMed records beyond the MEDLINE subset. |
| Europe PMC, REST search | 718 | 6/6 | Title/abstract search across indexed sources. Restricted to MED and the six IDs only for the recovery test. |
| OpenAlex, Works API | 2,154 | 6/6 | Title, abstract and indexed full text. Count confirmed with the OpenAlex connector. |
| NASA NTRS, citations API | 6 for the disease/setting query and 65 for the setting phrase | Untested | Report searches complement journal indexes. Deduplicate across both queries at formal export. |
| UNAL institutional EBSCO Discovery Service | 2,429 | 2 confirmed, 4 unresolved | The authenticated multidisciplinary search displayed 10 first-page records. Conkin and Ercan were visible in the combined strategy and title probes. Four probes lacked a verified result count or matching title. Individual CINAHL and SPORTDiscus coverage and one default interface filter require verification. [EBSCO pilot record](../data/chamber/publication-review/ebsco-pilot.json) |
| Cochrane Library, Search Manager | Unavailable | Untested | HTTP 403 at the public advanced-search entry point. |
| LILACS via BVS and SciELO Search | Unavailable | Untested | Both public interfaces returned HTTP 403 on initial multilingual trials. |
| FAA technical reports via US DOT ROSA P | Unavailable | Untested | The search form returned HTTP 403. Direct access to the 1977 Valdez report landing page succeeded. |

## Exact candidate strategies

**PubMed**, ESearch `db=pubmed`, final warning-free query. An earlier version with three Spanish phrases in quotation marks still recovered 6/6 but PubMed omitted those phrases from its translation. The final version uses separate fielded words.

```text
("Decompression Sickness"[Mesh] OR "decompression sickness"[tiab] OR "decompression illness"[tiab] OR bends[tiab] OR (enfermedad[tiab] AND (descompresiva[tiab] OR descompresion[tiab]))) AND (hypobar*[tiab] OR altitude[tiab] OR chamber*[tiab] OR hipobar*[tiab] OR (camara[tiab] AND altura[tiab]))
```

**Europe PMC**, REST `query`, final title/abstract query. An initial draft included an unsupported `MESH` field and returned 0/6 seeds. An unfielded trial returned 7,842 hits and 6/6. The final fielded strategy retained seed recovery and reduced retrieval volume. [Europe PMC search fields](https://www.ebi.ac.uk/europepmc/webservices/rest/fields?format=json)

```text
(TITLE_ABS:"decompression sickness" OR TITLE_ABS:"decompression illness" OR TITLE_ABS:bends OR TITLE_ABS:"enfermedad descompresiva" OR TITLE_ABS:"enfermedad por descompresión") AND (TITLE_ABS:hypobar* OR TITLE_ABS:altitude OR TITLE_ABS:chamber* OR TITLE_ABS:hipobár* OR TITLE_ABS:hipobar* OR TITLE_ABS:"cámara de altura")
```

**OpenAlex**, Works API `search`, default search fields.

```text
("decompression sickness" OR "decompression illness" OR "enfermedad descompresiva" OR "enfermedad por descompresión") AND (hypobaric OR altitude OR "low pressure chamber" OR "low-pressure chamber" OR "cámara hipobárica" OR "cámara de altura")
```

**EBSCOhost**, run separately in CINAHL and SPORTDiscus using Boolean/Phrase mode. Proposed title/abstract query for both. Check the local thesaurus for “Decompression Sickness” and equivalent descriptors, and document any accepted expansion before the full search.

```text
(TI ("decompression sickness" OR "decompression illness" OR bends OR "enfermedad descompresiva" OR "enfermedad por descompresión") OR AB ("decompression sickness" OR "decompression illness" OR bends OR "enfermedad descompresiva" OR "enfermedad por descompresión")) AND (TI (hypobar* OR altitude OR chamber* OR hipobar* OR hipobár* OR "cámara de altura") OR AB (hypobar* OR altitude OR chamber* OR hipobar* OR hipobár* OR "cámara de altura"))
```

**Cochrane Library**, proposed Search Manager expression. Record CENTRAL and Cochrane Reviews separately. A review may lead to an eligible primary report, while a controlled-trials register can have limited coverage of surveillance cohorts. [Cochrane interface syntax](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/chapter04-tech-supplonlinepdfv65270924)

```text
("decompression sickness" OR "decompression illness" OR bends OR "enfermedad descompresiva" OR "enfermedad por descompresión"):ti,ab,kw AND (hypobar* OR altitude OR chamber* OR hipobar* OR hipobár* OR "cámara de altura"):ti,ab,kw
```

**LILACS via BVS**, proposed multilingual strategy. **SciELO**, run the second expression in the regional, all-indices search. Include Portuguese terms for Brazilian publications. Record each portal's result counts and actual exports separately.

```text
tw:("decompression sickness" OR "decompression illness" OR "enfermedad descompresiva" OR "enfermedad por descompresión" OR "doença descompressiva" OR "doença de descompressão") AND tw:(hypobaric OR hipobárica OR hipobarica OR altitude OR altitud OR "cámara de altura" OR "câmara de altitude" OR "altitude chamber") AND db:("LILACS")
```

```text
("decompression sickness" OR "decompression illness" OR "enfermedad descompresiva" OR "enfermedad por descompresión" OR "doença descompressiva" OR "doença de descompressão") AND (hypobaric OR hipobárica OR hipobarica OR altitude OR altitud OR "cámara de altura" OR "câmara de altitude" OR "altitude chamber")
```

**NASA NTRS**, citations API `q`, two independent queries. Use paginated export after approval. Check for originals cited by outcome reviews, and distinguish the original report from a later reprint.

```text
"decompression sickness" AND (hypobaric OR altitude OR chamber)
"altitude chamber"
```

**FAA technical reports**, search the US DOT ROSA P catalogue with each phrase in the `terms` field. Inspect agency, authorship and report series at retrieval. Calibrate with Valdez's FAA-AM-77-4 and DOT/FAA/AM-90/12 before exporting. Search terms describing reactions are important for historical reporting. [ROSA P known-item record](https://rosap.ntl.bts.gov/view/dot/55970)

```text
"altitude chamber"
"decompression sickness"
"evolved gas"
```

**Citation searching and updates.** After strategy approval, inspect the reference lists and forward citations of the six seeds and additional eligible reports. Log the citation platform, date, originating report and relationship for each record. Track multiple routes to the same publication, preserve the search version and record changes in scope or access. Advance unresolved reports and translations to reviewer decision. The proposed strategies for databases with restricted access require an interface check before interpreting their yields. [PRISMA 2020 flow diagrams](https://www.prisma-statement.org/prisma-2020-flow-diagram)
