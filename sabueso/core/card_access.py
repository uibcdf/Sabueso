"""Bounded literal access to one detached Card context (#148).

Literal access and the first shared scientific adapter use the same capture.
Supported literal selections share portable saved reading; unknown content and seals remain literal.
"""

from __future__ import annotations

import hashlib
import os
import secrets
import tempfile
from copy import deepcopy
from dataclasses import dataclass, field, replace
from pathlib import Path

from sabueso._private.argdigest import arg_digest

from .card_capture import _capture_cards
from .errors import ArgumentError, StorageError
from .snapshot import canonical_json, digest

LOCATION_FORMAT = "card_access_location@1"
PAGE_FORMAT = "sabueso.card_access_page@1"


def _handle(prefix, value):
    return prefix + digest(canonical_json(value)).split(":", 1)[1]


def _size(value):
    return len(canonical_json(value).encode("utf-8"))


def _type(value):
    return {
        dict: "object",
        list: "array",
        str: "string",
        bool: "boolean",
        int: "integer",
        float: "number",
        type(None): "null",
    }[type(value)]


def _page_limits(limit, max_bytes):
    if type(limit) is not int or not 1 <= limit <= 256:
        raise ArgumentError("limit must be an integer from 1 to 256.")
    if type(max_bytes) is not int or not 1024 <= max_bytes <= 1048576:
        raise ArgumentError("max_bytes must be an integer from 1024 to 1048576.")


def _text_slice(text_slice):
    if text_slice is None:
        return None
    if (
        not isinstance(text_slice, dict)
        or set(text_slice) != {"start", "stop"}
        or any(type(text_slice[k]) is not int for k in text_slice)
        or not 0 <= text_slice["start"] <= text_slice["stop"]
    ):
        raise ArgumentError(
            "text_slice requires integer start/stop with 0 <= start <= stop."
        )
    return dict(text_slice)


@dataclass(frozen=True)
class _Entry:
    location: dict
    key: object
    value: object = field(repr=False)
    ordinal: int | None = None


@dataclass(frozen=True, repr=False)
class AccessSelection:
    """Fixed captured selection; pages never reread a mutable Card."""

    _access: object
    _result_ref: str
    _selection_ref: str
    _entries: tuple = field(repr=False)
    _context_location: dict = field(repr=False)
    _target: dict = field(repr=False)
    _operation: str = field(repr=False)
    _slice: dict | None = field(default=None, repr=False)
    _scientific: object = field(default=None, repr=False)
    _fields: tuple = field(default=(), repr=False)
    _outcome_override: object = field(default=None, repr=False)

    @property
    def result_ref(self):
        return self._result_ref

    @property
    def selection_ref(self):
        return self._selection_ref

    @property
    def count(self):
        return len(self._entries)

    @property
    def capabilities(self):
        return {
            "page": True,
            "save": self._can_save(),
            "scientific_adapter": self._scientific is not None,
        }

    def _can_save(self):
        from .card_exploration_storage import can_save_selection

        return can_save_selection(self)

    @arg_digest()
    def save(self, path, *, overwrite=False, skip_digestion=False):
        """Persist a supported machine selection through the shared exploration bundle."""
        from .card_exploration_storage import save_selection

        return save_selection(self, path, overwrite)

    @arg_digest()
    def page(self, *, limit=32, max_bytes=65536, cursor=None, skip_digestion=False):
        """A canonical-JSON envelope bounded by both item count and UTF-8 bytes."""
        _page_limits(limit, max_bytes)
        start = self._access._offset(self.selection_ref, cursor)
        items, end = [], start
        blocked = None
        for index in range(start, min(self.count, start + limit)):
            item = self._access._entry_frame(self, index)
            trial = self._frame([*items, item], start, index + 1, limit, max_bytes)
            if _size(trial) > max_bytes:
                item = self._access._defer(item)
                trial = self._frame([*items, item], start, index + 1, limit, max_bytes)
            if _size(trial) > max_bytes:
                if not items:
                    blocked = {"code": "item_too_large", "location": item["location"]}
                break
            items.append(item)
            end = index + 1
        frame = self._frame(items, start, end, limit, max_bytes, blocked)
        if _size(frame) > max_bytes:
            error = ArgumentError(
                "response_budget_too_small: mandatory envelope metadata exceeds max_bytes.",
                argument="max_bytes",
            )
            error.extra["reason"] = "response_budget_too_small"
            raise error
        return frame

    def _frame(self, items, start, end, limit, max_bytes, blocked=None):
        capture = self._access._focal
        complete = end == self.count
        result = self._scientific
        frame = {
            "format": PAGE_FORMAT,
            "selection_ref": self.selection_ref,
            "result_ref": self.result_ref,
            "context": {
                "card_ref": capture.pin,
                "snapshot_id": capture.snapshot,
                "mode": self._access.mode,
                "profile": self._access.profile,
                "adapter": "literal_access@1",
                "context_location": self._context_location,
            },
            "outcome": {"status": "ok" if self.count else "empty", "reason": None},
            "coverage": {
                "detail": "referenced",
                "inspection_required": True,
                "location": self._access._coverage_location,
            },
            "node": deepcopy(self._target),
            "items": items,
            "page": {
                "offset": start,
                "returned": len(items),
                "total": self.count,
                "complete": complete,
                "values_complete": all(item["value_included"] for item in items),
                "next_cursor": self._access._cursor(self.selection_ref, end)
                if not complete and end > start
                else None,
                "limit": limit,
                "max_bytes": max_bytes,
                "blocked": blocked,
            },
        }
        if self._outcome_override is not None:
            frame["outcome"] = deepcopy(self._outcome_override)
        if result is not None:
            frame["context"].update(adapter=result.wire["context"]["adapter"])
            frame["outcome"] = deepcopy(result.wire["outcome"])
            frame["coverage"]["location"] = self._access._location(
                result.location("coverage")
            )
        return frame

    def __repr__(self):
        return f"AccessSelection({self.selection_ref}, count={self.count}; use page())"


class CardAccess:
    """Read-only captured access, with session-owned selections and cursors.

    Construct through ``Card.access()``. Complete raw export is explicit; printing
    this object does not serialize its Card or enumerate scientific views.
    """

    __slots__ = (
        "_captures",
        "_focal_key",
        "_mode",
        "_metadata_refs",
        "_exploration_session",
        "_inputs",
        "_locations",
        "_objects",
        "_selections",
        "_cursors",
        "_tokens",
        "_nonce",
        "_coverage_location",
        "_scientific_cache",
        "_scientific_items",
    )

    @arg_digest()
    def __init__(self, card, related_cards=(), skip_digestion=False):
        self._captures, self._inputs = _capture_cards(card, related_cards)
        self._focal_key = self._inputs[0]
        self._mode = "live"
        self._metadata_refs = set()
        self._exploration_session = None
        self._locations, self._objects, self._selections = {}, {}, {}
        self._cursors, self._tokens = {}, {}
        self._nonce = secrets.token_hex(16)
        self._scientific_cache, self._scientific_items = {}, {}
        self._set_coverage_location()

    def _set_coverage_location(self):
        self._coverage_location = self._object_location(
            {
                "basis": "stored_literal",
                "classification": "not_evaluated",
                "quality_location": self._location(
                    self._card_location(segments=[{"type": "Key", "value": "quality"}])
                ),
                "reason": "Literal access does not classify source knowledge coverage.",
            }
        )

    def _for_capture(self, key):
        """Switch the focal capture without serializing or changing supplied inputs."""
        other = object.__new__(CardAccess)
        for name in self.__slots__:
            setattr(other, name, getattr(self, name))
        other._focal_key = key
        other._selections, other._cursors, other._tokens = {}, {}, {}
        other._scientific_items = {}
        if other.mode == "saved" and other._exploration_session is not None:
            for view in other._exploration_session["views"].values():
                selection = view._selection
                if selection._access._focal_key != key:
                    continue
                rebound = replace(selection, _access=other)
                other._selections.setdefault(rebound.selection_ref, rebound)
                if rebound._scientific is not None:
                    for entry in rebound._entries:
                        ref = _handle(
                            "XI_",
                            {
                                "result_ref": rebound.result_ref,
                                "location": entry.location,
                            },
                        )
                        other._scientific_items[ref] = (rebound._scientific, entry.key)
        other._set_coverage_location()
        return other

    @property
    def mode(self):
        return self._mode

    @property
    def _focal(self):
        return self._captures[self._focal_key]

    @property
    def profile(self):
        nature = self._focal.data["meta"].get("entity_type")
        return (
            nature if nature in ("protein", "small_molecule", "disease") else "generic"
        )

    @property
    def root_location(self):
        return self._location(self._card_location())

    @property
    def context(self):
        return {
            "card_ref": self._focal.pin,
            "snapshot_id": self._focal.snapshot,
            "inputs": list(self._inputs),
            "captures": sorted(self._captures),
            "profile": self.profile,
            "mode": self.mode,
            "adapter": "literal_access@1",
        }

    @property
    def capabilities(self):
        return {
            "catalog": ["topics", "fields", "selections"],
            "read": True,
            "export_card": True,
            "select": True,
            "explain": True,
            "save": False,
            "scientific_topics": ["structures"]
            if self.profile == "protein"
            and (
                self.mode == "live"
                or any(
                    selection._scientific is not None
                    for selection in self._selections.values()
                )
            )
            else [],
            **(
                {
                    "not_saved_topics": ["structures"]
                    if self.profile == "protein"
                    and not any(
                        selection._scientific is not None
                        for selection in self._selections.values()
                    )
                    else []
                }
                if self.mode == "saved"
                else {}
            ),
        }

    def _card_location(self, *, segments=None):
        return {
            "format": LOCATION_FORMAT,
            "kind": "card",
            "card_ref": self._focal.pin,
            "snapshot_id": self._focal.snapshot,
            "segments": segments or [],
        }

    def _location(self, full):
        key = _handle("XL_", {"session": self._nonce, "location": full})
        self._locations.setdefault(key, deepcopy(full))
        return {"format": LOCATION_FORMAT, "kind": "lookup", "location_ref": key}

    def _object_location(self, value):
        key = _handle("XR_", {"adapter": "literal_metadata@1", "value": value})
        self._objects.setdefault(key, deepcopy(value))
        self._metadata_refs.add(key)
        return self._location(
            {
                "format": LOCATION_FORMAT,
                "kind": "result",
                "result_ref": key,
                "segments": [],
            }
        )

    def _resolve(self, location):
        if not isinstance(location, dict) or location.get("format") != LOCATION_FORMAT:
            raise ArgumentError("location requires a card_access_location@1 mapping.")
        location = deepcopy(location)
        if location.get("kind") == "lookup":
            if set(location) != {"format", "kind", "location_ref"}:
                raise ArgumentError("A lookup location has unknown members.")
            try:
                location = self._locations[location["location_ref"]]
            except (KeyError, TypeError) as exc:
                raise ArgumentError(
                    "This location is not retained in this access session."
                ) from exc
        kind = location.get("kind")
        segments = location.get("segments")
        if not isinstance(segments, list):
            raise ArgumentError("A location requires typed segments.")
        if kind == "card":
            if set(location) != {
                "format",
                "kind",
                "card_ref",
                "snapshot_id",
                "segments",
            }:
                raise ArgumentError("A Card location has unknown or missing members.")
            key = location["card_ref"] or location["snapshot_id"]
            try:
                capture = self._captures[key]
            except (KeyError, TypeError) as exc:
                raise ArgumentError("That Card capture was not supplied.") from exc
            if (
                capture.pin != location["card_ref"]
                or capture.snapshot != location["snapshot_id"]
            ):
                raise ArgumentError(
                    "The location does not bind this captured snapshot."
                )
            node = capture.data
        elif kind == "result":
            if set(location) != {"format", "kind", "result_ref", "segments"}:
                raise ArgumentError("A result location has unknown or missing members.")
            try:
                node = self._objects[location["result_ref"]]
            except (KeyError, TypeError) as exc:
                raise ArgumentError(
                    "That literal metadata result is not retained."
                ) from exc
        else:
            raise ArgumentError("Unsupported literal location kind.")
        walked = []
        try:
            for segment in segments:
                if not isinstance(segment, dict) or set(segment) != {"type", "value"}:
                    raise ArgumentError(
                        "Each location segment requires type and value."
                    )
                value, tag = segment["value"], segment["type"]
                store = kind == "card" and walked in (
                    [{"type": "Key", "value": "source_assertion_store"}],
                    [{"type": "Key", "value": "relationship_store"}],
                )
                if tag == "Key" and isinstance(value, str) and isinstance(node, dict):
                    node = node[value]
                elif (
                    tag == "Index"
                    and type(value) is int
                    and value >= 0
                    and isinstance(node, list)
                    and not store
                ):
                    node = node[value]
                elif (
                    tag == "Record"
                    and isinstance(value, str)
                    and isinstance(node, list)
                    and store
                ):
                    matches = [entry for entry in node if entry["id"] == value]
                    if len(matches) != 1:
                        raise KeyError(value)
                    node = matches[0]
                else:
                    raise ArgumentError(
                        "The segment type does not match this literal node."
                    )
                walked.append(segment)
        except (KeyError, IndexError) as exc:
            raise ArgumentError(
                "This location does not exist in the captured payload."
            ) from exc
        return node, deepcopy(location)

    def _children(self, value, location):
        if isinstance(value, dict):
            return tuple(
                _Entry(
                    {
                        **location,
                        "segments": [
                            *location["segments"],
                            {"type": "Key", "value": k},
                        ],
                    },
                    k,
                    v,
                )
                for k, v in sorted(value.items())
            )
        if isinstance(value, list):
            store = location["kind"] == "card" and location["segments"] in (
                [{"type": "Key", "value": "source_assertion_store"}],
                [{"type": "Key", "value": "relationship_store"}],
            )
            entries = [
                _Entry(
                    {
                        **location,
                        "segments": [
                            *location["segments"],
                            {
                                "type": "Record" if store else "Index",
                                "value": v["id"] if store else i,
                            },
                        ],
                    },
                    v["id"] if store else i,
                    v,
                    i,
                )
                for i, v in enumerate(value)
            ]
            return tuple(sorted(entries, key=lambda e: e.key) if store else entries)
        return (_Entry(location, None, value),)

    def _make_selection(self, operation, location, value, text_slice=None):
        request = {
            "operation": operation,
            "location": location,
            "text_slice": text_slice,
        }
        result_ref = _handle(
            "XR_",
            {
                "format": "literal_access_result@1",
                "inputs": sorted(self._captures),
                "request": request,
            },
        )
        selection_ref = _handle(
            "XA_",
            {
                "format": "card_access_selection@1",
                "result_ref": result_ref,
                "request": request,
            },
        )
        if selection_ref not in self._selections:
            entries = (
                (_Entry(location, None, value),)
                if text_slice is not None
                else self._children(value, location)
            )
            context_location = self._object_location(
                {"context": self.context, "request": request}
            )
            self._selections[selection_ref] = AccessSelection(
                self,
                result_ref,
                selection_ref,
                entries,
                context_location,
                {
                    "node_type": _type(value),
                    "size": len(value)
                    if isinstance(value, (dict, list, str))
                    else None,
                    "location": self._location(location),
                    "owner": {
                        key: location[key]
                        for key in ("card_ref", "snapshot_id", "result_ref")
                        if key in location
                    },
                },
                operation,
                text_slice,
            )
        return self._selections[selection_ref]

    @arg_digest()
    def catalog(self, kind="topics", locator=None, skip_digestion=False):
        """Discover only implemented capabilities or immediate literal children."""
        if kind not in ("topics", "fields", "selections"):
            raise ArgumentError("kind must be topics, fields or selections.")
        if locator is not None and kind != "fields":
            raise ArgumentError("locator is valid only for the fields catalog.")
        if kind == "fields":
            node, location = self._resolve(
                self.root_location if locator is None else locator
            )
            return self._make_selection("fields", location, node)
        if kind == "topics":
            data = {
                "content": {
                    "key": "content",
                    "scientific_adapter": False,
                    "operations": ["read", "export_card"],
                    "description": "Complete stored Card content; scientific topics have separate descriptors.",
                }
            }
            if self.profile == "protein":
                from .card_scientific_access import descriptor

                data["structures"] = descriptor()
                if self.mode == "saved":
                    from .card_exploration_adapter_v1 import _descriptor

                    data["structures"] = _descriptor()
                    data["structures"]["availability"] = (
                        "retained"
                        if any(
                            selection._scientific is not None
                            for selection in self._selections.values()
                        )
                        else "not_saved"
                    )
                # Selection is an access-layer policy over the unchanged native
                # adapter schema; never rewrite a retained scientific wire result.
                data["structures"].update(
                    machine_filter=True,
                    machine_order=True,
                    machine_membership=True,
                    selection_policy="structure_access_selection@1",
                    selection_availability="retained_requests_only"
                    if self.mode == "saved"
                    else "live",
                )
        else:
            # Freeze before creating this catalog's own selection.
            data = {
                key: {
                    "selection_ref": s.selection_ref,
                    "result_ref": s.result_ref,
                    "count": s.count,
                }
                for key, s in sorted(self._selections.items())
                if s._operation != "catalog:selections"
            }
        location = self._object_location(data)
        node, full = self._resolve(location)
        return self._make_selection(f"catalog:{kind}", full, node)

    @arg_digest()
    def read(self, location, *, text_slice=None, skip_digestion=False):
        """Select immediate literal children, a scalar, or an exact Unicode text range."""
        node, full = self._resolve(location)
        text_slice = _text_slice(text_slice)
        if text_slice is not None:
            if not isinstance(node, str) or text_slice["stop"] > len(node):
                raise ArgumentError(
                    "text_slice requires a string and bounds within its length."
                )
        return self._make_selection("read", full, node, text_slice)

    @arg_digest()
    def select(
        self,
        topic,
        *,
        fields=None,
        where=None,
        item_refs=None,
        order_by=None,
        options=None,
        skip_digestion=False,
    ):
        """Select shared structures with typed equality, exact members and order.

        Display selection preserves the full underlying result and source scope.
        Saved mode looks up exact retained requests; it never executes a reader.
        """
        from .card_scientific_access import (
            materialize,
            options_for_structures,
            projection,
        )
        from .card_structure_selection_v1 import (
            active,
            evaluate,
            normalize,
            selection_ref,
        )

        if not isinstance(topic, str) or topic != "structures":
            raise ArgumentError(
                "Scientific selection currently supports structures only."
            )
        if self.mode == "saved":
            from .card_exploration_science import _saved_selection

            return _saved_selection(
                self, topic, fields, options, where, item_refs, order_by
            )
        options, fields = options_for_structures(options), projection(fields)
        query = normalize(where, item_refs, order_by)
        key = canonical_json(
            {"focal": self._focal_key, "topic": topic, "options": options}
        )
        if key not in self._scientific_cache:
            self._scientific_cache[key] = materialize(self, options)
        result = self._scientific_cache[key]
        entries, spec = (
            evaluate(result, query) if active(query) else (result.entries, None)
        )
        ref = (
            selection_ref(result, fields, spec)
            if spec is not None
            else _handle(
                "XA_",
                {
                    "format": "scientific_access_selection@1",
                    "result_ref": result.result_ref,
                    "fields": fields,
                },
            )
        )
        if ref not in self._selections:
            request = {"topic": topic, "fields": list(fields), "options": options}
            if spec is not None:
                request["selection"] = spec
            context = self._object_location(
                {"context": result.wire["context"], "request": request}
            )
            self._selections[ref] = AccessSelection(
                self,
                result.result_ref,
                ref,
                entries,
                context,
                {
                    "node_type": "scientific_result",
                    "location": self._location(result.location("native_payload")),
                    "size": len(result.entries),
                },
                "select:structures",
                _scientific=result,
                _fields=fields,
            )
            for entry in result.entries:
                item_ref = _handle(
                    "XI_", {"result_ref": result.result_ref, "location": entry.location}
                )
                self._scientific_items[item_ref] = (result, entry.key)
        return self._selections[ref]

    @arg_digest()
    def explain(self, item_ref, skip_digestion=False):
        """Read the original materialized explanation; never rerun a scientific reader."""
        try:
            result, key = self._scientific_items[item_ref]
        except (KeyError, TypeError) as exc:
            raise ArgumentError(
                "This scientific item is not retained in this access session."
            ) from exc
        return self.read(result.location("explanations", key))

    @arg_digest()
    def selection(self, selection_ref, skip_digestion=False):
        """Return an existing selection without reconstructing or recomputing it."""
        try:
            return self._selections[selection_ref]
        except (KeyError, TypeError) as exc:
            raise ArgumentError(
                "That selection is not retained in this access session."
            ) from exc

    def _cursor(self, selection_ref, offset):
        key = (selection_ref, offset)
        if key not in self._tokens:
            token = secrets.token_urlsafe(24)
            self._tokens[key] = token
            self._cursors[token] = key
        return self._tokens[key]

    def _offset(self, selection_ref, cursor):
        if cursor is None:
            return 0
        try:
            owner, offset = self._cursors[cursor]
        except (KeyError, TypeError) as exc:
            raise ArgumentError(
                "The cursor is malformed, foreign or no longer retained."
            ) from exc
        if owner != selection_ref:
            raise ArgumentError("The cursor belongs to another selection.")
        return offset

    def _quantity_context(self, location):
        from .quantities import NEGOTIATED_UNITS, is_quantity_node, to_quantity

        if location["kind"] != "card" or not location["segments"]:
            return None
        segments = location["segments"]
        parent_location = {**location, "segments": segments[:-1]}
        parent, _ = self._resolve(parent_location)
        if not is_quantity_node(parent):
            return None
        keys = [s["value"] for s in segments[:-1] if s["type"] == "Key"]
        template = None
        if keys and keys[0] == "sections":
            template = ".".join(keys[1:])
        elif len(segments) >= 4 and keys[:2] == ["relationship_store", "qualifiers"]:
            rel, _ = self._resolve({**location, "segments": segments[:2]})
            template = ".".join(["relationships", rel["predicate"], *keys[2:]])
        if template not in NEGOTIATED_UNITS:
            return None
        from pyunitwizard import QuantityRecord

        return {
            "field": template,
            "record": QuantityRecord.from_quantity(
                to_quantity(parent), field=template, unit=parent["unit"]
            ).to_dict(),
            "original_location": self._location(parent_location),
        }

    def _entry_frame(self, selection, index):
        entry = selection._entries[index]
        if selection._scientific is not None:
            return selection._scientific.frame(self, selection, entry)
        node = entry.value
        location = self._location(entry.location)
        scalar = not isinstance(node, (dict, list))
        value = node if scalar else None
        frame = {
            "item_ref": _handle(
                "XI_", {"result_ref": selection.result_ref, "location": entry.location}
            ),
            "kind": "literal",
            "node_type": _type(node),
            "key": entry.key,
            "ordinal": entry.ordinal,
            "location": location,
            "size": len(node) if isinstance(node, (str, list, dict)) else None,
            "state": "present",
            "support_basis": "stored_literal",
            "value_included": scalar,
            "value": value,
        }
        if not scalar:
            frame["value_location"] = location
        if selection._slice is not None:
            start, stop = selection._slice["start"], selection._slice["stop"]
            frame["value"] = node[start:stop]
            frame["text_range"] = {
                "start": start,
                "stop": stop,
                "total": len(node),
                "partial": start != 0 or stop != len(node),
            }
        quantity = self._quantity_context(entry.location)
        if quantity is not None:
            frame["quantity_context"] = quantity
        return frame

    def _defer(self, item):
        if item.get("kind") == "structure":
            return {
                key: deepcopy(item[key])
                for key in (
                    "item_ref",
                    "kind",
                    "location",
                    "payload_location",
                    "state",
                    "support_location",
                    "interpretation_location",
                )
            } | {
                "value_included": False,
                "value_location": item["location"],
                "reason": "value_and_interpretation_exceed_response_budget",
            }
        frame = deepcopy(item)
        frame.pop("value", None)
        frame["value_included"] = False
        frame["value_location"] = frame["location"]
        frame["reason"] = "value_exceeds_response_budget"
        if "quantity_context" in frame:
            frame["interpretation_location"] = frame.pop("quantity_context")[
                "original_location"
            ]
        if _size(frame.get("key")) > 128:
            frame["key_location"] = self._object_location(frame.pop("key"))
        return frame

    @arg_digest()
    def export_card(self, path, *, overwrite=False, skip_digestion=False):
        """Atomically export the exact captured focal Card, including its existing seal."""
        if not isinstance(overwrite, bool):
            raise ArgumentError("overwrite must be True or False.")
        if not isinstance(path, (str, os.PathLike)) or not str(path):
            raise ArgumentError("path must be a nonempty file path.")
        destination = Path(path)
        payload = canonical_json(self._focal.data).encode("utf-8")
        temporary = None
        try:
            fd, temporary = tempfile.mkstemp(
                dir=destination.parent, prefix=".sabueso-access-"
            )
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            if overwrite:
                os.replace(temporary, destination)
            else:
                # Atomic no-clobber publication; no exists-then-replace race.
                os.link(temporary, destination)
        except OSError as exc:
            raise StorageError(
                f"Cannot export captured Card to {destination}: {exc}"
            ) from exc
        finally:
            if temporary is not None:
                Path(temporary).unlink(missing_ok=True)
        return {
            "path": str(destination),
            "snapshot_id": self._focal.snapshot,
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    def __repr__(self):
        if not hasattr(self, "_captures"):
            return "CardAccess(uninitialized)"
        return f"CardAccess(profile={self.profile!r}, captures={len(self._captures)}; use catalog())"
