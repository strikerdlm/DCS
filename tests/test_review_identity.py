from pathlib import Path

from scripts.review_identity import resolve
from scripts.review_legacy import legacy_records

ROOT = Path(__file__).resolve().parents[1]


def record(
    key,
    title="Incidence of decompression sickness in hypobaric training",
    pmid=None,
    doi=None,
    oa=None,
    year=1986,
    venue=None,
):
    return {
        "record_key": key,
        "stream": "catalog",
        "source_key": key,
        "title": title,
        "pmid": pmid,
        "doi": doi,
        "openalex_id": oa,
        "year": year,
        "url": "https://example.org/shared-access-route",
        "raw": {"venue": venue},
    }


def test_exact_ids_link_across_catalogs_and_keep_reviewed_name():
    rows = [
        record("a", pmid="123", doi="10.1234/ABC"),
        record("b", doi="https://doi.org/10.1234/abc", oa="https://openalex.org/W222"),
        record("c", oa="W222"),
    ]
    aliases = {"c": "reviewed:example"}
    result = resolve(rows, aliases)
    assert result == (dict.fromkeys("abc", "reviewed:example"), [])
    assert resolve(reversed(rows), aliases) == result


def test_clashing_identifier_with_an_unattributable_doi_only_record():
    rows = [
        record("a", pmid="123", doi="10.1234/abc"),
        record("b", pmid="124", doi="10.1234/abc"),
        record("c", doi="10.1234/abc"),
    ]
    mapping, candidates = resolve(rows, {})
    assert len(set(mapping.values())) == 3
    conflicts = {(a, b) for a, b, reason in candidates if "conflicting pmid" in reason}
    assert conflicts == {("a", "b"), ("a", "c"), ("b", "c")}
    assert mapping["c"] != "doi:10.1234/abc"
    assert resolve(reversed(rows), {}) == (mapping, candidates)


def test_near_identical_titles_are_suggestions_even_when_urls_match():
    rows = [
        record("a", pmid="123"),
        record("b", title="Incidence of decompression sickness in hypobaric trainings", year=1996),
        record("c", title="Obscure heading unrelated to any other report"),
    ]
    mapping, candidates = resolve(rows, {})
    assert len(set(mapping.values())) == 3
    assert [(a, b) for a, b, _ in candidates] == [("a", "b")]
    assert "publication years differ" in candidates[0][2]


def test_same_report_title_and_document_url_preserve_both_occurrence_keys():
    rows = [record("first"), record("second")]
    for row in rows:
        row["url"] = "https://example.org/reports/chamber-1986.pdf"
    mapping, candidates = resolve(rows, {})
    assert set(mapping) == {"first", "second"}
    assert mapping["first"] == mapping["second"]
    assert candidates == []


def test_provisional_reviewed_record_cannot_absorb_a_doi_only_occurrence():
    rows = [record("a", doi="10.1234/abc"), record("b", doi="10.1234/abc")]
    mapping, candidates = resolve(rows, {"a": "provisional:possible-commentary"})
    assert mapping["a"] != mapping["b"]
    assert any("provisional" in reason for _, _, reason in candidates)


def test_shared_doi_editorial_different_venues_and_openalex_conflicts():
    baseline = record("a", doi="10.1234/abc", oa="W101", venue="Medicine")
    variants = [
        record("b", doi="10.1234/abc", title="Correction: " + baseline["title"]),
        record("b", doi="10.1234/abc", venue="Journal of Correspondence"),
        record("b", doi="10.1234/abc", oa="W102"),
        record("b", doi="10.1234/abc", title="Unrelated letter concerning a published article"),
    ]
    for variant in variants:
        mapping, candidates = resolve([baseline, variant], {})
        assert mapping["a"] != mapping["b"]
        assert any("shared doi" in reason for _, _, reason in candidates)


def test_legacy_release_links_preserve_distinct_reports_and_intake_strata():
    rows = list(legacy_records(ROOT))
    mapping, _ = resolve(rows, {})
    by_file = {
        (row["stream"].removeprefix("data/chamber/"), row["source_key"]): mapping[row["record_key"]]
        for row in rows
    }
    nasa = by_file["v1.4/sources.csv", "conkin18"]
    assert nasa != by_file["v1.4/sources.csv", "watson68"]
    intake_file = "intake-2026-11-19/outcome_sources.csv"
    assert by_file[intake_file, "jsc18:type_i:dcs"] == nasa
    assert by_file[intake_file, "jsc18:observers:dcs"] == nasa
    assert by_file[intake_file, "crowell83:combined_profiles:dcs"] != nasa
    refs = "v1.5/references.csv"
    assert by_file[refs, "mahon2014:53"] == by_file[refs, "mahon2014:84"]
    assert by_file[refs, "mahon2014:8"] == by_file["v1.5/sources.csv", "bassett_survey"]


def test_recent_source_and_historical_hit_import_preserves_archived_rows():
    rows = list(legacy_records(ROOT))
    assert len(rows) == len({r["record_key"] for r in rows})
    hits = [r for r in rows if r["stream"].endswith("/search_hits.csv")]
    assert len(hits) == 3489
    assert len({r["stream"] for r in hits}) == 34

    assert any(r["stream"].endswith("v1.40/sources.csv") for r in rows)
    by_source = {(r["stream"], r["source_key"]): r for r in rows}
    oa = by_source["data/chamber/v1.7/search_hits.csv", "openalex_fallback:1"]
    assert oa["raw"]["identifier"] == "W2807139063; DOI:10.5772/intechopen.74231"
    assert oa["openalex_id"] == "W2807139063"
    assert oa["doi"] == "10.5772/intechopen.74231"
    assert oa["raw"]["disposition"] == "excluded"
    assert by_source["data/chamber/v1.9/sources.csv", "krutz87"]["pmid"] == "3675514"


def test_recent_crosswalks_and_compound_documents():
    rows = list(legacy_records(ROOT))
    mapping, _ = resolve(rows, {})
    assigned = {
        (r["stream"].removeprefix("data/chamber/"), r["source_key"]): mapping[r["record_key"]]
        for r in rows
    }

    def report(release, source, table="sources.csv"):
        return assigned[release + "/" + table, source]

    assert report("v1.6", "kumar93") == report("v1.7", "kumar93")
    assert report("v1.6", "harding92") != report("v1.6", "baumgartner92")
    assert report("zotero-dcs-2026-11-19", "IWH4E7C6") == report(
        "sharepoint-2026-11-19", "nasa04_exercise"
    )
    assert report("zotero-dcs-2026-11-19", "DJXIVZDZ") == report("sharepoint-2026-11-19", "asma18")
    assert report("v1", "cheok21") != report("zotero-dcs-2026-11-19", "DJXIVZDZ")
    assert report("rojas-2015", "rojas15_attachment") == report("sharepoint-2026-11-19", "rojas15")
    assert report("v1.7", "tavily_general:2", "search_hits.csv") == report("v1.7", "balldin02")
    assert report("v1.7", "public_regional:4", "search_hits.csv") != report("v1.7", "ata21")
    assert report("v1.7", "tex17:6", "search_hits.csv") != report("v1.7", "lapostol24")
    assert report("v1.11", "cadet_tavily_primary:4", "search_hits.csv") != report(
        "v1.11", "motley45"
    )
    assert report("v1.10", "expedition_full_source_verification:5", "search_hits.csv") != report(
        "v1.10", "molenat02_fulltext"
    )
