"""Frozen v1 expected-record predicates for saved-science consistency checks.

Baseline: Sabueso 2c32d7f, named rules in the constants below. These private
predicates compare retained decisions at their original inputs; they never replace
saved knowledge, call ordinary scientific readers or consult current catalogs.
Evolving semantics requires a new historical verifier/version, not editing v1.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

from .card_exploration_history import _rule

KNOWLEDGE_STATE_RULE = "knowledge_state@5"

RULE = "knowledge_state_explanation@2"

STATED_FIELDS = frozenset(
    {
        "annotations.activity_regulation",
        "annotations.alternative_products",
        "annotations.catalytic_activity",
        "annotations.disease",
        "annotations.domain_notes",
        "annotations.function",
        "annotations.isoforms",
        "annotations.lineage",
        "annotations.miscellaneous",
        "annotations.organism",
        "annotations.pathway",
        "annotations.polymorphism",
        "annotations.ptm",
        "annotations.similarity",
        "annotations.source_cautions",
        "annotations.subcellular_location",
        "annotations.subunit",
        "annotations.taxon_id",
        "annotations.tissue_specificity",
        "features_positional.active_site",
        "features_positional.alternative_sequence",
        "features_positional.binding_site",
        "features_positional.chain",
        "features_positional.disulfide_bond",
        "features_positional.domains",
        "features_positional.glycosylation",
        "features_positional.lipidation",
        "features_positional.modified_residue",
        "features_positional.motif",
        "features_positional.mutagenesis",
        "features_positional.natural_variant",
        "features_positional.region",
        "features_positional.secondary_structure",
        "features_positional.sequence_conflict",
        "features_positional.topological_domain",
        "features_positional.transmembrane",
        "identifiers.ensembl_transcripts",
        "identifiers.gene_loci",
        "identifiers.uniprot",
        "names.abbreviations",
        "names.canonical_name",
        "names.gene_names",
        "names.synonyms",
        "sequence.checksums",
        "sequence.length",
        "sequence.molecular_weight",
        "sequence.primary",
    }
)

STATED_PREDICATES = frozenset(
    {
        "annotated_with",
        "classified_in",
        "described_in",
        "has_structure",
        "interacts_with",
    }
)

CONTEXT_FIELDS = (
    "annotations.stage_expression",
    "annotations.essentiality",
    "annotations.accessibility",
    "annotations.metabolic_role",
)

_ENRICHMENTS = (
    ("relationships.has_structure (entry details)", "RCSB PDB", {"source": "RCSB PDB"}),
    ("relationships.has_bioactivity", "ChEMBL", {"source": "ChEMBL"}),
    ("relationships.has_bioactivity", "BindingDB", {"source": "BindingDB"}),
    (
        "relationships.has_bioactivity",
        "PubChem BioAssay",
        {"source": "PubChem BioAssay"},
    ),
    ("relationships.functionally_associated_with", "STRING", {"source": "STRING"}),
    (
        "relationships.has_ligand_site",
        "PDBe-KB",
        {"data": "ligand_sites", "source": "PDBe-KB"},
    ),
    (
        "relationships.has_interface_with",
        "PDBe-KB",
        {"data": "interface_residues", "source": "PDBe-KB"},
    ),
    (
        "relationships.has_predicted_structure",
        "AlphaFold DB",
        {"source": "AlphaFold DB"},
    ),
    ("annotations.taxonomy", "NCBI Taxonomy", {"source": "NCBI Taxonomy"}),
    ("features_positional.family_site", "InterPro", {"source": "InterPro"}),
    ("annotations.pathogen_phenotypes", "PHI-base", {"source": "PHI-base"}),
    ("relationships.associated_with", "DISEASES", {"source": "DISEASES"}),
    ("relationships.associated_with", "Open Targets", {"source": "Open Targets"}),
    ("relationships.associated_with", "Orphanet", {"source": "Orphanet"}),
    ("relationships.participates_in", "Reactome", {"source": "Reactome"}),
    ("annotations.population_variants", "gnomAD", {"data": None, "source": "gnomAD"}),
    (
        "annotations.exon_usage_by_tissue",
        "gnomAD",
        {"data": "pext", "source": "gnomAD"},
    ),
    (
        "annotations.isoform_coding_exons",
        "gnomAD",
        {"data": "pext", "source": "gnomAD"},
    ),
    ("annotations.tissue_terms", "GTEx", {"source": "GTEx"}),
    ("annotations.clinical_variants", "ClinVar", {"source": "ClinVar"}),
    ("annotations.interface_mutations", "SKEMPI", {"source": "SKEMPI"}),
    ("annotations.antibody_complexes", "SAbDab", {"source": "SAbDab"}),
    ("relationships.ortholog_of", "OMA", {"source": "OMA"}),
    ("identifiers.uniref", "UniProt", {"data": "uniref", "source": "UniProt"}),
    (
        "relationships.clustered_with",
        "UniProt",
        {"data": "uniref", "source": "UniProt"},
    ),
    ("annotations.kinase_classification", "KLIFS", {"source": "KLIFS"}),
    ("annotations.kinase_structures", "KLIFS", {"source": "KLIFS"}),
    ("annotations.kinase_pocket", "KLIFS", {"source": "KLIFS"}),
    ("annotations.gpcr_classification", "GPCRdb", {"source": "GPCRdb"}),
    ("annotations.gpcr_segments", "GPCRdb", {"source": "GPCRdb"}),
    ("annotations.gpcr_residues", "GPCRdb", {"source": "GPCRdb"}),
    ("annotations.gpcr_structures", "GPCRdb", {"source": "GPCRdb"}),
    ("relationships.mentioned_in", "Europe PMC", {"source": "Europe PMC"}),
    (
        "relationships.structure_mentioned_in",
        "Europe PMC",
        {
            "data": "located_accession_annotations",
            "mapping": "located_accession_mapping@2",
            "source": "Europe PMC",
        },
    ),
    ("relationships.same_as (MedGen)", "MedGen", {"source": "MedGen"}),
    ("relationships.same_as (MONDO)", "MONDO", {"source": "MONDO"}),
    ("relationships.subclass_of (MONDO)", "MONDO", {"source": "MONDO"}),
)

_COUNTS = {
    ("relationships.mentioned_in", "Europe PMC"): "uniprot_mention_count",
    ("relationships.structure_mentioned_in", "Europe PMC"): "structure_mention_count",
}

_DETAILS = {
    ("relationships.structure_mentioned_in", "Europe PMC"): "Located PDB mention "
    "context requires "
    "explicit "
    "article_ids; "
    "bibliographic search "
    "does not query "
    "article annotations."
}


def _v1_protein_enrichments():
    return deepcopy(_ENRICHMENTS)


def _count_by_area():
    return _COUNTS


def _not_queried_details_by_area():
    return _DETAILS


def _v1_row(area, source, state, release=None, count=None, **basis) -> Dict[str, Any]:
    return {
        "area": area,
        "source": source,
        "release": release,
        "state": state,
        "count": count,
        "basis": {k: v for k, v in basis.items() if v is not None},
    }


def _v1_enrichment_counts(area: str, source: str, records: List[Dict[str, Any]]):
    """Reported counts, never a reconstruction of per-request assertion membership."""
    count_key = _count_by_area().get((area, source), "count")
    counts = []
    for index, record in enumerate(records):
        count, basis, field = (None, "request_not_counted", None)
        if record.get("status") in ("added", "partial"):
            field = count_key if count_key in record else "count"
            reported = record.get(field)
            if (
                isinstance(reported, (int, float))
                and (not isinstance(reported, bool))
                and (reported >= 0)
                and (reported < float("inf"))
            ):
                count, basis = (reported, "reported_count")
            elif area == "records" and source in ("ChEMBL", "PDB CCD", "PubChem"):
                ids = record.get("records")
                if isinstance(ids, list) and all(
                    (isinstance(i, str) and i for i in ids)
                ):
                    count, basis, field = (
                        len(set(ids)),
                        "native_record_ids",
                        "records",
                    )
                else:
                    basis = "count_not_reported"
            elif area == "records" and source == "UniChem":
                compound = record.get("uci")
                if (
                    isinstance(compound, (int, str))
                    and (not isinstance(compound, bool))
                    and str(compound)
                ):
                    count, basis, field = (1, "native_compound_id", "uci")
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
        if any((item["count"] is None for item in successful))
        else sum((item["count"] for item in successful))
    )
    return (total, counts)


def _v1_enrichment_row(area: str, source: str, records: List[Dict[str, Any]]):
    if not records:
        detail = _not_queried_details_by_area().get((area, source))
        return _v1_row(area, source, "not_queried", detail=detail)
    if all((r.get("status") in ("not_applicable", "not_queried") for r in records)):
        details = sorted({r["detail"] for r in records if r.get("detail")})
        return _v1_row(area, source, "not_queried", detail="; ".join(details) or None)
    statuses = [r.get("status") for r in records]
    count, counts = _v1_enrichment_counts(area, source, records)

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
        basis["reported_count_subtotal"] = sum((c["count"] or 0 for c in counts))
    missing = sorted(
        {str(item) for record in records for item in record.get("missing") or []}
    )
    if missing:
        basis["missing"] = missing
    failed, incomplete = (which("error"), which("partial"))
    truncated = [
        str(r.get("structure") or r.get("identifier") or r.get("data") or "")
        for r in records
        if r.get("truncated")
    ] or None
    if (
        incomplete
        or truncated
        or (
            any((status in ("added", "partial") for status in statuses))
            and (missing or failed or unrecognized)
        )
    ):
        return _v1_row(
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
        return _v1_row(area, source, "known", release, count, **basis)
    if "error" in statuses or unrecognized:
        return _v1_row(area, source, "unavailable", release, **basis)
    return _v1_row(area, source, "not_stated", release, 0, **basis)


def _v1_supporting_sources(card: Any, ids: List[str]) -> Dict[str, set]:
    by_source: Dict[str, set] = {}
    for sa_id in ids:
        sa = card.source_assertion_store.get(sa_id) or {}
        source = (sa.get("source") or {}).get("name")
        if source:
            by_source.setdefault(source, set()).add(
                str((sa.get("source") or {}).get("version") or "")
            )
    return by_source


def _v1_knowledge_state(card: Any, *, _support: list | None = None) -> Dict[str, Any]:
    """``{"rows": [...], "rule": {...}}``; see the module docstring."""
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
    for path in sorted(fields):
        sources = _v1_supporting_sources(card, fields[path]["source_assertion_ids"])
        for source, releases in sorted(sources.items()):
            value = fields[path].get("value")
            emit(
                _v1_row(
                    path,
                    source,
                    "conflicting" if path in conflicting else "known",
                    "; ".join(sorted((r for r in releases if r))) or None,
                    len(value) if isinstance(value, list) else None,
                ),
                basis="selected_field",
                field_path=path,
                source_assertion_ids=[
                    identifier
                    for identifier in fields[path]["source_assertion_ids"]
                    if source in _v1_supporting_sources(card, [identifier])
                ],
            )
    is_protein = card.meta.get("entity_type") == "protein"
    uniprot = [
        s
        for s in (
            (card.quality.get("entity_resolution") or {}).get("decision") or {}
        ).get("sources")
        or []
        if s.get("name") == "UniProt" and s.get("record")
    ]
    if is_protein and (uniprot or "identifiers.uniprot" in fields):
        release = None
        if "identifiers.uniprot" in fields:
            releases = _v1_supporting_sources(
                card, fields["identifiers.uniprot"]["source_assertion_ids"]
            ).get("UniProt", set())
            release = "; ".join(sorted((r for r in releases if r))) or None
        for path in sorted(STATED_FIELDS - set(fields)):
            emit(
                _v1_row(path, "UniProt", "not_stated", release or None, 0),
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
                (
                    1
                    for r in relationships
                    if r["predicate"] == predicate
                    and "UniProt"
                    in _v1_supporting_sources(card, r.get("source_assertion_ids") or [])
                )
            )
            emit(
                _v1_row(
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
                    in _v1_supporting_sources(card, r.get("source_assertion_ids") or [])
                ],
                consultation_sources=uniprot,
                anchor_field="identifiers.uniprot"
                if "identifiers.uniprot" in fields
                else None,
            )
    if is_protein:
        for path in CONTEXT_FIELDS:
            if path not in fields:
                emit(
                    _v1_row(path, "Literature", "not_queried", None, route="curation"),
                    basis="curation_field_not_stored",
                    field_path=path,
                )
    enrichments = card.quality.get("enrichments") or []
    if is_protein:
        stated = {(r["area"], r["source"]) for r in rows}
        for area, source, match in _v1_protein_enrichments():
            if (area, source) in stated:
                continue
            records = [
                r for r in enrichments if all((r.get(k) == v for k, v in match.items()))
            ]
            emit(
                _v1_enrichment_row(area, source, records),
                basis="enrichment_reports",
                match=match,
                enrichment_indexes=[
                    i
                    for i, r in enumerate(enrichments)
                    if all((r.get(k) == v for k, v in match.items()))
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
                _v1_enrichment_row(area, source, [enrichments[i] for i in indexes]),
                basis="enrichment_reports",
                match=match,
                excluded_data=excluded_data,
                enrichment_indexes=indexes,
            )
    return {
        "rows": rows,
        "rule": _rule(
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


def _v1_explain_knowledge_state(card, knowledge_area=None, knowledge_source=None):
    pin = card.pinned_ref()
    inputs = []
    view = _v1_knowledge_state(card, _support=inputs)
    gaps = []

    def assertion_ids(groups):
        for group in groups:
            if isinstance(group, str):
                yield group
            else:
                yield from assertion_ids(group)

    def assertions(ids):
        rows = [
            {**a, "source_assertion_ref": f"{pin}#{a['id']}"}
            for a in card.explain(sorted(set(ids)), skip_digestion=True)
        ]
        for a in rows:
            if not a["found"]:
                gaps.append(
                    {
                        "reason": "missing_source_assertion",
                        "source_assertion_ref": a["source_assertion_ref"],
                    }
                )
        return rows

    def field(path):
        node = card.get(path)
        if node is None:
            return {"field_path": path, "stored": False}
        ids = node.get("source_assertion_ids") or []
        if not ids:
            gaps.append({"reason": "no_selected_source_assertion", "field_path": path})
        conflicts = [
            c for c in card.quality.get("conflicts") or [] if c.get("field") == path
        ]
        selection_alternatives = [
            c for c in card.quality.get("alternatives") or [] if c.get("field") == path
        ]
        return {
            "field_path": path,
            "stored": True,
            "node": node,
            "source_assertions": assertions(ids),
            "alternatives": assertions(
                [
                    a["id"]
                    for a in card.source_assertion_store.to_list()
                    if a.get("field_path") == path and a["id"] not in ids
                ]
            ),
            "conflicts": conflicts,
            "selection_alternatives": selection_alternatives,
            "context_source_assertions": assertions(
                list(
                    assertion_ids(
                        [
                            c.get("source_assertion_ids") or []
                            for c in conflicts + selection_alternatives
                        ]
                    )
                )
            ),
            "selection_rules": card.selection_rules,
        }

    def relationship(rel):
        ids = rel.get("source_assertion_ids") or []
        if not ids and (not rel.get("derivation")):
            gaps.append(
                {
                    "reason": "no_relationship_support",
                    "relationship_ref": f"{pin}#{rel['id']}",
                }
            )
        return {
            "relationship_ref": f"{pin}#{rel['id']}",
            "relationship": rel,
            "source_assertions": assertions(ids),
        }

    def source_context(row):
        area, source = (row["area"], row["source"])
        predicate = area.split(" ", 1)[0].removeprefix("relationships.")
        related = [
            r
            for r in card.relationships()
            if (
                area == "records"
                or (area.startswith("relationships.") and r["predicate"] == predicate)
            )
            and (
                source
                in _v1_supporting_sources(card, r.get("source_assertion_ids") or [])
                or (r.get("qualifiers") or {}).get("source") == source
            )
        ]
        fields = [
            field(path)
            for path in card.list_fields()
            if (area == "records" or path == area)
            and isinstance(card.get(path), dict)
            and (
                source
                in _v1_supporting_sources(
                    card, (card.get(path) or {}).get("source_assertion_ids") or []
                )
            )
        ]
        return {
            "basis": "same_source_and_area_context",
            "request_membership": "not_recorded",
            "fields": fields,
            "relationships": [
                relationship(r) for r in sorted(related, key=lambda r: r["id"])
            ],
        }

    rows = []
    for row, basis in zip(view["rows"], inputs):
        if knowledge_area is not None and row["area"] != knowledge_area:
            continue
        if knowledge_source is not None and row["source"] != knowledge_source:
            continue
        support = {"row": row, "classification_inputs": basis}
        kind = basis["basis"]
        if kind == "selected_field":
            support["field"] = field(basis["field_path"])
            support["source_assertions"] = assertions(basis["source_assertion_ids"])
        if kind in {"uniprot_field_not_stored", "uniprot_relationship_count"}:
            support["consultation"] = {
                "basis": "stored_resolution_or_uniprot_identifier",
                "sources": basis["consultation_sources"],
                "anchor": field(basis["anchor_field"])
                if basis["anchor_field"]
                else None,
                "absence_basis": "declared_source_coverage_and_stored_card",
                "negative_source_assertion": False,
            }
        if kind == "uniprot_relationship_count":
            support["relationships"] = [
                relationship(card.relationship_store.get(identifier))
                for identifier in sorted(basis["relationship_ids"])
            ]
        if kind == "enrichment_reports":
            key = (row["area"], row["source"])
            _, counts = _v1_enrichment_counts(
                *key,
                [card.quality["enrichments"][i] for i in basis["enrichment_indexes"]],
            )
            support["classification_inputs"] = {
                **basis,
                "count_field": _count_by_area().get(key, "count"),
                "count_fallback": "count",
                "count_inputs": [
                    {
                        **item,
                        "enrichment_index": basis["enrichment_indexes"][
                            item["report_index"]
                        ],
                    }
                    for item in counts
                ],
                "not_queried_detail": _not_queried_details_by_area().get(key),
                "reports": [
                    {
                        "locator": {
                            "card_ref": pin,
                            "field_path": "quality.enrichments",
                            "index": i,
                        },
                        "record": card.quality["enrichments"][i],
                    }
                    for i in basis["enrichment_indexes"]
                ],
            }
            support["stored_knowledge_context"] = source_context(row)
        rows.append(support)
    unclassified = []
    represented = {
        r["classification_inputs"]["field_path"]
        for r in rows
        if r["classification_inputs"]["basis"] == "selected_field"
    }
    for path in card.list_fields():
        node = card.get(path) or {}
        if (
            not isinstance(node, dict)
            or "source_assertion_ids" not in node
            or path in represented
        ):
            continue
        if knowledge_area not in (None, "records", path):
            continue
        ids = node.get("source_assertion_ids") or []
        if ids and all((_v1_supporting_sources(card, [i]) for i in ids)):
            continue
        gaps.append({"reason": "unidentified_selected_source", "field_path": path})
        unclassified.append(
            {
                "basis": "source_not_identifiable_from_selected_support",
                "field": field(path),
            }
        )
    unclassified_relationships = []
    for rel in card.relationships():
        area = f"relationships.{rel['predicate']}"
        if (
            knowledge_area not in (None, "records")
            and knowledge_area.split(" ", 1)[0] != area
        ):
            continue
        ids = rel.get("source_assertion_ids") or []
        if any((card.source_assertion_store.get(i) is None for i in ids)) or (
            not ids and (not rel.get("derivation"))
        ):
            unclassified_relationships.append(
                {
                    "basis": "incomplete_stored_relationship_support",
                    "relationship": relationship(rel),
                }
            )
    gaps = list({str(g): g for g in gaps}.values())
    return deepcopy(
        {
            "rule": _rule(
                RULE,
                inputs=[pin],
                parameters={
                    "knowledge_area": knowledge_area,
                    "knowledge_source": knowledge_source,
                },
            ),
            "card_ref": pin,
            "state_rule": view["rule"],
            "rows": rows,
            "status": "partial" if gaps else "on_card" if rows else "not_on_card",
            "reason": "incomplete_stored_support"
            if gaps
            else None
            if rows
            else "no_matching_state_row",
            "unclassified_fields": unclassified,
            "unclassified_relationships": unclassified_relationships,
            "support_basis": "stored_classification_inputs_and_separate_knowledge_context",
            "gaps": gaps,
        }
    )
