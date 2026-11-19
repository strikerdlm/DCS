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
