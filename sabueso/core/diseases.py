"""A protein's diseases, grouped across sources by stated identity (#90).

Diseases reach a protein card from several sources, each with its own ids:

- ``associated_with`` relationships: DISEASES (``doid:``), Open Targets (``mondo:``,
  ``efo:``) and Orphanet (``orphanet:ORPHA:``), one id each;
- UniProt's ``annotations.disease``, through the MIM id it states for each disease;
- ClinVar's ``annotations.clinical_variants``: each condition of a variant is **one**
  statement with every id ClinVar states for it (MedGen, OMIM, Orphanet, MONDO…).
  ClinVar states that those ids name the same condition.

``disease_statements`` lists them. Two enrichments then state identity, each as a
``same_as`` relationship backed by its source's SourceAssertion:
- ``medgen``: which MedGen record (UID) each MedGen concept id is, as MedGen states it
  (``MEDGEN:C1860808`` → ``MEDGEN:349893``, rule ``medgen_concept@1``);
- ``disease_identity``: which ids MONDO states are the same disease as one of its terms
  (→ ``mondo:<term>``, rule ``mondo_equivalence@1``), MedGen UIDs included.

The historical rule ``disease_grouping@1`` groups statements by MONDO term as follows.
It remains available through an explicit ``grouping_rule`` selector. Historical
``disease_grouping@2`` retains every stored identity path, rejects conflicting
targets of one identifier before granularity, and preserves unfinished MedGen
branches and alternative labels/paths (see :mod:`sabueso.core.disease_grouping`).
The development default ``disease_grouping@3`` adds identifier-scoped coverage
(``disease_identity_coverage@1``). Missing/failed or unscoped request records never
establish a source-stated lack of equivalence. Both older rules remain explicit.

Historical behavior:
- a statement joins a MONDO term when one of its ids is that term, or reaches it
  through the stated ``same_as`` chain. Nothing groups by name;
- a statement whose ids reach several terms joins the broadest one when MONDO places
  every other term under it (``subclass_of``, ``mondo_hierarchy@1``, recorded by
  ``disease_identity``). The source named the disease at two granularities. What holds
  for a subtype holds for the disease it belongs to, and the reverse does not: ClinVar
  names "Obesity" with the Orphanet id of obesity due to MC4R deficiency. The narrower
  terms are kept in the statement (``narrower``), with MONDO's chain;
- otherwise the statement is not grouped: it is reported as ``conflicting_identity``,
  with every term, and none is chosen;
- ClinVar's placeholders are not diseases: "not provided" (MedGen C3661900) and "not
  specified" (CN169374) are ``condition_not_provided``;
- what reaches no term stays apart with its reason: ``no_stated_equivalence``,
  ``obsolete_term``, ``namespace_not_mapped`` (e.g. a phenotype term), ``no_id_stated``
  (a condition named only by text), or ``identity_not_queried`` when
  ``disease_identity`` was not asked.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from .relationship_store import make_derivation

RULE = "disease_grouping@3"
LEGACY_RULE = "disease_grouping@1"
#: ClinVar's condition placeholders, by the MedGen concept ids it uses for them.
CLINVAR_PLACEHOLDERS = {
    "MEDGEN:C3661900": "not provided",
    "MEDGEN:CN169374": "not specified",
}


def disease_statements(
    get: Callable[[str], Any], relationships: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Every statement naming a disease: ``{refs, curies, unmapped, source, kind, ...}``.

    ``get(path)`` returns a field's value; ``relationships`` are the card's."""
    from sabueso.tools.db.mondo import normalize

    out: List[Dict[str, Any]] = []

    def add(refs: List[str], **statement: Any) -> None:
        curies = [normalize(r) for r in refs]
        out.append(
            {
                "refs": refs,
                "curies": [c for c in curies if c],
                "unmapped": [r for r, c in zip(refs, curies) if not c],
                **{k: v for k, v in statement.items() if v is not None},
            }
        )

    for rel in relationships:
        if rel.get("predicate") != "associated_with":
            continue
        q = rel.get("qualifiers") or {}
        add(
            [rel["object_ref"]],
            source=q.get("source"),
            kind="association",
            channel=q.get("channel"),
            name=q.get("disease_name"),
            relationship_id=rel.get("id"),
        )
    for item in get("annotations.disease") or []:
        for xref in item.get("cross_references") or []:
            if xref.get("database") == "MIM" and xref.get("id"):
                add(
                    [f"omim:{xref['id']}"],
                    source="UniProt",
                    kind="uniprot_disease",
                    name=item.get("name"),
                    accession=item.get("accession"),
                )
    for variant in get("annotations.clinical_variants") or []:
        for index, condition in enumerate(variant.get("conditions") or []):
            add(
                list(condition.get("xrefs") or []),
                source="ClinVar",
                kind="clinvar_condition",
                name=condition.get("name"),
                variant=variant.get("accession"),
                condition=index,
            )
    return out


def _card_statements(card: Any) -> List[Dict[str, Any]]:
    def get(path: str) -> Any:
        node = card.get(path)
        return node.get("value") if isinstance(node, dict) else None

    return disease_statements(get, card.relationships())


def _same_as(card: Any, source: str) -> Dict[str, Dict[str, Any]]:
    return {
        rel["subject_ref"]: rel
        for rel in card.relationships("same_as")
        if (rel.get("qualifiers") or {}).get("source") == source
    }


def diseases_view(card: Any, grouping_rule: str = RULE) -> Dict[str, Any]:
    """Read a versioned grouping view; historical lookup is available explicitly."""
    if grouping_rule == LEGACY_RULE:
        return _legacy_diseases_view(card)
    if grouping_rule not in {"disease_grouping@2", RULE}:
        raise ValueError(f"Unsupported disease grouping rule: {grouping_rule}")
    from .disease_grouping import diseases_view_v2, diseases_view_v3

    return (
        diseases_view_v2(card)
        if grouping_rule == "disease_grouping@2"
        else diseases_view_v3(card)
    )


def _legacy_diseases_view(card: Any) -> Dict[str, Any]:
    """The card's disease statements grouped by MONDO term; see the module docstring."""
    mondo_of = _same_as(card, "MONDO")
    narrower_of: Dict[str, Dict[str, List[str]]] = {}
    for rel in card.relationships("subclass_of"):
        if (rel.get("qualifiers") or {}).get("source") != "MONDO":
            continue
        term = rel["subject_ref"].split(":", 1)[1]
        broader = rel["object_ref"].split(":", 1)[1]
        narrower_of.setdefault(broader, {})[term] = (rel.get("qualifiers") or {}).get(
            "path"
        ) or [term, broader]
    medgen_of = _same_as(card, "MedGen")
    records = card.quality.get("enrichments") or []
    queried = any(e.get("source") == "MONDO" for e in records)
    unresolved = {
        u["curie"]: u["reason"]
        for e in records
        if e.get("source") == "MONDO"
        for u in e.get("ungrouped") or []
    }

    def term_of(curie: str) -> tuple | None:
        """``(mondo id, basis)`` a curie reaches through stated identity, or None."""
        if curie.startswith("MONDO:") and curie not in unresolved:
            return curie, "named_directly"
        if curie in mondo_of:
            return mondo_of[curie]["object_ref"].split(":", 1)[1], "same_as"
        if curie in medgen_of:
            uid = medgen_of[curie]["object_ref"]
            if uid in mondo_of:
                return mondo_of[uid]["object_ref"].split(":", 1)[1], "medgen_same_as"
        return None

    groups: Dict[str, Dict[str, Any]] = {}
    ungrouped: List[Dict[str, Any]] = []
    for statement in _card_statements(card):
        if any(c in CLINVAR_PLACEHOLDERS for c in statement["curies"]):
            ungrouped.append({**statement, "reason": "condition_not_provided"})
            continue
        reached: Dict[str, List[Dict[str, str]]] = {}
        for curie in statement["curies"]:
            found = term_of(curie)
            if found:
                reached.setdefault(found[0], []).append(
                    {"id": curie, "basis": found[1]}
                )
        narrower = {}
        if len(reached) > 1:
            broadest = [
                t
                for t in reached
                if all(o == t or o in narrower_of.get(t, {}) for o in reached)
            ]
            if len(broadest) != 1:
                ungrouped.append(
                    {**statement, "reason": "conflicting_identity", "terms": reached}
                )
                continue
            (term,) = broadest
            narrower = {
                other: {"ids": via, "path": narrower_of[term][other]}
                for other, via in reached.items()
                if other != term
            }
            reached = {term: reached[term]}
        if not reached:
            if not statement["refs"]:
                reason = "no_id_stated"
            elif not statement["curies"]:
                reason = "namespace_not_mapped"
            elif not queried:
                reason = "identity_not_queried"
            else:
                reasons = {
                    unresolved.get(c, "no_stated_equivalence")
                    for c in statement["curies"]
                }
                reason = (
                    "obsolete_term"
                    if reasons == {"obsolete_term"}
                    else "no_stated_equivalence"
                )
            ungrouped.append({**statement, "reason": reason})
            continue
        ((mondo, via),) = reached.items()
        group = groups.setdefault(
            mondo, {"mondo": mondo, "names": set(), "refs": set(), "statements": []}
        )
        for hop in via:
            link = mondo_of.get(hop["id"]) or mondo_of.get(
                (medgen_of.get(hop["id"]) or {}).get("object_ref", "")
            )
            name = ((link or {}).get("qualifiers") or {}).get("mondo_name")
            if name:
                group["mondo_name"] = name
        if statement.get("name"):
            group["names"].add(statement["name"])
        group["refs"].update(statement["refs"])
        entry = {**statement, "grouped_by": via}
        if narrower:
            entry["narrower"] = narrower
        group["statements"].append(entry)
    diseases = []
    for mondo in sorted(groups):
        group = groups[mondo]
        diseases.append(
            {
                **group,
                "names": sorted(group["names"]),
                "refs": sorted(group["refs"]),
                "sources": sorted(
                    {s.get("source") for s in group["statements"]} - {None}
                ),
            }
        )
    return {
        "diseases": diseases,
        "ungrouped": ungrouped,
        "rule": make_derivation(
            LEGACY_RULE,
            inputs=[
                "relationships.associated_with",
                "annotations.disease",
                "annotations.clinical_variants",
                "relationships.same_as",
                "relationships.subclass_of",
            ],
            parameters={
                "identity": ["mondo_equivalence@1", "medgen_concept@1"],
                "placeholders": sorted(CLINVAR_PLACEHOLDERS),
                "granularity": "mondo_hierarchy@1",
            },
        ),
    }
