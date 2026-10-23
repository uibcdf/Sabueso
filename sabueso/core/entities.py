"""The glossary of molecular entities a card mentions (uibcdf/sabueso#52).

A card mentions entities under the records its sources use: a ligand as
``pdb.ligand:BTS`` in a ligand site and as ``chembl:CHEMBL1161789`` in a measurement, a
partner protein as ``uniprot:P01903`` or as a STRING id. ``build_entities`` lists each
molecular entity once, with every record the card mentions for it:

- key: the anchor when known (``uniprot:<acc>``, ``inchikey:<key>``), else the first
  record;
- ``entity_type``: protein, small_molecule or polymer (a chain without a UniProt entry);
- ``records``, ``names``, ``stated_types`` (as sources state them; Sabueso does not
  classify ions or lipids), ``parent_ref`` (the ChEMBL parent of a tested salt),
  ``appears_in`` (where the card mentions it) and ``identity`` (how and when an anchor
  was resolved, when it was).

Records merge into one entity only where a source states they are the same: PDBe-KB
naming a ligand's ChEMBL id, a resolved identity (a curated molecule's InChIKey and the
records UniChem links), a molecule card's ``same_as`` links. Relationships keep citing
the record their source gave (their provenance); ``resolve_ref`` finds its entity.

Structures, publications, GO terms and families are records, documents and concepts,
not molecular entities: they have their own views.

The glossary is derived from the card's relationships and the identities stored in
``card.entity_identities``; it is rebuilt deterministically whenever the card is stored.
"""

from __future__ import annotations

from typing import Any, Dict, List

#: Namespace order for choosing an entity's key and anchor.
ANCHORS = ("uniprot:", "inchikey:", "mondo:")
PREFERENCE = (
    "uniprot:",
    "inchikey:",
    "chembl:",
    "pdb.ligand:",
    "pubchem:",
    "string:",
    "pdbe_kb.partner:",
    "pdb.polymer:",
)


def _rank(ref: str) -> tuple:
    for i, prefix in enumerate(PREFERENCE):
        if ref.startswith(prefix):
            return (i, ref)
    return (len(PREFERENCE), ref)


class _Glossary:
    """Records grouped into entities by union-find over stated identities."""

    def __init__(self) -> None:
        self.parent: Dict[str, str] = {}
        self.info: Dict[str, Dict[str, Any]] = {}

    def _find(self, ref: str) -> str:
        self.parent.setdefault(ref, ref)
        while self.parent[ref] != ref:
            self.parent[ref] = self.parent[self.parent[ref]]
            ref = self.parent[ref]
        return ref

    def add(
        self,
        ref: str,
        entity_type: str,
        appears_in: str,
        name: str | None = None,
        stated_type: str | None = None,
        parent_ref: str | None = None,
    ) -> None:
        if not ref:
            return
        self._find(ref)
        info = self.info.setdefault(
            ref,
            {
                "types": set(),
                "names": set(),
                "stated": set(),
                "appears": set(),
                "parents": set(),
            },
        )
        info["types"].add(entity_type)
        info["appears"].add(appears_in)
        if name:
            info["names"].add(name)
        if stated_type:
            info["stated"].add(stated_type)
        if parent_ref and parent_ref != ref:
            info["parents"].add(parent_ref)

    def same(self, a: str, b: str) -> None:
        if a and b:
            self.parent[self._find(a)] = self._find(b)

    def entries(self, identities: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        groups: Dict[str, List[str]] = {}
        for ref in list(self.parent):
            groups.setdefault(self._find(ref), []).append(ref)
        out: Dict[str, Any] = {}
        for refs in groups.values():
            refs = sorted(refs, key=_rank)
            anchor = next((r for r in refs if r.startswith(ANCHORS)), None)
            infos = [self.info.get(r) or {} for r in refs]
            types = set().union(*(i.get("types", set()) for i in infos))
            entity_type = (
                "protein"
                if "protein" in types
                else "small_molecule"
                if "small_molecule" in types
                else sorted(types)[0]
                if types
                else "unknown"
            )
            parents = sorted(
                set().union(*(i.get("parents", set()) for i in infos)) - set(refs)
            )
            entry: Dict[str, Any] = {
                "entity_type": entity_type,
                "anchor": anchor,
                "records": [r for r in refs if r != anchor],
                "names": sorted(set().union(*(i.get("names", set()) for i in infos))),
                "stated_types": sorted(
                    set().union(*(i.get("stated", set()) for i in infos))
                ),
                "appears_in": sorted(
                    set().union(*(i.get("appears", set()) for i in infos))
                ),
                "identity": identities.get(anchor, {}).get("resolved")
                if anchor
                else None,
            }
            if parents:
                entry["parent_ref"] = parents[0] if len(parents) == 1 else parents
            out[anchor or refs[0]] = entry
        return dict(sorted(out.items()))


def _subject_ref(card: Any) -> str | None:
    card_id = card.meta.get("card_id") or ""
    prefix = f"sabueso:{card.meta.get('entity_type') or ''}:"
    return card_id[len(prefix) :] if card_id.startswith(prefix) else None


def build_entities(card: Any) -> Dict[str, Any]:
    """The card's glossary, derived from its relationships and stored identities."""
    g = _Glossary()
    subject = _subject_ref(card)
    entity_type = card.meta.get("entity_type") or "unknown"
    if subject:
        name = (card.get("names.canonical_name") or {}).get("value")
        g.add(subject, entity_type, "subject", name=name)
    for anchor, identity in (card.entity_identities or {}).items():
        g.add(anchor, identity.get("entity_type", "small_molecule"), "identity")
        for record in identity.get("records") or []:
            g.add(record, identity.get("entity_type", "small_molecule"), "identity")
            g.same(record, anchor)

    for rel in card.relationships():
        predicate, obj = rel["predicate"], rel["object_ref"]
        q = rel.get("qualifiers") or {}
        if predicate == "same_as" and (
            str(obj).startswith("mondo:") or q.get("source") == "MedGen"
        ):
            # A disease id MONDO states is the same disease as its term, or a MedGen
            # concept id and its record (#90).
            g.add(rel["subject_ref"], "disease", "same_as")
            g.add(obj, "disease", "same_as", name=q.get("mondo_name"))
            g.same(rel["subject_ref"], obj)
        elif predicate == "same_as":
            g.add(rel["subject_ref"], entity_type, "same_as")
            g.same(rel["subject_ref"], obj)
            g.add(obj, entity_type, "same_as", name=q.get("name"))
        elif predicate in ("interacts_with", "possibly_same_as", "isoform_of"):
            g.add(obj, "protein", predicate, name=q.get("partner_gene"))
        elif predicate == "functionally_associated_with":
            g.add(obj, "protein", predicate, name=q.get("partner_name"))
        elif predicate == "has_interface_with":
            kind = "protein" if q.get("partner_type") == "UNP" else "polymer"
            g.add(
                obj,
                kind,
                predicate,
                name=q.get("partner_name"),
                stated_type=q.get("partner_type"),
            )
        elif predicate == "has_structure":
            structure = obj.split(":", 1)[-1]
            for other in q.get("other_entities") or []:
                accessions = other.get("uniprot") or []
                if accessions:
                    for accession in accessions:
                        g.add(
                            f"uniprot:{accession}",
                            "protein",
                            predicate,
                            name=other.get("description"),
                        )
                else:
                    g.add(
                        f"pdb.polymer:{structure}_{other.get('polymer_entity')}",
                        "polymer",
                        predicate,
                        name=other.get("description"),
                    )
            ligands = q.get("ligands")
            for ligand in ligands if isinstance(ligands, list) else []:
                if not isinstance(ligand, dict):
                    continue
                if ligand.get("comp_id"):
                    g.add(
                        f"pdb.ligand:{ligand['comp_id']}",
                        "small_molecule",
                        predicate,
                        name=ligand.get("description"),
                    )
        elif predicate == "has_ligand_site":
            g.add(obj, "small_molecule", predicate, name=q.get("ligand_name"))
            for key, namespace in (
                ("chembl_id", "chembl"),
                ("drugbank_id", "drugbank"),
            ):
                if q.get(key):  # PDBe-KB states the ligand's record in that resource
                    ref = f"{namespace}:{q[key]}"
                    g.add(ref, "small_molecule", predicate)
                    g.same(ref, obj)
        elif predicate == "engages":
            g.add(obj, "small_molecule", predicate)
            if q.get("molecule_ref"):
                g.same(obj, q["molecule_ref"])
        elif predicate == "has_bioactivity":
            g.add(
                obj,
                "small_molecule",
                predicate,
                name=q.get("molecule_name"),
                parent_ref=q.get("parent_molecule"),
            )
            if q.get("parent_molecule") and q["parent_molecule"] != obj:
                g.add(q["parent_molecule"], "small_molecule", predicate)
            if q.get("molecule_ref"):
                g.same(obj, q["molecule_ref"])
    return g.entries(card.entity_identities or {})


def resolve_ref(card: Any, ref: str) -> tuple:
    """``(key, entry)`` of the entity a record belongs to, or ``(None, None)``."""
    entities = build_entities(card)
    if ref in entities:
        return ref, entities[ref]
    for key, entry in entities.items():
        if ref in entry["records"]:
            return key, entry
    return None, None
