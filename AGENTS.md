# Working with the chamber evidence

These rules apply across this repository when acquiring, extracting, reviewing or modeling hypobaric evidence. Both studies use the same versioned evidence inputs. Publish their analysis databases as a matched pair.

## Where to put a finding

| Finding | Version-controlled destination | What to record |
| --- | --- | --- |
| Search or retrieval | `data/chamber/publication-review/retrievals-YYYY-MM-DD-<topic>.json` | Follow an adjacent file. Use a unique run ID and provider record ID. Record the query, date, provider, status, number reported, returned records and access limitations. Keep legitimate repeat retrievals. |
| Verified publication, study or overlap | `data/chamber/publication-review/curation.json` | Reuse the canonical report and study IDs. Record the basis, primary URL and page or table for an alias or relationship. Give distinct reports about one cohort distinct report IDs. |
| Screening or quality assessment | `data/chamber/publication-review/screening.csv` or `quality.json` | Record reviewer, stage, revision, date, decision and the required reason or locator. Preserve prior decisions. A discovery result alone has no screening decision. |
| New public outcome extraction or correction | A new numbered supplement under `data/chamber/v1.N/` | Follow the latest applicable schema. Record source ID, endpoint, stratum, counting unit, numerator, denominator, window, analysis role, locator and overlap. Put a correction in a revision row and retain the original value. |
| New evidence for an older published case | The supplement or existing source extraction, the review retrieval, and `data/chamber/publication-review/case-links.csv` | Reuse the original source, stratum and endpoint. Identify the precise review occurrence and observation. Keep separate fields for onset, presentation, recurrence and follow-up. |
| Generated products | `artifacts/chamber-products/<release>/` | Build both SQLite files and their checksum manifest together. Commit changes to the source records and their manifests. Keep machine-specific paths, private case files and generated databases outside the commit. |

## Before counting a case or cohort

1. Search the review catalog by DOI, PMID, title and technical-report number. Then search the extraction by study, period, source ID, published case number and stratum. A shared person or protocol can occur in several distinct exposures.
2. Decide what the source contributes. A reprint can document an existing result. A follow-up can supply a missing measurement for an existing episode. An independent exposure needs evidence for its identity, timing and outcome. If identity is uncertain, preserve the source and flag the possible overlap. Keep that observation out of pooled and fitted totals pending adjudication.
3. For a case link, check both source locators. A second paper about the identical episode needs an explicit, evidence-backed `same_published_case` report relation. A common site, cohort or date alone is insufficient. Preserve missing values as blank CSV fields or JSON null. Record the source's diagnostic certainty and distinguish observations from reconstructed values.
4. For meta-analysis, identify the primary risk set, role, outcome window, counting unit and overlap before selecting an effect. For the DCS model, apply the existing development and holdout definitions. Case narratives can improve timing and case characterization. Fitting incidence requires a compatible denominator. Store VGE grade, detection method and observation interval separately from clinical DCS.
5. Capture only authorized public or de-identified material in public inputs. Record a citation, identifier, access status and locator for restricted material. Keep identifiable clinical records in the authorized registry.

## Working from two computers

Fetch current branches and inspect open intake PRs before reserving a supplement number. Use one branch per intake batch and a distinct topic in its retrieval filename and run IDs. If two branches selected the same unused number, renumber the later, unmerged supplement and update its paths, loader, tests and manifests together. Keep links to any shared reports and cases. Preserve unrelated local edits.

When adding a numbered release, update its input manifest, the publication-review manifest, the source and search streams in `scripts/review_legacy.py`, and the public loader in `scripts/build_chamber_database.py`. Hash the actual UTF-8, LF-terminated input bytes with SHA-256. Review changes to hashes against the underlying records. Do not refresh hashes to silence an unexplained mismatch.

Run the commands in the [linked database guide](docs/chamber-linked-databases.md). In the PR, report the changes in search occurrences, distinct reports, unique cases, eligible denominators and unresolved overlap. List the exact tests and release ID. Use one merge coordinator for overlapping batches. Both computers can search and extract concurrently. After each merge, sync the source branch and rebuild the pair locally.
