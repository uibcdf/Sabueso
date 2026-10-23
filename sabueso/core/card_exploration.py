"""Readable navigation over the literal Card capture (#148).

Literal inspection and the first shared structural adapter use one captured state.
Destination navigation uses supplied captures only. Literal/field sessions support saved reading.
"""

from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass, field, replace
from types import MappingProxyType

from sabueso._private.argdigest import arg_digest

from .card_access import CardAccess, _Entry, _handle, _type
from .errors import ArgumentError

_LABELS = {
    "meta": "Card details",
    "sections": "Knowledge",
    "source_assertion_store": "Source statements",
    "relationship_store": "Relationships",
    "selection_rules": "Selection rules",
    "quality": "Coverage and quality records",
    "quantities": "Quantity integrity",
    "entities": "Entity records",
}
_TOPICS = {
    "chemistry": (
        "Chemical identity",
        "Retained chemical representations and source-stated identity links.",
    ),
    "properties": (
        "Physicochemical properties",
        "Stored values, units, source methods and alternatives.",
    ),
    "definition": (
        "Disease definition",
        "Ontology definition, scoped synonyms and retained term metadata.",
    ),
    "classification": (
        "Disease classification",
        "Retained parent relationships; identity terminology is separate.",
    ),
    "identity": (
        "Identity terminology",
        "Equivalent identifiers and related xrefs, explicitly separated.",
    ),
    "quality": (
        "Stored quality records",
        "Complete original quality, enrichment and selection records.",
    ),
    "function": (
        "Protein function",
        "Retained function, catalytic annotations and identity; no inferred function.",
    ),
    "structures": (
        "Experimental structures",
        "Existing inventory, original state rules and pinned support.",
    ),
    "content": ("Explore all content", "Complete retained Card content."),
    "sources": ("Source statements", "Original statements retained from sources."),
    "coverage": (
        "Knowledge coverage",
        "Original source/area knowledge states and their classification inputs.",
    ),
}


def _key(value):
    return {"type": "Key", "value": value}


@dataclass(frozen=True)
class Cell:
    """One retained value; public mutable values and support are defensive copies."""

    _value: object = field(repr=False)
    state: str = "present"
    reason: str | None = None
    _support: tuple = field(default=(), repr=False)

    @property
    def value(self):
        return deepcopy(self._value)

    @property
    def support(self):
        return deepcopy(list(self._support))

    def to_dict(self):
        return {
            "value": self.value,
            "state": self.state,
            "reason": self.reason,
            "support": self.support,
        }


@dataclass(frozen=True, repr=False)
class CardItem:
    """A labeled item bound to its originating selected view."""

    _view: object = field(repr=False)
    _entry: _Entry = field(repr=False)

    @property
    def item_ref(self):
        return _handle(
            "XI_",
            {"result_ref": self._view.result_ref, "location": self._entry.location},
        )

    @property
    def kind(self):
        if self._view._link_panel:
            return "link"
        if self._view._record_panel:
            return (
                "knowledge_state"
                if self._view._record_panel == "coverage"
                else "relationship"
            )
        if self._view._field_panel:
            from .card_exploration_profiles import is_field

            return "field" if is_field(self._entry) else "identity_statement"
        if self._view._selection._scientific is not None:
            return "structure"
        return "route" if self._view._route_catalog else "literal"

    @property
    def label(self):
        if self._view._link_panel:
            return self._entry.value["label"]
        if self._view._record_panel:
            if (
                self._view._record_panel == "coverage"
                and self._view._explorer.mode == "saved"
            ):
                return f"{self._entry.value['area']} · {self._entry.value['source']}"
            if self._view._record_panel == "classification":
                from .card_exploration_labels import relationship_basis

                return (
                    f"{relationship_basis(self)[0]} · {self._entry.value['object_ref']}"
                )
            from .card_exploration_profiles import record_label

            return record_label(self._view._record_panel, self._entry.value)
        if self._view._field_panel:
            from .card_exploration_profiles import field_label

            return field_label(self._view._field_panel, self._entry)
        if self._view._selection._scientific is not None:
            return self._entry.value["structure_ref"]
        if self._view._route_catalog:
            if self._view._question_catalog:
                return self._view._explorer._questions[self._entry.key]["label"]
            return self._view._explorer._topic_label(self._entry.key)
        segments = self._entry.location["segments"]
        if len(segments) == 1 and segments[0]["type"] == "Key":
            return _LABELS.get(self._entry.key, str(self._entry.key))
        node = self._entry.value
        if segments and segments[-1]["type"] == "Record" and isinstance(node, dict):
            if segments[0]["value"] == "source_assertion_store":
                source = node.get("source", {})
                name = source.get("name") if isinstance(source, dict) else source
                from .card_exploration_labels import source_role

                label = " · ".join(
                    str(v)
                    for v in (
                        name,
                        source.get("record_id") if isinstance(source, dict) else None,
                        node.get("field_path"),
                    )
                    if v is not None
                ) or str(self._entry.key)
                role = source_role(self)
                return f"{role} · {label}" if role else label
            return f"{node.get('predicate', 'Relationship')} → {node.get('object_ref', '')}"
        return str(self._entry.key) if self._entry.key is not None else "Value"

    @property
    def payload_location(self):
        return deepcopy(self._entry.location)

    @property
    def is_selected(self):
        return self._entry in self._view._selected

    @property
    def support(self):
        if self._view._link_panel:
            return deepcopy(self._entry.value["support"])
        if self._view._record_panel == "coverage":
            return [
                {
                    "basis": "derived_knowledge_state",
                    "rule": deepcopy(
                        self._view._explorer._coverage_result.native["rule"]
                    ),
                    "location": self.payload_location,
                    "explanation_available": True,
                }
            ]
        if self._view._selection._scientific is not None:
            return [
                deepcopy(
                    self._view._selection._scientific.wire["support"][self._entry.key]
                )
            ]
        return self._view._explorer._support(self._entry.location)

    @property
    def cells(self):
        if self._view._link_panel:
            return MappingProxyType(
                {
                    key: Cell(
                        self.label
                        if key == "label"
                        else self.kind
                        if key == "kind"
                        else self._entry.value[key],
                        _support=tuple(self.support),
                    )
                    for key in ("label", "kind", "role", "target_ref", "availability")
                }
            )
        if self._view._record_panel:
            from .card_exploration_profiles import RECORD_COLUMNS

            if (
                self._view._record_panel == "coverage"
                and self._view._explorer.mode == "saved"
            ):
                from .card_exploration_adapter_v1 import COVERAGE_COLUMNS

                columns = COVERAGE_COLUMNS
            else:
                columns = RECORD_COLUMNS[self._view._record_panel]
            return MappingProxyType(
                {
                    column: Cell(
                        value,
                        state="unknown" if value is None else "present",
                        _support=tuple(self.support),
                    )
                    for column in (
                        "label",
                        "kind",
                        *columns,
                    )
                    for value in (
                        self.label
                        if column == "label"
                        else self.kind
                        if column == "kind"
                        else self._entry.value.get(column),
                    )
                }
            )
        result = self._view._selection._scientific
        if result is not None:
            if self._view._explorer.mode == "saved":
                from .card_exploration_adapter_v1 import COLUMNS
            else:
                from .card_scientific_access import COLUMNS

            return MappingProxyType(
                {
                    column: Cell(
                        record["value"],
                        record["state"],
                        record["reason"],
                        tuple(record["support"]),
                    )
                    for column in ("label", "kind", *COLUMNS)
                    for record in (result.cell(self._entry.key, column),)
                }
            )
        from .card_exploration_profiles import is_field

        value = self._entry.value
        field_item = bool(self._view._field_panel) and is_field(self._entry)
        # Only declared Card quantities are converted; extension lookalikes stay raw.
        access = self._view._explorer.access
        quantity = None
        if isinstance(value, dict) and "value" in value and "unit" in value:
            quantity = access._quantity_context(
                {
                    **self._entry.location,
                    "segments": [*self._entry.location["segments"], _key("value")],
                }
            )
        if quantity is not None:
            from pyunitwizard import QuantityRecord

            value = QuantityRecord.from_dict(quantity["record"]).to_quantity(
                field=quantity["field"], unit=value["unit"]
            )
        elif field_item:
            value = value["value"]
        return MappingProxyType(
            {
                "label": Cell(self.label),
                "kind": Cell(self.kind),
                "value": Cell(
                    value,
                    state="conflicting"
                    if self._conflicts
                    else "unknown"
                    if field_item and value is None
                    else "present",
                    reason="Stored conflict; inspect explain() and the quality records."
                    if self._conflicts
                    else "No retained value for this field."
                    if field_item and value is None
                    else None,
                    _support=tuple(self.support),
                ),
                "type": Cell(
                    "quantity"
                    if field_item and quantity is not None
                    else _type(value)
                    if field_item
                    else _type(self._entry.value)
                ),
            }
        )

    @property
    def _conflicts(self):
        location = self._entry.location
        segments = location["segments"]
        if (
            location["kind"] != "card"
            or not segments
            or segments[0] != _key("sections")
        ):
            return []
        keys = [s["value"] for s in segments[1:] if s["type"] == "Key"]
        path = ".".join(keys)
        quality = self._view._explorer.access._focal.data.get("quality", {})
        conflicts = quality.get("conflicts", []) if isinstance(quality, dict) else []
        if not isinstance(conflicts, list):
            return []
        return [
            conflict
            for conflict in conflicts
            if isinstance(conflict, dict)
            and conflict.get("field") in (path, path.removesuffix(".value"))
        ]

    def open(self):
        """Open all retained detail, or follow a labeled catalog route."""
        if self._view._link_panel:
            from .card_context_navigation import follow

            return follow(self)
        if self._view._route_catalog:
            if self._view._question_catalog:
                return self._view._explorer._answer(self._entry.key, {}, self._view)
            return self._view._explorer._topic(self._entry.key, self._view)
        if self._view._selection._scientific is not None:
            return replace(
                self._view,
                _selected=(self._entry,),
                _origin=self._view,
                _focus=self._entry.key,
                _display_request=None,
                title=f"Structure {self.label}",
                presentation="detail",
            )
        return replace(
            self._view._explorer._inspect(
                self._entry.location, self._view, title=self.label
            ),
            _request=self._view._request,
            _display_request=None,
            _context_only=self._view._context_only,
            _context_override=self._view._context_override,
        )

    def related(self):
        """Explore retained sources, relationship endpoints and supplied Cards."""
        from .card_context_navigation import related

        if self._view._explorer.mode == "saved":
            from .card_exploration_storage import saved_item_operation

            return saved_item_operation(self, "links")
        result = related(self)
        from .card_exploration_storage import operation_key

        self._view._explorer._session["links"][operation_key(self)] = result
        return result

    def explain(self):
        """Inspect original support without interpreting a source's silence."""
        if self._view._explorer.mode == "saved":
            from .card_exploration_storage import saved_item_operation

            return saved_item_operation(self, "explanations")
        result = self._live_explain()
        from .card_exploration_storage import operation_key

        self._view._explorer._session["explanations"][operation_key(self)] = result
        return result

    def _live_explain(self):
        if self._view._link_panel:
            return self._view._explorer._metadata(
                {"rule": "retained_context_links@1", "link": self._entry.value},
                f"Link support for {self.label}",
                self._view,
            )
        if self._view._record_panel == "coverage":
            from .card_coverage_exploration import explain

            return explain(self._view._explorer, self._entry.value, self._view)
        result = self._view._selection._scientific
        if result is not None:
            selection = self._view._explorer.access.explain(self.item_ref)
            view = self._view._explorer._inspect(
                selection._target["location"],
                self._view,
                title=f"Scientific support for {self.label}",
            )
            entries = []
            seen = set()
            for statement in result.wire["support"][self._entry.key][
                "source_assertions"
            ]:
                if statement["state"] == "present" and statement["id"] not in seen:
                    value, location = self._view._explorer.access._resolve(
                        statement["location"]
                    )
                    entries.append(_Entry(location, statement["id"], value))
                    seen.add(statement["id"])
            return replace(
                view,
                _selected=tuple(entries),
                _selection=replace(view._selection, _entries=tuple(entries)),
                _native_override=result.explanations[self._entry.key],
                _request=self._view._request,
                _reason="Original source records for this structure relationship; complete scientific explanation remains in native_payload.",
            )
        from .card_exploration_profiles import alternatives

        alternative_context = (
            alternatives(self._view._explorer, self._entry)
            if self._view._field_panel
            else {}
        )
        view = self._view._explorer._metadata(
            {
                "basis": "stored_literal",
                "support": self.support,
                "stored_conflicts": self._conflicts,
                **alternative_context,
                "selection_rules": self._view._explorer.access._focal.data.get(
                    "selection_rules", {}
                ),
                "quality_location": self._view._explorer._location("quality"),
                "reason": "Original support only; no new scientific explanation is derived.",
            },
            f"Support for {self.label}",
            self._view,
        )
        view = replace(view, _request=self._view._request)
        if self._view._field_panel or self._view._record_panel == "classification":
            # Direct source-record rows spare the researcher a traversal through
            # support bookkeeping. Missing records stay explicit in native_payload.
            entries = []
            seen = set()
            for support in self.support:
                for statement in support.get("statements", []):
                    if statement["state"] == "present" and statement["id"] not in seen:
                        value, location = self._view._explorer.access._resolve(
                            statement["location"]
                        )
                        entries.append(_Entry(location, statement["id"], value))
                        seen.add(statement["id"])
            for statement in [
                *alternative_context.get("alternative_source_assertions", []),
                *alternative_context.get("unclassified_field_source_assertions", []),
            ]:
                if statement["state"] == "present" and statement["id"] not in seen:
                    value, location = self._view._explorer.access._resolve(
                        statement["location"]
                    )
                    entries.append(_Entry(location, statement["id"], value))
                    seen.add(statement["id"])
            return replace(
                view,
                _selected=tuple(entries),
                _selection=replace(view._selection, _entries=tuple(entries)),
                _reason="Original source records; unretained support and alternatives remain in native_payload.",
            )
        return view

    def back(self):
        return self._view

    def __repr__(self):
        from .card_exploration_render import preview

        return f"CardItem({preview(self.label)}; open(), explain(), related(), back())"


@dataclass(frozen=True, repr=False)
class CardItems(Sequence):
    """All selected items; rendering previews never truncate this sequence."""

    _view: object = field(repr=False)

    def __len__(self):
        return len(self._view._selected)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return tuple(self._view._item(e) for e in self._view._selected[index])
        return self._view._item(self._view._selected[index])

    def __repr__(self):
        return (
            f"CardItems({len(self)} items; index, slice or iterate for complete access)"
        )


@dataclass(frozen=True, repr=False)
class CardView:
    """One captured result with independent presentation and navigation state."""

    _explorer: object = field(repr=False)
    _selection: object = field(repr=False)
    _selected: tuple = field(repr=False)
    title: str
    _origin: object = field(default=None, repr=False)
    _route_catalog: bool = False
    _question_catalog: bool = False
    _field_panel: str | None = field(default=None, repr=False)
    _record_panel: str | None = field(default=None, repr=False)
    _link_panel: bool = field(default=False, repr=False)
    _context_override: object = field(default=None, repr=False)
    _context_only: bool = field(default=False, repr=False)
    _request: object = field(default=None, repr=False)
    _status: str = "ok"
    _reason: str | None = None
    presentation: str = "summary"
    _focus: str | None = field(default=None, repr=False)
    _native_override: object = field(default=None, repr=False)
    _saved_state: object = field(default=None, repr=False)
    _display_request: object = field(default=None, repr=False)
    _machine_ref: str | None = field(default=None, repr=False)

    def __post_init__(self):
        self._explorer._session["views"][id(self)] = self

    def _item(self, entry):
        if self._saved_state is not None:
            from .card_exploration_storage import _SavedItem

            return _SavedItem(self, entry)
        return CardItem(self, entry)

    @property
    def explorer(self):
        return None if self._context_only else self._explorer

    @property
    def result_ref(self):
        return self._selection.result_ref

    @property
    def view_ref(self):
        return _handle(
            "XV_",
            {
                "format": "literal_human_view@1",
                "result_ref": self.result_ref,
                "selection": [item.item_ref for item in self.items()],
                "presentation": self.presentation,
                "title": self.title,
                "route_catalog": self._route_catalog,
                **({"link_panel": True} if self._link_panel else {}),
                **(
                    {"context": self._context_override}
                    if self._context_override
                    else {}
                ),
                **({"focus": self._focus} if self._focus is not None else {}),
                **(
                    {"question_request": self._request}
                    if self._request is not None
                    else {}
                ),
                **({"question_catalog": True} if self._question_catalog else {}),
                **({"field_panel": self._field_panel} if self._field_panel else {}),
                **({"record_panel": self._record_panel} if self._record_panel else {}),
            },
        )

    @property
    def at_root(self):
        return self._origin is None

    @property
    def context(self):
        if self._saved_state is not None:
            return {**deepcopy(self._saved_state["context"]), "mode": "saved"}
        if self._context_override is not None:
            return deepcopy(self._context_override)
        if self._link_panel:
            return {**self._explorer.context, "adapter": "retained_context_links@1"}
        if self._selection._scientific is not None:
            return deepcopy(self._selection._scientific.wire["context"])
        if self._record_panel or self._field_panel:
            adapter = (
                "knowledge_coverage_exploration@1"
                if self._record_panel == "coverage"
                else "disease_classification_fields@1"
                if self._record_panel
                else "protein_function_fields@1"
                if self._field_panel == "function"
                else f"{self._field_panel}_fields@1"
            )
            return {
                **self._explorer.context,
                "adapter": adapter,
                "used_captures": [self._explorer.access._focal_key],
            }
        return {**self._explorer.context, "adapter": "literal_human@1"}

    @property
    def outcome(self):
        return {"status": self._status, "reason": self._reason}

    @property
    def validation(self):
        """Reported saved integrity/binding scope, or None for a live interpretation."""
        return (
            deepcopy(self._explorer._session.get("validation"))
            if self._explorer.mode == "saved"
            else None
        )

    @property
    def request(self):
        """Explicit question binding, or None for ordinary topic/literal views."""
        return deepcopy(self._request)

    @property
    def coverage(self):
        if self._saved_state is not None:
            return deepcopy(self._saved_state["coverage"])
        if self._record_panel == "coverage" and self._explorer._coverage_result.native:
            return {
                "basis": "original_knowledge_state",
                **deepcopy(self._explorer._coverage_result.native),
                "reason": "Source/area/request scope only; no global completeness denominator is known.",
            }
        if self._selection._scientific is not None:
            return deepcopy(self._selection._scientific.wire["coverage"])
        return {
            "classification": "not_evaluated",
            "basis": "stored_literal",
            "quality_location": None
            if self._context_only
            else self._explorer._location("quality"),
            "reason": "Inspect the stored quality records; no source coverage is inferred.",
        }

    @property
    def capabilities(self):
        capabilities = {
            "items": True,
            "rows": True,
            "inspect": not self._context_only,
            "explain": True,
            "filter": ["label", "kind"],
            "sort": ["label", "kind"],
            "related": not self._context_only,
            "save": self._can_save(),
            "scientific_adapter": False,
        }
        if self._link_panel:
            capabilities.update(
                filter=self.schema["columns"], sort=self.schema["columns"], follow=True
            )
        if self._record_panel:
            capabilities.update(
                filter=self.schema["columns"], sort=self.schema["columns"]
            )
            capabilities["scientific_adapter"] = self._record_panel == "coverage"
        if self._selection._scientific is not None:
            capabilities.update(
                scientific_adapter=True,
                filter=self.schema["columns"],
                sort=[
                    c for c in self.schema["columns"] if c not in ("chains", "state")
                ],
            )
        if self._machine_ref is not None:
            capabilities["root_machine_selection_ref"] = self._machine_ref
        if self._explorer.mode == "saved":
            from .card_exploration_storage import operation_key

            keys = [operation_key(CardItem(self, entry)) for entry in self._selected]
            capabilities["explain"] = bool(keys) and all(
                key in self._explorer._session["explanations"] for key in keys
            )
            capabilities["related"] = bool(keys) and all(
                key in self._explorer._session["links"] for key in keys
            )
        return capabilities

    @property
    def schema(self):
        if self._saved_state is not None:
            return deepcopy(self._saved_state["schema"])
        if self._explorer.mode == "saved":
            from .card_exploration_adapter_v1 import (
                COVERAGE_HUMAN_SCHEMA,
                STRUCTURE_HUMAN_SCHEMA,
            )

            if self._selection._scientific is not None:
                return deepcopy(STRUCTURE_HUMAN_SCHEMA)
            if self._record_panel == "coverage":
                return deepcopy(COVERAGE_HUMAN_SCHEMA)
        if self._link_panel:
            return {
                "kind": "link",
                "grain": "one retained destination role",
                "columns": ["label", "kind", "role", "target_ref", "availability"],
                "presentations": ["summary", "table"],
            }
        if self._record_panel:
            from .card_exploration_profiles import RECORD_COLUMNS

            return {
                "kind": "knowledge_state"
                if self._record_panel == "coverage"
                else "relationship",
                "grain": "one original source/area classification row"
                if self._record_panel == "coverage"
                else "one retained parent relationship",
                "columns": ["label", "kind", *RECORD_COLUMNS[self._record_panel]],
                "presentations": ["summary", "table"],
            }
        if self._selection._scientific is not None:
            from .card_scientific_access import COLUMNS

            return {
                "kind": "structure",
                "grain": "one retained structural inventory entry",
                "columns": ["label", "kind", *COLUMNS],
                "presentations": ["summary", "table", "detail"],
                "quantity_expectations": {
                    "resolution": {
                        "field": "relationships.has_structure.resolution",
                        "unit": "angstrom",
                    }
                },
            }
        from .quantities import FIELD_UNITS

        return {
            "kind": "field"
            if self._field_panel
            else "route"
            if self._route_catalog
            else "literal",
            "grain": "one retained field or source-stated identity statement"
            if self._field_panel == "chemistry"
            else f"one retained {self._explorer.profile} field"
            if self._field_panel
            else "retained literal nodes, or navigation catalog entries",
            "columns": ["label", "kind", "value", "type"],
            "presentations": ["summary", "table"],
            "selection_columns": ["label", "kind"],
            **(
                {
                    "quantity_expectations": {
                        path: {"field": path, "unit": unit}
                        for path, unit in FIELD_UNITS.items()
                        if path.startswith("properties.physchem.")
                    }
                }
                if self._field_panel == "properties"
                else {}
            ),
        }

    @property
    def exclusions(self):
        """Original scientific exclusions, separate from display filtering."""
        return (
            deepcopy(self._selection._scientific.wire["exclusions"])
            if self._selection._scientific is not None
            else []
        )

    @property
    def native_payload(self):
        if self._native_override is not None:
            return deepcopy(self._native_override)
        if self._selection._scientific is not None:
            result = self._selection._scientific
            return deepcopy(
                result.native_item(self._focus)
                if self._focus is not None
                else result.native
            )
        return deepcopy(
            self._explorer.access._resolve(self._selection._target["location"])[0]
        )

    def items(self):
        return CardItems(self)

    def rows(self):
        """Explicit complete selected rows, including unabridged typed values."""
        return [
            {
                "item_ref": item.item_ref,
                "kind": item.kind,
                "label": item.label,
                "cells": {key: cell.to_dict() for key, cell in item.cells.items()},
                "support": item.support,
                "payload_location": item.payload_location,
            }
            for item in self.items()
        ]

    @arg_digest()
    def item(self, item_ref, skip_digestion=False):
        """Find an exact original item, including one hidden by a display filter."""
        for entry in self._selection._entries:
            item = self._item(entry)
            if item.item_ref == item_ref:
                return item
        raise ArgumentError("This item reference does not belong to this result.")

    @arg_digest()
    def follow(self, item_ref, skip_digestion=False):
        """Open an exact link in this result, including display-filtered links."""
        if not self._link_panel:
            raise ArgumentError("follow requires a link view.")
        return self.item(item_ref).open()

    @arg_digest()
    def filter(self, column, *, equals, skip_digestion=False):
        """Select exact declared cells without changing the scientific result."""
        self._check_column(column)
        scientific = self._selection._scientific is not None
        if scientific:
            if self._explorer.mode == "saved":
                from .card_exploration_adapter_v1 import (
                    _validate_equality as validate_equality,
                )
            else:
                from .card_scientific_access import validate_equality

            validate_equality(column, equals)
        elif self._record_panel == "coverage" and column == "count":
            import math

            if type(equals) not in (int, float) or not math.isfinite(equals):
                raise ArgumentError(
                    "count equality requires a finite number, not a boolean."
                )
        elif not isinstance(equals, str):
            raise ArgumentError("This column requires string equality.")
        if self._status not in ("ok", "empty") and not (
            self._link_panel and self._status == "ambiguous"
        ):
            return replace(self, _origin=self)
        if scientific and self._explorer.mode == "saved":
            from .card_exploration_adapter_v1 import _equal_values as equal_values
        else:
            from .card_scientific_access import equal_values

        entries = tuple(
            item._entry
            for item in self.items()
            if item.cells[column].state in ("present", "conflicting")
            and equal_values(column, item.cells[column]._value, equals)
        )
        return replace(
            self,
            _selected=entries,
            _origin=self,
            _status=("ambiguous" if self._status == "ambiguous" else "ok")
            if entries
            else "empty",
            _reason=None if entries else "No items match this display selection.",
            _display_request={
                "operation": "filter",
                "column": column,
                "equals": deepcopy(equals),
            },
        )

    @arg_digest()
    def sort(self, column, descending=False, skip_digestion=False, *, unit=None):
        """Sort declared scalar cells with missing values last and explicit units."""
        self._check_column(column)
        if type(descending) is not bool:
            raise ArgumentError("descending must be True or False.")
        if unit is not None and (not isinstance(unit, str) or not unit.strip()):
            raise ArgumentError("unit requires a nonempty unit name or None.")
        if self._selection._scientific is not None and self._explorer.mode == "saved":
            from .card_exploration_adapter_v1 import _sorted_entries as sorted_entries
        else:
            from .card_scientific_access import sorted_entries

        if self._record_panel or self._link_panel:
            if unit is not None:
                raise ArgumentError("These record columns do not take a quantity unit.")
            present, missing = [], []
            for item in self.items():
                value = item.cells[column]._value
                (missing if value is None else present).append((value, item._entry))
            present.sort(key=lambda pair: pair[0], reverse=descending)
            entries = tuple(entry for _, entry in [*present, *missing])
        else:
            entries = sorted_entries(self, column, descending, unit)
        return replace(
            self,
            _selected=entries,
            _origin=self,
            _display_request={
                "operation": "sort",
                "column": column,
                "descending": descending,
                "unit": unit,
            },
        )

    def _check_column(self, column):
        if (
            not isinstance(column, str)
            or column not in self.schema["columns"]
            or (
                self._selection._scientific is None
                and not self._record_panel
                and not self._link_panel
                and column not in ("label", "kind")
            )
        ):
            raise ArgumentError(
                f"Available selection columns: {self.capabilities['filter']}."
            )

    def _can_save(self):
        from .card_exploration_storage import can_save

        return can_save(self)

    @arg_digest()
    def save(self, path, *, overwrite=False, skip_digestion=False):
        """Save supported retained views and their original captured context atomically."""
        from .card_exploration_storage import save_exploration

        return save_exploration(self, path, overwrite=overwrite)

    def summary(self):
        return replace(
            self,
            presentation="summary",
            _origin=self,
            _display_request={"operation": "presentation"},
        )

    def table(self):
        return replace(
            self,
            presentation="table",
            _origin=self,
            _display_request={"operation": "presentation"},
        )

    def back(self):
        return self if self.at_root else self._origin

    def __repr__(self):
        from .card_exploration_render import render_text

        return render_text(self)

    def _repr_html_(self):
        from .card_exploration_render import render_html

        return render_html(self)


class CardExplorer:
    """Readable focal Card inspection with the exact same capture as ``access``.

    Start with ``overview()`` or ``topics()``. This generic first slice supports
    every valid Card nature; proteins also have function fields, structural views
    and explicit scientific questions. Navigation opens only captured destinations.
    """

    __slots__ = (
        "_access",
        "_coverage_result",
        "_origin",
        "_navigation_cache",
        "_session",
    )

    @arg_digest()
    def __init__(self, card, related_cards=(), skip_digestion=False):
        self._access = CardAccess(card, related_cards)
        self._coverage_result = None
        self._origin = None
        self._navigation_cache = {}
        self._session = {
            "views": {},
            "explanations": {},
            "links": {},
        }
        self._access._exploration_session = self._session

    @property
    def access(self):
        return self._access

    @property
    def profile(self):
        return self.access.profile

    @property
    def mode(self):
        return self.access.mode

    @property
    def context(self):
        return self.access.context

    @property
    def capabilities(self):
        capabilities = {
            "topics": list(self._topics),
            "inspect": True,
            "search": "literal_casefold",
            "scientific_questions": bool(self._questions),
            "question_keys": list(self._questions),
            "scientific_topics": [*self._nature_topics, "coverage"]
            if self._nature_topics
            else [],
            "cross_card_navigation": True,
            "save": True,
        }

        if self.mode == "saved":
            views = [
                view
                for view in self._session["views"].values()
                if view._saved_state is not None
                and view._explorer.access._focal_key == self.access._focal_key
            ]
            topics = {
                view._field_panel
                for view in views
                if view._field_panel in self._nature_topics
                and view._field_panel is not None
            }
            topics.update(
                view._record_panel
                for view in views
                if view._record_panel in ("classification", "coverage")
            )
            from .card_structure_selection_v1 import original

            if any(original(view._selection) for view in views):
                topics.add("structures")
            questions = {
                view.request["question"] for view in views if view.request is not None
            }
            capabilities.update(
                scientific_topics=sorted(topics),
                question_keys=sorted(questions),
                scientific_questions=bool(questions),
                not_saved_topics=sorted(
                    set(capabilities["scientific_topics"]) - topics
                ),
            )
        return capabilities

    def start_new(self):
        """Start a new local interpretation from the captures, without source access."""
        from .card_exploration_storage import start_new

        return start_new(self)

    @property
    def _nature_topics(self):
        from .card_exploration_profiles import NATURE_TOPICS

        return NATURE_TOPICS.get(self.profile, ())

    @property
    def _topics(self):
        keys = (
            (*self._nature_topics, "sources", "coverage", "quality", "content")
            if self._nature_topics
            else ("sources", "coverage", "content")
        )
        return {
            key: (
                "Coverage and quality records",
                "Original stored quality records; source knowledge coverage is not evaluated.",
            )
            if key == "coverage" and not self._nature_topics
            else _TOPICS[key]
            for key in keys
        }

    def _topic_label(self, topic):
        return (
            "Coverage and quality records"
            if topic == "coverage" and not self._nature_topics
            else _TOPICS[topic][0]
        )

    @property
    def _questions(self):
        from .card_exploration_profiles import QUESTIONS

        return QUESTIONS.get(self.profile, {})

    def _location(self, *keys):
        return self.access._card_location(segments=[_key(key) for key in keys])

    def _inspect(self, location, origin=None, *, title="All retained content"):
        node, full = self.access._resolve(location)
        origin = self._origin if origin is None else origin
        if full["kind"] == "card" and (
            full["card_ref"] != self.context["card_ref"]
            or full["snapshot_id"] != self.context["snapshot_id"]
        ):
            raise ArgumentError(
                "Inspection is limited to the focal capture; open a related link to switch context explicitly."
            )
        selection = self.access.read(full)
        return CardView(
            self,
            selection,
            selection._entries,
            title,
            origin,
            _status="ok" if selection.count else "empty",
            _reason=None if selection.count else "This retained container is empty.",
        )

    def _metadata(self, value, title, origin=None):
        return self._inspect(self.access._object_location(value), origin, title=title)

    def overview(self):
        """Readable opening with recorded identity and explicit navigation routes."""
        if self._nature_topics:
            return replace(self.topics(), title="Card overview")
        return self._inspect(self.access.root_location, title="Card overview")

    def topics(self):
        """Only delivered routes; no unavailable scientific panels are advertised."""
        descriptors = {
            key: {"description": value[1]} for key, value in self._topics.items()
        }
        if self.mode == "saved":
            missing = set(self.capabilities["not_saved_topics"])
            for key, descriptor in descriptors.items():
                descriptor["availability"] = (
                    "not_saved" if key in missing else "retained"
                )
        result = self._metadata(descriptors, "Where would you like to explore?")
        order = tuple(self._topics)
        return replace(
            result,
            _route_catalog=True,
            _selected=tuple(
                sorted(result._selected, key=lambda entry: order.index(entry.key))
            ),
        )

    def questions(self):
        """Delivered question routes, their scope and required explicit inputs."""
        if self._questions:
            result = self._metadata(self._questions, "Scientific questions")
            order = tuple(self._questions)
            return replace(
                result,
                _selected=tuple(
                    sorted(result._selected, key=lambda entry: order.index(entry.key))
                ),
                _route_catalog=True,
                _question_catalog=True,
            )
        return replace(
            self._metadata({}, "Scientific questions"),
            _status="unsupported",
            _reason="Scientific question adapters are not implemented. Use topics() or inspect().",
        )

    def _topic(self, topic, origin=None, options=None):
        if self.mode == "saved":
            from .card_exploration_storage import saved_topic

            return saved_topic(self, topic, origin, options)
        return self._live_topic(topic, origin, options)

    def _live_topic(self, topic, origin=None, options=None):
        origin = self._origin if origin is None else origin
        if not isinstance(topic, str):
            raise ArgumentError("topic requires a declared topic key.")
        if options is not None and not isinstance(options, dict):
            raise ArgumentError("Scientific options require a mapping or None.")
        from .card_exploration_profiles import PANELS

        if topic in PANELS:
            if options not in (None, {}):
                raise ArgumentError(f"{topic} has no scientific options.")
            return self._field_view(topic, origin)
        if topic == "classification":
            if options not in (None, {}):
                raise ArgumentError("classification has no scientific options.")
            return self._classification(origin)
        if topic == "coverage" and self._nature_topics:
            if options not in (None, {}):
                raise ArgumentError("coverage has no scientific options.")
            from .card_coverage_exploration import view

            return view(self, origin)
        if topic == "structures":
            selection = self.access.select(topic, options=options)
            result = selection._scientific
            return CardView(
                self,
                selection,
                selection._entries,
                "Experimental structures",
                origin,
                _status=result.wire["outcome"]["status"],
                _reason=result.wire["outcome"]["reason"],
            )
        if options not in (None, {}):
            raise ArgumentError("Scientific options are valid only for structures.")
        if not isinstance(topic, str) or topic not in self._topics:
            raise ArgumentError(f"Available topics: {', '.join(_TOPICS)}.")
        location = {
            "content": self.access.root_location,
            "sources": self._location("source_assertion_store"),
            "coverage": self._location("quality"),
            "quality": self._location("quality"),
        }[topic]
        return self._inspect(location, origin, title=self._topic_label(topic))

    def _field_view(self, topic, origin):
        from .card_exploration_profiles import PANELS, field_entries

        nature = PANELS[topic][0]
        applicable = self.profile == nature
        entries, gaps = field_entries(self, topic) if applicable else ((), [])
        result = self._metadata(
            {
                "adapter": "protein_function_fields@1"
                if topic == "function"
                else f"{topic}_fields@1",
                "context": self.context,
                "fields": {entry.key: entry.value for entry in entries},
                "field_gaps": gaps,
                "scope": "Retained fields only; no function is inferred from a name. Source coverage is not evaluated."
                if topic == "function"
                else "Retained source statements only; no chemical calculation, diagnosis or identity inference. Source coverage is not evaluated.",
            },
            _TOPICS[topic][0],
            origin,
        )
        return replace(
            result,
            _selection=replace(result._selection, _entries=entries),
            _selected=entries,
            _field_panel=topic,
            _status="not_applicable"
            if not applicable
            else "ok"
            if entries
            else "empty",
            _reason=f"The {topic} route requires a {nature} Card."
            if not applicable
            else "Function description has no supported retained field value; inspect field_gaps and the original content."
            if topic == "function"
            and any(row["field"] == "annotations.function" for row in gaps)
            else "Only retained values are shown; inspect field_gaps for missing or unsupported fields."
            if gaps
            else None,
        )

    def _classification(self, origin):
        nature = self.profile == "disease"
        card_id = self.access._focal.data.get("meta", {}).get("card_id")
        focal = (
            card_id.removeprefix("sabueso:disease:")
            if isinstance(card_id, str) and card_id.startswith("sabueso:disease:")
            else None
        )
        parent = self._location("relationship_store")
        entries = tuple(
            entry
            for entry in self.access._children(
                self.access._focal.data["relationship_store"], parent
            )
            if nature
            and focal
            and entry.value["predicate"] == "subclass_of"
            and entry.value["subject_ref"] == focal
        )
        result = self._metadata(
            {
                "adapter": "disease_classification_fields@1",
                "context": self.context,
                "focal_ref": focal,
                "relationships": [entry.value for entry in entries],
                "identity_route": "identity",
                "scope": "Exact focal-subject stored parent relationships only; no parent Card is opened or fetched.",
            },
            "Disease classification",
            origin,
        )
        return replace(
            result,
            _selection=replace(result._selection, _entries=entries),
            _selected=entries,
            _record_panel="classification",
            _status="not_applicable"
            if not nature
            else "missing_prerequisite"
            if not focal
            else "ok"
            if entries
            else "empty",
            _reason="This route requires a disease Card."
            if not nature
            else "A focal disease identity is required."
            if not focal
            else "Parent term Cards were not opened. Identity terminology: explorer.view('identity'); equivalence and related xrefs are separate from parent edges.",
        )

    @arg_digest()
    def view(self, topic, skip_digestion=False, *, options=None):
        """Open a delivered topic by its catalog key."""
        return self._topic(topic, options=options)

    def _answer(self, question, options, origin=None):
        if self.mode == "saved":
            from .card_exploration_storage import saved_answer

            return saved_answer(self, question, options, origin)
        return self._live_answer(question, options, origin)

    def _live_answer(self, question, options, origin=None):
        if not isinstance(question, str) or question not in self._questions:
            raise ArgumentError(
                f"Available question keys: {', '.join(self._questions) or '(none for this Card nature)'}."
            )
        if not isinstance(options, dict):
            raise ArgumentError("Question options require a mapping.")
        if question != "region_coverage":
            view = self._topic(self._questions[question]["topic"], origin, options)
            effective = {}
        else:
            from .card_protein_exploration import region_request

            effective, status, reason = region_request(self, options)
            if status == "ok":
                view = self._topic(
                    "structures",
                    origin,
                    {
                        key: value
                        for key, value in effective.items()
                        if key != "sequence_ref"
                    },
                )
            else:
                view = replace(
                    self._metadata(
                        {
                            "question": question,
                            "options": effective,
                            "outcome": {"status": status, "reason": reason},
                        },
                        "Structural region coverage",
                        origin,
                    ),
                    _status=status,
                    _reason=reason,
                )
                view = replace(
                    view, _selection=replace(view._selection, _entries=()), _selected=()
                )
        return replace(
            view,
            _request={
                "question": question,
                "options": deepcopy(effective),
                "topic": self._questions[question]["topic"],
            },
        )

    @arg_digest()
    def answer(self, question, skip_digestion=False, *, options=None):
        """Follow a registered scientific question over the same captured results.

        ``region_coverage`` requires an explicit canonical UniProt sequence_ref
        and region in ``options``. Missing scope never starts a source query.
        """
        return self._answer(question, {} if options is None else options)

    @arg_digest()
    def inspect(self, field_path=None, *, locator=None, skip_digestion=False):
        """Inspect everything, a dotted section field, or an exact typed location.

        Literal keys containing dots are reached through items or ``locator``;
        dotted paths are convenient section-field paths, never a key-guessing rule.
        """
        if field_path is not None and locator is not None:
            raise ArgumentError("Use field_path or locator, not both.")
        if field_path is not None:
            if not isinstance(field_path, str) or any(
                not part.strip() for part in field_path.split(".")
            ):
                raise ArgumentError("field_path requires nonempty dotted segments.")
            locator = self._location("sections", *field_path.split("."))
        return self._inspect(self.access.root_location if locator is None else locator)

    @arg_digest()
    def search(self, text, skip_digestion=False):
        """Find every literal key/scalar match locally, using Unicode casefold."""
        if not isinstance(text, str) or not text.strip():
            raise ArgumentError("text must be a nonempty string.")
        needle, matches = text.casefold(), []
        stack = [_Entry(self.access._card_location(), None, self.access._focal.data)]
        while stack:
            entry = stack.pop()
            value = entry.value
            if (entry.key is not None and needle in str(entry.key).casefold()) or (
                not isinstance(value, (list, dict)) and needle in str(value).casefold()
            ):
                matches.append(entry)
            if isinstance(value, (list, dict)):
                stack.extend(reversed(self.access._children(value, entry.location)))
        base = self._metadata({"query": text}, "Literal search")
        # The complete captured inputs and query bind a deterministic search result;
        # hit locations always point to original content, never copied search rows.
        selection = replace(
            base._selection,
            _result_ref=_handle(
                "XR_",
                {
                    "format": "literal_human_search@1",
                    "inputs": self.context["captures"],
                    "focal": self.context["snapshot_id"],
                    "text": text,
                },
            ),
            _entries=tuple(matches),
            _target={"location": self.access.root_location},
        )
        return replace(
            base,
            _selection=selection,
            _selected=tuple(matches),
            _status="ok" if matches else "empty",
            _reason="Literal matches only; no scientific meaning or completeness is inferred.",
        )

    def _support(self, location):
        """Nearest original field/record support; metadata is never source evidence."""
        if location["kind"] != "card":
            return [{"basis": "navigation_metadata", "location": deepcopy(location)}]
        segments = location["segments"]
        # Start at the outside: objects nested inside a field's original value
        # cannot redeclare lineage merely by resembling a field node.
        for stop in range(1, len(segments) + 1):
            owner = {**location, "segments": segments[:stop]}
            node, _ = self.access._resolve(owner)
            store = segments[0]["value"]
            if stop == 2 and store == "source_assertion_store":
                return [{"basis": "original_assertion", "location": owner}]
            relationship = stop == 2 and store == "relationship_store"
            field_support = (
                store == "sections"
                and isinstance(node, dict)
                and "value" in node
                and isinstance(node.get("source_assertion_ids"), list)
                and all(isinstance(ref, str) for ref in node["source_assertion_ids"])
            )
            if relationship or field_support:
                refs = node.get("source_assertion_ids", [])
                support = {
                    "basis": "relationship_level"
                    if relationship
                    else "original_field_support",
                    "location": owner,
                    "source_assertion_ids": deepcopy(refs),
                    "statements": [self._statement(ref) for ref in refs]
                    if isinstance(refs, list)
                    and all(isinstance(ref, str) for ref in refs)
                    else [],
                }
                if relationship:
                    for key in ("derivation", "qualifier_conflicts"):
                        if key in node:
                            support[key] = deepcopy(node[key])
                return [support]
        return [{"basis": "stored_literal", "location": deepcopy(location)}]

    def _statement(self, ref):
        location = {
            **self._location("source_assertion_store"),
            "segments": [
                _key("source_assertion_store"),
                {"type": "Record", "value": ref},
            ],
        }
        try:
            self.access._resolve(location)
        except ArgumentError:
            return {"id": ref, "state": "not_retained", "location": None}
        return {"id": ref, "state": "present", "location": location}

    def __repr__(self):
        if not hasattr(self, "_access"):
            return "CardExplorer(initializing)"
        return repr(self.overview())

    def _repr_html_(self):
        return self.overview()._repr_html_()
