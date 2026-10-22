"""Explain knowledge-state classification from exact stored inputs (#91).

Enrichment reports explain reported counts and request outcomes. Related stored
knowledge is separate context: no per-request assertion membership is invented.
Absent fields, missing queries and failed requests never become source assertions.
"""

from copy import deepcopy

from .knowledge_state import _enrichment_counts, _supporting_sources, knowledge_state
from .relationship_store import make_derivation

RULE = "knowledge_state_explanation@2"


def explain_knowledge_state(
    card, knowledge_area=None, knowledge_source=None, *, _captured=None
):
    pin = card.pinned_ref()
    inputs = []
    if _captured is None:
        view = knowledge_state(card, _support=inputs)
    else:
        view, inputs = _captured["view"], _captured["inputs"]
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
        if not ids and not rel.get("derivation"):
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
        area, source = row["area"], row["source"]
        predicate = area.split(" ", 1)[0].removeprefix("relationships.")
        related = [
            r
            for r in card.relationships()
            if (
                area == "records"
                or (area.startswith("relationships.") and r["predicate"] == predicate)
            )
            and (
                source in _supporting_sources(card, r.get("source_assertion_ids") or [])
                or (r.get("qualifiers") or {}).get("source") == source
            )
        ]
        fields = [
            field(path)
            for path in card.list_fields()
            if (area == "records" or path == area)
            and isinstance(card.get(path), dict)
            and source
            in _supporting_sources(
                card, (card.get(path) or {}).get("source_assertion_ids") or []
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
            from sabueso.enrichers import count_by_area, not_queried_details_by_area

            key = (row["area"], row["source"])
            _, counts = _enrichment_counts(
                *key,
                [card.quality["enrichments"][i] for i in basis["enrichment_indexes"]],
                _count_field=_captured["counts"].get(key, "count")
                if _captured is not None
                else None,
            )
            support["classification_inputs"] = {
                **basis,
                "count_field": (
                    _captured["counts"] if _captured is not None else count_by_area()
                ).get(key, "count"),
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
                "not_queried_detail": (
                    _captured["details"]
                    if _captured is not None
                    else not_queried_details_by_area()
                ).get(key),
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

    # Selected fields whose support has disappeared may no longer produce a state
    # row at all. Report that gap without manufacturing a source or a new state.
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
        if ids and all(_supporting_sources(card, [i]) for i in ids):
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
        if any(card.source_assertion_store.get(i) is None for i in ids) or (
            not ids and not rel.get("derivation")
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
            "rule": make_derivation(
                _captured["explanation_rule"] if _captured is not None else RULE,
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
