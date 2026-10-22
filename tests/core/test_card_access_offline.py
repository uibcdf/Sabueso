"""Bounded literal access contracts. Synthetic content is not source knowledge."""

import hashlib
import json
import socket
from copy import deepcopy
from dataclasses import FrozenInstanceError

import pytest
import pyunitwizard as puw
from argdigest import UnknownArgumentError
from pyunitwizard import QuantityRecord
from pyunitwizard.record import RecordError

from sabueso._private.smonitor.warnings import NewerCardSchemaWarning
from sabueso.core.card import Card
from sabueso.core.card_access import CardAccess
from sabueso.core.errors import ArgumentError, StorageError
from sabueso.core.snapshot import canonical_json


def _card(payload=None, nature=None):
    card = Card(meta={"entity_type": nature} if nature else {})
    card.unknown_stored["synthetic"] = {} if payload is None else payload
    return card


def _location(access, *keys):
    return {
        "format": "card_access_location@1",
        "kind": "card",
        "card_ref": access.context["card_ref"],
        "snapshot_id": access.context["snapshot_id"],
        "segments": [
            {"type": "Index" if type(k) is int else "Key", "value": k} for k in keys
        ],
    }


def _pages(selection, limit=7, max_bytes=8192):
    cursor = None
    while True:
        frame = selection.page(limit=limit, max_bytes=max_bytes, cursor=cursor)
        assert len(canonical_json(frame).encode("utf-8")) <= max_bytes
        assert frame["page"]["returned"] <= limit
        assert frame["page"]["blocked"] is None
        yield frame
        cursor = frame["page"]["next_cursor"]
        if cursor is None:
            assert frame["page"]["complete"]
            break


def _reconstruct(access, location):
    selection = access.read(location)
    pages = list(_pages(selection))
    kind = pages[0]["node"]["node_type"]
    items = [item for page in pages for item in page["items"]]
    if kind == "object":
        return {item["key"]: _reconstruct(access, item["location"]) for item in items}
    if kind == "array":
        return [
            _reconstruct(access, item["location"])
            for item in sorted(items, key=lambda item: item["ordinal"])
        ]
    assert len(items) == 1 and items[0]["value_included"]
    return items[0]["value"]


@pytest.mark.parametrize(
    "nature", [None, "protein", "small_molecule", "disease", "unknown"]
)
def test_complete_literal_reconstruction(nature):
    payload = {
        "dots.are.literal": [False, 0, None, "", {}, []],
        "Unicode": "α🧬 café",
        "nested": {"x": [1, 2.5, {"y": "z"}]},
        "quantity_lookalike": {"value": 12, "unit": "native fictional unit"},
    }
    card = _card(payload, nature)
    original = card.to_dict()
    access = card.access()
    assert _reconstruct(access, access.root_location) == original
    assert access.profile == (
        nature if nature in ("protein", "small_molecule", "disease") else "generic"
    )
    assert access.context["card_ref"] is None
    assert access.capabilities["scientific_topics"] == (
        ["structures"] if nature == "protein" else []
    )


def test_capture_once_isolation_and_defensive_public_values(monkeypatch):
    card = _card({"field": [1, 2, 3]})
    original, calls = card.to_dict, []

    def serialize():
        calls.append(True)
        return original()

    monkeypatch.setattr(card, "to_dict", serialize)
    access = card.access(related_cards=[card, card])
    assert len(calls) == 1
    assert len(access.context["inputs"]) == 3
    assert len(access.context["captures"]) == 1
    selection = access.read(_location(access, "synthetic", "field"))
    before = selection.page()
    card.unknown_stored["synthetic"]["field"][0] = 99
    access.context["inputs"].clear()
    before["items"][0]["value"] = 77
    assert selection.page()["items"][0]["value"] == 1
    assert len(calls) == 1
    with pytest.raises((AttributeError, FrozenInstanceError)):
        selection.count = 22
    with pytest.raises(AttributeError):
        access.profile = "invented"


def test_related_revisions_are_preserved_not_merged():
    first = _card({"x": 1})
    first.meta["card_id"] = "sabueso:protein:uniprot:P52270"
    other = Card.from_dict(first.to_dict())
    other.unknown_stored["synthetic"]["x"] = 2
    access = first.access([other])
    assert len(access.context["captures"]) == 2
    assert access.context["card_ref"].startswith(first.id + "@")
    assert _reconstruct(access, _location(access, "synthetic")) == {"x": 1}
    other_pin = next(
        pin for pin in access.context["captures"] if pin != access.context["card_ref"]
    )
    other_location = _location(access, "synthetic", "x")
    other_location["card_ref"] = other_pin
    other_location["snapshot_id"] = other_pin.split("@", 1)[1]
    page = access.read(other_location).page()
    assert page["items"][0]["value"] == 2
    assert page["node"]["owner"]["card_ref"] == other_pin


@pytest.mark.parametrize("limit", [1, 3, 32, 256])
@pytest.mark.parametrize("budget", [3072, 4096, 8192])
def test_page_bounds_membership_and_retry(limit, budget):
    access = _card(list(range(39))).access()
    selection = access.read(_location(access, "synthetic"))
    frames = list(_pages(selection, limit, budget))
    items = [item for frame in frames for item in frame["items"]]
    assert [item["value"] for item in items] == list(range(39))
    assert len({item["item_ref"] for item in items}) == 39
    first = frames[0]
    if first["page"]["next_cursor"]:
        token = first["page"]["next_cursor"]
        assert selection.page(cursor=token, limit=limit, max_bytes=budget) == frames[1]
    assert (
        selection.selection_ref
        == access.selection(selection.selection_ref).selection_ref
    )


def test_cursors_are_selection_and_session_bound():
    access = _card([1, 2, 3]).access()
    first = access.read(_location(access, "synthetic"))
    token = first.page(limit=1)["page"]["next_cursor"]
    second = access.catalog()
    for selection, cursor in (
        (second, token),
        (first, "invented"),
        (_card([1, 2, 3]).access().catalog(), token),
    ):
        with pytest.raises(ArgumentError, match="cursor"):
            selection.page(cursor=cursor)
    assert [x["value"] for x in first.page(cursor=token, limit=2)["items"]] == [2, 3]


def test_large_text_deferral_and_exact_unicode_ranges():
    text = "α🧬e\u0301" * 6000
    access = _card(text).access()
    location = _location(access, "synthetic")
    frame = access.read(location).page(max_bytes=4096)
    assert frame["page"]["complete"]
    assert not frame["page"]["values_complete"]
    item = frame["items"][0]
    assert item["value_included"] is False and "value" not in item
    assert item["size"] == len(text)
    pieces = []
    for start in range(0, len(text), 37):
        stop = min(start + 37, len(text))
        part = access.read(
            item["value_location"], text_slice={"start": start, "stop": stop}
        ).page(max_bytes=4096)
        value = part["items"][0]
        assert value["text_range"] == {
            "start": start,
            "stop": stop,
            "total": len(text),
            "partial": True,
        }
        pieces.append(value["value"])
    assert "".join(pieces) == text
    empty = access.read(
        location, text_slice={"start": len(text), "stop": len(text)}
    ).page()
    assert empty["items"][0]["value"] == ""


def test_large_keys_are_reachable_without_copying_them_into_every_frame():
    key = "large🧬" * 3000
    access = _card({key: "retained"}).access()
    page = access.read(_location(access, "synthetic")).page(max_bytes=4096)
    item = page["items"][0]
    assert "key" not in item and item["key_location"]
    key_part = access.read(
        item["key_location"], text_slice={"start": 0, "stop": 12}
    ).page()
    assert key_part["items"][0]["value"] == key[:12]
    assert access.read(item["location"]).page()["items"][0]["value"] == "retained"


@pytest.mark.parametrize("payload,kind", [([], "array"), ({}, "object")])
def test_empty_container_type_is_explicit(payload, kind):
    access = _card(payload).access()
    page = access.read(_location(access, "synthetic")).page()
    assert page["node"]["node_type"] == kind and page["node"]["size"] == 0
    assert page["items"] == [] and page["page"]["complete"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"limit": True},
        {"limit": 0},
        {"limit": 257},
        {"max_bytes": True},
        {"max_bytes": 1023},
        {"max_bytes": 1048577},
        {"cursor": []},
    ],
)
@pytest.mark.parametrize("skip", [False, True])
def test_limits_fail_through_diagnostics_even_when_skipped(kwargs, skip):
    selection = _card().access().catalog()
    with pytest.raises(ArgumentError) as error:
        selection.page(**kwargs, skip_digestion=skip)
    assert error.value.code


@pytest.mark.parametrize(
    "slice_value",
    [
        {"start": True, "stop": 1},
        {"start": -1, "stop": 1},
        {"start": 2, "stop": 1},
        {"start": 0, "stop": 4},
        {},
        [0, 1],
    ],
)
def test_bad_text_slice_is_an_argument_error(slice_value):
    access = _card("abc").access()
    with pytest.raises(ArgumentError):
        access.read(_location(access, "synthetic"), text_slice=slice_value)


def test_location_validation_and_unknown_kwargs():
    access = _card({"x": 1}).access()
    valid = _location(access, "synthetic", "x")
    cases = [
        None,
        "sections.x",
        {**valid, "extra": True},
        {**valid, "snapshot_id": "sha256:" + "0" * 64},
        {**valid, "segments": [{"type": "Key", "value": "missing"}]},
        {**valid, "segments": [{"type": "Index", "value": -1}]},
        _card().access().root_location,
    ]
    for location in cases:
        with pytest.raises(ArgumentError):
            access.read(location)
    with pytest.raises(ArgumentError):
        access.catalog(locator=valid)
    with pytest.raises(ArgumentError):
        access.catalog(kind="made_up")
    with pytest.raises(UnknownArgumentError):
        access.read(valid, fetch=True)


def test_selections_catalog_does_not_recursively_catalog_itself():
    access = _card().access()
    access.catalog()
    first = access.catalog("selections")
    assert access.catalog("selections") is first
    assert first.count == 1
    assert repr(access).find("synthetic") == -1
    assert len(repr(first)) < 160


def test_no_source_acquisition_scientific_views_or_repeated_serialization(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("No acquisition or scientific view in literal reading")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(Card, "structures", forbidden)
    monkeypatch.setattr(Card, "knowledge_state", forbidden)
    card = _card({"x": 1})
    access = card.access()
    monkeypatch.setattr(Card, "to_dict", forbidden)
    assert _reconstruct(access, _location(access, "synthetic")) == {"x": 1}
    assert access.catalog().count == 1


def test_bad_schema_and_unqualified_quantity_are_refused():
    bad = _card()
    bad.meta["schema_version"] = "99.0.0"
    with pytest.raises(StorageError):
        bad.access()
    bad = _card()
    bad.sections["unknown"] = {"value": 3, "unit": "nanomolar"}
    with pytest.raises(StorageError) as error:
        bad.access()
    assert "negotiated" in str(error.value)


def test_newer_readable_schema_warns_and_keeps_extension_content():
    card = _card({"future": ["kept"]})
    card.meta["schema_version"] = "0.3.99"
    with pytest.warns(NewerCardSchemaWarning):
        access = card.access()
    assert _reconstruct(access, _location(access, "synthetic")) == {"future": ["kept"]}


def test_quantity_leaves_retain_provider_record_and_explicit_field():
    card = Card(
        sections={
            "properties": {
                "physchem": {
                    "molecular_weight": {
                        "value": 260.25,
                        "unit": "dalton",
                        "source_assertion_ids": [],
                    }
                }
            }
        }
    )
    with puw.context(standard_units=["nm", "ps", "K", "mole", "gram"]):
        access = card.access()
        page = access.read(
            _location(
                access,
                "sections",
                "properties",
                "physchem",
                "molecular_weight",
                "value",
            )
        ).page()
    item = page["items"][0]
    assert item["value"] == 260.25
    quantity = QuantityRecord.from_dict(item["quantity_context"]["record"]).to_quantity(
        field="properties.physchem.molecular_weight", unit="dalton"
    )
    assert puw.get_value(quantity, to_unit="dalton") == pytest.approx(260.25)
    with pytest.raises(RecordError):
        QuantityRecord.from_dict(item["quantity_context"]["record"]).to_quantity(
            unit="nanometer"
        )
    extension = _card({"value": 12, "unit": "nanomolar"}).access()
    item = extension.read(_location(extension, "synthetic", "value")).page()["items"][0]
    assert "quantity_context" not in item


def test_capture_rejects_a_changed_quantity_with_an_original_seal(monkeypatch):
    card = Card(
        sections={
            "properties": {
                "physchem": {
                    "molecular_weight": {
                        "value": 260.25,
                        "unit": "dalton",
                        "source_assertion_ids": [],
                    }
                }
            }
        }
    )
    bad = card.to_dict()
    bad["sections"]["properties"]["physchem"]["molecular_weight"]["value"] = 999
    monkeypatch.setattr(card, "to_dict", lambda: bad)
    with pytest.raises(StorageError, match="seal"):
        card.access()


def test_public_frozen_card_record_ids_reordering_quantities_and_raw_export(tmp_path):
    card = Card.from_json("temp_data/frozen_cards/schema_0.3.9__P52270.json")
    original = card.to_dict()
    access = card.access()
    records = access.read(_location(access, "relationship_store"))
    pages = list(_pages(records, max_bytes=8192))
    first = pages[0]["items"][0]
    assert first["key"].startswith("REL_")
    with pytest.raises(ArgumentError):
        access.read(_location(access, "relationship_store", 0))
    reordered = deepcopy(original)
    reordered["relationship_store"].reverse()
    other = Card.from_dict(reordered).access()
    assert other.context["snapshot_id"] == access.context["snapshot_id"]
    assert (
        other.read(_location(other, "relationship_store")).result_ref
        == records.result_ref
    )
    target = tmp_path / "card.json"
    receipt = access.export_card(target)
    assert json.loads(target.read_text()) == original
    assert receipt["sha256"] == hashlib.sha256(target.read_bytes()).hexdigest()
    assert Card.from_json(target).pinned_ref() == access.context["card_ref"]
    structure = next(
        r
        for r in original["relationship_store"]
        if r["object_ref"] == "pdb:1SUX" and r["predicate"] == "has_structure"
    )
    location = _location(access, "relationship_store")
    location["segments"].extend(
        [
            {"type": "Record", "value": structure["id"]},
            {"type": "Key", "value": "qualifiers"},
            {"type": "Key", "value": "resolution"},
            {"type": "Key", "value": "value"},
        ]
    )
    cell = access.read(location).page()["items"][0]
    q = QuantityRecord.from_dict(cell["quantity_context"]["record"]).to_quantity(
        field="relationships.has_structure.resolution", unit="angstrom"
    )
    assert float(puw.get_value(q, to_unit="angstrom")) == 2.0
    preserved = target.read_bytes()
    with pytest.raises(StorageError):
        access.export_card(target)
    assert target.read_bytes() == preserved
    assert not list(tmp_path.glob(".sabueso-access-*"))


def test_failed_atomic_export_preserves_existing_file(tmp_path, monkeypatch):
    target = tmp_path / "card.json"
    target.write_bytes(b"caller data")
    import sabueso.core.card_access as module

    def fail(*args):
        raise OSError("synthetic publication failure")

    monkeypatch.setattr(module.os, "replace", fail)
    with pytest.raises(StorageError):
        _card().access().export_card(target, overwrite=True)
    assert target.read_bytes() == b"caller data"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["card.json"]


def test_literal_metadata_budget_failure_is_not_an_empty_scientific_answer():
    access = _card("x").access()
    with pytest.raises(ArgumentError) as error:
        access.catalog().page(max_bytes=1024)
    assert error.value.extra["reason"] == "response_budget_too_small"


@pytest.mark.parametrize("skip", [False, True])
def test_constructor_rejects_invalid_card_and_related_context(skip):
    with pytest.raises(ArgumentError):
        CardAccess(None, skip_digestion=skip)
    with pytest.raises(ArgumentError):
        _card().access(related_cards="a path", skip_digestion=skip)
