"""Knowledge packets: one declared question, one pinned, cited answer (uibcdf/sabueso#71).

A **KnowledgeQuery** is a structured question, not natural language: a subject protein,
an optional comparator, the aspects asked for, and constraints. A **KnowledgePacket** is
the composed answer. It is a composition over cards, not a new kind of knowledge:

- ``entities``: the pinned card states it was composed from (never copies);
- ``facts``: per aspect, the output of Sabueso's views, each with its named rule;
- ``conflicts``: where sources disagree, as the cards record it;
- ``unknowns``: per source, what is not stated, not queried, unavailable or partial,
  for the areas of the aspects asked (``knowledge_state@5`` in current compositions;
  historical packets keep their original rule);
- ``provenance``: the sources, their releases and retrieval dates.

**Deterministic.** The packet payload is a pure function of the query and card states. It
never calls an LLM, never ranks, never summarizes, and holds the aspects the query
declares, nothing else. The same query and the same card states give the same packet.
Composition automatically attaches detached ``packet.attribution``. A
``sabueso.attribution()`` context collects these records; they never enter the
scientific payload or its hashes.

**Two ids.** ``snapshot_id`` is the exact state, retrieval times included: the citable
pin, ``sabueso:packet:<name>@sha256:…``. ``content_id`` leaves out retrieval times and
the Sabueso version that built the cards, so two assemblies of unchanged knowledge have
the same ``content_id`` even when the sources were read again (``same_knowledge``).

What each aspect asks the sources for, and which knowledge areas it covers, is fixed by
the mapping (``packet_aspects@8`` now). It never changes once published: a change is a new
version, and a test pins what each version asks. ``@1`` was published in 0.6.0; ``@2``
(0.7.0) adds SKEMPI's interface mutations to the ``oligomer`` aspect (#83), and MONDO's
disease identity and the grouped diseases to ``disease_association`` (#90). ``@3``
adds the kinase and GPCR classifications to ``identity``, kinase conformations, GPCR
states and antibody complexes to ``structures``, the kinase pocket to
``ligand_sites``, GPCR segments and generic numbers to ``sequence_features``, gnomAD's
pext to ``biological_context`` (#102), and the ``orthology`` aspect (OMA), asked only
when named (#83). ``@4`` adds UniRef to ``identity``: the entry's sequence clusters and
the entries ``clustered_with`` it, never the same entity (#103). ``@5`` adds GTEx's
tissue terms (UBERON, or EFO for a cell line) to ``biological_context``, next to the
pext they name (#102).
``@6`` adds direct UniProt mentions and derived PDB mention context to ``literature``.
Automatic acquisition asks Europe PMC for bibliography only; located annotations
require explicit article ids and can enter a packet through prebuilt cards.

The shared contract (query and packet shapes, references, the boundary with MOLI's
Context Assembly) is proposed in uibcdf/moli#22; this is Sabueso's prototype of it.
"""

from __future__ import annotations

import copy
import json
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from sabueso._private.argdigest import arg_digest

from .errors import StorageError
from .snapshot import canonical_json, digest, parse_ref, pinned_ref, snapshot_content

QUERY_FORMAT = "knowledge_query@2"
#: ``@2`` adds ``detail`` (#88); a ``@1`` query reads as ``detail="full"``.
READABLE_QUERY_FORMATS = ("knowledge_query@1", "knowledge_query@2")
PACKET_FORMAT = "knowledge_packet@3"
#: Formats a packet can be read in. ``@2`` references instead of copying: grouped
#: disease statements name the statement they group, and the joint structure inventory
#: names each role's structure by its relationship id (#88). ``@3`` states its
#: ``detail``: ``full`` facts, or an ``index`` of what the cards hold (#88).
READABLE_FORMATS = ("knowledge_packet@1", "knowledge_packet@2", "knowledge_packet@3")
#: Levels of detail a query may ask for (``knowledge_query@2``).
DETAILS = ("full", "index")
INDEX_RULE = "packet_index@1"
#: The views a ``full`` packet holds per aspect, which an ``index`` leaves to be
#: computed from the pinned card (``card.<view>()``).
FULL_VIEWS = {
    "identity": ("identity_audit (together)",),
    "structures": (
        "structures",
        "predicted_structures",
        "structure_inventory (together)",
    ),
    "oligomer": ("oligomer", "interface_mutations"),
    "ligand_sites": ("ligand_sites",),
    "bioactivities": ("bioactivities",),
    "sequence_features": (),
    "literature": ("literature", "claims"),
    "disease_association": ("diseases",),
    "biological_context": (),
    "orthology": (),
}
ASPECT_MAPPING = "packet_aspects@8"
#: Aspect mappings a packet can carry; packets of different mappings are not compared.
#: ``@3`` adds KLIFS and GPCRdb (identity, structures, ligand sites, sequence features),
#: SAbDab (structures) and the ``orthology`` aspect (OMA), which a query asks for by
#: name: a protein has thousands of orthologs (#83, #88). ``@4`` adds UniRef to
#: ``identity``: the entry's clusters, and the entries ``clustered_with`` it (#103).
#: ``@5`` adds GTEx's tissue terms to ``biological_context`` (#102).
#: ``@6`` adds both mention areas to ``literature`` and asks Europe PMC bibliography
#: automatically, without guessing article ids (#71, #92).
#: ``@7`` uses disease_grouping@3 with identifier-scoped identity coverage (#144).
#: ``@8`` adds explicit ligand-instance identity/axis scope (#148), retaining @6/@7 native projections.
PACKET_PREFIX = "sabueso:packet:"

#: Keys left out of a content-equivalence id: when the sources were read, and which
#: Sabueso version built the card. Neither is knowledge.
NOT_KNOWLEDGE = ("retrieved_at", "sabueso_version")

#: Identity fields a packet shows (the full sequence stays on the card).
IDENTITY_FIELDS = (
    "identifiers.uniprot",
    "identifiers.gene_loci",
    "names.canonical_name",
    "names.gene_names",
    "annotations.organism",
    "annotations.taxon_id",
    "annotations.lineage",
    "annotations.taxonomy",
    "sequence.length",
    "sequence.checksums",
)

#: Areas ``@3`` adds to existing aspects; they enter an aspect's facts only when the card
#: holds them, so a protein without them keeps its facts.
CLASSIFICATION_FIELDS = (
    "annotations.kinase_classification",
    "annotations.gpcr_classification",
)
STRUCTURE_FIELDS = (
    "annotations.kinase_structures",
    "annotations.gpcr_structures",
    "annotations.antibody_complexes",
)

#: ``packet_aspects@8``: per aspect, the knowledge areas (field paths and relationships,
#: as ``knowledge_state`` names them) whose facts, conflicts and unknowns it reports,
#: matched by prefix; and the options of the bespoke sources it needs. The options of
#: declared enrichers are derived (``aspect_options``): an aspect asks every enricher
#: that answers one of its areas through its default request. Areas requiring a
#: separate explicit request remain not queried with a declared explanation (#86).
ASPECTS: Dict[str, Dict[str, Any]] = {
    "identity": {
        "bespoke_options": {},
        "areas": (
            "identifiers.",
            "names.",
            "annotations.organism",
            "annotations.taxon_id",
            "annotations.lineage",
            "annotations.taxonomy",
            "sequence.",
            *CLASSIFICATION_FIELDS,
            "relationships.clustered_with",
        ),
    },
    "structures": {
        "bespoke_options": {"structures": "all"},
        "areas": (
            "relationships.has_structure",
            "relationships.has_predicted_structure",
            *STRUCTURE_FIELDS,
        ),
    },
    "oligomer": {
        "bespoke_options": {"structures": "all"},
        "areas": (
            "annotations.subunit",
            "relationships.has_interface_with",
            "features_positional.family_site",
            "annotations.interface_mutations",
        ),
    },
    "ligand_sites": {
        "bespoke_options": {},
        "areas": (
            "relationships.has_ligand_site",
            "features_positional.binding_site",
            "features_positional.active_site",
            "features_positional.family_site",
            "annotations.kinase_pocket",
        ),
    },
    "bioactivities": {
        "bespoke_options": {},  # from the bioactivity_sources constraint
        "areas": ("relationships.has_bioactivity",),
    },
    "sequence_features": {
        "bespoke_options": {},
        "areas": (
            "features_positional.",
            "annotations.isoforms",
            "annotations.alternative_products",
            "annotations.population_variants",
            "annotations.gpcr_segments",
            "annotations.gpcr_residues",
        ),
    },
    "literature": {
        "bespoke_options": {},
        "areas": (
            "relationships.described_in",
            "relationships.mentioned_in",
            "relationships.structure_mentioned_in",
            "literature.",
        ),
    },
    "disease_association": {
        "bespoke_options": {},
        "areas": (
            "relationships.associated_with",
            "annotations.disease",
            "annotations.clinical_variants",
            "relationships.same_as (MONDO)",
            "relationships.same_as (MedGen)",
        ),
    },
    "biological_context": {
        "bespoke_options": {},
        "areas": (
            "relationships.participates_in",
            "annotations.pathogen_phenotypes",
            "annotations.stage_expression",
            "annotations.essentiality",
            "annotations.accessibility",
            "annotations.metabolic_role",
            "annotations.subcellular_location",
            "annotations.tissue_specificity",
            "annotations.pathway",
            "annotations.exon_usage_by_tissue",
            "annotations.isoform_coding_exons",
            "annotations.tissue_terms",
        ),
    },
    "orthology": {
        "bespoke_options": {},
        "areas": ("relationships.ortholog_of",),
    },
}
#: Aspects a query asks for when it names none: every aspect but ``orthology``, whose
#: thousands of orthologs per protein a query asks for by name.
DEFAULT_ASPECTS = tuple(sorted(a for a in ASPECTS if a != "orthology"))


def aspect_options(aspect: str) -> Dict[str, Any]:
    """The resolve options an aspect needs: its bespoke sources', and every declared
    enricher answering one of its areas (``packet_aspects@8``)."""
    from sabueso.enrichers import ENRICHERS

    options = dict(ASPECTS[aspect]["bespoke_options"])
    for enricher in ENRICHERS:
        if enricher.entity_type == "protein" and any(
            _in_areas(area, [aspect]) for area in enricher.areas
        ):
            options[enricher.option] = enricher.default_request
    return options


#: Bioactivity sources a query may name, and the resolve option each needs.
BIOACTIVITY_SOURCES = {
    "ChEMBL": ("chembl", {}),
    "BindingDB": ("bindingdb", {}),
    "PubChem BioAssay": ("pubchem_bioassay", True),
}
#: Constraints and their defaults (``knowledge_query@1``).
CONSTRAINTS = {"bioactivity_sources": ("ChEMBL",)}

UNKNOWN_STATES = ("not_stated", "not_queried", "unavailable", "partial")


class KnowledgeQuery:
    """A declared question about a protein, optionally beside a comparator.

    ``subject`` and ``comparator`` are UniProt accessions (``P60174`` or
    ``uniprot:P60174``). ``aspects`` are names of ``packet_aspects@8`` (default: all
    of them but ``orthology``). ``constraints``: ``bioactivity_sources``, among ChEMBL, BindingDB and
    PubChem BioAssay (default ChEMBL). ``detail``: ``"full"`` (default), the views'
    output whole, or ``"index"``, per aspect what the cards hold and the reference of
    every item, without values (``packet_index@1``). Anything else is refused, never
    ignored.
    """

    @arg_digest()
    def __init__(
        self,
        subject: str,
        comparator: str | None = None,
        aspects: Iterable[str] | None = None,
        constraints: Mapping[str, Any] | None = None,
        detail: str = "full",
        skip_digestion: bool = False,
    ) -> None:
        self.subject = subject
        self.detail = detail
        self.comparator = comparator
        self.aspects = tuple(sorted(aspects)) if aspects else DEFAULT_ASPECTS
        merged = dict(CONSTRAINTS)
        merged.update(constraints or {})
        self.constraints = {
            "bioactivity_sources": tuple(sorted(merged["bioactivity_sources"]))
        }
        if subject == comparator:
            raise ValueError("A subject is not its own comparator.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": QUERY_FORMAT,
            "subject": self.subject,
            "comparator": self.comparator,
            "aspects": list(self.aspects),
            "constraints": {k: list(v) for k, v in self.constraints.items()},
            "detail": self.detail,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "KnowledgeQuery":
        if data.get("format") not in READABLE_QUERY_FORMATS:
            raise ValueError(
                f"Not a knowledge query Sabueso reads "
                f"({', '.join(READABLE_QUERY_FORMATS)}): format {data.get('format')!r}."
            )
        return cls(
            data["subject"],
            data.get("comparator"),
            data.get("aspects"),
            data.get("constraints"),
            data.get("detail", "full"),
        )

    def options(self) -> Dict[str, Any]:
        """The resolve options the aspects need (``packet_aspects@8``)."""
        options: Dict[str, Any] = {}
        for aspect in self.aspects:
            options.update(aspect_options(aspect))
        if "bioactivities" in self.aspects:
            for source in self.constraints["bioactivity_sources"]:
                option, value = BIOACTIVITY_SOURCES[source]
                options[option] = value
        return options

    def __eq__(self, other: object) -> bool:
        return isinstance(other, KnowledgeQuery) and self.to_dict() == other.to_dict()

    def __repr__(self) -> str:
        if not hasattr(self, "constraints"):  # refused while being built
            return "KnowledgeQuery(<not built>)"
        return f"KnowledgeQuery({self.to_dict()!r})"


def as_stated(data: Any) -> Any:
    """View output as JSON: a quantity becomes its node ``{value, unit}`` (the unit is
    never dropped), tuples become lists and sets sorted lists. Anything else that JSON
    cannot state is refused."""
    import pyunitwizard as puw

    from .quantities import canonical_unit, quantity_node

    if isinstance(data, dict):
        return {str(k): as_stated(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [as_stated(v) for v in data]
    if isinstance(data, (set, frozenset)):
        return sorted((as_stated(v) for v in data), key=canonical_json)
    if data is None or isinstance(data, (str, bool, int, float)):
        return data
    if puw.is_quantity(data):
        # Its own unit, named: the value is read in that unit, never in a session's.
        unit = canonical_unit(str(puw.get_unit(data)))
        value = puw.get_value(data, to_unit=unit)
        value = value.item() if hasattr(value, "item") else value
        return quantity_node(value, unit)
    raise TypeError(f"A packet cannot state {type(data).__name__}: {data!r}")


def without_retrieval(data: Any) -> Any:
    """A copy without the keys that are not knowledge (``NOT_KNOWLEDGE``)."""
    if isinstance(data, dict):
        return {
            k: without_retrieval(v) for k, v in data.items() if k not in NOT_KNOWLEDGE
        }
    if isinstance(data, list):
        return [without_retrieval(v) for v in data]
    return data


def card_content_id(card: Any) -> str:
    """The content-equivalence id of a card: its snapshot content without retrieval
    times and without the Sabueso version that built it."""
    content = without_retrieval(snapshot_content(card.to_dict()))
    for key in ("source_assertion_store", "relationship_store"):
        content[key] = sorted(content.get(key) or [], key=canonical_json)
    return digest(canonical_json(content))


def _in_areas(area: str, aspects: Iterable[str]) -> bool:
    return any(
        area.startswith(prefix) for a in aspects for prefix in ASPECTS[a]["areas"]
    )


def _fields(card: Any, paths: Iterable[str]) -> Dict[str, Any]:
    out = {}
    for path in paths:
        node = card.get(path)
        if node is not None:
            out[path] = node
    return out


def _positional(card: Any) -> Dict[str, Any]:
    paths = [p for p in card.list_fields() if p.startswith("features_positional.")]
    paths = {p.split(".")[0] + "." + p.split(".")[1] for p in paths}
    return _fields(
        card,
        sorted(paths)
        + [
            "annotations.isoforms",
            "annotations.alternative_products",
            "annotations.population_variants",
            "annotations.gpcr_segments",
            "annotations.gpcr_residues",
        ],
    )


def _relationships(card: Any, predicate: str) -> List[Dict[str, Any]]:
    return [
        {
            "relationship_id": r["id"],
            **{k: r[k] for k in ("object_ref", "qualifiers", "source_assertion_ids")},
        }
        for r in sorted(
            card.relationships(predicate=predicate),
            key=lambda r: (r["object_ref"], r["id"]),
        )
    ]


def _facts(aspect: str, card: Any, *, mapping: str = ASPECT_MAPPING) -> Dict[str, Any]:
    if aspect == "identity":
        decision = (card.quality.get("entity_resolution") or {}).get("decision") or {}
        return {
            "card_id": card.id,
            "fields": _fields(
                card, (*IDENTITY_FIELDS, *CLASSIFICATION_FIELDS, "identifiers.uniref")
            ),
            "resolution": {k: decision.get(k) for k in ("rules", "sources", "route")},
            # Related entries UniProt clusters with it, only when stated (#103).
            **(
                {"clustered_with": _relationships(card, "clustered_with")}
                if card.relationships(predicate="clustered_with")
                else {}
            ),
        }
    if aspect == "structures":
        return {
            "experimental": card.structures(),
            "predicted": card.predicted_structures(),
            **_fields(card, STRUCTURE_FIELDS),
        }
    if aspect == "oligomer":
        return {**card.oligomer(), "interface_mutations": card.interface_mutations()}
    if aspect == "ligand_sites":
        if mapping in ("packet_aspects@6", "packet_aspects@7"):
            from ._ligand_sites_legacy_v1 import ligand_sites_view

            native = ligand_sites_view(card)
        else:
            native = card.ligand_sites()
        return {**native, **_fields(card, ["annotations.kinase_pocket"])}
    if aspect == "bioactivities":
        return card.bioactivities()
    if aspect == "sequence_features":
        return _positional(card)
    if aspect == "literature":
        return {"publications": card.literature(), "claims": card.claims()}
    if aspect == "disease_association":
        return {
            "uniprot": _fields(card, ["annotations.disease"]),
            "clinical_variants": _fields(card, ["annotations.clinical_variants"]),
            "associations": [
                {
                    "relationship_id": r["id"],
                    **{
                        k: r[k]
                        for k in ("object_ref", "qualifiers", "source_assertion_ids")
                    },
                }
                for r in sorted(
                    card.relationships(predicate="associated_with"),
                    key=lambda r: (r["object_ref"], r["qualifiers"].get("channel", "")),
                )
            ],
            "grouped": _grouped_by_reference(
                card.diseases(
                    grouping_rule="disease_grouping@2"
                    if mapping == "packet_aspects@6"
                    else "disease_grouping@3"
                ),
                coverage=mapping != "packet_aspects@6",
            ),
        }
    if aspect == "biological_context":
        return {
            **_fields(card, ASPECTS["biological_context"]["areas"][1:]),
            "pathways": [
                {
                    "relationship_id": r["id"],
                    **{
                        k: r[k]
                        for k in ("object_ref", "qualifiers", "source_assertion_ids")
                    },
                }
                for r in sorted(
                    card.relationships(predicate="participates_in"),
                    key=lambda r: r["object_ref"],
                )
            ],
        }
    if aspect == "orthology":
        return {"orthologs": _relationships(card, "ortholog_of")}
    raise KeyError(aspect)


def _index(aspect: str, card: Any) -> Dict[str, Any]:
    """What a card holds in an aspect's areas, without values (``packet_index@1``).

    Per field: how many items it holds, from which sources, and the SourceAssertions
    that state them. Per relationship area: how many, from which sources, and each
    relationship's id. Every item is cited through the card's pin
    (``packet.cite(role, id)``) and read from the store; nothing is ranked, selected
    or summarized beyond counting.
    """
    areas = ASPECTS[aspect]["areas"]
    store = card.source_assertion_store

    def sources(ids: Iterable[str]) -> Dict[str, int]:
        counted: Dict[str, int] = {}
        for sa_id in ids:
            name = ((store.get(sa_id) or {}).get("source") or {}).get("name")
            counted[name or "unknown"] = counted.get(name or "unknown", 0) + 1
        return dict(sorted(counted.items()))

    out: Dict[str, Any] = {}
    field_areas = [a for a in areas if not a.startswith("relationships.")]
    for path in card.list_fields():
        if path.count(".") != 1 or not path.startswith(tuple(field_areas)):
            continue
        node = card.get(path)
        if not isinstance(node, dict) or "value" not in node:
            continue
        ids = list(node.get("source_assertion_ids") or [])
        value = node["value"]
        out[path] = {
            "count": len(value) if isinstance(value, list) else 1,
            "by_source": sources(ids),
            "source_assertion_ids": ids,
        }
    for area in areas:
        if not area.startswith("relationships."):
            continue
        predicate, _, source = area[len("relationships.") :].partition(" (")
        source = source.rstrip(")") or None
        held = []
        for rel in card.relationships(predicate=predicate):
            named = sources(rel.get("source_assertion_ids") or [])
            if source is None or source in named:
                held.append((rel["id"], named))
        if not held:
            continue
        by_source: Dict[str, int] = {}
        for _, named in held:
            for name in named:
                by_source[name] = by_source.get(name, 0) + 1
        out[area] = {
            "count": len(held),
            "by_source": dict(sorted(by_source.items())),
            "relationship_ids": sorted(rid for rid, _ in held),
        }
    return {
        "areas": dict(sorted(out.items())),
        "full_views": list(FULL_VIEWS[aspect]),
        "full_rules": full_rules()[aspect],
        "rule": INDEX_RULE,
    }


def full_rules(mapping: str = ASPECT_MAPPING) -> Dict[str, List[str]]:
    """Per aspect, the named rules a full packet's views apply (``FULL_VIEWS``), read
    from the modules that define them, so an index names the rules a reader would get
    by computing the views from the pinned cards."""
    from sabueso.mappings.europepmc import STRUCTURE_MENTION_RULE

    from . import (
        bioactivities,
        diseases,
        identity_audit,
        interface_mutations,
        ligand_sites,
        measurements,
        oligomer,
        structures,
    )
    from ._ligand_sites_legacy_v1 import SITE_OVERLAP_RULE as LEGACY_SITE_RULE

    rules = {
        "identity": [identity_audit.IDENTITY_RULE],
        "structures": [
            structures.COVERAGE_CLASS_RULE,
            structures.STATE_RULE,
            structures.INVENTORY_RULE,
        ],
        "oligomer": [
            oligomer.PARTNER_RULE,
            oligomer.AGREEMENT_RULE,
            interface_mutations.RULE,
        ],
        "ligand_sites": [LEGACY_SITE_RULE]
        if mapping in ("packet_aspects@6", "packet_aspects@7")
        else [ligand_sites.SITE_OVERLAP_RULE],
        "bioactivities": [
            bioactivities.BIOACTIVITY_CLASS_RULE,
            bioactivities.PCHEMBL_RULE,
            bioactivities.SCALE_RULE,
            measurements.MEASUREMENT_RULE,
        ],
        "disease_association": ["disease_grouping@2"]
        if mapping == "packet_aspects@6"
        else [diseases.RULE, "disease_identity_coverage@1"],
        "literature": [STRUCTURE_MENTION_RULE],
    }
    if mapping not in ("packet_aspects@6", "packet_aspects@7"):
        rules["ligand_sites"].append(ligand_sites.INSTANCE_RULE)
    return {aspect: sorted(rules.get(aspect, [])) for aspect in ASPECTS}


#: What names a disease statement in the aspect it comes from (``knowledge_packet@2``).
STATEMENT_KEYS = {
    "association": ("relationship_id",),
    "uniprot_disease": ("accession",),
    "clinvar_condition": ("variant", "condition"),
}
#: What a grouping adds to a statement, kept beside its reference.
GROUPING_KEYS = ("grouped_by", "narrower", "reason", "terms")


def _grouped_by_reference(
    view: Dict[str, Any], *, coverage: bool = True
) -> Dict[str, Any]:
    """``Card.diseases()`` with each statement named, not copied: an association by its
    relationship id (``associations``), a UniProt disease by its accession
    (``uniprot``), a ClinVar condition by its variant and index (``clinical_variants``)
    — all in the same aspect."""

    def reference(statement: Dict[str, Any]) -> Dict[str, Any]:
        keys = ("kind", "source", *STATEMENT_KEYS.get(statement.get("kind"), ()))
        named = {k: statement[k] for k in keys if k in statement}
        if len(named) == 2:  # a statement of a kind this format cannot name
            return statement
        return {
            **named,
            **{
                k: statement[k]
                for k in (
                    *GROUPING_KEYS,
                    *(("identity_paths", "identity_coverage") if coverage else ()),
                )
                if k in statement
            },
        }

    return {
        **view,
        "diseases": [
            {**d, "statements": [reference(s) for s in d["statements"]]}
            for d in view["diseases"]
        ],
        "ungrouped": [reference(s) for s in view["ungrouped"]],
    }


#: What the joint inventory adds to a structure each role's ``structures`` holds.
INVENTORY_KEYS = ("relationship_id", "card_id", "substitutions_in_reference")


def _together(
    aspect: str, subject: Any, comparator: Any, facts: Dict[str, Any]
) -> Dict[str, Any] | None:
    """What an aspect says of the two proteins side by side."""
    from .deck import Deck

    if aspect == "identity":
        return {"identity_audit": Deck([subject, comparator]).identity_audit()}
    if aspect == "structures":
        inventory = Deck([subject, comparator]).structure_inventory()
        # Each structure is in its role's facts already: the inventory names it.
        held = {
            item["relationship_id"]
            for role in ("subject", "comparator")
            for item in facts[role]["experimental"]["items"]
        }
        inventory["items"] = [
            {k: item[k] for k in INVENTORY_KEYS if k in item}
            if item.get("relationship_id") in held
            else item
            for item in inventory["items"]
        ]
        return {"inventory": inventory}
    if aspect == "orthology":
        # Whether OMA states the two proteins orthologs of each other: their own
        # relationships, by the accession each card is anchored at.
        refs = {
            "subject": f"uniprot:{_anchor(subject)}",
            "comparator": f"uniprot:{_anchor(comparator)}",
        }
        stated = sorted(
            item["relationship_id"]
            for role, other in (("subject", "comparator"), ("comparator", "subject"))
            for item in facts[role]["orthologs"]
            if item["object_ref"] == refs[other]
        )
        return {"stated_orthologs": stated}
    return None


def _anchor(card: Any) -> str | None:
    return (card.get("identifiers.uniprot") or {}).get("value")


def _unknowns(card: Any, aspects: Iterable[str]) -> Dict[str, Any]:
    state = card.knowledge_state()
    return {
        "rows": [
            r
            for r in state["rows"]
            if r["state"] in UNKNOWN_STATES and _in_areas(r["area"], aspects)
        ],
        "rule": state["rule"],
    }


def _conflicts(card: Any, aspects: Iterable[str]) -> List[Dict[str, Any]]:
    return [
        c
        for c in card.quality.get("conflicts") or []
        if _in_areas(str(c.get("field") or ""), aspects)
    ]


def _provenance(card: Any) -> Dict[str, Any]:
    from .source_assertion_store import acquisition_of

    sources: Dict[str, Dict[str, Any]] = {}
    for sa in card.source_assertion_store.to_list():
        source = sa.get("source") or {}
        entry = sources.setdefault(
            source.get("name") or "unknown",
            {"releases": set(), "retrieved": set(), "assertions": 0, "acquired": {}},
        )
        entry["assertions"] += 1
        # How the statements entered (#92): a model-extracted statement is never
        # reported as curated.
        record = acquisition_of(sa)
        how = record["method"] + (
            f" ({record['origin']})" if record.get("origin") else ""
        )
        entry["acquired"][how] = entry["acquired"].get(how, 0) + 1
        if source.get("version") is not None:
            entry["releases"].add(str(source["version"]))
        if sa.get("retrieved_at"):
            entry["retrieved"].add(str(sa["retrieved_at"]))
    enrichments: Dict[str, Dict[str, int]] = {}
    for record in card.quality.get("enrichments") or []:
        name = record.get("source") or "unknown"
        if record.get("data"):
            name += f" {record['data']}"
        by_status = enrichments.setdefault(name, {})
        status = str(record.get("status"))
        by_status[status] = by_status.get(status, 0) + 1
    return {
        "sources": {
            name: {
                "releases": sorted(e["releases"]),
                "assertions": e["assertions"],
                "acquisition": dict(sorted(e["acquired"].items())),
                "retrieved_at": sorted(e["retrieved"])[:1] + sorted(e["retrieved"])[-1:]
                if e["retrieved"]
                else [],
            }
            for name, e in sorted(sources.items())
        },
        "enrichments": enrichments,
    }


def _comparison_scope(data: Mapping[str, Any]) -> tuple:
    """Formats, aspect mappings and detail levels define comparable knowledge."""
    return data.get("format"), data.get("aspect_mapping"), data.get("detail", "full")


class KnowledgePacket:
    """A composed, pinned answer to a KnowledgeQuery. Build it with
    ``compose_packet`` or ``sabueso.knowledge_packet``; read ``facts``, ``unknowns``,
    ``conflicts``, ``entities`` and ``provenance``."""

    def __init__(self, data: Dict[str, Any], ref: str | None = None) -> None:
        if data.get("format") not in READABLE_FORMATS:
            raise StorageError(
                f"Not a knowledge packet Sabueso reads ({', '.join(READABLE_FORMATS)}):"
                f" format {data.get('format')!r}."
            )
        self._data = data
        # Runtime attribution belongs to the result, outside its scientific hash.
        # A saved scientific payload alone cannot reconstruct an original capture.
        self._attribution = None
        self._acquisition_trace = None
        self.ref = ref

    @property
    def attribution(self) -> dict | None:
        """Detached composition record; None for a payload loaded without its sidecar.

        Save this record beside ``to_dict()`` to retain the original producer and
        source versions. Reading a packet never creates a replacement capture.
        """
        return copy.deepcopy(self._attribution)

    @property
    def acquisition_trace(self) -> dict | None:
        """Original source access during ``knowledge_packet``; None on saved reads.

        Composition over existing cards makes no new source-acquisition claim.
        Save the original runtime trace separately from the scientific payload.
        """
        return copy.deepcopy(self._acquisition_trace)

    format = property(lambda self: self._data["format"])
    #: ``full`` or ``index`` (``knowledge_packet@3``); earlier formats are ``full``.
    detail = property(lambda self: self._data.get("detail", "full"))
    query = property(lambda self: KnowledgeQuery.from_dict(self._data["query"]))
    entities = property(lambda self: self._data["entities"])
    facts = property(lambda self: self._data["facts"])
    conflicts = property(lambda self: self._data["conflicts"])
    unknowns = property(lambda self: self._data["unknowns"])
    provenance = property(lambda self: self._data["provenance"])

    def to_dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._data)

    def snapshot_id(self) -> str:
        """The exact state, retrieval times included: what a pin names."""
        return digest(canonical_json(self._data))

    def content_id(self) -> str:
        """The knowledge, without retrieval times or the building Sabueso version."""
        content = without_retrieval(self._data)
        for entity in content["entities"].values():
            entity.pop("ref", None)
        return digest(canonical_json(content))

    def same_knowledge(self, other: "KnowledgePacket") -> bool | None:
        """Whether two packets hold the same knowledge, however often it was read.
        None when they are in different formats, aspect mappings or levels of detail:
        their ids cannot be compared."""
        if _comparison_scope(self._data) != _comparison_scope(other._data):
            return None
        return self.content_id() == other.content_id()

    def cite(self, role: str, item_id: str) -> str:
        """The pinned reference of a SourceAssertion or relationship of an entity,
        e.g. ``cite("subject", "SA_…")``."""
        card_id, sid, _ = parse_ref(self.entities[role]["ref"])
        return pinned_ref(card_id, sid, item_id)

    def item(self, role: str, item_id: str, store: Any) -> Dict[str, Any]:
        """A SourceAssertion (``SA_…``) or relationship (``REL_…``) of an entity, read
        from a knowledge store at the card state the packet pins: how an ``index``
        packet's references are read (#88)."""
        ref = self.cite(role, item_id)
        if item_id.startswith("REL_"):
            return store.relationship(ref)
        return store.source_assertion(ref)

    @arg_digest()
    def terms(
        self, use: str, store: Any, skip_digestion: bool = False
    ) -> Dict[str, Any]:
        """Report terms of the packet's stored statement support (``packet_terms@1``).
        Read exact card pins from ``store``; bibliography and article fragments have
        separate terms. Full and index use the same support scope at aspect mapping
        ``@6``. Other mappings need an adapter and are refused by this operation.
        The report uses today's packaged registry with its stated review dates;
        it is not added to the immutable packet or credited to a runtime session.
        """
        from .packet_terms import packet_terms

        return packet_terms(self, use, store)

    def __repr__(self) -> str:
        roles = ", ".join(f"{r}={e['card_id']}" for r, e in self.entities.items())
        return f"KnowledgePacket({roles}; aspects={list(self.facts)})"


def compose_packet(
    knowledge_query: KnowledgeQuery, subject: Any, comparator: Any = None
) -> KnowledgePacket:
    """Compose a deterministic packet payload from a query and card states.

    The cards are used as they are: an aspect whose sources they were not built with
    shows as ``not_queried`` in ``unknowns``, never as absent knowledge.
    Composition attaches a detached attribution record; active contexts collect it.
    """
    roles: List[Tuple[str, Any]] = [("subject", subject)]
    if comparator is not None:
        roles.append(("comparator", comparator))
    elif knowledge_query.comparator is not None:
        raise ValueError("The query names a comparator; give its card.")
    for role, card in roles:
        wanted = getattr(knowledge_query, role)
        anchor = (card.get("identifiers.uniprot") or {}).get("value")
        if wanted.split(":", 1)[1] != anchor:
            raise ValueError(
                f"The {role} card is {card.id}, but the query asks about {wanted}."
            )
    aspects = knowledge_query.aspects
    index = knowledge_query.detail == "index"
    facts: Dict[str, Any] = {}
    for aspect in aspects:
        if index:
            facts[aspect] = {role: _index(aspect, card) for role, card in roles}
            continue
        facts[aspect] = {role: _facts(aspect, card) for role, card in roles}
        if comparator is not None:
            together = _together(aspect, subject, comparator, facts[aspect])
            if together is not None:
                facts[aspect]["together"] = together
    data = {
        "format": PACKET_FORMAT,
        "detail": knowledge_query.detail,
        "aspect_mapping": ASPECT_MAPPING,
        "query": knowledge_query.to_dict(),
        "entities": {
            role: {
                "card_id": card.id,
                "ref": card.pinned_ref(),
                "content_id": card_content_id(card),
            }
            for role, card in roles
        },
        "facts": facts,
        "conflicts": {role: _conflicts(card, aspects) for role, card in roles},
        "unknowns": {role: _unknowns(card, aspects) for role, card in roles},
        "provenance": {role: _provenance(card) for role, card in roles},
    }
    # The packet is what its canonical JSON states, so a stored packet reads back
    # identical, with every quantity as a node.
    packet = KnowledgePacket(json.loads(canonical_json(as_stated(data))))
    from .attribution import _record_packet

    packet._attribution = _record_packet(packet, roles)
    return packet
