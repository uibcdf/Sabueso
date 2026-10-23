"""Inspectable structural cell delivery over public inputs and synthetic variants."""

import gzip
import hashlib
import importlib
import json
import socket
from pathlib import Path

import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.core.snapshot import canonical_json

PUBLIC = Path("temp_data/frozen_cards/schema_0.3.9__P52270.json")
FROZEN = Path("tests/core/data/card_agent_selection_v1.json.gz")
FIELDS = [
    "label",
    "kind",
    "structure_ref",
    "method",
    "resolution",
    "chains",
    "coverage",
    "coverage_class",
    "state",
]


def forbidden(*args, **kwargs):
    raise AssertionError("No acquisition or new scientific evaluation allowed")


@pytest.fixture(autouse=True)
def no_queries(monkeypatch):
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


@pytest.fixture
def card():
    return Card.from_dict(json.loads(PUBLIC.read_text(encoding="utf-8")))


def walk(access, location):
    """Reconstruct only through the public bounded protocol, including strings."""
    selection = access.read(location)
    frames, cursor = [], None
    while True:
        page = selection.page(limit=8, max_bytes=8192, cursor=cursor)
        assert len(canonical_json(page).encode()) <= 8192
        assert not page["page"]["blocked"]
        frames.extend(page["items"])
        cursor = page["page"]["next_cursor"]
        if cursor is None:
            break
    kind = page["node"]["node_type"]
    if kind == "object":
        return {item["key"]: walk(access, item["location"]) for item in frames}
    if kind == "array":
        return [walk(access, item["location"]) for item in frames]
    if kind == "string" and not frames[0]["value_included"]:
        return "".join(
            access.read(
                location,
                text_slice={
                    "start": start,
                    "stop": min(start + 1024, page["node"]["size"]),
                },
            ).page(max_bytes=8192)["items"][0]["value"]
            for start in range(0, page["node"]["size"], 1024)
        )
    return frames[0]["value"]


def pick(access, fields):
    return access.select(
        "structures", fields=fields, where={"structure_ref": "pdb:1SUX"}
    )


@pytest.mark.parametrize("column", FIELDS)
def test_each_cell_has_exact_field_support_and_value_location(card, column):
    access = card.access()
    selection = pick(access, [column])
    page = selection.page(max_bytes=16384)
    item = page["items"][0]
    cell = item["cells"][column]
    assert page["page"]["values_complete"]
    assert cell["value_included"] and not item["inspection_required"]
    assert cell["field"] == {"adapter": "structure_exploration@1", "column": column}
    assert cell["support_basis"] == item["support"]["basis"] == "relationship_level"
    assert cell["support_ref"] == item["support"]["ref"] == item["relationship_ref"]
    assert item["subject_ref"] == card.id
    assert walk(access, cell["value_location"]) == cell["value"]
    assert walk(access, cell["interpretation_location"]) == item["interpretation"]
    support = walk(access, item["support_location"])
    assert item["support"]["source_assertions"] == support["source_assertions"]
    assert [s["id"] for s in item["support"]["source_assertions"]] == support[
        "source_assertion_ids"
    ]
    for assertion in item["support"]["source_assertions"]:
        assert walk(access, assertion["location"])["id"] == assertion["id"]


@pytest.mark.parametrize("large", ["support", "interpretation", "value"])
@pytest.mark.parametrize("fields", [[], ["method"], FIELDS])
def test_large_closure_is_atomic_and_typed_even_with_empty_projection(
    card, large, fields
):
    rel = next(
        r for r in card.relationships("has_structure") if r["object_ref"] == "pdb:1SUX"
    )
    if large == "support":
        rel["source_assertion_ids"].extend(
            f"SA_SYNTHETIC_MISSING_{i}" for i in range(120)
        )
    elif large == "interpretation":
        rel["qualifier_conflicts"] = {"method": ["X-ray", "synthetic" + "界" * 5000]}
    else:
        rel["qualifiers"]["method"] = "synthetic" + "界" * 5000
    access = card.access()
    selection = pick(access, fields)
    page = selection.page(max_bytes=8192)
    assert len(canonical_json(page).encode()) <= 8192
    assert page["page"]["complete"] and not page["page"]["blocked"]
    assert not page["page"]["values_complete"]
    item = page["items"][0]
    assert item["inspection_required"] and not item["value_included"]
    assert "support" not in item and "interpretation" not in item
    assert set(item["cells"]) == set(fields)
    for column, cell in item["cells"].items():
        assert not cell["value_included"] and "value" not in cell
        assert cell["support_basis"] == "relationship_level"
        assert cell["support_ref"] == item["relationship_ref"]
        assert cell["interpretation_location"] == item["interpretation_location"]
        assert walk(access, cell["value_location"]) is not None
    if large == "support":
        support = walk(access, item["support_location"])
        assert len(support["source_assertions"]) == 122
        assert all(
            s["state"] == "not_retained" and s["location"] is None
            for s in support["source_assertions"][2:]
        )
    else:
        assert (
            walk(access, item["interpretation_location"])["state"]["method"].startswith(
                "synthetic"
            )
            if large == "value"
            else walk(access, item["interpretation_location"])["qualifier_conflicts"][
                "method"
            ][1].startswith("synthetic")
        )


def test_unknown_and_conflicting_states_are_not_delivery_states(card):
    rel = next(
        r for r in card.relationships("has_structure") if r["object_ref"] == "pdb:1SUX"
    )
    rel["qualifiers"].pop("resolution", None)
    rel["qualifier_conflicts"] = {"method": ["X-ray", "NMR"]}
    rel["source_assertion_ids"].append("SA_SYNTHETIC_NOT_RETAINED")
    access = card.access()
    page = pick(access, ["method", "resolution"]).page(max_bytes=16384)
    item = page["items"][0]
    assert page["page"]["values_complete"]
    assert item["cells"]["resolution"]["value"] is None
    assert item["cells"]["resolution"]["state"] == "unknown"
    assert item["cells"]["method"]["state"] == "conflicting"
    assert item["interpretation"]["qualifier_conflicts"]["method"] == ["X-ray", "NMR"]
    assert item["support"]["source_assertions"][-1] == {
        "id": "SA_SYNTHETIC_NOT_RETAINED",
        "state": "not_retained",
        "location": None,
    }


def test_fitting_items_continue_on_next_page_without_unnecessary_deferral(card):
    access = card.access()
    selection = access.select("structures", fields=["structure_ref", "resolution"])
    cursor, refs = None, []
    while True:
        page = selection.page(limit=7, max_bytes=8192, cursor=cursor)
        assert len(canonical_json(page).encode()) <= 8192
        assert not page["page"]["blocked"]
        assert page["page"]["values_complete"]
        refs.extend(item["item_ref"] for item in page["items"])
        next_cursor = page["page"]["next_cursor"]
        assert selection.page(limit=7, max_bytes=8192, cursor=cursor) == page
        if next_cursor is None:
            break
        cursor = next_cursor
    assert len(refs) == len(set(refs)) == selection.count == 7


def test_frozen_original_selection_gets_current_delivery_without_new_science(
    tmp_path, monkeypatch
):
    payload = gzip.decompress(FROZEN.read_bytes())
    assert (
        hashlib.sha256(payload).hexdigest()
        == "4f88069416426c4b32cab97d8029dd061d167bac7769831da7aad0b4dd89a81d"
    )
    path = tmp_path / "original.json"
    path.write_bytes(payload)
    for module, function in [
        ("sabueso.core.card_scientific_access", "materialize"),
        ("sabueso.core.structures", "structure_inventory"),
        ("sabueso.core.knowledge_state", "knowledge_state"),
        ("sabueso.core.structure_explanation", "explain_structure_inventory"),
    ]:
        monkeypatch.setattr(importlib.import_module(module), function, forbidden)
    saved = sabueso.read_exploration(path)
    access = saved.explorer.access
    selection = access.selection(
        "XA_cb2ba0b7cbc9cf8e7008ff30467617852445d1bb80d571bc8917da8f9d4b439b"
    )
    before = canonical_json(selection._scientific.wire)
    page = selection.page(limit=1, max_bytes=8192)
    assert page["context"]["mode"] == "saved"
    assert page["page"]["values_complete"]
    item = page["items"][0]
    assert item["cells"]["resolution"]["support_basis"] == "relationship_level"
    assert (
        walk(access, item["support_location"])["source_assertions"]
        == item["support"]["source_assertions"]
    )
    assert canonical_json(selection._scientific.wire) == before
    assert path.read_bytes() == payload
    assert saved.validation["verified_selection_policies"] == [
        "structure_access_selection@1"
    ]
