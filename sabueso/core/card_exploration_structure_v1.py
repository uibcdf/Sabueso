"""Frozen v1 expected-record predicates for saved-science consistency checks.

Baseline: Sabueso 2c32d7f, named rules in the constants below. These private
predicates compare retained decisions at their original inputs; they never replace
saved knowledge, call ordinary scientific readers or consult current catalogs.
Evolving semantics requires a new historical verifier/version, not editing v1.
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Dict, List, Sequence

from .card_exploration_history import _rule
from .errors import ArgumentError
from .quantities import to_quantity

COVERAGE_CLASS_RULE = "structure_coverage_class@1"

COVERAGE_THRESHOLDS = {"full_length_min": 0.9, "partial_min": 0.3}

METHOD_ALIASES = {
    "X-RAY DIFFRACTION": "X-ray",
    "ELECTRON MICROSCOPY": "EM",
    "SOLUTION NMR": "NMR",
    "SOLID-STATE NMR": "NMR",
    "NEUTRON DIFFRACTION": "Neutron",
    "FIBER DIFFRACTION": "Fiber",
}

STATE_RULE = "structure_state@2"

INVENTORY_RULE = "structure_inventory@1"

STATE_KEYS = ("method", "coverage", "sequence", "ligands", "oligomer", "in_complex")

GROUP_KEYS = STATE_KEYS + ("ligands:interest", "substitutions")

_LIGANDS_OF_INTEREST = {
    "ligand_of_interest": "ligand_of_interest",
    "no_ligand_of_interest": "none_of_interest",
    "no_ligands": "none_of_interest",
    "unstated": "unstated",
}

_SUBSTITUTION = re.compile("^([A-Z])(\\d+)([A-Z])$")
EXPLANATION_RULE = "structure_inventory_explanation@1"


def _v1_author_position(segments: List[list] | None, position: int) -> str | None:
    """The author residue id of a UniProt position, from ``author_numbering`` segments."""
    for beg, end, author in segments or []:
        if beg <= position <= end:
            return str(author + (position - beg)) if isinstance(author, int) else author
    return None


def _v1_normalize_methods(methods: Sequence[str]) -> str | None:
    """One method label, e.g. ['X-RAY DIFFRACTION'] -> 'X-ray'; hybrids joined by '+'."""
    labels = sorted({METHOD_ALIASES.get(m.upper(), m) for m in methods if m})
    return "+".join(labels) if labels else None


def _v1_merge_ranges(ranges: Sequence[Sequence[int]]) -> List[List[int]]:
    """Sorted, non-overlapping inclusive ranges."""
    merged: List[List[int]] = []
    for beg, end in sorted(((int(b), int(e)) for b, e in ranges)):
        if merged and beg <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([beg, end])
    return merged


def _v1_coverage(ranges: Sequence[Sequence[int]], length: int | None) -> float | None:
    """Fraction of a reference sequence of ``length`` residues covered by ``ranges``."""
    if not length or not ranges:
        return None
    covered = sum((end - beg + 1 for beg, end in _v1_merge_ranges(ranges)))
    return round(min(covered / length, 1.0), 3)


def _v1_coverage_class(value: float | None) -> str | None:
    if value is None:
        return None
    if value >= COVERAGE_THRESHOLDS["full_length_min"]:
        return "full_length"
    if value >= COVERAGE_THRESHOLDS["partial_min"]:
        return "partial"
    return "fragment_or_peptide"


def _v1_coverage_derivation() -> Dict[str, Any]:
    return _rule(
        COVERAGE_CLASS_RULE,
        inputs=["has_structure.coverage"],
        parameters=dict(COVERAGE_THRESHOLDS),
    )


def _v1_state_derivation() -> Dict[str, Any]:
    return _rule(
        STATE_RULE,
        inputs=[
            "has_structure.mutations",
            "has_structure.sequence_differences",
            "has_structure.chimeric_with",
            "has_structure.ligands",
            "has_structure.assemblies",
            "has_structure.other_entities",
            "has_structure.observed",
        ],
        parameters={
            "sequence": {
                "mutant": "RCSB states an engineered mutation",
                "chimera": "the entities also map to other proteins",
                "differs": "aligned residues differ from the reference sequence, none stated as engineered (a variant, a conflict or unannotated)",
                "reference": "no difference and no engineered mutation",
            },
            "ligands": "PDB subject-of-investigation flag",
            "oligomer": "RCSB global symmetry of the author-defined assemblies, else of the software-defined ones; disagreement between the two is flagged",
            "unknown": "None: the structure was not fetched from RCSB with these data",
        },
    )


def _v1_sequence_state(q: Dict[str, Any]) -> tuple:
    """(state, substitutions, modified residues) of a has_structure relationship."""
    if "mutations" not in q:
        return (None, None, None)
    mutations = q.get("mutations") or []
    differences = q.get("sequence_differences")
    stated = [
        m
        for m in mutations
        if m.get("reference") and m.get("residue") and (m["reference"] != m["residue"])
    ]
    changed = differences if differences is not None else stated
    substitutions = sorted(
        {f"{d['reference']}{d['position']}{d['residue']}" for d in changed},
        key=lambda label: int("".join((c for c in label if c.isdigit())) or 0),
    )
    modified = sorted(
        {
            f"{m['reference']}{m['position']}"
            for m in mutations
            if m.get("name") != "engineered mutation"
            and m.get("reference")
            and (m.get("reference") == m.get("residue"))
        }
    )
    if q.get("chimeric_with"):
        state = "chimera"
    elif any((m.get("name") == "engineered mutation" for m in mutations)):
        state = "mutant"
    elif substitutions:
        state = "differs"
    elif differences is None:
        state = None
    else:
        state = "reference"
    return (state, substitutions, modified)


def _v1_oligomer(assemblies: List[Dict[str, Any]] | None) -> Dict[str, Any]:
    """The oligomeric state of a structure (rule ``structure_state@2``).

    RCSB states who defined each assembly: the authors, software (e.g. PISA), or both.
    The state comes from the assemblies the authors defined, since they state what the
    structure was determined to show; from the software's when the authors defined none.
    Several distinct states are joined with " / ". A software assembly whose state the
    authors' do not include is a disagreement, flagged and never resolved.
    """
    if not assemblies:
        return {"state": None, "basis": None, "disagreement": None, "by_basis": None}
    author = sorted(
        {
            a["oligomeric_state"]
            for a in assemblies
            if a.get("oligomeric_state") and "author" in str(a.get("defined_by") or "")
        }
    )
    software = sorted(
        {
            a["oligomeric_state"]
            for a in assemblies
            if a.get("oligomeric_state")
            and "software" in str(a.get("defined_by") or "")
        }
    )
    chosen, basis = (author, "author") if author else (software, "software")
    if not chosen:
        chosen = sorted(
            {a["oligomeric_state"] for a in assemblies if a.get("oligomeric_state")}
        )
        basis = None
    return {
        "state": " / ".join(chosen) if chosen else None,
        "basis": basis,
        "disagreement": bool(author and software and set(software) - set(author)),
        "by_basis": {"author": author, "software": software},
    }


def _v1_ligand_state(ligands: List[Dict[str, Any]] | None) -> str | None:
    if ligands is None:
        return None
    if not ligands:
        return "no_ligands"
    flags = [lig.get("subject_of_investigation") for lig in ligands]
    if any((flag is True for flag in flags)):
        return "ligand_of_interest"
    if all((flag is False for flag in flags)):
        return "no_ligand_of_interest"
    return "unstated"


def _v1_author_substitutions(
    q: Dict[str, Any], substitutions: List[str] | None
) -> List[str] | None:
    """The substitutions in the authors' numbering (#73), e.g. ``E104D`` for UniProt
    ``E105D``, read from the first chain that numbers the position. None without author
    numbering; ``?`` for a position no chain numbers."""
    numbering = q.get("author_numbering")
    if substitutions is None or not numbering:
        return None
    out = []
    for label in substitutions:
        match = _SUBSTITUTION.match(label)
        if not match:
            continue
        position = int(match.group(2))
        author = next(
            (
                a
                for chain in sorted(numbering)
                if (a := _v1_author_position(numbering[chain], position)) is not None
            ),
            "?",
        )
        out.append(f"{match.group(1)}{author}{match.group(3)}")
    return out


def _v1_missing(
    q: Dict[str, Any], region: Sequence[int] | None
) -> Dict[str, List[int]] | None:
    """Per chain, the region's positions without coordinates in that chain."""
    observed = q.get("observed")
    if region is None or observed is None:
        return None
    out = {}
    for chain, ranges in sorted(observed.items()):
        have = {p for beg, end in ranges for p in range(beg, end + 1)}
        out[chain] = [p for p in region if p not in have]
    return out


def _v1_secondary_in_region(
    q: Dict[str, Any], region: Sequence[int] | None
) -> Dict[str, Dict[str, List[int]]] | None:
    """Per chain, the region's positions the entry assigns to a helix or a strand (#80).
    A chain the entry assigns nothing to is left out: not stated, never coil."""
    secondary = q.get("secondary_structure")
    if region is None or secondary is None:
        return None
    out = {}
    for chain, item in sorted(secondary.items()):
        out[chain] = {
            element: [
                p
                for p in region
                if any((b <= p <= e for b, e in item.get(element, [])))
            ]
            for element in ("helix", "strand")
        }
    return out


def _v1_structures_view(
    card: Any, include_fragments: bool = False, region: Sequence[int] | None = None
) -> Dict[str, Any]:
    """Protein-centric summary of the card's ``has_structure`` relationships.

    Returns ``{"items", "excluded", "classification", "state_rule"}``. Fragments and
    peptides are excluded by default, and the exclusion is reported, never silent.
    ``region`` (UniProt positions) adds, per chain, the region's residues without
    coordinates (``missing_in_region``), the chains that have them all
    (``complete_chains``), and the region's positions in a helix or a strand
    (``secondary_structure_in_region``).
    """
    items: List[Dict[str, Any]] = []
    excluded: List[str] = []
    for rel in card.relationships(predicate="has_structure"):
        q = rel.get("qualifiers", {})
        sequence_state, substitutions, modified = _v1_sequence_state(q)
        assemblies = q.get("assemblies")
        refinement = [r for r in q.get("refinement") or [] if r.get("r_free")]
        missing = _v1_missing(q, region)
        oligomer = _v1_oligomer(assemblies)
        summary = {
            "structure_ref": rel["object_ref"],
            "relationship_id": rel["id"],
            "method": q.get("method"),
            "resolution": to_quantity(q["resolution"]) if q.get("resolution") else None,
            "chains": q.get("chains"),
            "ranges": q.get("ranges"),
            "coverage": q.get("coverage"),
            "coverage_class": _v1_coverage_class(q.get("coverage")),
            "other_entities": q.get("other_entities"),
            "ligands": q.get("ligands"),
            "sources": sorted(
                {
                    card.source_assertion_store.get(sa)["source"]["name"]
                    for sa in rel.get("source_assertion_ids", [])
                    if card.source_assertion_store.get(sa)
                }
            ),
            "qualifier_conflicts": rel.get("qualifier_conflicts"),
            "released": q.get("released"),
            "r_free": refinement[0]["r_free"] if refinement else None,
            "substitutions": substitutions,
            "author_substitutions": _v1_author_substitutions(q, substitutions),
            "author_numbering": q.get("author_numbering"),
            "secondary_structure": q.get("secondary_structure"),
            "modified_residues": modified,
            "ligands_of_interest": None
            if q.get("ligands") is None
            else sorted(
                {
                    lig["comp_id"]
                    for lig in q["ligands"]
                    if lig.get("subject_of_investigation") and lig.get("comp_id")
                }
            ),
            "expression_host": None
            if q.get("construct") is None
            else sorted(
                {
                    h["name"]
                    for c in q["construct"]
                    for h in c.get("expression_host") or []
                    if h.get("name")
                }
            ),
            "observed": q.get("observed"),
            "oligomer_basis": oligomer["basis"],
            "oligomer_disagreement": oligomer["disagreement"],
            "assembly_states": oligomer["by_basis"],
            "missing_in_region": missing,
            "secondary_structure_in_region": _v1_secondary_in_region(q, region),
            "complete_chains": None
            if missing is None
            else sorted((chain for chain, gaps in missing.items() if not gaps)),
            "state": {
                "method": q.get("method"),
                "coverage": _v1_coverage_class(q.get("coverage")),
                "sequence": sequence_state,
                "ligands": _v1_ligand_state(q.get("ligands")),
                "oligomer": oligomer["state"],
                "in_complex": bool(q["other_entities"])
                if "other_entities" in q
                else None,
            },
        }
        if summary["coverage_class"] == "fragment_or_peptide" and (
            not include_fragments
        ):
            excluded.append(rel["object_ref"])
            continue
        items.append(summary)
    items.sort(key=lambda s: s["structure_ref"])
    return {
        "items": items,
        "excluded": sorted(excluded),
        "classification": _v1_coverage_derivation(),
        "state_rule": _v1_state_derivation(),
    }


def _v1_in_reference(
    labels: List[str] | None, mapping: Dict[int, int] | None
) -> List[Dict[str, Any]] | None:
    """Substitutions as ``{position, reference_position, residue, label}``; the reference
    position is None when the card has no map, or its map does not cover the position."""
    if labels is None:
        return None
    out = []
    for label in labels:
        match = _SUBSTITUTION.match(label)
        if not match:
            continue
        position = int(match.group(2))
        out.append(
            {
                "label": label,
                "position": position,
                "reference_position": None
                if mapping is None
                else mapping.get(position),
                "residue": match.group(3),
            }
        )
    return out


def _v1_structure_inventory(
    cards: Sequence[Any],
    regions: Any = None,
    include_fragments: bool = False,
    group_by: Sequence[str] | None = None,
    residue_maps: Dict[str, Dict[int, int]] | None = None,
    reference: str | None = None,
) -> Dict[str, Any]:
    """The experimental structures of several proteins, side by side, grouped by state.

    Each protein's structures are summarised as in ``Card.structures()``. Structures
    in the same state (coverage class, sequence, ligands, oligomer, complex) are listed
    together, one list per protein, so that like can be compared with like. A state
    shared by every protein is marked ``shared``. Structures whose state is unknown,
    because they were not fetched from RCSB with the data a state needs, are listed
    apart (``not_inventoried``) with the reason: ``not_requested`` (build the card with
    ``structures="all"``), ``not_found`` or ``error`` (RCSB did not answer), or
    ``fetched_without_state`` (a card built before schema 0.3.4: refresh it).

    ``regions`` is one region (UniProt positions and ranges) for every card, or
    ``{card_id: region}``, since numbering differs between proteins.

    ``group_by`` chooses the keys of a group, among ``GROUP_KEYS`` (default: every state
    key, ``STATE_KEYS``). ``residue_maps`` (``{card_id: {position: reference position}}``,
    e.g. from a MolSysMT alignment) places each card's substitutions in the numbering of
    the ``reference`` card, whose own positions need no map. Substitutions at one
    reference position with one residue, in several proteins, are then listed
    (``shared_substitutions``), and ``substitutions`` groups them together. Equal numbers
    in two proteins are never taken as equivalent positions: a card without a map keeps
    its own numbering, and its substitutions match no other card's.

    Choosing a structure stays with the reader; the inventory states facts and groups
    them by a named rule, whose parameters record the choices above.
    """
    keys = tuple(group_by) if group_by else STATE_KEYS
    maps = {card_id: dict(m) for card_id, m in (residue_maps or {}).items()}
    if reference is not None:
        maps.setdefault(reference, None)
    items: List[Dict[str, Any]] = []
    not_inventoried: Dict[str, List[Dict[str, str]]] = {}
    excluded: Dict[str, List[str]] = {}
    states: Dict[tuple, Dict[str, List[str]]] = {}
    substituted: Dict[tuple, Dict[str, set]] = {}
    ids = [card.id for card in cards]
    for card in cards:
        region = regions.get(card.id) if isinstance(regions, dict) else regions
        fetched = {
            f"pdb:{e['structure']}": e.get("status")
            for e in card.quality.get("enrichments") or []
            if e.get("source") == "RCSB PDB" and e.get("structure")
        }
        if card.id == reference:
            mapping = None
            in_frame = True
        else:
            mapping = maps.get(card.id)
            in_frame = mapping is not None
        view = _v1_structures_view(
            card, include_fragments=include_fragments, region=region
        )
        if view["excluded"]:
            excluded[card.id] = view["excluded"]
        for item in view["items"]:
            state = dict(item["state"])
            mapped = _v1_in_reference(item.get("substitutions"), mapping)
            if card.id == reference and mapped is not None:
                for m in mapped:
                    m["reference_position"] = m["position"]
            row = {"card_id": card.id, **item, "substitutions_in_reference": mapped}
            items.append(row)
            if state["sequence"] is None:
                status = fetched.get(item["structure_ref"])
                reason = {None: "not_requested", "added": "fetched_without_state"}.get(
                    status, status
                )
                not_inventoried.setdefault(card.id, []).append(
                    {"structure_ref": item["structure_ref"], "reason": reason}
                )
                continue
            state["ligands:interest"] = _LIGANDS_OF_INTEREST.get(state["ligands"])
            state["substitutions"] = tuple(
                sorted(
                    (
                        (m["reference_position"], m["residue"])
                        if in_frame and m["reference_position"] is not None
                        else (card.id, m["label"])
                        for m in mapped or []
                    )
                )
            )
            for m in mapped or []:
                if in_frame and m["reference_position"] is not None:
                    found = substituted.setdefault(
                        (m["reference_position"], m["residue"]), {}
                    )
                    found.setdefault(card.id, set()).add(item["structure_ref"])
            key = tuple((state[k] for k in keys))
            states.setdefault(key, {}).setdefault(card.id, []).append(
                item["structure_ref"]
            )

    def shown(key: str, value: Any) -> Any:
        if key != "substitutions":
            return value
        return [
            f"{pos}{res}" if isinstance(pos, int) else f"{res} ({pos})"
            for pos, res in value
        ]

    grouped = [
        {
            "state": {k: shown(k, v) for k, v in zip(keys, key)},
            "structures": {i: sorted(by_card.get(i, [])) for i in ids},
            "shared": all((by_card.get(i) for i in ids)),
        }
        for key, by_card in states.items()
    ]
    grouped.sort(key=lambda g: (not g["shared"], [str(v) for v in g["state"].values()]))
    shared_substitutions = [
        {
            "reference_position": position,
            "residue": residue,
            "structures": {i: sorted(found[i]) for i in ids if i in found},
        }
        for (position, residue), found in sorted(substituted.items())
        if len(found) > 1
    ]
    parameters: Dict[str, Any] = {"state": list(keys), "state_rule": STATE_RULE}
    if residue_maps or reference:
        parameters["reference"] = reference
        parameters["mapped"] = sorted((c for c in maps if c != reference))
    return {
        "rule": _rule(INVENTORY_RULE, inputs=["has_structure"], parameters=parameters),
        "items": items,
        "states": grouped,
        "shared_substitutions": shared_substitutions,
        "not_inventoried": not_inventoried,
        "excluded": excluded,
    }


def _v1_support(card: Any, relationship: Dict[str, Any], pin: str) -> Dict[str, Any]:
    """Relationship-level support, never invented attribution per qualifier.

    Reference fields describe the pinned card's context. They do not claim to recover
    the exact inputs of a mapping performed when the card was built.
    """

    def assertions(ids):
        return [
            {**record, "source_assertion_ref": f"{pin}#{record['id']}"}
            for record in card.explain(ids, skip_digestion=True)
        ]

    context = []
    for path in ("sequence.length", "sequence.primary"):
        node = card.get(path)
        if node is not None:
            context.append(
                {
                    "field_path": path,
                    "node": node,
                    "source_assertions": assertions(
                        node.get("source_assertion_ids", [])
                    ),
                    "conflicts": [
                        record
                        for record in card.quality.get("conflicts") or []
                        if record.get("field") == path
                    ],
                }
            )
    return {
        "card_ref": pin,
        "structure_ref": relationship["object_ref"],
        "relationship_ref": f"{pin}#{relationship['id']}",
        "relationship": relationship,
        "support_basis": "relationship",
        "source_assertions": assertions(relationship.get("source_assertion_ids", [])),
        "reference_context": {"basis": "stored_card_fields", "fields": context},
        "enrichments": [
            record
            for record in card.quality.get("enrichments") or []
            if record.get("source") == "RCSB PDB"
            and f"pdb:{record.get('structure')}" == relationship["object_ref"]
        ],
    }


def _v1_explain_structure_inventory(
    cards: Sequence[Any],
    card_id: str,
    structure_ref: str,
    inventory: Dict[str, Any],
    *,
    regions: Any = None,
    include_fragments: bool = False,
    residue_maps: Any = None,
    reference: str | None = None,
) -> Dict[str, Any]:
    """Explain one item and the support of every member of its group.

    The complete options and every protein card's pin identify what was read, including
    cards lacking a member of the group. A missing relationship means ``not_on_card``,
    never that the structure does not exist. Unknown or excluded states keep the
    inventory's reasons. Returned records are detached from the cards.
    """
    proteins = [c for c in cards if c.meta.get("entity_type") == "protein"]
    by_id = {c.id: c for c in proteins}
    if len(by_id) != len(proteins):
        raise ArgumentError(
            argument="card_id",
            value=card_id,
            caller="Deck.explain",
            reason="an inventory explanation requires distinct protein card ids",
        )
    pins = {c.id: c.pinned_ref() for c in proteins}
    out = {
        "rule": _rule(
            EXPLANATION_RULE,
            inputs=list(pins.values()),
            parameters={
                "card_id": card_id,
                "structure_ref": structure_ref,
                "regions": regions,
                "include_fragments": include_fragments,
                "group_by": inventory["rule"]["parameters"]["state"],
                "residue_maps": residue_maps,
                "reference": reference,
            },
        ),
        "card_id": card_id,
        "card_ref": pins.get(card_id),
        "structure_ref": structure_ref,
        "status": "not_on_card",
        "reason": "no_has_structure_relationship",
        "item": None,
        "group": None,
        "rules": [_v1_coverage_derivation(), _v1_state_derivation(), inventory["rule"]],
        "members": [],
    }
    card = by_id.get(card_id)
    if card is None:
        out["status"] = "not_inventoried"
        out["reason"] = (
            "not_protein"
            if any((c.id == card_id for c in cards))
            else "card_not_in_deck"
        )
        return deepcopy(out)
    relationships = card.relationships("has_structure", object_ref=structure_ref)
    if not relationships:
        return deepcopy(out)
    (relationship,) = relationships
    out["members"] = [_v1_support(card, relationship, pins[card_id])]
    out["item"] = next(
        (
            row
            for row in inventory["items"]
            if row["card_id"] == card_id and row["structure_ref"] == structure_ref
        ),
        None,
    )
    if structure_ref in inventory["excluded"].get(card_id, []):
        out["status"], out["reason"] = ("excluded", "fragment_or_peptide")
        region = regions.get(card_id) if isinstance(regions, dict) else regions
        out["item"] = next(
            (
                item
                for item in _v1_structures_view(
                    card, include_fragments=True, region=region
                )["items"]
                if item["structure_ref"] == structure_ref
            )
        )
    else:
        group = next(
            (
                group
                for group in inventory["states"]
                if structure_ref in group["structures"].get(card_id, [])
            ),
            None,
        )
        if group is None:
            out["status"] = "not_inventoried"
            out["reason"] = next(
                (
                    row["reason"]
                    for row in inventory["not_inventoried"].get(card_id, [])
                    if row["structure_ref"] == structure_ref
                )
            )
        else:
            out["status"], out["reason"], out["group"] = ("grouped", None, group)
            out["members"] = [
                _v1_support(by_id[member_id], rel, pins[member_id])
                for member_id, refs in group["structures"].items()
                for ref in refs
                for rel in by_id[member_id].relationships(
                    "has_structure", object_ref=ref
                )
            ]
    return deepcopy(out)
