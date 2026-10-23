"""Human wording over original retained support, never new scientific decisions.

These helpers do not change cells, schemas, saved wording or source records.
Missing declaration of a role/basis remains explicit instead of being guessed.
"""


def source_record(item):
    location = item._entry.location
    segments = location.get("segments", [])
    return (
        location.get("kind") == "card"
        and len(segments) == 2
        and segments[0] == {"type": "Key", "value": "source_assertion_store"}
        and segments[1].get("type") == "Record"
        and isinstance(item._entry.value, dict)
    )


def explanation_context(view):
    """Read the original backing object without copying its potentially large body."""
    original, location = view._explorer.access._resolve(
        view._selection._target["location"]
    )
    if location["kind"] != "result":
        return {}
    native = view._native_override if view._native_override is not None else original
    return (
        native
        if isinstance(native, dict)
        and native.get("basis") == "stored_literal"
        and {
            "support",
            "stored_conflicts",
            "selection_rules",
            "quality_location",
            "reason",
        }
        <= native.keys()
        and isinstance(native["support"], list)
        and all(isinstance(row, dict) for row in native["support"])
        else {}
    )


def structural_explanation(view):
    """Recognize an exact original explanation location in a registered adapter.

    A literal dictionary with matching keys or a matching title is insufficient.
    Historical views keep their original items; this only reads their context.
    """
    access = view._explorer.access
    original, location = access._resolve(view._selection._target["location"])
    segments = location.get("segments", [])
    if (
        location["kind"] != "result"
        or location["result_ref"] in access._metadata_refs
        or len(segments) != 2
        or segments[0] != {"type": "Key", "value": "explanations"}
        or segments[1].get("type") != "Key"
    ):
        return None
    wire = access._objects[location["result_ref"]]
    key = segments[1]["value"]
    if wire.get("context", {}).get(
        "adapter"
    ) != "structure_exploration@1" or key not in wire.get("support", {}):
        return None
    return {
        "native": view._native_override
        if view._native_override is not None
        else original,
        "support": wire["support"][key],
        "options": wire["context"]["options"],
    }


def source_role(item):
    if not source_record(item):
        return None
    structural = structural_explanation(item._view)
    if structural is not None:
        return (
            "Relationship support"
            if item._entry.key in structural["support"]["source_assertion_ids"]
            else None
        )
    native = explanation_context(item._view)
    ref = item._entry.key
    for support in native.get("support", []):
        if ref in support.get("source_assertion_ids", []):
            if support.get("basis") == "relationship_level":
                return "Relationship support"
            if native.get("selection_support_state") == "declared":
                return "Selected support"
    for key, label in (
        ("alternative_source_assertions", "Alternative statement"),
        ("unclassified_field_source_assertions", "Selection role unknown"),
    ):
        if any(row.get("id") == ref for row in native.get(key, [])):
            return label
    return None


def relationship_basis(item):
    row = item._entry.value
    derivation = row.get("derivation")
    if derivation is not None:
        rule = derivation.get("rule") if isinstance(derivation, dict) else None
        return (
            ("Derived broader term", rule)
            if isinstance(rule, str)
            and rule.rpartition("@")[0]
            and rule.rpartition("@")[2].isdecimal()
            else ("Broader term; derivation incomplete", None)
        )
    refs = row.get("source_assertion_ids")
    if isinstance(refs, list) and refs and all(isinstance(ref, str) for ref in refs):
        # The relationship declares its support; do not infer it from names,
        # sequence, path length, record count or a supplied destination Card.
        present = any(
            item._view._explorer._statement(ref)["state"] == "present" for ref in refs
        )
        if present:
            return "Source-supported broader term", None
        return "Broader term; support not retained", None
    return "Broader term; basis not retained", None


SYNONYM_SCOPES = {
    "exact_synonym": "exact synonym",
    "related_synonym": "related synonym",
    "broad_synonym": "broad synonym",
    "narrow_synonym": "narrow synonym",
}


def synonym_scope(value):
    return (
        SYNONYM_SCOPES.get(value, value)
        if isinstance(value, str)
        else value
        if value is not None
        else "scope not retained"
    )
