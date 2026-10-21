"""One validated, detached capture factory for Card access facades."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .errors import ArgumentError, SchemaError, StorageError
from .quantities import verify
from .schema_version import check_card_schema
from .snapshot import canonical_json, parse_ref, snapshot_id


@dataclass(frozen=True)
class _Capture:
    data: dict
    snapshot: str
    pin: str | None


def _capture_cards(card, related_cards):
    from .card import CARD_SCHEMA_VERSION, Card

    if not isinstance(card, Card):
        raise ArgumentError("card must be a Card.")
    if not isinstance(related_cards, (list, tuple)) or not all(
        isinstance(item, Card) for item in related_cards
    ):
        raise ArgumentError("related_cards must be a list or tuple of Cards.")
    captures, inputs, by_object = {}, [], {}
    for item in (card, *related_cards):
        if id(item) not in by_object:
            try:
                # Canonical JSON establishes the stored types, not backend objects.
                data = json.loads(canonical_json(item.to_dict()))
                newer = check_card_schema(data.get("meta"), CARD_SCHEMA_VERSION)
                verify(data, data.get("quantities"))
                snapshot = snapshot_id(data)
                card_id = data["meta"].get("card_id")
                if card_id is not None:
                    ref = parse_ref(card_id)
                    if ref.snapshot_id or ref.item_id:
                        raise StorageError("A Card identity cannot already be pinned.")
                for store in ("source_assertion_store", "relationship_store"):
                    ids = [record["id"] for record in data[store]]
                    if any(not isinstance(key, str) or not key for key in ids) or len(
                        set(ids)
                    ) != len(ids):
                        raise StorageError(f"{store} requires unique nonempty IDs.")
            except (TypeError, ValueError, KeyError, UnicodeError, SchemaError) as exc:
                raise StorageError(
                    f"Cannot capture this Card's stored form: {exc}"
                ) from exc
            pin = f"{card_id}@{snapshot}" if card_id else None
            if newer:
                from sabueso._private.smonitor.outcomes import report_newer_schema

                report_newer_schema(card_id or "", data["meta"]["schema_version"])
            key = pin or snapshot
            captures.setdefault(key, _Capture(data, snapshot, pin))
            by_object[id(item)] = key
        inputs.append(by_object[id(item)])
    return captures, tuple(inputs)
