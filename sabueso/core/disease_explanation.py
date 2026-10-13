"""Explain existing disease groups through pinned, source-stated support (#91).

Selected annotation members are matched to their stored asserted values. Every
identity path and qualifier conflict remains visible. The historical lookup and
its explanation are available explicitly. No view creates SourceAssertions.
"""

from copy import deepcopy

from .disease_grouping import _sources
from .diseases import LEGACY_RULE, _same_as, disease_statements
from .diseases import RULE as GROUPING_RULE
from .relationship_store import make_derivation
from .source_assertion_store import assertion_value

RULE = "disease_group_explanation@3"
FIELDS = {
    "uniprot_disease": "annotations.disease",
    "clinvar_condition": "annotations.clinical_variants",
}


def explain_disease(card, disease_ref, grouping_rule=GROUPING_RULE):
    pin = card.pinned_ref()
    view = card.diseases(grouping_rule=grouping_rule)
    term = disease_ref.split(":", 1)[1]
    group = next((g for g in view["diseases"] if g["mondo"] == term), None)
    mondo, medgen = (
        (_same_as(card, "MONDO"), _same_as(card, "MedGen"))
        if grouping_rule == LEGACY_RULE
        else ({}, {})
    )
    unresolved = {
        u["curie"]
        for e in card.quality.get("enrichments") or []
        if e.get("source") == "MONDO"
        for u in e.get("ungrouped") or []
    }
    gaps = []

    def assertions(ids):
        rows = [
            {**r, "source_assertion_ref": f"{pin}#{r['id']}"}
            for r in card.explain(sorted(set(ids)), skip_digestion=True)
        ]
        for row in rows:
            if not row["found"]:
                gaps.append(
                    {
                        "reason": "missing_source_assertion",
                        "source_assertion_ref": row["source_assertion_ref"],
                    }
                )
        return rows

    def relationship(rel, *, selected=True):
        if not rel:
            return None
        return {
            "relationship_ref": f"{pin}#{rel['id']}",
            "selected": selected,
            "relationship": rel,
            "source_assertions": assertions(rel.get("source_assertion_ids") or []),
        }

    def identity(curie, statement):
        if grouping_rule != LEGACY_RULE:
            paths = [
                p for p in statement.get("identity_paths") or [] if p["id"] == curie
            ]
            links = {
                identifier: relationship(
                    card.relationship_store.get(identifier),
                    selected="grouped_by" in statement,
                )
                for path in paths
                for identifier in path["relationship_ids"]
            }
            for identifier, link in links.items():
                if link is None:
                    gaps.append(
                        {
                            "reason": "missing_relationship",
                            "relationship_ref": f"{pin}#{identifier}",
                        }
                    )
            return {
                "id": curie,
                "paths": [
                    {
                        **p,
                        "links": [links[i] for i in p["relationship_ids"] if links[i]],
                    }
                    for p in paths
                ],
                "links": [link for _, link in sorted(links.items()) if link],
                "alternatives": [],
            }
        links, alternatives = [], []
        if curie.startswith("MONDO:") and curie not in unresolved:
            return {
                "id": curie,
                "basis": "named_directly",
                "links": [],
                "alternatives": [],
            }
        # Follow exactly the stored lookup used by disease_grouping@1; make other
        # stored targets explicit rather than presenting the lookup as a unique fact.
        subjects = [(curie, "MONDO", mondo.get(curie))]
        if curie not in mondo and curie in medgen:
            first = medgen[curie]
            subjects = [
                (curie, "MedGen", first),
                (first["object_ref"], "MONDO", mondo.get(first["object_ref"])),
            ]
        for subject, source, chosen in subjects:
            if chosen:
                links.append(relationship(chosen))
            others = [
                rel
                for rel in card.relationships("same_as")
                if rel["subject_ref"] == subject
                and (rel.get("qualifiers") or {}).get("source") == source
                and rel != chosen
            ]
            alternatives.extend(relationship(rel, selected=False) for rel in others)
            if others:
                gaps.append(
                    {
                        "reason": "ambiguous_stored_identity",
                        "subject_ref": subject,
                        "basis": "disease_grouping@1_lookup",
                    }
                )
        return {"id": curie, "links": links, "alternatives": alternatives}

    def statement_support(statement):
        rel_id = statement.get("relationship_id")
        support = {
            "statement": statement,
            "input": None,
            "identity": [identity(c, statement) for c in statement["curies"]],
            "hierarchy": [],
        }
        if rel_id:
            rel = card.relationship_store.get(rel_id)
            support["input"] = {"basis": "relationship", **(relationship(rel) or {})}
            if rel is None:
                gaps.append(
                    {
                        "reason": "missing_relationship",
                        "relationship_ref": f"{pin}#{rel_id}",
                    }
                )
        else:
            path = FIELDS[statement["kind"]]
            node = card.get(path) or {}
            members = []
            for item in node.get("value") or []:
                candidates = disease_statements(
                    lambda p: [item] if p == path else None, []
                )
                if any(
                    all(statement.get(k) == v for k, v in candidate.items())
                    for candidate in candidates
                ):
                    members.append(item)
            ids = node.get("source_assertion_ids") or []
            matched = [
                identifier
                for identifier in ids
                if assertion_value(card.source_assertion_store.get(identifier) or {})
                in members
            ]
            missing_ids = [
                identifier
                for identifier in ids
                if card.source_assertion_store.get(identifier) is None
            ]
            if not matched:
                gaps.append(
                    {
                        "reason": "no_matching_selected_assertion",
                        "field_path": path,
                        "statement": statement,
                    }
                )
            support["input"] = {
                "basis": "selected_annotation_member",
                "field_path": path,
                "members": members,
                "source_assertions": assertions(matched),
                "missing_field_assertions": assertions(missing_ids),
            }
        for narrow, basis in (statement.get("narrower") or {}).items():
            relationships = [
                r
                for r in card.relationships("subclass_of")
                if r["subject_ref"] == f"mondo:{narrow}"
                and r["object_ref"] == disease_ref
                and (
                    (r.get("qualifiers") or {}).get("source") == "MONDO"
                    if grouping_rule == LEGACY_RULE
                    else "MONDO" in _sources(r)
                )
            ]
            support["hierarchy"].append(
                {
                    "term": narrow,
                    **{k: basis[k] for k in ("path", "paths") if k in basis},
                    "links": [
                        relationship(r)
                        for r in sorted(relationships, key=lambda r: r["id"])
                    ],
                }
            )
            if not relationships:
                gaps.append({"reason": "missing_hierarchy", "term": narrow})
        return support

    statements = [statement_support(s) for s in (group or {}).get("statements", [])]
    # Preserve all ungrouped outcomes as card-level context, even when there is no
    # selected group. This is not a claim that each belongs to the requested term.
    ungrouped = [statement_support(s) for s in view["ungrouped"]]
    fields = []
    for path in FIELDS.values():
        node = card.get(path)
        if node is not None:
            fields.append(
                {
                    "field_path": path,
                    "node": node,
                    "source_assertions": assertions(
                        node.get("source_assertion_ids") or []
                    ),
                    "alternatives": assertions(
                        [
                            a["id"]
                            for a in card.source_assertion_store.to_list()
                            if a.get("field_path") == path
                            and a["id"] not in (node.get("source_assertion_ids") or [])
                        ]
                    ),
                    "conflicts": [
                        r
                        for r in card.quality.get("conflicts") or []
                        if r.get("field") == path
                    ],
                }
            )
    return deepcopy(
        {
            "rule": make_derivation(
                "disease_group_explanation@1"
                if grouping_rule == LEGACY_RULE
                else "disease_group_explanation@2"
                if grouping_rule == "disease_grouping@2"
                else RULE,
                inputs=[pin],
                parameters={
                    "disease_ref": disease_ref,
                    **(
                        {"grouping_rule": grouping_rule}
                        if grouping_rule != LEGACY_RULE
                        else {}
                    ),
                },
            ),
            "card_ref": pin,
            "disease_ref": disease_ref,
            "group": group,
            "status": "partial" if gaps else "on_card" if group else "not_on_card",
            "reason": "incomplete_or_ambiguous_stored_support"
            if gaps
            else None
            if group
            else "no_stored_disease_group",
            "grouping_rule": view["rule"],
            "statements": statements,
            "ungrouped_context": {"basis": "whole_card", "statements": ungrouped},
            "field_context": {
                "basis": "stored_selected_fields",
                "fields": fields,
                "selection_rules": card.selection_rules,
            },
            "enrichments": [
                e
                for e in card.quality.get("enrichments") or []
                if e.get("source") in {"MONDO", "MedGen"}
            ],
            "support_basis": "stored_relationships_and_selected_annotation_members",
            **(
                {"coverage_context": _coverage_context(card, pin)}
                if grouping_rule == "disease_grouping@3"
                else {}
            ),
            "gaps": gaps,
        }
    )


def _coverage_context(card, pin):
    from .disease_identity_coverage import IdentityCoverage

    return IdentityCoverage(card).context(pin)
