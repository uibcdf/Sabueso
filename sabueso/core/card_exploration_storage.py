"""Portable exploration with verified captures and inert historical reading."""

from __future__ import annotations

import json
import os
import secrets
import tempfile
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

from sabueso._private.argdigest import arg_digest

from .card_access import AccessSelection, CardAccess, _Entry, _handle
from .card_capture import _Capture
from .card_exploration import CardExplorer, CardItem, CardView, Cell
from .errors import ArgumentError, StorageError
from .snapshot import SNAPSHOT_ID, canonical_json, digest, parse_ref, snapshot_id

FORMAT = "sabueso.card_exploration@1"
VERIFIER = "literal_exploration_binding@1"
_FLAGS = (
    "title",
    "_route_catalog",
    "_question_catalog",
    "_field_panel",
    "_record_panel",
    "_link_panel",
    "_context_override",
    "_context_only",
    "_request",
    "_status",
    "_reason",
    "presentation",
    "_focus",
    "_display_request",
    "_machine_ref",
)


def _require(condition, message):
    if not condition:
        raise StorageError(message)


def operation_key(item):
    return canonical_json([item._view._explorer.access._focal_key, item.item_ref])


def admitted_selection(selection):
    if selection._scientific is not None:
        return (
            selection._scientific.wire.get("context", {}).get("adapter")
            == "structure_exploration@1"
        )
    try:
        node, location = selection._access._resolve(selection._target["location"])
        if location["kind"] == "result":
            if location["result_ref"] not in selection._access._metadata_refs:
                return (
                    selection._access._objects[location["result_ref"]]
                    .get("context", {})
                    .get("adapter")
                    == "structure_exploration@1"
                )
            node = selection._access._objects[location["result_ref"]]
            if isinstance(node, dict):
                if node.get("question") == "region_coverage":
                    return True
                rule = node.get("rule")
                rule = rule.get("rule", "") if isinstance(rule, dict) else rule
                if node.get(
                    "adapter"
                ) == "knowledge_coverage_exploration@1" or rule in (
                    "knowledge_state@5",
                    "knowledge_state_explanation@2",
                    "structure_inventory_explanation@1",
                ):
                    return True
                if isinstance(rule, str) and rule.startswith(
                    (
                        "knowledge_state@",
                        "knowledge_state_explanation@",
                        "structure_inventory_explanation@",
                    )
                ):
                    return False
    except (ArgumentError, KeyError):
        return False
    return True


def can_save_selection(selection):
    if not admitted_selection(selection):
        return False
    if selection._access.mode == "saved":
        session = selection._access._exploration_session
        if session is None:
            return False
        for entry in selection._entries:
            ref = _handle(
                "XI_", {"result_ref": selection.result_ref, "location": entry.location}
            )
            key = canonical_json([selection._access._focal_key, ref])
            if any(key not in session[kind] for kind in ("explanations", "links")):
                return False
    return True


def admitted_view(view):
    seen = set()
    while view is not None and id(view) not in seen:
        seen.add(id(view))
        if not admitted_selection(view._selection):
            return False
        view = view._origin
    return True


def required_views(root):
    pending, seen = [root], set()
    while pending:
        view = pending.pop()
        if view is None or id(view) in seen:
            continue
        seen.add(id(view))
        yield view
        pending.extend([view._origin, view._explorer._origin])


def can_save(view):
    if not admitted_view(view):
        return False
    if view._explorer.mode == "saved":
        for retained in required_views(view):
            for entry in retained._selection._entries:
                key = operation_key(CardItem(retained, entry))
                if any(
                    key not in view._explorer._session[kind]
                    for kind in ("explanations", "links")
                ):
                    return False
    return True


def _cell_record(item, column, cell):
    value = cell.value
    location = item.payload_location
    context = (
        item._view._explorer.access._quantity_context(
            {
                **location,
                "segments": [*location["segments"], {"type": "Key", "value": "value"}],
            }
        )
        if isinstance(item._entry.value, dict)
        and "unit" in item._entry.value
        and "value" in item._entry.value
        else None
    )
    if (
        column == "resolution"
        and item._view._selection._scientific is not None
        and value is not None
    ):
        context = {
            "field": "relationships.has_structure.resolution",
            "record": {"manifest": {"unit": "angstrom"}},
        }
    if (
        (column == "value" or column == "resolution")
        and context is not None
        and value is not None
    ):
        # Only an existing declared literal codec can establish a quantity binding.
        import pyunitwizard as puw
        from pyunitwizard import QuantityRecord

        try:
            puw.get_unit(value)
        except (TypeError, ValueError, AttributeError):
            context = None
        if context is not None:
            record = QuantityRecord.from_quantity(
                value,
                field=context["field"],
                unit=context["record"]["manifest"]["unit"],
            ).to_dict()
            return {
                **cell.to_dict(),
                "value": record,
                "encoding": "quantity_record",
                "field": context["field"],
                "unit": context["record"]["manifest"]["unit"],
            }
    return {**cell.to_dict(), "value": value, "encoding": "json"}


def _cell(record):
    value = deepcopy(record["value"])
    if record["encoding"] == "quantity_record":
        from pyunitwizard import QuantityRecord

        value = QuantityRecord.from_dict(value).to_quantity(
            field=record["field"], unit=record["unit"]
        )
    else:
        _require(record["encoding"] == "json", "Unknown saved cell encoding.")
    return Cell(value, record["state"], record["reason"], tuple(record["support"]))


class _SavedItem(CardItem):
    @property
    def _record(self):
        return self._view._saved_state["items"][self.item_ref]

    @property
    def label(self):
        return self._record["label"]

    @property
    def kind(self):
        return self._record["kind"]

    @property
    def support(self):
        return deepcopy(self._record["support"])

    @property
    def cells(self):
        return MappingProxyType(
            {key: _cell(value) for key, value in self._record["cells"].items()}
        )


def _freeze_view(view, ids):
    from .card_exploration_science import _encode, _encoding

    items = {}
    for entry in view._selection._entries:
        item = view._item(entry)
        items[item.item_ref] = {
            "label": item.label,
            "kind": item.kind,
            "support": item.support,
            "cells": {
                key: _cell_record(item, key, cell) for key, cell in item.cells.items()
            },
        }
    selection = view._selection
    flags = {name: deepcopy(getattr(view, name)) for name in _FLAGS}
    if (
        selection._scientific is not None
        and view._display_request
        and view._display_request.get("column") == "resolution"
        and view._display_request.get("operation") == "filter"
    ):
        from pyunitwizard import QuantityRecord

        flags["_display_request"]["equals"] = QuantityRecord.from_quantity(
            view._display_request["equals"],
            field="relationships.has_structure.resolution",
            unit="angstrom",
        ).to_dict()
        flags["_display_request"]["equals_encoding"] = "quantity_record"
    record = {
        "view_ref": view.view_ref,
        "focal": view._explorer.access._focal_key,
        "origin": ids.get(id(view._origin)),
        "explorer_origin": ids.get(id(view._explorer._origin)),
        "flags": flags,
        "selection": {
            "result_ref": selection.result_ref,
            "selection_ref": selection.selection_ref,
            "entries": [
                {
                    "location": entry.location,
                    "key": entry.key,
                    "value": entry.value,
                    "ordinal": entry.ordinal,
                }
                for entry in selection._entries
            ],
            "context_location": selection._context_location,
            "target": selection._target,
            "operation": selection._operation,
            "slice": selection._slice,
            "fields": list(selection._fields),
            "outcome_override": selection._outcome_override,
        },
        "selected": [CardItem(view, entry).item_ref for entry in view._selected],
        "state": {
            "items": items,
            "context": view.context,
            "schema": view.schema,
            "coverage": view.coverage,
        },
        "native_payload": _encode(view.native_payload, _encoding(view)),
    }
    if view._selection._scientific is not None:
        record["selection"]["scientific_result_ref"] = (
            view._selection._scientific.result_ref
        )
    if _encoding(view) != "json":
        record["native_encoding"] = _encoding(view)
    return record


def _objects_for(access, records):
    """Retain the referenced metadata closure, never unrelated scientific results."""
    objects, lookups = {}, {}

    def walk(value):
        if isinstance(value, dict):
            if value.get("format") == "card_access_location@1":
                if value.get("kind") == "lookup":
                    key = value.get("location_ref")
                    if key in access._locations and key not in lookups:
                        lookups[key] = access._locations[key]
                        walk(lookups[key])
                elif value.get("kind") == "result":
                    key = value.get("result_ref")
                    if key in access._objects and key not in objects:
                        obj = access._objects[key]
                        _require(
                            key
                            == _handle(
                                "XR_", {"adapter": "literal_metadata@1", "value": obj}
                            )
                            or (
                                isinstance(obj, dict)
                                and obj.get("context", {}).get("adapter")
                                == "structure_exploration@1"
                            ),
                            "This view needs a scientific result whose historical verifier is not yet supported.",
                        )
                        objects[key] = obj
                        walk(obj)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(records)
    return deepcopy(objects), deepcopy(lookups)


def _prepare(root):
    _require(
        admitted_view(root),
        "Saving derived structures/coverage or their originating trail requires a historical verifier not yet implemented. Save a supported literal/field view or inspect capabilities.",
    )
    _require(
        can_save(root),
        "Required saved explanation/link closure was not retained. Return to a retained view or explicitly start a new local exploration.",
    )
    session = root._explorer._session
    primary = [view for view in list(session["views"].values()) if admitted_view(view)]
    # Explicit saving prepares only support/navigation for already materialized
    # literal results. No unvisited scientific topic or recursive support tree runs.
    if root._explorer.mode == "live":
        seen = set()
        for view in primary:
            for entry in view._selection._entries:
                item = CardItem(view, entry)
                key = operation_key(item)
                if key in seen:
                    continue
                seen.add(key)
                if key not in session["explanations"]:
                    item.explain()
                if key not in session["links"]:
                    item.related()
    eligible = [view for view in list(session["views"].values()) if admitted_view(view)]
    # Include every actual originating step, preserving different histories for
    # equal semantic view handles. Identity is never an integer display position.
    ids = {id(view): f"N{i}" for i, view in enumerate(eligible)}
    _require(
        id(root) in ids, "The root view is not registered in its captured context."
    )
    records = {ids[id(view)]: _freeze_view(view, ids) for view in eligible}
    access = root._explorer.access
    objects, locations = _objects_for(access, list(records.values()))
    bundle = {
        "format": FORMAT,
        "producer": {
            "sabueso_version": __import__("sabueso").__version__,
            "verifier": VERIFIER,
            "scope": "literal fields, retained relationships and recorded context links; derived scientific persistence not supported",
        },
        "root_view_ref": root.view_ref,
        "root_navigation_ref": ids[id(root)],
        "cards": {
            key: {
                "data": capture.data,
                "snapshot_id": capture.snapshot,
                "card_ref": capture.pin,
            }
            for key, capture in access._captures.items()
        },
        "inputs": list(access._inputs),
        "objects": objects,
        "locations": locations,
        "views": records,
        "navigation": {
            kind: {
                key: ids[id(view)]
                for key, view in session[kind].items()
                if id(view) in ids
            }
            for kind in ("explanations", "links")
        },
        "capabilities": {
            "root_machine_selection_ref": root._machine_ref,
            "scientific_saved_adapters": [],
            "source_coverage": "not_evaluated_by_saved_reading",
        },
        "presentation_metadata": deepcopy(session.get("presentation_metadata", {})),
    }
    from .card_exploration_science import ADAPTERS, _scientific_metadata
    from .card_exploration_science import FORMAT as SCIENCE_FORMAT
    from .card_exploration_science import VERIFIER as SCIENCE_VERIFIER

    scientific = (
        any(
            view._selection._scientific is not None or view._record_panel == "coverage"
            for view in eligible
        )
        or any(_scientific_metadata(value) for value in objects.values())
        or any(ref not in access._metadata_refs for ref in objects)
    )
    if scientific:
        bundle["format"] = SCIENCE_FORMAT
        bundle["producer"].update(
            verifier=SCIENCE_VERIFIER,
            scope="original literal and scientific exploration; frozen historical decision consistency, no live scientific readers",
        )
        bundle["scientific_results"] = {}
        for view in eligible:
            for ref, obj in view._explorer.access._objects.items():
                if (
                    ref in objects
                    and ref not in view._explorer.access._metadata_refs
                    and isinstance(obj, dict)
                    and obj.get("context", {}).get("adapter") == ADAPTERS[0]
                ):
                    context = obj["context"]
                    focal = next(
                        key
                        for key, capture in access._captures.items()
                        if capture.pin == context["card_ref"]
                        and capture.snapshot == context["snapshot_id"]
                    )
                    bundle["scientific_results"][ref] = {"focal": focal}
        bundle["capabilities"]["scientific_saved_adapters"] = list(ADAPTERS)
    return bundle


def _seal(bundle):
    bundle.pop("digests", None)
    bundle.pop("bundle_digest", None)
    bundle["digests"] = {
        key: digest(canonical_json(value)) for key, value in bundle.items()
    }
    bundle["bundle_digest"] = digest(canonical_json(bundle))
    return bundle


def save_exploration(view, path, *, overwrite=False):
    if (
        not isinstance(path, (str, os.PathLike))
        or not str(path)
        or type(overwrite) is not bool
    ):
        raise ArgumentError("save requires a nonempty file path and boolean overwrite.")
    bundle = _seal(_prepare(view))
    _restore(bundle, bundle["bundle_digest"])
    destination, temporary = Path(path), None
    try:
        fd, temporary = tempfile.mkstemp(
            dir=destination.parent, prefix=".sabueso-exploration-"
        )
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(canonical_json(bundle))
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            os.replace(temporary, destination)
        else:
            os.link(temporary, destination)
    except OSError as exc:
        raise StorageError(f"Cannot save exploration to {destination}: {exc}") from exc
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
    return {
        "path": str(destination),
        "bundle_digest": bundle["bundle_digest"],
        "root_view_ref": view.view_ref,
    }


def _unique(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "Duplicate JSON member in exploration bundle.")
        result[key] = value
    return result


@arg_digest()
def read_exploration(path, expected_digest=None, skip_digestion=False):
    """Validate and reopen supported saved views without scientific computation."""
    if not isinstance(path, (str, os.PathLike)) or not str(path):
        raise ArgumentError("path requires a nonempty file path.")
    if expected_digest is not None and (
        not isinstance(expected_digest, str)
        or not SNAPSHOT_ID.fullmatch(expected_digest)
    ):
        raise ArgumentError("expected_digest requires sha256:<64 hex> or None.")
    try:
        with Path(path).open(encoding="utf-8") as stream:
            bundle = json.load(stream, object_pairs_hook=_unique)
        return _restore(bundle, expected_digest)
    except StorageError:
        raise
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        RecursionError,
    ) as exc:
        raise StorageError(f"Cannot read saved exploration: {exc}") from exc


def _access(captures, inputs, objects, locations, focal):
    access = object.__new__(CardAccess)
    access._captures, access._inputs, access._focal_key = captures, tuple(inputs), focal
    access._objects, access._locations = objects, locations
    access._metadata_refs = set(objects)
    access._exploration_session = None
    access._selections, access._cursors, access._tokens = {}, {}, {}
    access._nonce, access._mode = secrets.token_hex(16), "saved"
    access._scientific_cache, access._scientific_items = {}, {}
    access._set_coverage_location()
    return access


def _explorer(access, session):
    explorer = object.__new__(CardExplorer)
    explorer._access, explorer._session = access, session
    access._exploration_session = session
    explorer._coverage_result, explorer._origin, explorer._navigation_cache = (
        None,
        None,
        {},
    )
    return explorer


def _restore(bundle, expected_digest):
    try:
        return _restore_checked(bundle, expected_digest)
    except StorageError:
        raise
    except Exception as exc:
        raise StorageError(f"Saved exploration validation failed: {exc}") from exc


def _restore_checked(bundle, expected_digest):
    from .card_exploration_verification import verify_bundle, verify_views

    verify_bundle(bundle, expected_digest)
    from .card import CARD_SCHEMA_VERSION
    from .quantities import verify
    from .schema_version import check_card_schema

    captures = {}
    for key, record in bundle["cards"].items():
        data = record["data"]
        check_card_schema(data.get("meta"), CARD_SCHEMA_VERSION)
        verify(data, data.get("quantities"))
        snapshot = snapshot_id(data)
        card_id = data["meta"].get("card_id")
        if card_id:
            parsed = parse_ref(card_id)
            _require(
                not parsed.snapshot_id and not parsed.item_id,
                "Saved Card identity is already pinned.",
            )
        pin = f"{card_id}@{snapshot}" if card_id else None
        _require(
            record["snapshot_id"] == snapshot
            and record["card_ref"] == pin
            and key == (pin or snapshot),
            "Saved Card snapshot binding differs.",
        )
        for store in ("source_assertion_store", "relationship_store"):
            ids = [row["id"] for row in data[store]]
            _require(
                all(isinstance(ref, str) and ref for ref in ids)
                and len(ids) == len(set(ids)),
                "Saved store has invalid/duplicate identities.",
            )
        captures[key] = _Capture(deepcopy(data), snapshot, pin)
    _require(
        bool(bundle["inputs"]) and all(key in captures for key in bundle["inputs"]),
        "Saved inputs do not bind captured Cards.",
    )
    session = {
        "views": {},
        "explanations": {},
        "links": {},
        "presentation_metadata": deepcopy(bundle["presentation_metadata"]),
    }
    from .card_exploration_science import (
        _bind_coverage,
        _decode,
        _restore_result,
        _verify_objects,
    )

    accesses = {
        key: _access(
            captures,
            bundle["inputs"],
            deepcopy(bundle["objects"]),
            deepcopy(bundle["locations"]),
            key,
        )
        for key in captures
    }
    nodes, scientific_results = {}, {}
    for ref, record in bundle.get("scientific_results", {}).items():
        _require(
            record["focal"] in accesses and ref in bundle["objects"],
            "Missing scientific capture/result.",
        )
        scientific_results[ref] = _restore_result(
            ref, accesses[record["focal"]]._objects[ref]
        )
    for access in accesses.values():
        access._metadata_refs -= set(scientific_results)
    if "scientific_results" in bundle:
        _verify_objects(bundle, accesses)

    def node(key, visiting=None):
        if key in nodes:
            return nodes[key]
        visiting = set() if visiting is None else visiting
        _require(
            key in bundle["views"] and key not in visiting,
            "Saved navigation is missing or cyclic.",
        )
        visiting.add(key)
        record = bundle["views"][key]
        flags = deepcopy(record["flags"])
        _require(
            set(flags) == set(_FLAGS), "Missing or unknown saved presentation member."
        )
        _require(
            all(
                type(flags[name]) is bool
                for name in (
                    "_route_catalog",
                    "_question_catalog",
                    "_link_panel",
                    "_context_only",
                )
            ),
            "Saved presentation flags require booleans.",
        )
        _require(
            isinstance(flags["title"], str)
            and flags["presentation"] in ("summary", "table", "detail")
            and (flags["_focus"] is None or isinstance(flags["_focus"], str)),
            "Unsupported saved presentation shape.",
        )
        focal = record["focal"]
        _require(focal in captures, "Saved focal capture is missing.")
        if focal not in accesses:
            accesses[focal] = _access(
                captures,
                bundle["inputs"],
                deepcopy(bundle["objects"]),
                deepcopy(bundle["locations"]),
                focal,
            )
        explorer = _explorer(accesses[focal], session)
        explorer._origin = (
            node(record["explorer_origin"], visiting)
            if record["explorer_origin"] is not None
            else None
        )
        spec = record["selection"]
        scientific_ref = spec.get("scientific_result_ref")
        _require(
            scientific_ref is None
            or (
                scientific_ref in scientific_results
                and bundle["scientific_results"][scientific_ref]["focal"] == focal
            ),
            "Foreign scientific result capture.",
        )
        _require(
            flags["_focus"] is None or scientific_ref is not None,
            "Literal views cannot have a scientific detail focus.",
        )
        operation = flags["_display_request"]
        if isinstance(operation, dict) and "equals_encoding" in operation:
            _require(
                scientific_ref is not None
                and operation["operation"] == "filter"
                and operation["column"] == "resolution"
                and operation.pop("equals_encoding") == "quantity_record",
                "Unknown saved display quantity encoding.",
            )
            from pyunitwizard import QuantityRecord

            operation["equals"] = QuantityRecord.from_dict(
                operation["equals"]
            ).to_quantity(
                field="relationships.has_structure.resolution", unit="angstrom"
            )
        selection = AccessSelection(
            explorer.access,
            spec["result_ref"],
            spec["selection_ref"],
            tuple(_Entry(**entry) for entry in spec["entries"]),
            spec["context_location"],
            spec["target"],
            spec["operation"],
            spec["slice"],
            _fields=tuple(spec["fields"]),
            _outcome_override=spec["outcome_override"],
            _scientific=scientific_results.get(scientific_ref),
        )
        explorer.access._selections.setdefault(selection.selection_ref, selection)
        entries = {
            _handle(
                "XI_", {"result_ref": selection.result_ref, "location": entry.location}
            ): entry
            for entry in selection._entries
        }
        _require(
            len(entries) == len(selection._entries)
            and len(record["selected"]) == len(set(record["selected"])),
            "Duplicate saved item membership.",
        )
        _require(
            all(ref in entries for ref in record["selected"]),
            "Foreign saved item membership.",
        )
        origin = (
            node(record["origin"], visiting) if record["origin"] is not None else None
        )
        view = CardView(
            explorer,
            selection,
            tuple(entries[ref] for ref in record["selected"]),
            _origin=origin,
            _native_override=None
            if scientific_ref is not None
            else _decode(
                record["native_payload"], record.get("native_encoding", "json")
            ),
            _saved_state={
                **deepcopy(record["state"]),
                "_native_encoding": record.get("native_encoding", "json"),
            },
            **flags,
        )
        _bind_coverage(view, record["native_payload"])
        if selection._scientific is not None:
            for entry in selection._entries:
                explorer.access._scientific_items[CardItem(view, entry).item_ref] = (
                    selection._scientific,
                    entry.key,
                )
        _require(
            view.view_ref == record["view_ref"], "Saved presentation identity differs."
        )
        nodes[key] = view
        visiting.remove(key)
        return view

    for key in bundle["views"]:
        node(key)
    for kind in ("explanations", "links"):
        for key, ref in bundle["navigation"][kind].items():
            _require(
                ref in nodes, "Required saved support/navigation member is missing."
            )
            session[kind][key] = nodes[ref]
    retained_views = dict(session["views"])
    verify_views(bundle, nodes)
    session["views"] = retained_views
    session["validation"] = {
        "verifier": VERIFIER,
        "integrity": "verified",
        "independent_expected_digest": expected_digest is not None,
        "bindings": "captured snapshots, literal values/units/support, request and display membership",
        "recorded_navigation_decisions": "retained_context_links@1 verified against captured source basis",
        "scientific_classifications": "not_supported_by_this_saved_slice",
        "presentation_wording": "recorded",
        "source_authenticity_and_truth": "not_established_by_hashes",
    }
    if "scientific_results" in bundle:
        from .card_exploration_science import _verification_report

        session["validation"].update(_verification_report(bundle))
    root = nodes[bundle["root_navigation_ref"]]
    _require(
        root.view_ref == bundle["root_view_ref"], "Saved root view binding differs."
    )
    return root


def saved_item_operation(item, kind):
    explorer = item._view._explorer
    view = explorer._session[kind].get(operation_key(item))
    if view is None:
        return not_saved(explorer, f"This item's {kind} were not retained.", item._view)
    return replace(
        view,
        _explorer=explorer,
        _origin=item.open() if kind == "links" else item._view,
        _display_request=None,
    )


def not_saved(explorer, reason, origin=None):
    view = explorer._metadata(
        {"outcome": "not_saved", "reason": reason},
        "Not saved in this exploration",
        origin,
    )
    return replace(
        view,
        _selected=(),
        _selection=replace(view._selection, _entries=()),
        _status="not_saved",
        _reason=reason,
    )


def saved_topic(explorer, topic, origin, options):
    if not isinstance(topic, str) or (
        options is not None and not isinstance(options, dict)
    ):
        raise ArgumentError("Use a declared topic key and options mapping or None.")
    if topic in ("content", "sources", "quality") or (
        topic == "coverage" and not explorer._nature_topics
    ):
        return explorer._live_topic(topic, origin, options)
    if topic not in (
        *explorer._topics,
        "structures",
        "function",
        "chemistry",
        "properties",
        "definition",
        "classification",
        "identity",
    ):
        raise ArgumentError("Unknown saved topic.")
    if topic == "structures":
        from .card_exploration_science import _options

        options = _options(options)
    elif options not in (None, {}):
        raise ArgumentError("This topic has no scientific options.")
    for view in list(explorer._session["views"].values()):
        if (
            view._saved_state is not None
            and view._explorer.access._focal_key == explorer.access._focal_key
            and (
                view._field_panel == topic
                or (
                    topic in ("classification", "coverage")
                    and view._record_panel == topic
                )
                or (
                    topic == "structures"
                    and view._selection._scientific is not None
                    and view._selection._scientific.options == options
                    and view._focus is None
                )
            )
            and view._selected == view._selection._entries
            and view._display_request is None
            and view.request is None
        ):
            return replace(
                view,
                _explorer=explorer,
                _origin=explorer._origin if origin is None else origin,
            )
    return not_saved(
        explorer,
        f"Topic {topic!r} was not retained with a supported historical verifier.",
        origin,
    )


def saved_answer(explorer, question, options, origin):
    if (
        not isinstance(question, str)
        or question not in explorer._questions
        or not isinstance(options, dict)
    ):
        raise ArgumentError("Use a registered question and an options mapping.")
    if question == "region_coverage":
        from .card_exploration_science import _options

        sequence_ref = options.get("sequence_ref")
        if sequence_ref is not None and (
            not isinstance(sequence_ref, str) or not sequence_ref.strip()
        ):
            raise ArgumentError("sequence_ref requires an explicit nonempty string.")
        if set(options) - {"sequence_ref", "region", "include_fragments"}:
            raise ArgumentError("Unknown region question option.")
        options = {
            "sequence_ref": options.get("sequence_ref"),
            **_options(
                {key: value for key, value in options.items() if key != "sequence_ref"}
            ),
        }
    for view in list(explorer._session["views"].values()):
        if (
            view._saved_state is not None
            and view._explorer.access._focal_key == explorer.access._focal_key
            and view.request is not None
            and view.request["question"] == question
            and (
                view._field_panel == explorer._questions[question]["topic"]
                or (
                    view._selection._scientific is not None
                    and explorer._questions[question]["topic"] == "structures"
                    and view._focus is None
                )
                or (
                    view._record_panel == "classification"
                    and explorer._questions[question]["topic"] == "classification"
                )
                or (
                    question == "region_coverage"
                    and isinstance(view.native_payload, dict)
                    and view.native_payload.get("question") == question
                )
            )
            and view._display_request is None
            and view.request["options"] == options
            and view._selected == view._selection._entries
        ):
            return replace(
                view,
                _explorer=explorer,
                _origin=explorer._origin if origin is None else origin,
            )
    if question == "region_coverage":
        from sabueso._private.argdigest.argument.region import digest_region

        if set(options) - {"sequence_ref", "region", "include_fragments"}:
            raise ArgumentError("Unknown region question option.")
        if (
            "include_fragments" in options
            and type(options["include_fragments"]) is not bool
        ):
            raise ArgumentError("include_fragments must be True or False.")
        digest_region(options.get("region"))
    elif options:
        raise ArgumentError("This question has no scientific options.")
    return not_saved(
        explorer,
        f"Question {question!r} and these effective inputs were not retained.",
        origin,
    )


def start_new(explorer):
    # Share only immutable captures; all materialized interpretations and session
    # ownership are fresh. No caller Card serialization, current store or source.
    access = _access(
        explorer.access._captures,
        explorer.access._inputs,
        {},
        {},
        explorer.access._focal_key,
    )
    access._mode = "live"
    return _explorer(access, {"views": {}, "explanations": {}, "links": {}})


def save_selection(selection, path, overwrite):
    _require(
        can_save_selection(selection),
        "Scientific selection persistence requires an unsupported historical verifier.",
    )
    session = selection._access._exploration_session
    if session is None:
        session = {"views": {}, "explanations": {}, "links": {}}
    explorer = _explorer(selection._access, session)
    view = CardView(
        explorer,
        selection,
        selection._entries,
        "Saved machine selection",
        _machine_ref=selection.selection_ref,
    )
    return save_exploration(view, path, overwrite=overwrite)


def missing_selection(access, topic, options, projection):
    location = access._object_location(
        {
            "topic": topic,
            "options": options,
            "fields": list(projection),
            "outcome": "not_saved",
        }
    )
    selection = access.read(location)
    return replace(
        selection,
        _entries=(),
        _outcome_override={
            "status": "not_saved",
            "reason": "No supported retained scientific selection is available.",
        },
    )
