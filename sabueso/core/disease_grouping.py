"""Deterministic, source-stated disease identity paths (disease_grouping@2).

An identifier with contradictory targets is ambiguous even when those targets
share a hierarchy. Granularity applies only across separately stated identifiers
with unique targets. Names, source versions and storage order never select identity.
"""

import json

from .diseases import CLINVAR_PLACEHOLDERS, _card_statements
from .relationship_store import make_derivation

RULE = "disease_grouping@2"


def _key(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _ordered(values):
    return sorted(values, key=_key)


def _unique(values):
    return [_value for _, _value in sorted({_key(v): v for v in values}.items())]


def _sources(relationship):
    return {
        (relationship.get("qualifiers") or {}).get("source"),
        *(relationship.get("qualifier_conflicts") or {}).get("source", []),
    }


def identity_paths(card, curie):
    """Every direct or MedGen/MONDO path, including unfinished MedGen branches.

    This is a bounded traversal of the two supported source contracts, not a
    general equivalence closure. Each path retains the exact stored relationships.
    """
    links = card.relationships("same_as")

    def from_source(subject, source):
        return _ordered(
            [r for r in links if r["subject_ref"] == subject and source in _sources(r)]
        )

    unresolved = {
        u["reason"]
        for e in card.quality.get("enrichments") or []
        if e.get("source") == "MONDO"
        for u in e.get("ungrouped") or []
        if u["curie"] == curie
    }
    paths = []
    if curie.startswith("MONDO:") and not unresolved:
        paths.append(
            {
                "id": curie,
                "term": curie,
                "basis": "named_directly",
                "relationship_ids": [],
            }
        )

    def add(chain, basis):
        target = chain[-1]["object_ref"]
        path = {
            "id": curie,
            "term": target.removeprefix("mondo:")
            if target.startswith("mondo:MONDO:")
            else None,
            "basis": basis,
            "relationship_ids": [r["id"] for r in chain],
        }
        if path["term"] is None:
            path["reason"] = "no_stated_equivalence"
        paths.append(path)

    for link in from_source(curie, "MONDO"):
        add([link], "same_as")
    for concept in from_source(curie, "MedGen"):
        targets = from_source(concept["object_ref"], "MONDO")
        if targets:
            for target in targets:
                add([concept, target], "medgen_same_as")
        else:
            paths.append(
                {
                    "id": curie,
                    "term": None,
                    "basis": "medgen_same_as",
                    "relationship_ids": [concept["id"]],
                    "reason": "no_stated_equivalence",
                }
            )
    return _unique(paths)


def diseases_view_v2(card):
    return _view(card)


def diseases_view_v3(card):
    from .disease_identity_coverage import IdentityCoverage

    return _view(card, coverage=IdentityCoverage(card))


def _view(card, coverage=None):
    hierarchy = {}
    for rel in card.relationships("subclass_of"):
        if "MONDO" not in _sources(rel):
            continue
        narrow = rel["subject_ref"].removeprefix("mondo:")
        broad = rel["object_ref"].removeprefix("mondo:")
        paths = hierarchy.setdefault(broad, {}).setdefault(narrow, [])
        paths.append((rel.get("qualifiers") or {}).get("path") or [narrow, broad])
        paths.extend((rel.get("qualifier_conflicts") or {}).get("path") or [])
    records = card.quality.get("enrichments") or []
    queried = any(e.get("source") == "MONDO" for e in records)
    unresolved = {}
    for e in records:
        if e.get("source") == "MONDO":
            for u in e.get("ungrouped") or []:
                unresolved.setdefault(u["curie"], set()).add(u["reason"])
    relationships = {r["id"]: r for r in card.relationships("same_as")}
    groups, ungrouped = {}, []
    for statement in _ordered(_card_statements(card)):
        if coverage is not None:
            statement = {
                **statement,
                "identity_coverage": coverage.statement(statement),
            }
        if any(c in CLINVAR_PLACEHOLDERS for c in statement["curies"]):
            ungrouped.append({**statement, "reason": "condition_not_provided"})
            continue
        paths = _unique(
            [
                p
                for c in statement["curies"]
                for p in (
                    identity_paths(card, c) if coverage is None else coverage.paths(c)
                )
            ]
        )
        statement = {**statement, "identity_paths": paths}
        reached, targets = {}, {}
        for path in paths:
            if path["term"]:
                reached.setdefault(path["term"], []).append(
                    {"id": path["id"], "basis": path["basis"]}
                )
                targets.setdefault(path["id"], set()).add(path["term"])
        reached = {term: _unique(via) for term, via in sorted(reached.items())}
        if any(len(ts) > 1 for ts in targets.values()):
            ungrouped.append(
                {**statement, "reason": "conflicting_identity", "terms": reached}
            )
            continue
        if reached and any(p["term"] is None for p in paths):
            ungrouped.append(
                {**statement, "reason": "incomplete_identity", "terms": reached}
            )
            continue
        narrower = {}
        if len(reached) > 1:
            broadest = [
                t
                for t in reached
                if all(o == t or o in hierarchy.get(t, {}) for o in reached)
            ]
            if len(broadest) != 1:
                ungrouped.append(
                    {**statement, "reason": "conflicting_identity", "terms": reached}
                )
                continue
            (term,) = broadest
            for other, via in reached.items():
                if other != term:
                    routes = _unique(hierarchy[term][other])
                    narrower[other] = {
                        "ids": via,
                        **(
                            {"path": routes[0]}
                            if len(routes) == 1
                            else {"paths": routes}
                        ),
                    }
            reached = {term: reached[term]}
        if not reached:
            if not statement["refs"]:
                reason = "no_id_stated"
            elif not statement["curies"]:
                reason = "namespace_not_mapped"
            elif coverage is not None:
                reason = coverage.reason(statement["identity_coverage"])
            elif not queried:
                reason = "identity_not_queried"
            else:
                reasons = set().union(
                    *(
                        unresolved.get(c, {"no_stated_equivalence"})
                        for c in statement["curies"]
                    )
                )
                reason = (
                    "obsolete_term"
                    if reasons == {"obsolete_term"}
                    else "no_stated_equivalence"
                )
            ungrouped.append({**statement, "reason": reason})
            continue
        ((term, via),) = reached.items()
        group = groups.setdefault(
            term,
            {
                "mondo": term,
                "names": set(),
                "refs": set(),
                "statements": [],
                "mondo_names": set(),
            },
        )
        for path in paths:
            if path["term"] != term:
                continue
            for identifier in path["relationship_ids"]:
                link = relationships[identifier]
                if "MONDO" not in _sources(link):
                    continue
                name = (link.get("qualifiers") or {}).get("mondo_name")
                if name:
                    group["mondo_names"].add(name)
                group["mondo_names"].update(
                    (link.get("qualifier_conflicts") or {}).get("mondo_name") or []
                )
        if statement.get("name"):
            group["names"].add(statement["name"])
        group["refs"].update(statement["refs"])
        entry = {**statement, "grouped_by": via}
        if narrower:
            entry["narrower"] = narrower
        group["statements"].append(entry)
    diseases = []
    for term, group in sorted(groups.items()):
        names = sorted(group["mondo_names"])
        diseases.append(
            {
                **group,
                "names": sorted(group["names"]),
                "refs": sorted(group["refs"]),
                "mondo_names": names,
                **({"mondo_name": names[0]} if len(names) == 1 else {}),
                "sources": sorted(
                    {s.get("source") for s in group["statements"]} - {None}
                ),
            }
        )
    return {
        "diseases": diseases,
        "ungrouped": ungrouped,
        "rule": make_derivation(
            RULE if coverage is None else "disease_grouping@3",
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
                "ambiguity": "all_stored_identity_paths",
                **(
                    {"identity_coverage": "disease_identity_coverage@1"}
                    if coverage is not None
                    else {}
                ),
            },
        ),
    }
