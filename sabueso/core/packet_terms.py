"""Read-time terms of packet statement support, without changing packet payloads."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .errors import StorageError
from .literature_explanation import literature_basis
from .terms import assertion_label, record_label, report_items

RULE = "packet_terms@1"
SUPPORTED_MAPPINGS = {"packet_aspects@6", "packet_aspects@7"}


def _references(node: Any) -> tuple[set[str], set[str]]:
    assertions, relationships = set(), set()

    def identifiers(value):
        if isinstance(value, str):
            if value.startswith("SA_"):
                assertions.add(value)
            elif value.startswith("REL_"):
                relationships.add(value)
        elif isinstance(value, list):
            for child in value:
                identifiers(child)

    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {
                    "source_assertion_id",
                    "source_assertion_ids",
                    "relationship_id",
                    "relationship_ids",
                    "inputs",
                }:
                    identifiers(child)
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(node)
    return assertions, relationships


def _items(card: Any, facts: dict, role: str, conflicts: list) -> list[dict]:
    """The statements named by views, plus stored relationship dependencies.

    Do not use whole-card provenance: it includes sources outside the asked aspects.
    Do not interpret snippets as IDs, or infer citations from publication titles.
    """
    ids, rel_ids = _references(facts)
    conflict_ids, conflict_rels = _references(conflicts)
    ids.update(conflict_ids)
    rel_ids.update(conflict_rels)
    # Grouped diseases expose identity names without IDs for the relationships
    # that supplied them. Use the stored identity/hierarchy context, explicitly
    # broader than the exact grouping inputs (which the mapping did not record).
    if "disease_association" in facts:
        for rel in card.relationships():
            if rel["predicate"] in {"same_as", "subclass_of"} and any(
                (
                    (card.source_assertion_store.get(identifier) or {}).get("source")
                    or {}
                ).get("name")
                in {"MONDO", "MedGen"}
                for identifier in rel.get("source_assertion_ids") or []
            ):
                rel_ids.add(rel["id"])
    if "literature" in facts:
        for publication in facts["literature"]["publications"]["publications"]:
            held, support = literature_basis(card, publication)
            rel_ids.update(r["id"] for r in held)
            ids.update(support)
    relationships = {}
    pending = list(rel_ids)
    while pending:
        identifier = pending.pop()
        if identifier in relationships:
            continue
        rel = card.relationship_store.get(identifier)
        if rel is None:
            raise StorageError(
                f"Packet terms require missing relationship {card.pinned_ref()}#{identifier}."
            )
        relationships[identifier] = rel
        support, dependencies = _references(rel)
        ids.update(support)
        pending.extend(dependencies - relationships.keys())
    assertions = {}
    for identifier in sorted(ids):
        assertion = card.source_assertion_store.get(identifier)
        if assertion is None:
            raise StorageError(
                f"Packet terms require missing SourceAssertion {card.pinned_ref()}#{identifier}."
            )
        assertions[identifier] = assertion
    pin = card.pinned_ref()
    labels = {
        identifier: {assertion_label(sa)} for identifier, sa in assertions.items()
    }
    deposited = {}
    for rel in relationships.values():
        depositor = ((rel.get("qualifiers") or {}).get("assay") or {}).get("depositor")
        if depositor:
            for identifier in rel.get("source_assertion_ids") or []:
                deposited.setdefault(identifier, set()).add(
                    record_label(assertion_label(assertions[identifier]), depositor)
                )
    labels.update(deposited)

    def sources(identifiers):
        return sorted(
            {name for identifier in identifiers for name in labels[identifier]}
        )

    items = [
        {
            "kind": "source_assertion",
            "id": identifier,
            "source_assertion_ref": f"{pin}#{identifier}",
            "role": role,
            "path": sa.get("field_path"),
            "sources": sorted(labels[identifier]),
        }
        for identifier, sa in sorted(assertions.items())
    ]
    from .article_metadata import article_terms

    for item in items:
        sa = assertions[item["id"]]
        if sa.get("field_path") == "literature.article_metadata":
            item["article_terms"] = article_terms(sa["asserted_value"])
    for identifier, rel in sorted(relationships.items()):
        direct = set(rel.get("source_assertion_ids") or [])
        requirements = [sources(direct)] if direct else []
        if rel.get("derivation"):
            inputs, dependencies = _references(
                {"qualifiers": rel.get("qualifiers"), "derivation": rel["derivation"]}
            )
            covered = set(direct)
            for dependency in sorted(dependencies):
                support = set(
                    relationships[dependency].get("source_assertion_ids") or []
                )
                requirements.append(sources(support))
                covered.update(support)
            requirements.extend(sources([i]) for i in sorted(inputs - covered))
        items.append(
            {
                "kind": "relationship",
                "id": identifier,
                "relationship_ref": f"{pin}#{identifier}",
                "role": role,
                "predicate": rel["predicate"],
                "object_ref": rel["object_ref"],
                "sources": sorted({s for group in requirements for s in group}),
                "requirements": requirements,
            }
        )
    return items


def packet_terms(packet: Any, use: str, store: Any) -> dict:
    """Same support scope for full and index, from exact saved cards at mapping @6.

    Historical mappings remain readable but require their own scope adapter. Never
    substitute current areas or rules for a mapping the packet actually recorded.
    """
    from .packets import _facts, full_rules

    mapping = packet.to_dict().get("aspect_mapping")
    if mapping not in SUPPORTED_MAPPINGS:
        raise StorageError(
            f"{RULE} has no scope adapter for {mapping!r}; the packet remains readable."
        )
    if store is None:
        raise StorageError(
            "Packet terms require a KnowledgeStore containing the pinned cards."
        )
    groups, scopes = [], {}
    for role, entity in sorted(packet.entities.items()):
        card = store.load(entity["ref"])
        if card.pinned_ref() != entity["ref"]:
            raise StorageError(
                f"Packet terms require an exact card pin: {entity['ref']}."
            )
        facts = {}
        for aspect in packet.query.aspects:
            represented = packet.facts[aspect][role]
            if packet.detail == "index":
                if represented.get("full_rules") != full_rules(mapping=mapping)[aspect]:
                    raise StorageError(
                        f"Packet terms cannot reconstruct unrecognized {aspect} view rules."
                    )
                facts[aspect] = _facts(aspect, card, mapping=mapping)
            else:
                facts[aspect] = represented
        items = _items(card, facts, role, packet.conflicts.get(role) or [])
        groups.append((card.id, items))
        scopes[role] = {"card_ref": entity["ref"], "items": items}
    report = report_items(groups, use)
    return deepcopy(
        {
            **report,
            "packet_rule": RULE,
            "packet_snapshot_id": packet.snapshot_id(),
            "aspect_mapping": mapping,
            "aspects": list(packet.query.aspects),
            "scope": scopes,
            "support_basis": "stored_statement_support",
            "terms_basis": "current_packaged_registry_with_review_dates",
            "lineage_note": "Stored statement support and packet conflicts are reported; unrecorded mapping or qualifier lineage is not reconstructed. Disease grouping includes the stored MONDO/MedGen identity and hierarchy context, not exact selected inputs. This is a read-time report, not a historical terms-registry snapshot.",
        }
    )
