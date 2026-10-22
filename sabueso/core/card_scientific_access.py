"""Shared captured scientific results for human and bounded machine access (#148).

The first adapter delegates to the existing single-protein structural inventory,
knowledge-state reader and inventory explanation. It never acquires source data.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from .card_access import _Entry, _handle
from .errors import ArgumentError

ADAPTER = "structure_exploration@1"
RESOLUTION_FIELD = "relationships.has_structure.resolution"
COLUMNS = (
    "structure_ref",
    "method",
    "resolution",
    "chains",
    "coverage",
    "coverage_class",
    "state",
)
DEFAULT_FIELDS = COLUMNS[:5]


def options_for_structures(options):
    from sabueso._private.argdigest.argument.region import digest_region

    if options is None:
        options = {}
    if not isinstance(options, dict) or set(options) - {"include_fragments", "region"}:
        raise ArgumentError("structures options: include_fragments and region only.")
    include = options.get("include_fragments", False)
    if type(include) is not bool:
        raise ArgumentError("include_fragments must be True or False.")
    return {
        "include_fragments": include,
        "region": digest_region(options.get("region")),
    }


def projection(fields):
    if fields is None:
        return DEFAULT_FIELDS
    if isinstance(fields, str):
        fields = [fields]
    if (
        not isinstance(fields, (list, tuple))
        or any(
            not isinstance(key, str) or key not in ("label", "kind", *COLUMNS)
            for key in fields
        )
        or len(set(fields)) != len(fields)
    ):
        raise ArgumentError(
            f"fields requires unique keys from label, kind, {', '.join(COLUMNS)}."
        )
    return tuple(fields)


def descriptor():
    return {
        "key": "structures",
        "label": "Experimental structures",
        "description": "Existing structural inventory over this captured protein.",
        "adapter": ADAPTER,
        "scientific_adapter": True,
        "operations": ["select", "explain", "read", "page"],
        "columns": {
            key: {"type": kind}
            for key, kind in {
                "structure_ref": "string",
                "method": "string|null",
                "resolution": "quantity|null",
                "chains": "array[string]|null",
                "coverage": "number|null",
                "coverage_class": "string|null",
                "state": "object",
            }.items()
        },
        "default_fields": list(DEFAULT_FIELDS),
        "quantity_expectations": {
            "resolution": {"field": RESOLUTION_FIELD, "unit": "angstrom"}
        },
        "options": {"include_fragments": False, "region": None},
        "projection": True,
        "machine_filter": False,
        "machine_order": False,
        "machine_membership": False,
        "mandatory_interpretation": [
            "structure_kind",
            "coverage_scope",
            "qualifier_conflicts",
            "rules",
        ],
    }


def _resolution_record(value):
    from pyunitwizard import QuantityRecord

    return QuantityRecord.from_quantity(
        value, field=RESOLUTION_FIELD, unit="angstrom"
    ).to_dict()


def _wire_row(row):
    row = deepcopy(row)
    if row.get("resolution") is not None:
        row["resolution"] = _resolution_record(row["resolution"])
    return row


def _wire_inventory(native):
    return {
        **deepcopy({k: v for k, v in native.items() if k != "items"}),
        "items": [_wire_row(row) for row in native.get("items", [])],
    }


def _wire_explanation(native):
    return {
        **deepcopy({k: v for k, v in native.items() if k != "item"}),
        "item": _wire_row(native["item"]) if native.get("item") else None,
    }


def _rule_identity(rule):
    # Only generated, declared rule records lose producer metadata for semantic
    # identity. Original stored records/fields, including similarly named keys, stay.
    return {key: value for key, value in rule.items() if key != "sabueso_version"}


class _CapturedCard:
    """Private reader input whose pin is the already verified capture, never a reseal."""

    def __init__(self, capture):
        from .card import Card

        self._card = Card.from_dict(capture.data)
        self._pin = capture.pin

    def __getattr__(self, name):
        return getattr(self._card, name)

    def pinned_ref(self):
        return self._pin


@dataclass(frozen=True)
class _ScientificResult:
    result_ref: str
    native: dict = field(repr=False)
    explanations: dict = field(repr=False)
    wire: dict = field(repr=False)
    options: dict = field(repr=False)
    entries: tuple = field(repr=False)
    _native_rows: dict = field(default_factory=dict, repr=False)

    def location(self, *keys):
        return {
            "format": "card_access_location@1",
            "kind": "result",
            "result_ref": self.result_ref,
            "segments": [{"type": "Key", "value": key} for key in keys],
        }

    def native_item(self, key):
        return self._native_rows[key]

    def cell(self, key, column):
        row = self.native_item(key)
        value = (
            row["structure_ref"]
            if column == "label"
            else "structure"
            if column == "kind"
            else row[column]
        )
        conflicts = row.get("qualifier_conflicts") or {}
        state = (
            "conflicting"
            if column in conflicts
            else "unknown"
            if value is None
            else "present"
        )
        reason = (
            "Original qualifier conflict; inspect the explanation."
            if state == "conflicting"
            else "The existing reader has no retained value."
            if state == "unknown"
            else None
        )
        return {
            "value": value,
            "state": state,
            "reason": reason,
            "support": [self.wire["support"][key]],
        }

    def frame(self, access, selection, entry):
        key = entry.key
        cells = {}
        for column in selection._fields:
            cell = self.cell(key, column)
            value = cell["value"]
            cells[column] = {
                "state": cell["state"],
                "reason": cell["reason"],
                "value": deepcopy(self.wire["items"][key]["resolution"])
                if column == "resolution" and value is not None
                else deepcopy(value),
            }
        return {
            "item_ref": _handle(
                "XI_", {"result_ref": self.result_ref, "location": entry.location}
            ),
            "kind": "structure",
            "label": entry.value["structure_ref"],
            "location": access._location(entry.location),
            "payload_location": access._location(entry.location),
            "state": "conflicting"
            if entry.value.get("qualifier_conflicts")
            else "present",
            "support_location": access._location(self.location("support", key)),
            "interpretation": deepcopy(self.wire["interpretations"][key]),
            "interpretation_location": access._location(
                self.location("interpretations", key)
            ),
            "cells": cells,
            "value_included": True,
        }


def materialize(access, options):
    """Evaluate once per normalized scientific request; all later reads use the result."""
    from .knowledge_state import knowledge_state
    from .structure_explanation import EXPLANATION_RULE, explain_structure_inventory
    from .structures import coverage_derivation, state_derivation, structure_inventory

    native, explanations, excluded, rows = {}, {}, [], {}
    rules = []
    outcome = {
        "status": "not_applicable",
        "reason": "The structures adapter requires a protein Card.",
    }
    coverage = {
        "basis": "stored_literal",
        "classification": "not_evaluated",
        "rows": [],
    }
    if access.profile == "protein" and not access._focal.pin:
        outcome = {
            "status": "missing_prerequisite",
            "reason": "A captured Card identity is required for pinned structural explanations. Use literal inspection.",
        }
    elif access.profile == "protein":
        card = _CapturedCard(access._focal)
        native = structure_inventory(
            [card],
            regions=options["region"],
            include_fragments=options["include_fragments"],
        )
        rules = [native["rule"], coverage_derivation(), state_derivation()]
        knowledge = knowledge_state(card)
        coverage = {
            "basis": "original_scoped_knowledge_state",
            "rule": knowledge["rule"],
            "rows": [
                row
                for row in knowledge["rows"]
                if row["area"].startswith("relationships.has_structure")
            ],
            "quality_location": access._card_location(
                segments=[{"type": "Key", "value": "quality"}]
            ),
            "scope_note": "Retained source/request scope; inventory sequence coverage does not establish coordinate completeness.",
        }
        for row in native["items"]:
            key = row["relationship_id"]
            rows[key] = _wire_row(row)
            explanations[key] = explain_structure_inventory(
                [card],
                card.id,
                row["structure_ref"],
                native,
                regions=options["region"],
                include_fragments=options["include_fragments"],
            )
        for ref in native["excluded"].get(card.id, []):
            original = explain_structure_inventory(
                [card],
                card.id,
                ref,
                native,
                regions=options["region"],
                include_fragments=options["include_fragments"],
            )
            excluded.append(
                {
                    "structure_ref": ref,
                    "reason": original["reason"],
                    "explanation": _wire_explanation(original),
                }
            )
        outcome = {
            "status": "ok" if rows else "empty",
            "reason": None
            if rows
            else "The existing inventory admits no retained entries under these options; inspect coverage and exclusions.",
        }
    identity_native = _wire_inventory(native)
    if "rule" in identity_native:
        identity_native["rule"] = _rule_identity(identity_native["rule"])
    coverage_identity = (
        {**coverage, "rule": _rule_identity(coverage["rule"])}
        if "rule" in coverage
        else coverage
    )
    result_ref = _handle(
        "XR_",
        {
            "format": "scientific_exploration_result@1",
            "adapter": ADAPTER,
            "inputs": sorted(access._captures),
            "focal": access._inputs[0],
            "options": options,
            "native": identity_native,
            "coverage": coverage_identity,
            "rules": [_rule_identity(rule) for rule in rules],
            "explanation_rule": EXPLANATION_RULE,
            "outcome": outcome,
        },
    )
    result = _ScientificResult(
        result_ref, native, explanations, {}, deepcopy(options), ()
    )
    support, interpretations = {}, {}
    relationships = {
        record["id"]: record for record in access._focal.data["relationship_store"]
    }
    available = {
        record["id"] for record in access._focal.data["source_assertion_store"]
    }
    for key, row in rows.items():
        rel = relationships[key]
        support[key] = {
            "basis": "relationship_level",
            "relationship_id": key,
            "relationship_location": access._card_location(
                segments=[
                    {"type": "Key", "value": "relationship_store"},
                    {"type": "Record", "value": key},
                ]
            ),
            "source_assertion_ids": deepcopy(rel.get("source_assertion_ids", [])),
            "rules": [deepcopy(rule) for rule in rules],
            "explanation_location": result.location("explanations", key),
        }
        support[key]["source_assertions"] = [
            {
                "id": ref,
                "state": "present" if ref in available else "not_retained",
                "location": access._card_location(
                    segments=[
                        {"type": "Key", "value": "source_assertion_store"},
                        {"type": "Record", "value": ref},
                    ]
                )
                if ref in available
                else None,
            }
            for ref in rel.get("source_assertion_ids", [])
        ]
        interpretations[key] = {
            "structure_kind": "experimental",
            "coverage_scope": "retained_sequence_ranges",
            "region": deepcopy(options["region"]),
            "region_axis": "captured canonical protein positions (existing UniProt-numbered reader)",
            "coordinate_completeness": "not_established_by_coverage",
            "qualifier_conflicts": deepcopy(row.get("qualifier_conflicts")),
            "state": deepcopy(row["state"]),
            "inventory_status": explanations[key]["status"],
            "inventory_reason": explanations[key]["reason"],
            "rules": [rule["rule"] for rule in rules],
            "quantity_expectations": {
                "resolution": {"field": RESOLUTION_FIELD, "unit": "angstrom"}
            },
        }
    wire = {
        "native_payload": _wire_inventory(native),
        "items": rows,
        "explanations": {
            key: _wire_explanation(value) for key, value in explanations.items()
        },
        "support": support,
        "interpretations": interpretations,
        "context": {
            **access.context,
            "adapter": ADAPTER,
            "options": deepcopy(options),
            "rules": deepcopy(rules),
            "used_captures": [access._inputs[0]],
        },
        "coverage": coverage,
        "exclusions": excluded,
        "outcome": outcome,
        "schema": descriptor(),
    }
    result = _ScientificResult(
        result_ref,
        native,
        explanations,
        wire,
        deepcopy(options),
        tuple(
            _Entry(result.location("items", key), key, row)
            for key, row in sorted(
                rows.items(), key=lambda pair: pair[1]["structure_ref"]
            )
        ),
        _native_rows={row["relationship_id"]: row for row in native.get("items", [])},
    )
    access._objects[result_ref] = wire
    return result


def validate_equality(column, value):
    """Types belong to the result schema, not the first nonmissing display row."""
    import math

    import pyunitwizard as puw

    if column == "resolution":
        if not puw.is_quantity(value):
            raise ArgumentError("resolution equality requires a length quantity.")
        try:
            scalar = puw.get_value(value, to_unit="angstrom")
            if getattr(scalar, "shape", ()) != () or not math.isfinite(float(scalar)):
                raise ValueError("not a finite scalar")
        except (ValueError, TypeError, AttributeError) as exc:
            raise ArgumentError(
                "resolution requires a finite scalar length quantity."
            ) from exc
    elif column == "coverage":
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ArgumentError(
                "coverage equality requires a finite number, not a boolean."
            )
    elif column == "chains":
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ArgumentError("chains equality requires a list of chain names.")
    elif column == "state":
        if not isinstance(value, dict):
            raise ArgumentError(
                "state equality requires the full retained state mapping."
            )
    elif not isinstance(value, str):
        raise ArgumentError(f"{column} equality requires a string.")


def equal_values(column, first, second):
    if column == "resolution":
        import pyunitwizard as puw

        return bool(
            puw.get_value(first, to_unit="angstrom")
            == puw.get_value(second, to_unit="angstrom")
        )
    return first == second


def sorted_entries(view, column, descending, unit):
    if unit is not None and column != "resolution":
        raise ArgumentError("unit is supported only for the resolution column.")
    if column in ("chains", "state"):
        raise ArgumentError(
            "List/object columns have no declared scientific sort order."
        )
    present, missing = [], []
    for item in view.items():
        cell = item.cells[column]
        (
            present
            if cell.state in ("present", "conflicting") and cell._value is not None
            else missing
        ).append(item)
    if column == "resolution":
        import pyunitwizard as puw

        target = unit or "angstrom"  # declared field unit, never a session default
        try:
            # Validate the unit also for an empty selection.
            puw.get_value(puw.quantity(1, "angstrom"), to_unit=target)
            present.sort(
                key=lambda item: float(
                    puw.get_value(item.cells[column]._value, to_unit=target)
                ),
                reverse=descending,
            )
        except (ValueError, TypeError, AttributeError) as exc:
            raise ArgumentError(
                "Resolution sorting requires a compatible length unit."
            ) from exc
    else:
        present.sort(key=lambda item: item.cells[column]._value, reverse=descending)
    return tuple(item._entry for item in [*present, *missing])
