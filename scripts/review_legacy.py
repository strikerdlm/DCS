"""Read the chamber project's original bibliographic occurrences for a review register."""

import csv
import re
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import unquote, urlsplit

SOURCE_REGISTERS = (
    "v1",
    *(f"v1.{i}" for i in range(1, 50)),
    "v1.53",
    "v1.54",
    "v1.55",
    "v1.56",
    "v1.57",
    "v1.58",
    "v1.59",
    "v1.60",
    "v1.61",
    "v1.62",
    "v1.63",
    "v1.64",
    "v1.65",
    "v1.66",
    "v1.67",
    "v1.68",
    "v1.69",
    "v1.70",
    "v1.72",
    "v1.74",
    "v1.75",
    "v1.76",
    "v1.78",
    "v1.79",
    "v1.80",
    "v1.81",
    "v1.82",
    "v1.83",
    "v1.84",
    "v1.85",
    "v1.89",
    "v1.92",
    "v1.93",
    "v1.94",
    "v1.95",
    "v1.96",
    "v1.97",
    "v1.98",
    "v1.99",
    "v1.100",
    "v1.101",
    "v1.102",
    "v1.103",
    "v1.104",
    "v1.105",
    "v1.106",
    "v1.107",
    "v1.108",
    "v1.109",
    "v1.110",
    "v1.111",
    "v1.113",
    "v1.114",
    "v1.115",
    "v1.116",
    "v1.117",
    "v1.118",
    "v1.119",
    "v1.120",
    "v1.121",
    "v1.122",
    "sharepoint-2026-11-19",
    "fac-official",
    "rojas-2015",
    "attachments-2026-11-19",
    "zotero-dcs-2026-11-19",
)
HISTORICAL_SEARCH_RELEASES = tuple(f"v1.{i}" for i in range(7, 43))


def _only(candidates: list[str]) -> str | None:
    """Preserve a disagreement in the raw record without arbitrating it on import."""
    values = {value for value in candidates if value}
    return next(iter(values)) if len(values) == 1 else None


def _record(stream: str, row: dict[str, str], key_fields: tuple[str, ...]) -> dict:
    source_key = ":".join(row[field] for field in key_fields)
    url = row.get("url") or row.get("public_url") or row.get("indexed_oa_url")
    if not url:
        url = row.get("europe_pmc_fulltext_url") or None
    citation = row.get("citation", "")
    identifier = row.get("identifier", "")
    doi_values = [row.get(key, "") for key in ("doi", "crossref_doi", "openalex_doi")]
    doi_values.extend(re.findall(r"(?:^|\bDOI\s*:\s*)(10\.\d{4,9}/\S+)", identifier, re.IGNORECASE))
    doi_values.extend(re.findall(r"\bDOI\s*:?\s*(10\.\d{4,9}/\S+)", citation, re.IGNORECASE))
    pmids = [row.get("pmid", ""), *re.findall(r"\bPMID\s*:?\s*(\d+)\b", citation, re.IGNORECASE)]
    pmids.extend(re.findall(r"\bPMID\s*:?\s*(\d+)\b", identifier, re.IGNORECASE))
    openalex = [row.get("openalex_id", ""), *re.findall(r"\bW[1-9]\d*\b", identifier)]
    # OA copies and secondary-table links can point to a different publication.
    if url and "indexed_oa_url" not in row and row.get("source_level") != "secondary_table":
        parts = urlsplit(url)
        path = unquote(parts.path).strip("/")
        if (
            parts.hostname in {"pubmed.ncbi.nlm.nih.gov", "www.pubmed.ncbi.nlm.nih.gov"}
            and path.isdigit()
        ):
            pmids.append(path)
        if parts.hostname in {"doi.org", "dx.doi.org"} and path.startswith("10."):
            doi_values.append(path)
        if parts.hostname == "openalex.org" and re.fullmatch(r"W[1-9]\d*", path):
            openalex.append(path)
    # In mixed identifier fields a semicolon introduces the next accession.
    doi = _only([v.strip().lower().rstrip(".,;") for v in doi_values])

    # Explicit citation years only. Study periods and numbers in local aliases
    # (e.g. sulaiman97) are not reliable sources for publication year.
    year = row.get("year") or row.get("publication_year")
    if not year:
        years = re.findall(r"\(((?:18|19|20)\d{2})\)", citation or row.get("edition", ""))
        years.extend(re.findall(r", ((?:18|19|20)\d{2})\.?$", row.get("printed_reference", "")))
        years.extend(
            re.findall(r"(?:^|[.,] )((?:18|19|20)\d{2})(?:;\d+|\.(?:$| PMID | DOI ))", citation)
        )
        year = _only(years)

    title = (
        row.get("title")
        or row.get("matched_title")
        or row.get("printed_reference")
        or citation
        or row.get("filename")
        or row["source_id"]
    )
    return {
        "record_key": f"legacy:{stream}#{source_key}",
        "stream": stream,
        "source_key": source_key,
        "title": title,
        "doi": doi,
        "pmid": _only(pmids),
        "openalex_id": _only(openalex),
        "year": int(year) if year else None,
        "url": url,
        "raw": row,
    }


def legacy_records(root: Path) -> Iterator[dict]:
    """Yield each original occurrence, including repeated sources and intake strata.

    root is the DCS checkout. stream and source_key identify the input file and
    its row independently of ordering. The original strings, including blanks,
    edition, locators and historical screening decisions, remain in raw.
    """
    inputs = [(f"{release}/sources.csv", ("source_id",)) for release in SOURCE_REGISTERS]
    inputs.extend(
        (f"{release}/search_hits.csv", ("search_id", "rank"))
        for release in HISTORICAL_SEARCH_RELEASES
    )
    inputs.extend(
        (
            ("v1.5/references.csv", ("citing_source_id", "ref_no")),
            ("v1.5/citers.csv", ("cited_source_id", "openalex_id")),
            ("intake-2026-11-19/outcome_sources.csv", ("source_id", "group", "endpoint")),
        )
    )
    for filename, key_fields in inputs:
        relative = Path("data/chamber") / filename
        stream = relative.as_posix()
        seen = set()
        with (root / relative).open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if not all(row.get(key) for key in key_fields):
                    raise ValueError(f"Incomplete source key in {stream}: {key_fields}")
                record = _record(stream, row, key_fields)
                if record["source_key"] in seen:
                    raise ValueError(f"Duplicate occurrence key: {record['record_key']}")
                seen.add(record["source_key"])
                yield record
