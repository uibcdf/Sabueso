"""What a card knows, and what it knows it does not know (uibcdf/sabueso#56).

``knowledge_state(card)`` gives one row per knowledge area and source:

- ``known``: the source states it (``count`` items, where it applies);
- ``conflicting``: sources disagree about it (``quality.conflicts``);
- ``not_stated``: the source was consulted and states nothing. For example UniProt,
  at its release, has no subcellular location for the entry, or ChEMBL has no
  target;
- ``not_queried``: the enrichment that would answer it was not requested, the source
  does not cover the entity (``basis.detail`` says why, e.g. a human-only source), the
  source needs a personal key that was not given, or,
  for the biological context only curation states (#60), nothing has been curated;
- ``unavailable``: the source failed or its request outcome cannot be evaluated;
- ``partial``: the source stated some of it, but failed, or answered incompletely, for
  some requests (e.g. two structures of many), or its answer was cut at a limit (e.g.
  the first 5000 associations of a gene). ``basis`` names them (``unavailable_for``,
  ``incomplete_for``, ``truncated_for``), so that "known" never hides a gap (#74, rule
  ``@2``; cuts since ``@3``, #88).

These are knowledge states, not Evidence. "Not stated by UniProt at release 120" is a
fact about a source; what the absence means for a project is interpreted in Nextia.
Rule ``knowledge_state@4`` separates counts and request coverage of areas answered
by the same enricher (direct accession mentions versus derived structure context).
Rule ``knowledge_state@5`` counts native molecular record ids and UniChem compounds,
keeps unknown counts unknown, separates molecular identity from clinical intake,
and exposes missing subsets without changing cards or original saved reports.
"""

from __future__ import annotations

from typing import Any, Dict, List

KNOWLEDGE_STATE_RULE = "knowledge_state@5"

#: Protein enrichments: (area, source, which enrichment records answer it).
PROTEIN_ENRICHMENTS = (
    ("relationships.has_structure (entry details)", "RCSB PDB", {"source": "RCSB PDB"}),
    ("relationships.has_bioactivity", "ChEMBL", {"source": "ChEMBL"}),
    ("relationships.has_bioactivity", "BindingDB", {"source": "BindingDB"}),
    (
        "relationships.has_bioactivity",
        "PubChem BioAssay",
        {"source": "PubChem BioAssay"},
    ),
)


def _protein_enrichments():
    """The bespoke enrichments above, then the areas the declared enrichers answer
    (``sabueso.enrichers``, #86): a new enricher appears here without editing."""
    from sabueso.enrichers import knowledge_areas

    return PROTEIN_ENRICHMENTS + tuple(knowledge_areas("protein"))


def _row(area, source, state, release=None, count=None, **basis) -> Dict[str, Any]:
    return {
        "area": area,
        "source": source,
        "release": release,
        "state": state,
        "count": count,
        "basis": {k: v for k, v in basis.items() if v is not None},
    }


def _enrichment_counts(
    area: str, source: str, records: List[Dict[str, Any]], *, _count_field=None
):
    """Reported counts, never a reconstruction of per-request assertion membership."""
    from sabueso.enrichers import count_by_area

    count_key = (
        _count_field
        if _count_field is not None
        else count_by_area().get((area, source), "count")
    )
    counts = []
    for index, record in enumerate(records):
        count, basis, field = None, "request_not_counted", None
        if record.get("status") in ("added", "partial"):
            field = count_key if count_key in record else "count"
            reported = record.get(field)
            if (
                isinstance(reported, (int, float))
                and not isinstance(reported, bool)
                and reported >= 0
                and reported < float("inf")
            ):
                count, basis = reported, "reported_count"
            elif area == "records" and source in ("ChEMBL", "PDB CCD", "PubChem"):
                ids = record.get("records")
                if isinstance(ids, list) and all(isinstance(i, str) and i for i in ids):
                    count, basis, field = len(set(ids)), "native_record_ids", "records"
                else:
                    basis = "count_not_reported"
            elif area == "records" and source == "UniChem":
                compound = record.get("uci")
                if (
                    isinstance(compound, (int, str))
                    and not isinstance(compound, bool)
                    and str(compound)
                ):
                    count, basis, field = 1, "native_compound_id", "uci"
                else:
                    basis = "count_not_reported"
            else:
                basis = "count_not_reported"
        counts.append(
            {"report_index": index, "count": count, "basis": basis, "field": field}
        )
    successful = [
        item
        for item, record in zip(counts, records)
        if record.get("status") in ("added", "partial")
    ]
    total = (
        None
        if any(item["count"] is None for item in successful)
        else sum(item["count"] for item in successful)
    )
    return total, counts


def _enrichment_row(area: str, source: str, records: List[Dict[str, Any]]):
    if not records:
        from sabueso.enrichers import not_queried_details_by_area

        detail = not_queried_details_by_area().get((area, source))
        return _row(area, source, "not_queried", detail=detail)
    if all(r.get("status") in ("not_applicable", "not_queried") for r in records):
        # The source does not cover this entity (e.g. a human-only source and a parasite
        # protein), or needs a key it was not given: nothing was asked, so nothing is
        # "not stated".
        details = sorted({r["detail"] for r in records if r.get("detail")})
        return _row(area, source, "not_queried", detail="; ".join(details) or None)
    statuses = [r.get("status") for r in records]
    count, counts = _enrichment_counts(area, source, records)

    def which(status: str) -> List[str] | None:
        found = [
            str(r.get("structure") or r.get("identifier") or r.get("data") or "")
            for r in records
            if r.get("status") == status
        ]
        return found or None

    releases = sorted({str(r["version"]) for r in records if r.get("version")})
    release = "; ".join(releases) or None
    details = sorted({r["detail"] for r in records if r.get("detail")})
    basis = dict(
        requests=len(records),
        not_found=statuses.count("not_found") or None,
        errors=statuses.count("error") or None,
        detail="; ".join(details) or None,
    )
    unrecognized = [
        i
        for i, status in enumerate(statuses)
        if status
        not in (
            "added",
            "partial",
            "error",
            "not_found",
            "not_queried",
            "not_applicable",
        )
    ]
    if unrecognized:
        basis["unrecognized_outcomes"] = unrecognized
    unknown = [c["report_index"] for c in counts if c["basis"] == "count_not_reported"]
    if unknown:
        basis["count_unknown_for"] = unknown
        basis["reported_count_subtotal"] = sum(c["count"] or 0 for c in counts)
    missing = sorted(
        {str(item) for record in records for item in record.get("missing") or []}
    )
    if missing:
        basis["missing"] = missing
    failed, incomplete = which("error"), which("partial")
    truncated = [
        str(r.get("structure") or r.get("identifier") or r.get("data") or "")
        for r in records
        if r.get("truncated")
    ] or None
    # Missing batch members and declared partial/capped responses remain partial
    # even if the returned subset is empty or its count was not reported.
    if (
        incomplete
        or truncated
        or (
            any(status in ("added", "partial") for status in statuses)
            and (missing or failed or unrecognized)
        )
    ):
        return _row(
            area,
            source,
            "partial",
            release,
            count,
            unavailable_for=failed,
            incomplete_for=incomplete,
            truncated_for=truncated,
            **basis,
        )
    if count is None or count > 0:
        return _row(area, source, "known", release, count, **basis)
    if "error" in statuses or unrecognized:
        # No received subset, and a failed/unrecognized request: not evaluated empty.
        return _row(area, source, "unavailable", release, **basis)
    return _row(area, source, "not_stated", release, 0, **basis)


def _supporting_sources(card: Any, ids: List[str]) -> Dict[str, set]:
    by_source: Dict[str, set] = {}
    for sa_id in ids:
        sa = card.source_assertion_store.get(sa_id) or {}
        source = (sa.get("source") or {}).get("name")
        if source:
            by_source.setdefault(source, set()).add(
                str((sa.get("source") or {}).get("version") or "")
            )
    return by_source


def knowledge_state(card: Any, *, _support: list | None = None) -> Dict[str, Any]:
    """``{"rows": [...], "rule": {...}}``; see the module docstring."""
    from sabueso.mappings.uniprot import STATED_FIELDS, STATED_PREDICATES

    from .relationship_store import make_derivation

    rows: List[Dict[str, Any]] = []

    def emit(row, **inputs):
        rows.append(row)
        if _support is not None:
            _support.append(inputs)

    conflicting = {c.get("field") for c in card.quality.get("conflicts", [])}
    fields = {}
    for path in card.list_fields():
        node = card.get(path)
        if isinstance(node, dict) and "source_assertion_ids" in node:
            fields[path] = node

    # Fields, by the sources that state them.
    for path in sorted(fields):
        sources = _supporting_sources(card, fields[path]["source_assertion_ids"])
        for source, releases in sorted(sources.items()):
            value = fields[path].get("value")
            emit(
                _row(
                    path,
                    source,
                    "conflicting" if path in conflicting else "known",
                    "; ".join(sorted(r for r in releases if r)) or None,
                    len(value) if isinstance(value, list) else None,
                ),
                basis="selected_field",
                field_path=path,
                source_assertion_ids=[
                    identifier
                    for identifier in fields[path]["source_assertion_ids"]
                    if source in _supporting_sources(card, [identifier])
                ],
            )

    is_protein = card.meta.get("entity_type") == "protein"
    uniprot = [
        s
        for s in (
            ((card.quality.get("entity_resolution") or {}).get("decision") or {}).get(
                "sources"
            )
            or []
        )
        if s.get("name") == "UniProt" and s.get("record")
    ]
    if is_protein and (uniprot or "identifiers.uniprot" in fields):
        release = None
        if "identifiers.uniprot" in fields:
            releases = _supporting_sources(
                card, fields["identifiers.uniprot"]["source_assertion_ids"]
            ).get("UniProt", set())
            release = "; ".join(sorted(r for r in releases if r)) or None
        # What UniProt could have stated and did not.
        for path in sorted(STATED_FIELDS - set(fields)):
            emit(
                _row(path, "UniProt", "not_stated", release or None, 0),
                basis="uniprot_field_not_stored",
                field_path=path,
                consultation_sources=uniprot,
                anchor_field="identifiers.uniprot"
                if "identifiers.uniprot" in fields
                else None,
            )
        relationships = card.relationship_store.to_list()
        for predicate in sorted(STATED_PREDICATES):
            count = sum(
                1
                for r in relationships
                if r["predicate"] == predicate
                and "UniProt"
                in _supporting_sources(card, r.get("source_assertion_ids") or [])
            )
            emit(
                _row(
                    f"relationships.{predicate}",
                    "UniProt",
                    "known" if count else "not_stated",
                    release or None,
                    count,
                ),
                basis="uniprot_relationship_count",
                relationship_ids=[
                    r["id"]
                    for r in relationships
                    if r["predicate"] == predicate
                    and "UniProt"
                    in _supporting_sources(card, r.get("source_assertion_ids") or [])
                ],
                consultation_sources=uniprot,
                anchor_field="identifiers.uniprot"
                if "identifiers.uniprot" in fields
                else None,
            )

    if is_protein:
        # Biological context comes only from curated publications (#60). Absent, the
        # literature was not consulted for it: not queried, never "not stated".
        from .curation import CONTEXT_FIELDS

        for path in CONTEXT_FIELDS:
            if path not in fields:
                emit(
                    _row(path, "Literature", "not_queried", None, route="curation"),
                    basis="curation_field_not_stored",
                    field_path=path,
                )

    enrichments = card.quality.get("enrichments") or []
    if is_protein:
        stated = {(r["area"], r["source"]) for r in rows}
        for area, source, match in _protein_enrichments():
            if (area, source) in stated:
                continue  # the field's own row already says what the source states
            records = [
                r for r in enrichments if all(r.get(k) == v for k, v in match.items())
            ]
            emit(
                _enrichment_row(area, source, records),
                basis="enrichment_reports",
                match=match,
                enrichment_indexes=[
                    i
                    for i, r in enumerate(enrichments)
                    if all(r.get(k) == v for k, v in match.items())
                ],
            )
    else:
        by_area: Dict[tuple, list] = {}
        for index, record in enumerate(enrichments):
            source = record.get("source") or "unknown"
            area = "records"
            if card.meta.get("entity_type") == "small_molecule":
                if source == "ChEMBL" and record.get("data") == "indications":
                    area = "relationships.investigated_for"
                elif source == "ClinicalTrials.gov":
                    area = "relationships.tested_in"
            by_area.setdefault((area, source), []).append(index)
        for (area, source), indexes in sorted(by_area.items()):
            match = {"source": source}
            excluded_data = []
            if card.meta.get("entity_type") == "small_molecule" and source == "ChEMBL":
                if area == "relationships.investigated_for":
                    match["data"] = "indications"
                else:
                    excluded_data = ["indications"]
            emit(
                _enrichment_row(area, source, [enrichments[i] for i in indexes]),
                basis="enrichment_reports",
                match=match,
                excluded_data=excluded_data,
                enrichment_indexes=indexes,
            )

    return {
        "rows": rows,
        "rule": make_derivation(
            KNOWLEDGE_STATE_RULE,
            inputs=[
                "sections",
                "relationships",
                "quality.enrichments",
                "quality.conflicts",
            ],
            parameters={
                "states": [
                    "known",
                    "conflicting",
                    "not_stated",
                    "not_queried",
                    "unavailable",
                    "partial",
                ],
                "uniprot_fields": sorted(STATED_FIELDS),
                "uniprot_predicates": sorted(STATED_PREDICATES),
                "enrichment_counts": "reported area count; native molecular record ids or UniChem compound id; unknown is not zero",
                "missing_subsets": "partial for received or declared incomplete requests; native not_found reports retain their missing ids",
                "molecular_clinical_areas": [
                    "relationships.investigated_for",
                    "relationships.tested_in",
                ],
            },
        ),
    }
