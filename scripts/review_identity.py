"""Resolve report identities while retaining occurrences and reviewable disagreements."""

import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
from itertools import combinations, pairwise
from urllib.parse import unquote, urlsplit

# These source-level crosswalks have matching primary documents in the frozen
# releases. A cohort-overlap annotation on its own never identifies a report.
_BASE = "data/chamber/"
_LIBRARY = "sharepoint-2026-11-19"
_INTAKE = "intake-2026-11-19"
_ATTACHMENTS = "attachments-2026-11-19"
_ZOTERO = "zotero-dcs-2026-11-19"
_LIBRARY_COPIES = {
    "v1": ("gerth18", "rice03", "cheok21"),
    "v1.1": ("ercan20", "piwinski86", "morgagni10", "brandt09", "bason91", "ohrui02"),
    "v1.4": ("pilmanis03",),
    "v1.5": ("webb03_sex", "webb05_susceptibility"),
}
_SOURCE_PAIRS = (
    [((release, key), (_LIBRARY, key)) for release, keys in _LIBRARY_COPIES.items() for key in keys]
    + [
        (("v1", "webb10"), ("v1.5", "webb10_activity")),
        (("v1.3", "sulaiman97"), ("v1.5", "sulaiman97_age")),
        (("v1.4", "webb98"), ("v1.5", "webb98_threshold")),
        (("v1.4", "conkin18"), (_INTAKE, "jsc18")),
        (("v1.3", "nasa03"), (_INTAKE, "conkin03")),
        (("v1.2", "connolly10"), (_INTAKE, "connolly10")),
        (("v1.6", "mcloughlin00"), ("v1.4", "mcloughlin00")),
        (("v1.6", "baumgartner92"), ("v1.4", "baumgartner92")),
        (("v1.6", "connolly23"), (_INTAKE, "connolly23")),
        (("v1.7", "furry73"), ("v1.6", "furry73")),
        (("v1.7", "kumar93"), ("v1.6", "kumar93")),
        (("v1.7", "olaya25"), ("v1.2", "olaya25")),
        (("v1.7", "bason76"), (_INTAKE, "bason76")),
        (("v1.7", "ata21"), (_INTAKE, "ata21")),
        (("v1.10", "molenat02_fulltext"), ("v1.3", "molenat02")),
        (("rojas-2015", "rojas15_attachment"), (_LIBRARY, "rojas15")),
        ((_ATTACHMENTS, "valdez77_attachment"), (_INTAKE, "valdez77")),
        ((_ATTACHMENTS, "smart04_attachment"), ("v1", "smart04")),
        ((_ATTACHMENTS, "brandt09_attachment"), (_LIBRARY, "brandt09")),
    ]
    + [
        (("v1.1", key), (_INTAKE, key))
        for key in ("ercan20", "piwinski86", "bason91", "ohrui02", "nakdimon22", "crowell83")
    ]
)

# Report-level matches verified in the attachment inventories, including
# alternate scans. A digest can cover a whole workshop or meeting issue.
_ZOTERO_COPIES = {
    _ATTACHMENTS: {
        "G8XFMZ92": "brandt09_attachment",
        "3P2KJRNH": "nasa_dcs_evidence_2013",
        "LL4DKYUQ": "webb_u2_2010",
        "KEXLPNKU": "kluis21",
        "MEEXDEYK": "valdez77_attachment",
        "R3ZAU4XC": "smart04_attachment",
    },
    _LIBRARY: {
        "V2DNFVQ3": "nasa04_exercise",
        "IWH4E7C6": "nasa04_exercise",
        "4YSE5Y62": "nasa11_eva",
        "AMD9QU8N": "nasa_treatment",
        "8P5SJNQY": "hancock20",
        "QSIMR77P": "butler02",
        "QDLMRKVG": "robinson99",
        "DJXIVZDZ": "asma18",
        "PJR4Q7HP": "adrac04",
        "N4C7X768": "nasa16_review",
        "8GR6W4CG": "rice03",
        "QHWTAB3X": "ohrui02",
        "FNKSM8YJ": "bason91",
        "RVTDQAEY": "piwinski86",
        "EECSBBYD": "gerth18",
    },
    "v1": {"LQ5EXNSS": "bip24"},
}
_SOURCE_PAIRS.extend(
    ((_ZOTERO, item), (release, source))
    for release, copies in _ZOTERO_COPIES.items()
    for item, source in copies.items()
)


def _hit_matches_source(hit, source):
    """A source_id on an archived hit may describe a lead cited on that page."""
    if source["raw"].get("access") == "metadata":
        return False
    hit_ids, source_ids = _identifier_values(hit), _identifier_values(source)
    if any(hit_ids[k] != source_ids[k] for k in hit_ids.keys() & source_ids.keys()):
        return False
    url = hit.get("url") or ""
    if url and url.rstrip("/") == (source.get("url") or "").rstrip("/"):
        return True
    citation = _text(source["title"])
    title = _text(hit["title"])
    if title == citation:
        return True
    # These release citations begin with the author list followed by the
    # article title. Match the title, not words from the surrounding journal
    # citation. Catalog records can append a subtitle or the repository name.
    parts = source["title"].split(". ")
    if len(parts) > 1:
        article = _text(parts[1].rstrip("."))
        if len(article.split()) >= 4 and (title == article or title.startswith(article + " ")):
            return True
    if hit.get("pmid") and hit["pmid"] == source.get("pmid"):
        return True
    return bool(hit.get("doi") and hit["doi"] == source.get("doi"))


def _legacy_links(rows):
    sources = defaultdict(list)
    links = []
    hits = []
    for key, row in rows.items():
        stream = row["stream"]
        if not stream.startswith(_BASE):
            continue
        raw = row["raw"]
        release, _, file = stream[len(_BASE) :].partition("/")
        if file == "sources.csv" or (release == _INTAKE and file == "outcome_sources.csv"):
            sources[release, raw["source_id"]].append(key)
        elif stream == _BASE + "v1.5/references.csv" and raw.get("source_id"):
            links.append((key, ("v1.5", raw["source_id"])))
        elif file == "search_hits.csv" and raw.get("source_id"):
            hits.append((key, (release, raw["source_id"])))
    yield from sources.values()
    for first, second in _SOURCE_PAIRS:
        if first in sources and second in sources:
            yield sources[first] + sources[second]
    for key, source in links:
        if source in sources:
            yield [key, *sources[source]]
    for key, source in hits:
        # The last two historical releases also retrieved items from a prior
        # source register. The hit keeps its own rank and historical disposition.
        if source == ("v1.11", "smedal48_review"):
            source = ("v1.10", "smedal48_review")
        if source in sources:
            for other in sources[source]:
                if _hit_matches_source(rows[key], rows[other]):
                    yield [key, other]


def _identifier_values(row):
    doi = unquote(str(row.get("doi") or "").strip()).lower()
    doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", doi)
    pmid = re.sub(
        r"^(?:https?://pubmed\.ncbi\.nlm\.nih\.gov/|pmid:\s*)",
        "",
        str(row.get("pmid") or "").strip(),
        flags=re.IGNORECASE,
    ).strip("/")
    oa = str(row.get("openalex_id") or "").strip().rstrip("/").rsplit("/", 1)[-1].upper()
    return {
        name: value
        for name, value, pattern in (
            ("pmid", pmid, r"[1-9][0-9]*"),
            ("doi", doi, r"10\.\d{4,9}/\S+"),
            ("openalex", oa, r"W[1-9][0-9]*"),
        )
        if re.fullmatch(pattern, value)
    }


def _text(value):
    text = unicodedata.normalize("NFKD", str(value or "").casefold())
    return " ".join(
        re.findall(r"[^\W_]+", "".join(c for c in text if not unicodedata.combining(c)))
    )


def _metadata(row):
    raw = row["raw"]
    # Staged rows name a local source alias rather than giving a title.
    title = "" if row["stream"] == _BASE + _INTAKE + "/outcome_sources.csv" else _text(row["title"])
    venue = raw.get("journal") or raw.get("venue") or row.get("venue")
    if isinstance(venue, dict):
        venue = venue.get("name") or venue.get("display_name")
    declared = raw.get("type") or []
    if isinstance(declared, str):
        declared = [declared]
    labels = {_text(v) for v in declared}
    role = None
    # A reply and the letter it answers can share virtually the entire title.
    notice = re.match(
        r"^(retraction|withdrawal|erratum|corrigendum|correction|reply|comment|letter)\b", title
    )
    if notice:
        role = notice[1]
        if re.search(r"\b(reply|response)$", title):
            role = "reply"
    elif labels & {
        "retraction of publication",
        "published erratum",
        "letter",
        "editorial",
        "comment",
    }:
        role = "notice"
    elif title:
        role = "article"
    return (title, str(row.get("year") or ""), _text(venue), role)


def _differences(a, b):
    title_a, year_a, venue_a, role_a = a
    title_b, year_b, venue_b, role_b = b
    if year_a and year_b and year_a != year_b:
        return "publication years differ"
    if venue_a and venue_b and venue_a != venue_b:
        return "venue names differ"
    if role_a and role_b and role_a != role_b:
        return "article or editorial roles differ"
    if title_a and title_b and title_a != title_b:
        tokens_a, tokens_b = set(title_a.split()), set(title_b.split())
        if len(tokens_a & tokens_b) < min(len(tokens_a), len(tokens_b)) * 0.55:
            return "titles differ"
    return None


def resolve(records, aliases):
    """Return record-to-report assignments and occurrence pairs for manual review.

    Aliases are reviewed assignments. Exact identifiers may extend a group only
    when competing identifiers or incompatible metadata do not make a match
    ambiguous. Similar titles nominate candidates but never join two groups.
    """
    rows = {}
    for row in records:
        key = row["record_key"]
        if key in rows:
            raise ValueError(f"Repeated occurrence key {key}")
        rows[key] = row
    unknown = aliases.keys() - rows.keys()
    if unknown:
        raise ValueError(f"Unknown reviewed occurrence keys: {sorted(unknown)}")
    groups = {k: {k} for k in rows}
    owner = {k: k for k in rows}
    checks = set()

    def merge(keys):
        roots = sorted({owner[k] for k in keys})
        if not roots:
            return
        first = roots[0]
        for other in roots[1:]:
            members = groups.pop(other)
            groups[first].update(members)
            for k in members:
                owner[k] = first

    reviewed = defaultdict(list)
    for key, report in aliases.items():
        if not report:
            raise ValueError(f"Empty reviewed report for {key}")
        reviewed[report].append(key)
    for keys in reviewed.values():
        merge(keys)
    for keys in _legacy_links(rows):
        labels = {aliases[k] for i in keys for k in groups[owner[i]] if k in aliases}
        if len(labels) > 1:
            raise ValueError(f"Conflicting reviewed assignments for legacy crosswalk: {keys}")
        merge(keys)

    identifiers = {key: _identifier_values(row) for key, row in rows.items()}
    metadata = {key: _metadata(row) for key, row in rows.items()}
    buckets = defaultdict(set)
    for key, ids in identifiers.items():
        for token in ids.items():
            buckets[token].add(key)
        # Two collectors can retrieve the very same titled resource. Keep both
        # search occurrences. A shared issue PDF or URL alone cannot identify
        # an article, and a search/list page can describe many documents.
        row = rows[key]
        parts = urlsplit(row.get("url") or "")
        title = metadata[key][0]
        if (parts.scheme in {"https", "http"} and parts.hostname and parts.path.strip("/")
                and len(title.split()) >= 4 and not parts.query and not parts.fragment
                and not re.search(r"/(?:search|topicpages|results|browse)(?:/|$)", parts.path, re.I)):
            buckets["titled_url", (parts.netloc.lower(), parts.path.rstrip("/"), title)].add(key)
    # Prefer PMID and OpenAlex to DOI, which a source may repeat on a translation,
    # journal digest, reply, or correction. Check entire groups before merging.
    for kind in ("pmid", "openalex", "doi", "titled_url"):
        for token in sorted(t for t in buckets if t[0] == kind):
            keys = buckets[token]
            roots = sorted({owner[k] for k in keys})
            if len(roots) < 2:
                continue
            reason = None
            members = set().union(*(groups[r] for r in roots))
            pinned = {aliases[k] for k in members if k in aliases}
            if any(label.startswith("provisional:") for label in pinned):
                reason = "provisional identity awaiting adjudication"
            elif len(pinned) > 1:
                reason = "distinct reviewed reports"
            for name in ("pmid", "openalex", "doi"):
                if len({identifiers[k][name] for k in members if name in identifiers[k]}) > 1:
                    reason = reason or f"conflicting {name} identifiers"
            if not reason:
                for left, right in combinations(sorted(members), 2):
                    if owner[left] != owner[right]:
                        reason = _differences(metadata[left], metadata[right])
                        if reason:
                            break
            if reason:
                for a, b in combinations(sorted(keys), 2):
                    if owner[a] != owner[b]:
                        checks.add((a, b, f"shared {kind}; {reason}"))
            else:
                merge(keys)

    owners_by_id = {token: {owner[k] for k in keys} for token, keys in buckets.items()}
    mapping = {}
    for root, members in groups.items():
        reviewed_ids = {aliases[k] for k in members if k in aliases}
        options = sorted(
            (order, name + ":" + value)
            for k in members
            for order, name in enumerate(("pmid", "doi", "openalex"))
            if (value := identifiers[k].get(name))
            and owners_by_id[name, value] == {root}
            and name + ":" + value not in reviewed
        )
        report = next(iter(reviewed_ids), options[0][1] if options else "record:" + root)
        mapping.update(dict.fromkeys(members, report))
    if len(set(mapping.values())) != len(groups):
        raise ValueError(
            "A reviewed report identifier collides with an unrelated fallback identifier"
        )

    # Search candidates sharing word pairs; skip unrelated short labels. Titles
    # may contain an author's name and source citation around the actual title.
    index = defaultdict(set)
    for key in sorted(rows):
        title = metadata[key][0]
        words = title.split()
        if len(words) < 3:
            continue
        pairs = set(pairwise(words))
        potential = set().union(*(index[pair] for pair in pairs))
        for other in sorted(potential):
            other_title = metadata[other][0]
            if mapping[other] == mapping[key]:
                continue
            if title != other_title:
                shorter = min(len(title), len(other_title))
                # Even a perfect substring match cannot reach the cutoff.
                if shorter < 22 or 20 * shorter < 9 * (len(title) + len(other_title)):
                    continue
                matcher = SequenceMatcher(None, title, other_title, autojunk=False)
                if matcher.quick_ratio() < 0.90 or matcher.ratio() < 0.90:
                    continue
            reason = "similar titles; verify report identity"
            difference = _differences(metadata[other], metadata[key])
            if difference:
                reason += f"; {difference}"
            checks.add((other, key, reason))
        for pair in pairs:
            index[pair].add(key)
    return mapping, sorted((a, b, reason) for a, b, reason in checks if mapping[a] != mapping[b])
