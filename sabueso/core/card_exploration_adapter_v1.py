"""Frozen structural adapter v1: expected records and inert original transport.

No live scientific module is imported. Expected records serve comparison only;
the saved result is never replaced by the verifier's reference records.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from .card_access import _Entry, _handle
from .card_exploration_coverage_v1 import _v1_knowledge_state
from .card_exploration_history import _ExpectedQuantity, _HistoricalInput
from .card_exploration_structure_v1 import (
    EXPLANATION_RULE,
    _v1_coverage_derivation,
    _v1_explain_structure_inventory,
    _v1_state_derivation,
    _v1_structure_inventory,
)
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
COVERAGE_COLUMNS = ("area", "source", "state", "count", "release")
STRUCTURE_HUMAN_SCHEMA = {
    "kind": "structure",
    "grain": "one retained structural inventory entry",
    "columns": ["label", "kind", *COLUMNS],
    "presentations": ["summary", "table", "detail"],
    "quantity_expectations": {
        "resolution": {"field": RESOLUTION_FIELD, "unit": "angstrom"}
    },
}
COVERAGE_HUMAN_SCHEMA = {
    "kind": "knowledge_state",
    "grain": "one original source/area classification row",
    "columns": ["label", "kind", *COVERAGE_COLUMNS],
    "presentations": ["summary", "table"],
}


def _descriptor():
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

    return _ExpectedQuantity(
        QuantityRecord.from_quantity(
            value, field=RESOLUTION_FIELD, unit="angstrom"
        ).to_dict()
    )


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
    return {key: value for key, value in rule.items() if key != "sabueso_version"}


@dataclass(frozen=True)
class _HistoricalResult:
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


def _v1_expected_structures(access, options):
    """Evaluate once per normalized scientific request; all later reads use the result."""
    native, explanations, excluded, rows = ({}, {}, [], {})
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
    if access.profile == "protein" and (not access._focal.pin):
        outcome = {
            "status": "missing_prerequisite",
            "reason": "A captured Card identity is required for pinned structural explanations. Use literal inspection.",
        }
    elif access.profile == "protein":
        card = _HistoricalInput(access._focal)
        native = _v1_structure_inventory(
            [card],
            regions=options["region"],
            include_fragments=options["include_fragments"],
        )
        rules = [native["rule"], _v1_coverage_derivation(), _v1_state_derivation()]
        knowledge = _v1_knowledge_state(card)
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
            explanations[key] = _v1_explain_structure_inventory(
                [card],
                card.id,
                row["structure_ref"],
                native,
                regions=options["region"],
                include_fragments=options["include_fragments"],
            )
        for ref in native["excluded"].get(card.id, []):
            original = _v1_explain_structure_inventory(
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
            "focal": access._focal_key,
            "options": options,
            "native": identity_native,
            "coverage": coverage_identity,
            "rules": [_rule_identity(rule) for rule in rules],
            "explanation_rule": EXPLANATION_RULE,
            "outcome": outcome,
        },
    )
    result = _HistoricalResult(
        result_ref, native, explanations, {}, deepcopy(options), ()
    )
    support, interpretations = ({}, {})
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
            "used_captures": [access._focal_key],
        },
        "coverage": coverage,
        "exclusions": excluded,
        "outcome": outcome,
        "schema": _descriptor(),
    }
    result = _HistoricalResult(
        result_ref,
        native,
        explanations,
        wire,
        deepcopy(options),
        tuple(
            (
                _Entry(result.location("items", key), key, row)
                for key, row in sorted(
                    rows.items(), key=lambda pair: pair[1]["structure_ref"]
                )
            )
        ),
        _native_rows={row["relationship_id"]: row for row in native.get("items", [])},
    )
    return result


def _region_options(options):
    from .card_exploration_science import _options

    return _options(options)


def _v1_region_node(explorer, path):
    """Read only an exact declared path; unrecognized shapes stay inspectable."""
    value = explorer.access._focal.data.get("sections", {})
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def _v1_region_request(explorer, options):
    """Validate exact canonical scope before invoking any structural reader."""
    if not isinstance(options, dict) or set(options) - {
        "sequence_ref",
        "region",
        "include_fragments",
    }:
        raise ArgumentError(
            "region_coverage options: sequence_ref, region and include_fragments only."
        )
    sequence_ref = options.get("sequence_ref")
    if sequence_ref is not None and (
        not isinstance(sequence_ref, str) or not sequence_ref.strip()
    ):
        raise ArgumentError(
            "sequence_ref requires a nonempty explicit sequence reference."
        )
    effective = _region_options(
        {key: value for key, value in options.items() if key != "sequence_ref"}
    )
    effective = {"sequence_ref": sequence_ref, **effective}
    if sequence_ref is None or effective["region"] is None:
        return (
            effective,
            "missing_prerequisite",
            "Supply options with sequence_ref='uniprot:<accession>' and region as positive positions or inclusive [begin, end] ranges.",
        )
    accession = _v1_region_node(explorer, "identifiers.uniprot")
    accession = accession.get("value") if isinstance(accession, dict) else None
    if not isinstance(accession, str) or not accession:
        return (
            effective,
            "missing_prerequisite",
            "No retained canonical UniProt accession identifies this sequence axis.",
        )
    if sequence_ref != f"uniprot:{accession}":
        return (
            effective,
            "unsupported",
            f"Only the captured canonical axis uniprot:{accession} is supported; no isoform, construct or residue-number mapping is inferred.",
        )
    data = explorer.access._focal.data
    identity = data.get("meta", {}).get("card_id")
    quality = data.get("quality", {})
    conflicts = quality.get("conflicts", []) if isinstance(quality, dict) else []
    conflicted = any(
        (
            isinstance(row, dict)
            and str(row.get("field")).removesuffix(".value")
            in {"identifiers.uniprot", "sequence.primary", "sequence.length"}
            for row in conflicts or []
        )
    )
    length, sequence = (
        _v1_region_node(explorer, "sequence.length"),
        _v1_region_node(explorer, "sequence.primary"),
    )
    length = length.get("value") if isinstance(length, dict) else None
    sequence = sequence.get("value") if isinstance(sequence, dict) else None
    if (
        identity != f"sabueso:protein:uniprot:{accession}"
        or conflicted
        or type(length) is not int
        or (length < 1)
        or (not isinstance(sequence, str))
        or (len(sequence) != length)
    ):
        return (
            effective,
            "missing_prerequisite",
            "A consistent retained canonical identity, sequence and length are required; inspect identity/sequence fields and stored conflicts.",
        )
    if effective["region"][-1] > length:
        raise ArgumentError(
            f"region extends beyond the retained canonical sequence length ({length})."
        )
    return (effective, "ok", None)


def _validate_equality(column, value):
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
        if not isinstance(value, list) or not all((isinstance(v, str) for v in value)):
            raise ArgumentError("chains equality requires a list of chain names.")
    elif column == "state":
        if not isinstance(value, dict):
            raise ArgumentError(
                "state equality requires the full retained state mapping."
            )
    elif not isinstance(value, str):
        raise ArgumentError(f"{column} equality requires a string.")


def _equal_values(column, first, second):
    if column == "resolution":
        import pyunitwizard as puw

        return bool(
            puw.get_value(first, to_unit="angstrom")
            == puw.get_value(second, to_unit="angstrom")
        )
    return first == second


def _sorted_entries(view, column, descending, unit):
    if unit is not None and column != "resolution":
        raise ArgumentError("unit is supported only for the resolution column.")
    if column in ("chains", "state"):
        raise ArgumentError(
            "List/object columns have no declared scientific sort order."
        )
    present, missing = ([], [])
    for item in view.items():
        cell = item.cells[column]
        (
            present
            if cell.state in ("present", "conflicting") and cell._value is not None
            else missing
        ).append(item)
    if column == "resolution":
        import pyunitwizard as puw

        target = unit or "angstrom"
        try:
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
    return tuple((item._entry for item in [*present, *missing]))
