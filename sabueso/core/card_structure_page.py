"""Current machine delivery over live or historically verified structural results.

This layer adds inspectable cell support, never scientific decisions or saved-wire
rewrites. Relationship support is shared by the projected cells; it does not
establish assertion lineage for an individual qualifier.
"""

from copy import deepcopy


def complete_frame(access, result, entry, frame):
    key = entry.key
    original = result.wire["support"][key]
    frame.update(
        subject_ref=entry.value["card_id"],
        relationship_ref=key,
        support={
            "ref": key,
            "basis": original["basis"],
            "source_assertions": deepcopy(original["source_assertions"]),
        },
        inspection_required=False,
    )
    for column, cell in frame["cells"].items():
        # The column identifies an adapter field, not an invented source path.
        # QuantityRecord separately retains its provider field/unit handshake.
        value_location = (
            access._object_location("structure")
            if column == "kind"
            else access._location(
                result.location(
                    "items", key, "structure_ref" if column == "label" else column
                )
            )
        )
        cell.update(
            field={"adapter": result.wire["context"]["adapter"], "column": column},
            support_basis=original["basis"],
            support_ref=key,
            value_included=True,
            value_location=value_location,
            interpretation_location=frame["interpretation_location"],
        )
    return frame


def defer_frame(item):
    """Defer values and their shared mandatory closure atomically, keeping states."""
    frame = {
        key: deepcopy(item[key])
        for key in (
            "item_ref",
            "kind",
            "location",
            "payload_location",
            "subject_ref",
            "relationship_ref",
            "state",
            "support_location",
            "interpretation_location",
        )
    }
    frame.update(
        cells={
            column: {
                key: deepcopy(value) for key, value in cell.items() if key != "value"
            }
            | {"value_included": False}
            for column, cell in item["cells"].items()
        },
        value_included=False,
        value_location=item["location"],
        inspection_required=True,
        reason="value_and_interpretation_exceed_response_budget",
    )
    return frame
