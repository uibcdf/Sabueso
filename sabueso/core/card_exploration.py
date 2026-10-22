"""Readable navigation over the literal Card capture (#148).

Literal inspection and the first shared structural adapter use one captured state.
Destination-Card joins and saved sessions remain pending. All access is local.
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
    "structures": (
        "Experimental structures",
        "Existing inventory, original state rules and pinned support.",
    ),
    "content": ("Explore all content", "Complete retained Card content."),
    "sources": ("Source statements", "Original statements retained from sources."),
    "coverage": (
        "Coverage and quality records",
        "Stored records only; this view does not assess source coverage.",
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
        if self._view._selection._scientific is not None:
            return "structure"
        return "route" if self._view._route_catalog else "literal"

    @property
    def label(self):
        if self._view._selection._scientific is not None:
            return self._entry.value["structure_ref"]
        if self._view._route_catalog:
            return _TOPICS[self._entry.key][0]
        segments = self._entry.location["segments"]
        if len(segments) == 1 and segments[0]["type"] == "Key":
            return _LABELS.get(self._entry.key, str(self._entry.key))
        node = self._entry.value
        if segments and segments[-1]["type"] == "Record" and isinstance(node, dict):
            if segments[0]["value"] == "source_assertion_store":
                source = node.get("source", {})
                name = source.get("name") if isinstance(source, dict) else source
                return " · ".join(
                    str(v)
                    for v in (
                        name,
                        source.get("record_id") if isinstance(source, dict) else None,
                        node.get("field_path"),
                    )
                    if v is not None
                ) or str(self._entry.key)
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
        if self._view._selection._scientific is not None:
            return [
                deepcopy(
                    self._view._selection._scientific.wire["support"][self._entry.key]
                )
            ]
        return self._view.explorer._support(self._entry.location)

    @property
    def cells(self):
        result = self._view._selection._scientific
        if result is not None:
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
        value = self._entry.value
        # Only declared Card quantities are converted; extension lookalikes stay raw.
        access = self._view.explorer.access
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
        return MappingProxyType(
            {
                "label": Cell(self.label),
                "kind": Cell(self.kind),
                "value": Cell(
                    value,
                    state="conflicting" if self._conflicts else "present",
                    reason="Stored conflict; inspect explain() and the quality records."
                    if self._conflicts
                    else None,
                    _support=tuple(self.support),
                ),
                "type": Cell(_type(self._entry.value)),
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
        quality = self._view.explorer.access._focal.data.get("quality", {})
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
        if self._view._route_catalog:
            return self._view.explorer._topic(self._entry.key, self._view)
        if self._view._selection._scientific is not None:
            return replace(
                self._view,
                _selected=(self._entry,),
                _origin=self._view,
                _focus=self._entry.key,
                title=f"Structure {self.label}",
                presentation="detail",
            )
        return self._view.explorer._inspect(
            self._entry.location, self._view, title=self.label
        )

    def explain(self):
        """Inspect original support without interpreting a source's silence."""
        result = self._view._selection._scientific
        if result is not None:
            selection = self._view.explorer.access.explain(self.item_ref)
            view = self._view.explorer._inspect(
                selection._target["location"],
                self._view,
                title=f"Scientific support for {self.label}",
            )
            return replace(view, _native_override=result.explanations[self._entry.key])
        return self._view.explorer._metadata(
            {
                "basis": "stored_literal",
                "support": self.support,
                "stored_conflicts": self._conflicts,
                "selection_rules": self._view.explorer.access._focal.data.get(
                    "selection_rules", {}
                ),
                "quality_location": self._view.explorer._location("quality"),
                "reason": "Original support only; no new scientific explanation is derived.",
            },
            f"Support for {self.label}",
            self._view,
        )

    def back(self):
        return self._view

    def __repr__(self):
        from .card_exploration_render import preview

        return f"CardItem({preview(self.label)}; open(), explain(), back())"


@dataclass(frozen=True, repr=False)
class CardItems(Sequence):
    """All selected items; rendering previews never truncate this sequence."""

    _view: object = field(repr=False)

    def __len__(self):
        return len(self._view._selected)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return tuple(CardItem(self._view, e) for e in self._view._selected[index])
        return CardItem(self._view, self._view._selected[index])

    def __repr__(self):
        return (
            f"CardItems({len(self)} items; index, slice or iterate for complete access)"
        )


@dataclass(frozen=True, repr=False)
class CardView:
    """One captured result with independent presentation and navigation state."""

    explorer: object = field(repr=False)
    _selection: object = field(repr=False)
    _selected: tuple = field(repr=False)
    title: str
    _origin: object = field(default=None, repr=False)
    _route_catalog: bool = False
    _status: str = "ok"
    _reason: str | None = None
    presentation: str = "summary"
    _focus: str | None = field(default=None, repr=False)
    _native_override: object = field(default=None, repr=False)

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
                **({"focus": self._focus} if self._focus is not None else {}),
            },
        )

    @property
    def at_root(self):
        return self._origin is None

    @property
    def context(self):
        if self._selection._scientific is not None:
            return deepcopy(self._selection._scientific.wire["context"])
        return {**self.explorer.context, "adapter": "literal_human@1"}

    @property
    def outcome(self):
        return {"status": self._status, "reason": self._reason}

    @property
    def coverage(self):
        if self._selection._scientific is not None:
            return deepcopy(self._selection._scientific.wire["coverage"])
        return {
            "classification": "not_evaluated",
            "basis": "stored_literal",
            "quality_location": self.explorer._location("quality"),
            "reason": "Inspect the stored quality records; no source coverage is inferred.",
        }

    @property
    def capabilities(self):
        capabilities = {
            "items": True,
            "rows": True,
            "inspect": True,
            "explain": True,
            "filter": ["label", "kind"],
            "sort": ["label", "kind"],
            "related": False,
            "save": False,
            "scientific_adapter": False,
        }
        if self._selection._scientific is not None:
            capabilities.update(
                scientific_adapter=True,
                filter=self.schema["columns"],
                sort=[
                    c for c in self.schema["columns"] if c not in ("chains", "state")
                ],
            )
        return capabilities

    @property
    def schema(self):
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
        return {
            "kind": "route" if self._route_catalog else "literal",
            "grain": "retained literal nodes, or navigation catalog entries",
            "columns": ["label", "kind", "value", "type"],
            "presentations": ["summary", "table"],
            "selection_columns": ["label", "kind"],
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
            self.explorer.access._resolve(self._selection._target["location"])[0]
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
            item = CardItem(self, entry)
            if item.item_ref == item_ref:
                return item
        raise ArgumentError("This item reference does not belong to this result.")

    @arg_digest()
    def filter(self, column, *, equals, skip_digestion=False):
        """Select exact declared cells without changing the scientific result."""
        self._check_column(column)
        scientific = self._selection._scientific is not None
        if scientific:
            from .card_scientific_access import validate_equality

            validate_equality(column, equals)
        elif not isinstance(equals, str):
            raise ArgumentError("Label and kind equality requires a string.")
        if self._status not in ("ok", "empty"):
            return replace(self, _origin=self)
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
            _status="ok" if entries else "empty",
            _reason=None if entries else "No items match this display selection.",
        )

    @arg_digest()
    def sort(self, column, descending=False, skip_digestion=False, *, unit=None):
        """Sort declared scalar cells with missing values last and explicit units."""
        self._check_column(column)
        if type(descending) is not bool:
            raise ArgumentError("descending must be True or False.")
        if unit is not None and (not isinstance(unit, str) or not unit.strip()):
            raise ArgumentError("unit requires a nonempty unit name or None.")
        from .card_scientific_access import sorted_entries

        entries = sorted_entries(self, column, descending, unit)
        return replace(self, _selected=entries, _origin=self)

    def _check_column(self, column):
        if (
            not isinstance(column, str)
            or column not in self.schema["columns"]
            or (self._selection._scientific is None and column not in ("label", "kind"))
        ):
            raise ArgumentError(
                f"Available selection columns: {self.capabilities['filter']}."
            )

    def summary(self):
        return replace(self, presentation="summary", _origin=self)

    def table(self):
        return replace(self, presentation="table", _origin=self)

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
    every valid Card nature; proteins also have the structural adapter. Scientific
    question aliases and cross-Card human navigation remain unavailable; capability metadata states that boundary explicitly.
    """

    __slots__ = ("_access",)

    @arg_digest()
    def __init__(self, card, related_cards=(), skip_digestion=False):
        self._access = CardAccess(card, related_cards)

    @property
    def access(self):
        return self._access

    @property
    def profile(self):
        return self.access.profile

    @property
    def mode(self):
        return "live"

    @property
    def context(self):
        return self.access.context

    @property
    def capabilities(self):
        return {
            "topics": list(self._topics),
            "inspect": True,
            "search": "literal_casefold",
            "scientific_questions": False,
            "scientific_topics": self.access.capabilities["scientific_topics"],
            "cross_card_navigation": False,
            "save": False,
        }

    @property
    def _topics(self):
        return {
            key: value
            for key, value in _TOPICS.items()
            if key != "structures" or self.profile == "protein"
        }

    def _location(self, *keys):
        return self.access._card_location(segments=[_key(key) for key in keys])

    def _inspect(self, location, origin=None, *, title="All retained content"):
        node, full = self.access._resolve(location)
        if full["kind"] == "card" and (
            full["card_ref"] != self.context["card_ref"]
            or full["snapshot_id"] != self.context["snapshot_id"]
        ):
            raise ArgumentError(
                "Human navigation is limited to the focal capture; use access.read() for supplied related captures."
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
        return self._inspect(self.access.root_location, title="Card overview")

    def topics(self):
        """Only delivered routes; no unavailable scientific panels are advertised."""
        result = self._metadata(
            {key: {"description": value[1]} for key, value in self._topics.items()},
            "Where would you like to explore?",
        )
        return replace(result, _route_catalog=True)

    def questions(self):
        """Honest empty catalog until nature-specific scientific adapters arrive."""
        return replace(
            self._metadata({}, "Scientific questions"),
            _status="unsupported",
            _reason="Scientific question adapters are not implemented. Use topics() or inspect().",
        )

    def _topic(self, topic, origin=None, options=None):
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
        }[topic]
        return self._inspect(location, origin, title=_TOPICS[topic][0])

    @arg_digest()
    def view(self, topic, skip_digestion=False, *, options=None):
        """Open a delivered topic by its catalog key."""
        return self._topic(topic, options=options)

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
