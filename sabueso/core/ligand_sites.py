"""Ligand sites of a protein crossed with its annotated sites (uibcdf/sabueso#28).

A ProteinCard can hold independent statements about where things bind:

- the functional sites UniProt annotates (``features_positional.active_site`` and
  ``binding_site``), each with its ECO evidence and, for binding sites, its ligand;
- the sites InterPro member databases place on the sequence from their family models
  (``features_positional.family_site``, e.g. CDD's catalytic triad, substrate binding site
  and dimer interface);
- the residues each ligand contacts in experimental structures, from PDBe-KB
  (``has_ligand_site`` relationships), in UniProt numbering.

``ligand_sites_view`` puts them side by side. Whether a ligand site overlaps an annotated
site is derived knowledge, computed here with rule ``annotated_site_overlap@2``: an exact
match of residue positions in UniProt numbering, against every annotated site. It is
never stored. Each overlap names the annotation and its source, because overlapping a
catalytic triad and overlapping a dimer interface mean different things.

Absence states stay distinct. "No annotated overlap" is not "binds elsewhere": UniProt
annotations are sparse (four residues for TIM), and a ligand can bind next to an annotated
residue without contacting it. When the card has no annotated site at all, the class says
so instead. Proximity over coordinates is not computed here; see uibcdf/sabueso#30.

Whether one ligand contacts more than one chain can only be read from **instance-level**
contacts. PDBe-KB aggregates all copies of a ligand, and its per-residue chains cannot
tell one ligand touching two chains from two copies in two chains. The card holds
per-instance contacts (from RCSB) only for the structures it has fetched, so
``spans_chains`` is ``None`` when no instance-level data is available, never ``[]``.
"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Dict, List

# @1 compared UniProt sites only; @2 adds InterPro family sites (uibcdf/sabueso#28).
SITE_OVERLAP_RULE = "annotated_site_overlap@2"
INSTANCE_RULE = "ligand_instance_scope@1"
ANNOTATED_SITES = {
    "active_site": "features_positional.active_site",
    "binding_site": "features_positional.binding_site",
    "family_site": "features_positional.family_site",
}


def _key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def annotated_sites(card: Any) -> List[Dict[str, Any]]:
    """The card's annotated functional sites, with the evidence of each one."""
    out: List[Dict[str, Any]] = []
    for kind, field_path in ANNOTATED_SITES.items():
        node = card.get(field_path) or {}
        assertions = [
            card.source_assertion_store.get(i)
            for i in node.get("source_assertion_ids") or []
        ]
        by_value = {_key(a["asserted_value"]): a for a in assertions if a}
        for item in node.get("value") or []:
            sequence = (item.get("location") or {}).get("sequence") or {}
            spans = sequence.get("fragments") or (
                [{"start": sequence["start"], "end": sequence.get("end")}]
                if sequence.get("start") is not None
                else []
            )
            positions = _positions(spans)
            if not positions:
                continue
            assertion = by_value.get(_key(item)) or {}
            signature = item.get("signature") or {}
            out.append(
                {
                    "kind": kind,
                    "start": positions[0],
                    "end": positions[-1],
                    "positions": positions,
                    "description": item.get("description") or None,
                    "ligand": item.get("ligand"),
                    "source": (assertion.get("source") or {}).get("name"),
                    "signature": signature.get("accession"),
                    "evidence": [
                        e.get("code")
                        for e in (assertion.get("source_metadata") or {}).get("eco")
                        or []
                    ],
                    "source_assertion_id": assertion.get("id"),
                }
            )
    return sorted(out, key=lambda s: (s["start"], s["kind"], s["description"] or ""))


def _positions(residues: List[Dict[str, Any]]) -> List[int]:
    return sorted(
        {p for r in residues for p in range(r["start"], (r["end"] or r["start"]) + 1)}
    )


def _structure_statements(card: Any, code: str) -> tuple:
    """PDB flags and per-instance contacts of this ligand in the card's structures."""
    flags: Dict[str, Any] = {}
    instances: List[Dict[str, Any]] = []
    relationships = set()
    for rel in card.relationships("has_structure"):
        for ligand in rel.get("qualifiers", {}).get("ligands") or []:
            if ligand.get("comp_id") != code:
                continue
            relationships.add(rel["id"])
            flags[rel["object_ref"]] = ligand.get("subject_of_investigation")
            for instance in ligand.get("instances") or []:
                instances.append(
                    {
                        "structure_ref": rel["object_ref"],
                        "relationship_id": rel["id"],
                        "sequence_ref": rel["subject_ref"],
                        "asym_id": instance.get("asym_id"),
                        "chains": deepcopy(instance.get("chains") or []),
                        "chain_scope": "recorded"
                        if instance.get("chains")
                        and all(
                            isinstance(chain, str) and chain
                            for chain in instance["chains"]
                        )
                        else "unknown",
                        "positions": sorted(
                            {
                                c["position"]
                                for c in instance.get("contacts") or []
                                if c.get("position") is not None
                                and f"uniprot:{c.get('uniprot')}" == rel["subject_ref"]
                            }
                        ),
                        "unplaced_contacts": deepcopy(
                            [
                                c
                                for c in instance.get("contacts") or []
                                if c.get("position") is None
                                or f"uniprot:{c.get('uniprot')}" != rel["subject_ref"]
                            ]
                        ),
                    }
                )
    instances.sort(key=lambda i: (i["structure_ref"], str(i["asym_id"])))
    return dict(sorted(flags.items())), instances, sorted(relationships)


def site_overlap_derivation() -> Dict[str, Any]:
    from .relationship_store import make_derivation

    return make_derivation(
        SITE_OVERLAP_RULE,
        inputs=[
            "has_ligand_site.residues",
            ANNOTATED_SITES["active_site"],
            ANNOTATED_SITES["binding_site"],
            ANNOTATED_SITES["family_site"],
        ],
        parameters={"match": "exact residue position", "numbering": "uniprot"},
    )


def _chain_spans(instances):
    """ligand_instance_scope@1: unidentified occurrences cannot prove a span."""
    identified = [
        i
        for i in instances
        if isinstance(i.get("asym_id"), str)
        and i["asym_id"]
        and i.get("chains")
        and i.get("chain_scope", "recorded") == "recorded"
    ]
    spans = sorted({i["structure_ref"] for i in identified if len(i["chains"]) > 1})
    return spans if spans or instances and len(identified) == len(instances) else None


def ligand_sites_view(card: Any) -> Dict[str, Any]:
    """Each ligand site of the card next to the card's annotated sites.

    Returns ``{"items", "curated_engagements", "annotated_sites", "classification"}``. Each item holds the
    ligand, its contacted positions (PDBe-KB, over all structures), the per-instance
    contacts of the structures the card holds (RCSB) and the structures where one
    instance contacts more than one chain, the relevance statements of both sources
    (PDBe-KB ``is_solvent`` and ``significance``; the PDB ``subject_of_investigation``
    flag), and the annotated sites its positions overlap.
    """
    annotated = annotated_sites(card)
    items: List[Dict[str, Any]] = []
    for rel in card.relationships("has_ligand_site"):
        q = rel.get("qualifiers", {})
        positions = _positions(q.get("residues") or [])
        code = rel["object_ref"].split(":", 1)[1]
        flags, instances, structure_relationships = _structure_statements(card, code)
        overlap = [
            {**site, "matched": sorted(set(site["positions"]) & set(positions))}
            for site in annotated
            if set(site["positions"]) & set(positions)
        ]
        if q.get("numbering") != "uniprot":
            site_class = "numbering_not_comparable"
            overlap = []
        elif not annotated:
            site_class = "no_annotated_sites"
        else:
            site_class = (
                "overlaps_annotated_site" if overlap else "no_annotated_overlap"
            )
        items.append(
            {
                "ligand_ref": rel["object_ref"],
                "name": q.get("ligand_name"),
                "positions": positions,
                "residues": [
                    {"position": r["start"], "residue": r["residue"]}
                    for r in q.get("residues") or []
                ],
                "structures": q.get("structures") or [],
                "instances": instances,
                "spans_chains": _chain_spans(instances),
                "instance_rule": INSTANCE_RULE,
                "is_solvent": q.get("is_solvent"),
                "significance": q.get("significance"),
                "subject_of_investigation": flags,
                "structure_support": {
                    "basis": "relationship_level",
                    "relationship_ids": structure_relationships,
                },
                "annotated_overlap": [
                    {
                        k: site[k]
                        for k in (
                            "kind",
                            "start",
                            "end",
                            "description",
                            "source",
                            "signature",
                            "matched",
                        )
                    }
                    for site in overlap
                ],
                "site_class": site_class,
                "relationship_id": rel["id"],
            }
        )
    items.sort(key=lambda i: i["ligand_ref"])
    # What papers state about how compounds act on residues (#61), next to what the
    # structures show; each keeps its source.
    curated = [
        {
            "molecule_ref": (rel.get("qualifiers") or {}).get("molecule_ref"),
            "ligand_ref": rel["object_ref"],
            "positions": [
                r["position"] for r in rel["qualifiers"].get("residues") or []
            ],
            "residues": rel["qualifiers"].get("residues"),
            "mechanism": rel["qualifiers"].get("mechanism"),
            "covalent_residue": rel["qualifiers"].get("covalent_residue"),
            "method": rel["qualifiers"].get("method"),
            "publication": rel["qualifiers"].get("publication"),
            "relationship_id": rel["id"],
        }
        for rel in card.relationships("engages")
    ]
    return {
        "items": items,
        "curated_engagements": sorted(
            curated, key=lambda c: (c["ligand_ref"], c["relationship_id"])
        ),
        "annotated_sites": annotated,
        "classification": site_overlap_derivation(),
    }
