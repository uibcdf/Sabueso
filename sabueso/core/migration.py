"""Migrating stored cards to the current schema, honestly (uibcdf/sabueso#51).

A migration does not have to be complete, but it must say what it did not do:

- ``migrate_card(data)`` converts a stored card, step by step, to the current card
  schema. Every step appends a record to ``quality.migration``: from which version to
  which, the rule, what was converted, and the **gaps**. A gap is what a card of the
  new schema can hold but the old card cannot, because its sources were not asked for
  it then:

  - ``missing``: a fresh build with the same options would have it, e.g. UniProt's
    taxon and lineage since 0.3.2;
  - ``available``: an enrichment that did not exist when the card was built, and can be
    asked for, e.g. NCBI Taxonomy since 0.3.4.

- The original is never changed. The record keeps its snapshot id, and ``store=``
  saves the original, when it is readable, and then the migrated card, as two
  revisions of one card.
- ``refresh_card(card)`` completes the gaps by building the card again from its
  sources, with the options its enrichments record. Curations are re-applied when a
  ``CurationStore`` is given, and keep their ids. A refresh record says which gaps were
  completed and which the sources still do not state.

Within one schema line, a step only re-labels the version: additions are optional. A
step between lines (``0.3`` → ``0.4``) is a function registered in ``STEPS``. None
exists yet, and loading a card of another line is refused, with a pointer here.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Tuple

from .errors import StorageError
from .schema_version import parse, same_line
from .source_acquisition import capture_acquisitions

MIGRATION_RULE = "card_migration@1"

#: What each schema version added, and how a card gets it (``filled_by``):
#: ``refresh`` (a fresh build with the same options states it), ``<option>`` (an
#: enrichment to ask for), or ``curation``. Paths are field paths or relationship
#: templates. ``entity_types``, when given, limits a change to the cards it applies to
#: (a molecule has no pathogen phenotypes, a protein no indications).
SCHEMA_CHANGES: Dict[str, List[Dict[str, str]]] = {
    "0.3.14": [
        {
            "path": "relationships.has_structure.derivation",
            "filled_by": "structures",
            "entity_types": ("protein",),
        },
        {
            "path": "source_assertion_store[].source_metadata.coordinate_scope",
            "filled_by": "gnomad",
            "entity_types": ("protein",),
        },
        {
            "path": "quality.enrichments[].request_options",
            "filled_by": "refresh",
            "explicit_only": True,
        },
        {
            "path": "quality.migration[].request_restoration",
            "filled_by": "refresh",
            "explicit_only": True,
        },
    ],
    "0.3.13": [
        {
            "path": "annotations.activity_regulation",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "annotations.domain_notes",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "annotations.similarity",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "annotations.source_cautions",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "annotations.miscellaneous",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "features_positional.domains",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "features_positional.chain",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "features_positional.lipidation",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "features_positional.motif",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "features_positional.region",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "features_positional.sequence_conflict",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "features_positional.topological_domain",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "features_positional.transmembrane",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
    ],
    "0.3.1": [{"path": "annotations.disease", "filled_by": "refresh"}],
    "0.3.2": [
        {"path": "annotations.taxon_id", "filled_by": "refresh"},
        {"path": "annotations.lineage", "filled_by": "refresh"},
        {"path": "identifiers.gene_loci", "filled_by": "refresh"},
        {
            "path": "relationships.classified_in (orthodb, eggnog)",
            "filled_by": "refresh",
        },
        {
            "path": "relationships.has_predicted_structure",
            "filled_by": "predicted_structures",
        },
        {
            "path": "relationships.has_bioactivity.measurement.normalized_upper",
            "filled_by": "refresh",
        },
        {"path": "relationships.engages", "filled_by": "curation"},
    ],
    "0.3.3": [
        {
            "path": "relationships.has_predicted_structure.isoform",
            "filled_by": "predicted_structures",
        },
    ],
    "0.3.4": [
        {"path": "annotations.taxonomy", "filled_by": "taxonomy"},
        {"path": "relationships.has_bioactivity (BindingDB)", "filled_by": "bindingdb"},
        {
            "path": "relationships.has_bioactivity (PubChem BioAssay)",
            "filled_by": "pubchem_bioassay",
        },
        {"path": "literature.claims", "filled_by": "curation"},
        {"path": "names.synonyms", "filled_by": "refresh"},
        {"path": "names.abbreviations", "filled_by": "refresh"},
        {"path": "names.gene_names", "filled_by": "refresh"},
        {
            "path": "relationships.has_structure.construct",
            "filled_by": "structures",
            "qualifier": True,
        },
    ],
    "0.3.5": [
        {
            "path": "relationships.has_structure.author_numbering",
            "filled_by": "structures",
            "qualifier": True,
        },
    ],
    "0.3.6": [
        {"path": "annotations.isoforms", "filled_by": "refresh"},
        {"path": "annotations.alternative_products", "filled_by": "refresh"},
        {"path": "features_positional.alternative_sequence", "filled_by": "refresh"},
        {"path": "features_positional.secondary_structure", "filled_by": "refresh"},
        {
            "path": "features_positional.natural_variant.substitution.missing",
            "filled_by": "refresh",
        },
        {
            "path": "features_positional.mutagenesis.substitution.missing",
            "filled_by": "refresh",
        },
        {
            "path": "relationships.has_structure.secondary_structure",
            "filled_by": "structures",
            "qualifier": True,
        },
        {"path": "annotations.stage_expression", "filled_by": "curation"},
        {"path": "annotations.essentiality", "filled_by": "curation"},
        {"path": "annotations.accessibility", "filled_by": "curation"},
        {"path": "annotations.metabolic_role", "filled_by": "curation"},
        {
            "path": "annotations.pathogen_phenotypes",
            "filled_by": "phi_base",
            "entity_types": ("protein",),
        },
        {
            "path": "relationships.investigated_for",
            "filled_by": "indications",
            "entity_types": ("small_molecule",),
        },
        {
            "path": "relationships.tested_in",
            "filled_by": "trials",
            "entity_types": ("small_molecule",),
        },
        {
            "path": "relationships.associated_with",
            "filled_by": "diseases",
            "entity_types": ("protein",),
        },
        {
            "path": "relationships.participates_in",
            "filled_by": "reactome",
            "entity_types": ("protein",),
        },
        {
            "path": "annotations.clinical_variants",
            "filled_by": "clinvar",
            "entity_types": ("protein",),
        },
        {
            "path": "annotations.population_variants",
            "filled_by": "gnomad",
            "entity_types": ("protein",),
        },
    ],
    "0.3.7": [
        {
            "path": "annotations.interface_mutations",
            "filled_by": "skempi",
            "entity_types": ("protein",),
        },
        # Disease cards are new in 0.3.7 (#90): no older card of theirs exists, and
        # older protein and molecule cards lack none of these fields.
        *(
            {"path": path, "filled_by": "refresh", "entity_types": ("disease",)}
            for path in (
                "identifiers.mondo",
                "identifiers.equivalent_ids",
                "identifiers.related_ids",
                "annotations.definition",
                "annotations.disease_subsets",
                "relationships.subclass_of",
            )
        ),
        {
            "path": "relationships.same_as (MONDO)",
            "filled_by": "disease_identity",
            "entity_types": ("protein",),
        },
        {
            "path": "relationships.same_as (MedGen)",
            "filled_by": "medgen",
            "entity_types": ("protein",),
        },
        {
            "path": "relationships.subclass_of (MONDO)",
            "filled_by": "disease_identity",
            "entity_types": ("protein",),
        },
        {
            "path": "relationships.mentioned_in",
            "filled_by": "europepmc",
            "entity_types": ("protein",),
        },
        # How each statement entered (#92). An older card's SourceAssertions read as
        # not_recorded until the card is built again.
        {"path": "source_assertion_store[].acquisition", "filled_by": "refresh"},
    ],
    # The rule that chose the records a capped source kept (#88, #98), ChEBI (#83), and
    # gnomAD on the canonical transcript (#85).
    "0.3.8": [
        *(
            {"path": path, "filled_by": "chebi", "entity_types": ("small_molecule",)}
            for path in (
                "identifiers.chebi",
                "annotations.chemical_classes",
                "annotations.chemical_roles",
                "annotations.definition",
            )
        ),
        {
            "path": "quality.enrichments[].record_order (BindingDB)",
            "filled_by": "bindingdb",
            "entity_types": ("protein",),
        },
        {
            "path": "quality.enrichments[].row_order (PubChem BioAssay)",
            "filled_by": "pubchem_bioassay",
            "entity_types": ("protein",),
        },
        # KLIFS (#83).
        *(
            {"path": path, "filled_by": "klifs", "entity_types": ("protein",)}
            for path in (
                "annotations.kinase_classification",
                "annotations.kinase_structures",
                "annotations.kinase_pocket",
            )
        ),
        # GPCRdb (#83).
        *(
            {"path": path, "filled_by": "gpcrdb", "entity_types": ("protein",)}
            for path in (
                "annotations.gpcr_classification",
                "annotations.gpcr_segments",
                "annotations.gpcr_residues",
                "annotations.gpcr_structures",
            )
        ),
        {
            "path": "annotations.antibody_complexes",
            "filled_by": "sabdab",
            "entity_types": ("protein",),
        },
        {
            "path": "relationships.ortholog_of",
            "filled_by": "oma",
            "entity_types": ("protein",),
        },
        *(
            {"path": path, "filled_by": "exon_usage", "entity_types": ("protein",)}
            for path in (
                "annotations.exon_usage_by_tissue",
                "annotations.isoform_coding_exons",
            )
        ),
        # Transmembrane segments RCSB integrates (OPM, PDBTM), set only when stated.
        {
            "path": "relationships.has_structure.membrane_segments",
            "filled_by": "structures",
            "entity_types": ("protein",),
        },
        # gnomAD's consequence on the canonical transcript (#85).
        *(
            {"path": path, "filled_by": "gnomad", "entity_types": ("protein",)}
            for path in (
                "annotations.population_variants[].transcript_version",
                "annotations.population_variants[].canonical_consequence",
                "quality.enrichments[].canonical_transcripts (gnomAD)",
            )
        ),
    ],
    # UniRef clusters, and the entries clustered with the card's (#103).
    "0.3.9": [
        *(
            {"path": path, "filled_by": "uniref", "entity_types": ("protein",)}
            for path in ("identifiers.uniref", "relationships.clustered_with")
        ),
        # quality.retries (#97) is not listed: it records a build's retries, present
        # only when the build asked a request again, so its absence is no gap (like
        # quality.retrievals, #100).
    ],
    # UniProt's Ensembl transcripts per isoform, and GTEx's tissue terms (#102).
    "0.3.10": [
        {
            "path": "identifiers.ensembl_transcripts",
            "filled_by": "refresh",
            "entity_types": ("protein",),
        },
        {
            "path": "annotations.tissue_terms",
            "filled_by": "gtex",
            "entity_types": ("protein",),
        },
    ],
    "0.3.11": [
        {
            "path": path,
            "filled_by": "europepmc",
            "entity_types": ("protein",),
            "explicit_only": True,
            **(
                {"qualifier": True}
                if path.startswith("relationships.") and path.count(".") > 1
                else {}
            ),
        }
        for path in (
            "relationships.mentioned_in.locations",
            "relationships.mentioned_in.article",
            "relationships.structure_mentioned_in",
            "relationships.structure_mentioned_in.structure_ref",
            "relationships.structure_mentioned_in.structure_context",
            "relationships.structure_mentioned_in.locations",
            "relationships.structure_mentioned_in.article",
            "source_assertion_store[].source_metadata.content_kind",
            "source_assertion_store[].source_metadata.requested_article",
            "source_assertion_store[].source_metadata.article",
            "source_assertion_store[].source_metadata.identity_basis",
            "quality.enrichments[].article_ids",
            "quality.enrichments[].annotation_count",
            "quality.enrichments[].returned_annotations",
            "quality.enrichments[].mapping",
            "quality.enrichments[].uniprot_mention_count",
            "quality.enrichments[].structure_mention_count",
            "quality.enrichments[].uniprot_annotation_count",
            "quality.enrichments[].pdb_annotation_count",
            "quality.enrichments[].unlinked_pdb_mentions",
        )
    ],
    "0.3.12": [
        {"path": path, "filled_by": "extractions", "explicit_only": True}
        for path in (
            "quality.literature_extractions",
            "relationships.mentioned_in.locations (literal extraction)",
            "quality.literature_extractions[].article_metadata_source_assertion_ids",
            "quality.literature_extractions[].metadata_binding_rule",
            "source_assertion_store[].source_metadata.requested_identifier (article metadata)",
            "source_assertion_store[].source_metadata.publication_ref (article metadata)",
            "source_assertion_store[].source_metadata.service_version (article metadata)",
            "source_assertion_store[].source_metadata.version_basis (article metadata)",
        )
    ],
}

#: Qualifiers every relationship of their predicate has when fetched with the schema
#: that added them, so their absence is a gap (others, such as ``isoform``, are set only
#: when they apply, and are checked through their relationship).
QUALIFIER_PATHS = frozenset(
    change["path"]
    for changes in SCHEMA_CHANGES.values()
    for change in changes
    if change.get("qualifier")
)

#: Steps between schema lines: ``(from line, to line) -> step(data) -> (data, notes)``,
#: where ``notes`` is ``{"converted": [...], "gaps": [...]}``. None exists yet.
STEPS: Dict[
    Tuple[str, str], Callable[[Dict[str, Any]], Tuple[Dict[str, Any], Dict[str, Any]]]
] = {}


def _line(version: Tuple[int, int, int]) -> str:
    return f"{version[0]}.{version[1]}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _has(data: Dict[str, Any], path: str) -> bool:
    """Whether a stored card holds ``path`` (a field, or a relationship template)."""
    if path == "relationships.has_structure.derivation":
        assertions = {
            row["id"]: row for row in data.get("source_assertion_store") or []
        }
        relevant = [
            row
            for row in data.get("relationship_store") or []
            if row.get("predicate") == "has_structure"
            and "ligands" in (row.get("qualifiers") or {})
            and any(
                (assertions.get(ref, {}).get("source") or {}).get("name") == "RCSB PDB"
                for ref in row.get("source_assertion_ids", [])
            )
        ]

        def recorded_basis(row):
            derivation = row.get("derivation") or {}
            if not isinstance(derivation, dict):
                return False
            parameters = derivation.get("parameters") or {}
            if (
                not isinstance(parameters, dict)
                or derivation.get("rule") != "rcsb_ligand_contacts@1"
                or parameters.get("qualifier_paths") != ["ligands[].instances"]
                or parameters.get("input_path")
                != ["asserted_value", "ligand_contact_inputs"]
            ):
                return False
            inputs = derivation.get("inputs")
            if not isinstance(inputs, list) or not all(
                isinstance(ref, str) for ref in inputs
            ):
                return False
            for ref in inputs:
                assertion = assertions.get(ref, {})
                value = assertion.get("asserted_value") or {}
                if not isinstance(value, dict):
                    continue
                original = value.get("ligand_contact_inputs") or {}
                if not isinstance(original, dict):
                    continue
                if (
                    assertion.get("field_path") == "relationships.has_structure"
                    and assertion.get("subject_ref") == row["object_ref"]
                    and (assertion.get("source") or {}).get("name") == "RCSB PDB"
                    and value.get("object_ref") == row["object_ref"]
                    and isinstance(original.get("polymer_entities"), list)
                ):
                    return True
            return False

        return all(recorded_basis(row) for row in relevant)
    if path == "source_assertion_store[].source_metadata.coordinate_scope":
        # This addition applies only to existing gnomAD variant assertions. Empty
        # or unrelated cards have no missing coordinate context; migration never
        # synthesizes it from an old dataset label or enrichment report.
        assertions = [
            row
            for row in data.get("source_assertion_store") or []
            if row.get("field_path") == "annotations.population_variants"
            and (row.get("source") or {}).get("name") == "gnomAD"
        ]
        return all(
            (row.get("source_metadata") or {}).get("coordinate_scope")
            for row in assertions
        )
    if path.startswith("relationships."):
        predicate = path.split(".")[1].split(" ")[0]
        rels = [
            r
            for r in data.get("relationship_store") or []
            if r.get("predicate") == predicate
        ]
        if path in QUALIFIER_PATHS:
            key = path.split(".")[2]
            return any(key in (r.get("qualifiers") or {}) for r in rels)
        if " (" in path:
            wanted = path.split("(", 1)[1].rstrip(")")
            if predicate == "classified_in":
                return any(
                    r["object_ref"].split(":")[0] in ("orthodb", "eggnog") for r in rels
                )
            return any(
                (r.get("qualifiers") or {}).get("source") == wanted for r in rels
            )
        return bool(rels)
    node: Any = data.get("sections") or {}
    if path.endswith(".substitution.missing"):
        # Before 0.3.6 a deletion was an item with no substitution (#80): only such an
        # item is a gap, not a card without deletions.
        for key in path.split(".")[:2]:
            node = node.get(key) if isinstance(node, dict) else None
        items = (node or {}).get("value") or []
        return all("substitution" in item for item in items if isinstance(item, dict))
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            return False
        node = node[key]
    return True


def _enrichment_options(data: Dict[str, Any]) -> set:
    """The enrichment options a stored card records it was built with: the bespoke
    enrichments, and those the declared enrichers derive (#86)."""
    from sabueso.enrichers import options_by_source

    known = {
        ("BindingDB", None): {"bindingdb"},
        ("PubChem BioAssay", None): {"pubchem_bioassay"},
        ("RCSB PDB", None): {"structures"},
        ("ChEMBL", "indications"): {"indications"},
        ("ClinicalTrials.gov", None): {"trials"},
        **options_by_source(),
    }
    options = set()
    for e in (data.get("quality") or {}).get("enrichments") or []:
        options |= known.get((e.get("source"), e.get("data")), set())
    return options


def within_line_gaps(
    data: Dict[str, Any], stated: str, target: str
) -> List[Dict[str, str]]:
    """The additions between two versions of one line the card does not hold."""
    have, want = parse(stated), parse(target)
    asked = _enrichment_options(data)
    gaps = []
    for version, changes in sorted(SCHEMA_CHANGES.items(), key=lambda kv: parse(kv[0])):
        if not (have < parse(version) <= want):
            continue
        entity_type = (data.get("meta") or {}).get("entity_type")
        for change in changes:
            if change.get("explicit_only"):
                continue  # Only explicit article ids ask for located annotations.
            if entity_type not in change.get("entity_types", (entity_type,)):
                continue
            if _has(data, change["path"]):
                continue
            filled_by = change["filled_by"]
            if filled_by == "curation":
                continue  # only a curator adds it; its absence is not a gap
            kind = (
                "missing"
                if filled_by == "refresh" or filled_by in asked
                else "available"
            )
            gaps.append(
                {
                    "introduced_in": version,
                    "path": change["path"],
                    "filled_by": filled_by,
                    "kind": kind,
                }
            )
    return gaps


def migrate_card(data: Dict[str, Any], store: Any = None) -> Any:
    """A card of the current schema from stored card data; see the module docstring."""
    from .card import CARD_SCHEMA_VERSION, Card
    from .quantities import seal
    from .snapshot import snapshot_id

    original = copy.deepcopy(dict(data))
    meta = original.get("meta") or {}
    stated = parse(meta.get("schema_version"))
    if stated is None:
        raise StorageError(
            f"Card {meta.get('card_id')} states no valid schema version; nothing to migrate from."
        )
    current = parse(CARD_SCHEMA_VERSION)
    if stated > current:
        raise StorageError(
            f"Card {meta.get('card_id')} has schema {meta['schema_version']}, newer than {CARD_SCHEMA_VERSION}; it cannot be migrated backwards."
        )
    records: List[Dict[str, Any]] = []
    work = copy.deepcopy(original)
    version = stated
    while not same_line(version, current):
        nxt = (
            (version[0], version[1] + 1, 0)
            if version[0] == 0
            else (version[0] + 1, 0, 0)
        )
        step = STEPS.get((_line(version), _line(nxt)))
        if step is None:
            raise StorageError(
                f"No migration from card schema line {_line(version)} to {_line(nxt)} "
                f"(card {meta.get('card_id')}); see uibcdf/sabueso#51."
            )
        work, notes = step(work)
        work.setdefault("meta", {})["schema_version"] = f"{nxt[0]}.{nxt[1]}.{nxt[2]}"
        records.append(
            {
                "from": f"{version[0]}.{version[1]}.{version[2]}",
                "to": work["meta"]["schema_version"],
                "step": "between_lines",
                **notes,
            }
        )
        version = nxt
    from_version = f"{version[0]}.{version[1]}.{version[2]}"
    if version != current:
        gaps = within_line_gaps(work, from_version, CARD_SCHEMA_VERSION)
        records.append(
            {
                "from": from_version,
                "to": CARD_SCHEMA_VERSION,
                "step": "within_line",
                "converted": [],
                "gaps": gaps,
            }
        )
    work["meta"]["schema_version"] = CARD_SCHEMA_VERSION
    stamp = {
        "rule": MIGRATION_RULE,
        "at": _now(),
        "original_schema": meta.get("schema_version"),
        "original_snapshot": snapshot_id(original),
        "steps": records,
    }
    work.setdefault("quality", {}).setdefault("migration", []).append(stamp)
    work.pop("quantities", None)
    work["quantities"] = seal(work)
    migrated = Card.from_dict(work)
    if store is not None:
        if same_line(stated, current):
            store.save(
                Card.from_dict(original),
                note=f"schema {meta.get('schema_version')}, before migration",
            )
        store.save(migrated, note=f"migrated to schema {CARD_SCHEMA_VERSION}")
    return migrated


def rebuild_options(card: Any) -> Dict[str, Any]:
    """The enrichment options a card records it was built with, to build it again."""
    from .refresh_scope import apply_overrides, restoration_plan

    options, report = restoration_plan(card)
    apply_overrides(report, {})
    return options


@capture_acquisitions
def refresh_card(
    card: Any, curations: Any = None, store: Any = None, **options: Any
) -> Tuple[Any, Any]:
    """Build the card again from its sources; see the module docstring.

    ``options`` add to, or override, the options the card records (clients included).
    Returns ``(refreshed card, resolution)``.
    """
    import sabueso

    if not card.id:
        raise StorageError("A card without meta.card_id cannot be refreshed.")
    anchor = card.id.split(":", 2)[2]
    from .refresh_scope import RESTORATION_RULE, apply_overrides, restoration_plan

    restored, scope = restoration_plan(card)
    apply_overrides(scope, options)
    given = {**restored, **options}
    refreshed, resolution = sabueso.resolve(anchor, curations=curations, **given)
    if refreshed is None:
        raise StorageError(f"Refreshing {card.id} failed: {resolution.status}.")
    history = copy.deepcopy(card.quality.get("migration") or [])
    open_gaps = [
        g
        for record in history
        for step in record.get("steps", [])
        for g in step.get("gaps", [])
    ]
    data = refreshed.to_dict()
    completed = sorted({g["path"] for g in open_gaps if _has(data, g["path"])})
    record = {
        "rule": MIGRATION_RULE,
        "at": _now(),
        "refresh_of": card.pinned_ref(),
        "request_restoration": {"rule": RESTORATION_RULE, "requests": scope},
        "options": sorted(
            k for k in given if not k.endswith("_client") and k != "resolver"
        ),
        "completed": completed,
        "not_stated": sorted(
            {g["path"] for g in open_gaps if g["kind"] == "missing"} - set(completed)
        ),
    }
    refreshed.quality["migration"] = history + [record]
    from .literature_extraction import preserve_extractions

    preserve_extractions(card, refreshed)
    if store is not None:
        store.save(card, note="before refresh")
        store.save(refreshed, note="refreshed from the sources")
    return refreshed, resolution
