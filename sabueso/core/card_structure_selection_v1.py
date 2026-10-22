"""Versioned display selection over an existing structural result (#148).

This policy does not produce scientific knowledge. Preserve v1 when changing the
selection grammar: original saved requests depend on these comparison decisions.
"""

from copy import deepcopy
from types import SimpleNamespace

from .card_access import _handle
from .errors import ArgumentError, StorageError
from .snapshot import canonical_json

FORMAT = "structure_access_selection@1"
SELECTION_FORMAT = "scientific_access_selection@2"
COLUMNS = (
    "label",
    "kind",
    "structure_ref",
    "method",
    "resolution",
    "chains",
    "coverage",
    "coverage_class",
    "state",
)


def item_ref(result, entry):
    return _handle("XI_", {"result_ref": result.result_ref, "location": entry.location})


class _Rows:
    def __init__(self, result, entries):
        self.result, self.entries = result, entries

    def items(self):
        for entry in self.entries:
            yield SimpleNamespace(
                _entry=entry,
                cells={
                    key: SimpleNamespace(state=cell["state"], _value=cell["value"])
                    for key in COLUMNS
                    for cell in [self.result.cell(entry.key, key)]
                },
            )


def normalize(where, item_refs, order_by, *, historical=False):
    """Validate before materialization, also when digestion is skipped."""
    if historical:
        from .card_exploration_adapter_v1 import (
            _sorted_entries as sorted_entries,
        )
        from .card_exploration_adapter_v1 import (
            _validate_equality as validate_equality,
        )
    else:
        from .card_scientific_access import sorted_entries, validate_equality

    if where is None:
        where = {}
    if not isinstance(where, dict):
        raise ArgumentError(
            "where requires a mapping of declared columns to equalities."
        )
    encoded = {}
    for column, value in where.items():
        if not isinstance(column, str) or column not in COLUMNS:
            raise ArgumentError("Unknown structural where column.")
        validate_equality(column, value)
        if column == "resolution":
            from pyunitwizard import QuantityRecord

            value = QuantityRecord.from_quantity(
                value, field="relationships.has_structure.resolution", unit="angstrom"
            ).to_dict()
        encoded[column] = deepcopy(value)
    try:
        canonical_json(encoded).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, StorageError) as exc:
        raise ArgumentError(
            "where operands require finite serializable values."
        ) from exc
    if item_refs is not None:
        from sabueso._private.argdigest.argument.item_ref import digest_item_ref

        if not isinstance(item_refs, (list, tuple)):
            raise ArgumentError(
                "item_refs requires a sequence of exact item references."
            )
        item_refs = [digest_item_ref(ref) for ref in item_refs]
        if len(set(item_refs)) != len(item_refs):
            raise ArgumentError("item_refs must not contain duplicates.")
        item_refs = sorted(item_refs)
    if order_by is not None:
        if (
            not isinstance(order_by, dict)
            or set(order_by) - {"column", "descending", "unit"}
            or not isinstance(order_by.get("column"), str)
            or order_by.get("column") not in COLUMNS
            or type(order_by.get("descending", False)) is not bool
        ):
            raise ArgumentError(
                "order_by requires column, optional descending and unit."
            )
        unit = order_by.get("unit")
        if unit is not None and (not isinstance(unit, str) or not unit.strip()):
            raise ArgumentError("order_by unit requires a nonempty unit name.")
        order_by = {
            "column": order_by["column"],
            "descending": order_by.get("descending", False),
            "unit": unit,
        }
        sorted_entries(_Rows(None, ()), **order_by)
    return {"where": encoded, "item_refs": item_refs, "order_by": order_by}


def active(query):
    return (
        bool(query["where"])
        or query["item_refs"] is not None
        or query["order_by"] is not None
    )


def evaluate(result, query, *, historical=False):
    """Return exact ordered members and inspectable display exclusions."""
    if historical:
        from .card_exploration_adapter_v1 import (
            _equal_values as equal_values,
        )
        from .card_exploration_adapter_v1 import (
            _sorted_entries as sorted_entries,
        )
    else:
        from .card_scientific_access import equal_values, sorted_entries

    membership = query["item_refs"]
    refs = {item_ref(result, entry) for entry in result.entries}
    if membership is not None and set(membership) - refs:
        raise ArgumentError(
            "item_refs contains an item outside this scientific result."
        )
    operands = deepcopy(query["where"])
    if "resolution" in operands:
        from pyunitwizard import QuantityRecord

        operands["resolution"] = QuantityRecord.from_dict(
            operands["resolution"]
        ).to_quantity(field="relationships.has_structure.resolution", unit="angstrom")
    selected, exclusions = [], []
    for entry in result.entries:
        ref, reasons = item_ref(result, entry), []
        if membership is not None and ref not in membership:
            reasons.append({"kind": "membership"})
        for column, operand in sorted(operands.items()):
            cell = result.cell(entry.key, column)
            if cell["state"] not in ("present", "conflicting") or not equal_values(
                column, cell["value"], operand
            ):
                reasons.append(
                    {"kind": "where", "column": column, "cell_state": cell["state"]}
                )
        if reasons:
            exclusions.append(
                {"item_ref": ref, "location": entry.location, "reasons": reasons}
            )
        else:
            selected.append(entry)
    entries = tuple(selected)
    if query["order_by"] is not None:
        entries = tuple(
            sorted(entries, key=lambda entry: (entry.value["structure_ref"], entry.key))
        )
        entries = sorted_entries(_Rows(result, entries), **query["order_by"])
    return entries, {
        "format": FORMAT,
        **deepcopy(query),
        "underlying_count": len(result.entries),
        "selected_count": len(entries),
        "members": [item_ref(result, entry) for entry in entries],
        "display_exclusions": exclusions,
    }


def selection_ref(result, fields, spec):
    return _handle(
        "XA_",
        {
            "format": SELECTION_FORMAT,
            "result_ref": result.result_ref,
            "fields": fields,
            "selection": spec,
        },
    )


def original(selection):
    """Whether a retained structural request has the original full membership."""
    return selection._scientific is not None and selection.selection_ref == _handle(
        "XA_",
        {
            "format": "scientific_access_selection@1",
            "result_ref": selection.result_ref,
            "fields": selection._fields,
        },
    )
