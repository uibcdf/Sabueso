"""Original public structure-local instances; altered cases are synthetic."""

import importlib
import json
import socket
import subprocess
import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.core.errors import ArgumentError, StorageError


def forbidden(*args, **kwargs):
    raise AssertionError("No acquisition or scientific reinterpretation")


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


@pytest.fixture
def card():
    return Card.from_dict(
        json.loads(Path("temp_data/frozen_cards/schema_0.3.9__P52270.json").read_text())
    )


def structure(card, ref="pdb:1SUX"):
    return next(
        row
        for row in card.relationship_store.store.values()
        if row["predicate"] == "has_structure" and row["object_ref"] == ref
    )


def test_instances_are_exact_original_nodes_with_relationship_support(card):
    original = card.to_dict()
    explorer = card.explore()
    view = explorer.answer("structure_ligands")
    assert view.result_ref == explorer.view("ligand_instances").result_ref
    expected = [
        instance
        for row in original["relationship_store"]
        if row["predicate"] == "has_structure"
        for ligand in row["qualifiers"].get("ligands", [])
        for instance in ligand.get("instances", [])
    ]
    assert len(view.items()) == len(expected) > 10
    assert [item.cells["value"].value for item in view.items()] == expected
    item = view.items()[0]
    assert item.kind == "ligand_instance"
    assert "pdb:1SUX · component BTS · instance J" in item.label
    assert item.open().native_payload == expected[0]
    assert item.support[0]["basis"] == "relationship_level"
    assert (
        item.support[0]["location"]["segments"] == item.payload_location["segments"][:2]
    )
    assert item.explain().native_payload["support"] == item.support
    assert item.open().back() is view and item.explain().back() is view
    assert item.related().filter("role", equals="source").items()
    assert "one original instance" in view.schema["grain"]
    assert card.to_dict() == original


def test_scoped_selection_uses_declared_context_not_formatted_labels(card):
    view = card.explore().view("ligand_instances")
    bts = view.filter("structure_ref", equals="pdb:1SUX").filter(
        "component_id", equals="BTS"
    )
    assert len(bts.items()) == 1 and bts.items()[0].cells["instance_id"].value == "J"
    assert bts.items()[0].cells["value"].value == view.items()[0].cells["value"].value
    assert bts.sort("instance_id").items()[0].item_ref == bts.items()[0].item_ref
    assert not view.filter("component_id", equals="Deliberately unmatched").items()
    assert bts.items()[0].cells["component_id"].support == bts.items()[0].support
    with pytest.raises(ArgumentError):
        view.filter("contacts", equals="J")


def test_original_numbering_distances_and_unknowns_are_visible(card):
    view = card.explore().view("ligand_instances")
    item = next(
        item
        for item in view.items()
        if "pdb:2OMA · component PEG · instance H" in item.label
    )
    text = repr(view.filter("label", equals=item.label))
    assert "position 118 / seq_id 117 / UniProt P52270" in text
    assert "3.386 angstrom" in text and "recorded bound flag: unknown" in text
    assert "investigation flag: False" in text
    assert "Historical mapping basis is not verified" in text and "relationship" in text
    assert "No assembly" in view.native_payload["scope"]
    assert " … (6 records; open() for all)" in text


def test_missing_empty_and_malformed_declarations_keep_original_scope(card):
    row = structure(card)
    row["qualifiers"]["ligands"] = [
        {"comp_id": "SYNTHETIC_MISSING"},
        {"comp_id": "SYNTHETIC_EMPTY", "instances": []},
        {"comp_id": "SYNTHETIC_BAD", "instances": "bad"},
        {"comp_id": "SYNTHETIC_PARTIAL", "instances": [None, {}]},
        "bad ligand",
    ]
    view = card.explore().view("ligand_instances")
    gaps = [
        gap
        for gap in view.native_payload["field_gaps"]
        if gap["field"].startswith(row["id"])
    ]
    assert [gap["state"] for gap in gaps] == [
        "not_retained",
        "retained_empty",
        "unrecognized_shape",
        "unrecognized_shape",
        "unrecognized_shape",
    ]
    item = next(
        item for item in view.items() if "component SYNTHETIC_PARTIAL" in item.label
    )
    assert "instance unknown" in item.label and item.open().native_payload == {}
    assert "recorded bound flag: unknown" in repr(
        item.back().filter("label", equals=item.label)
    )
    assert "Missing declarations are not absence" in repr(view)


@pytest.mark.parametrize("mode", ["missing", "wrong", "conflicting"])
def test_identity_prerequisite_does_not_turn_into_no_ligands(card, mode):
    if mode == "missing":
        card.meta.pop("card_id")
    elif mode == "wrong":
        card.get("identifiers.uniprot")["value"] = "P60174"
    else:
        card.quality["conflicts"] = [
            {"field": "identifiers.uniprot", "values": ["P52270", "P60174"]}
        ]
    view = card.explore().view("ligand_instances")
    assert view.outcome["status"] == "missing_prerequisite"
    assert not view.items()


def test_foreign_structure_and_aggregate_contacts_are_not_instances(card):
    original = card.explore().view("ligand_instances")
    row = deepcopy(structure(card))
    row["id"] += "_FOREIGN"
    row["subject_ref"] = "uniprot:P60174"
    card.relationship_store.add(row)
    assert len(card.explore().view("ligand_instances").items()) == len(original.items())
    assert all(
        item.payload_location["segments"][1]["value"] != row["id"]
        for item in original.items()
    )
    assert (
        card.explore()
        .view("sites")
        .filter("kind", equals="contact_relationship")
        .items()
    )


def test_repeated_component_and_instance_identifiers_remain_separate(card):
    row = structure(card)
    ligand = row["qualifiers"]["ligands"][0]
    ligand["instances"].append(deepcopy(ligand["instances"][0]))
    row["qualifiers"]["ligands"].append(deepcopy(ligand))
    view = card.explore().view("ligand_instances")
    duplicates = [item for item in view.items() if "component BTS" in item.label]
    assert len(duplicates) == 4
    assert len({item.item_ref for item in duplicates}) == 4
    assert (
        len({json.dumps(item.payload_location, sort_keys=True) for item in duplicates})
        == 4
    )


@pytest.mark.parametrize(
    "ligands,state",
    [(None, "not_retained"), ([], "retained_empty"), (17, "unrecognized_shape")],
)
def test_unavailable_declarations_are_saved_without_becoming_negative_knowledge(
    card, ligands, state, tmp_path
):
    row = structure(card)
    row["qualifiers"]["ligands"] = ligands
    view = card.explore().view("ligand_instances")
    path = tmp_path / "partial.json"
    view.save(path)
    saved = sabueso.read_exploration(path)
    gap = next(
        gap for gap in saved.native_payload["field_gaps"] if gap["field"] == row["id"]
    )
    assert gap["state"] == state
    assert saved.explorer.inspect(locator=gap["location"]).native_payload == ligands
    assert all("pdb:1SUX" not in item.label for item in saved.items())


@pytest.mark.parametrize("nature", ["small_molecule", "disease"])
def test_not_applicable_and_options_are_explicit(nature):
    view = Card(meta={"entity_type": nature}).explore().view("ligand_instances")
    assert view.outcome["status"] == "not_applicable" and not view.items()


def test_no_scientific_reader_or_new_request_runs(card, monkeypatch):
    for method in ("structures", "ligand_sites", "predicted_structures"):
        monkeypatch.setattr(Card, method, forbidden)
    explorer = card.explore()
    assert explorer.view("ligand_instances").items()
    with pytest.raises(ArgumentError):
        explorer.view("ligand_instances", options={"region": [96]})


def test_saved_instances_are_inert_and_bound_to_original_membership(
    card, tmp_path, monkeypatch
):
    view = card.explore().answer("structure_ligands")
    path = tmp_path / "original.json"
    view.save(path)
    original = path.read_bytes()
    labels = [item.label for item in view.items()]
    monkeypatch.setattr(Card, "from_dict", forbidden)
    monkeypatch.setattr(
        importlib.import_module("sabueso.core.card_exploration_profiles"),
        "field_entries",
        forbidden,
    )
    saved = sabueso.read_exploration(path)
    assert [item.label for item in saved.items()] == labels
    assert saved.explorer.answer("structure_ligands").view_ref == view.view_ref
    assert saved.items()[0].explain().back() is saved
    assert saved.items()[0].related().filter("role", equals="source").items()
    assert "3.351 angstrom" in repr(saved)
    assert path.read_bytes() == original
    bad = replace(view, _selected=(), _selection=replace(view._selection, _entries=()))
    with pytest.raises(StorageError, match="membership"):
        bad.save(tmp_path / "bad.json")


def test_independent_saved_reader_needs_no_live_reconstruction(card, tmp_path):
    path = tmp_path / "instances.json"
    view = card.explore().view("ligand_instances")
    view.save(path)
    script = """
import sys
from unittest.mock import patch
import sabueso
from sabueso.core.card import Card
def fail(*a, **k): raise AssertionError('No live reader or acquisition')
with patch.object(Card,'from_dict',fail),patch.object(Card,'structures',fail),patch.object(Card,'ligand_sites',fail),patch('socket.socket.connect',fail):
    view=sabueso.read_exploration(sys.argv[1])
    assert len(view.items())==int(sys.argv[2])
    assert view.items()[0].open().native_payload['asym_id']=='J'
    assert '3.351 angstrom' in repr(view)
"""
    subprocess.run(
        [sys.executable, "-c", script, str(path), str(len(view.items()))], check=True
    )


def test_false_empty_zero_and_conflicts_remain_visible(card):
    row = structure(card)
    row["qualifier_conflicts"] = {"synthetic": [1, 2]}
    instance = row["qualifiers"]["ligands"][0]["instances"][0]
    instance.update(
        is_bound=False,
        chains=[],
        contacts=[
            {
                "position": 0,
                "seq_id": 1,
                "min_distance": {"value": 0, "unit": "angstrom"},
            }
        ],
    )
    text = repr(card.explore().view("ligand_instances"))
    assert "recorded bound flag: False" in text and "[] (retained empty list)" in text
    assert "position 0 / seq_id 1" in text and "0 angstrom" in text
    assert "unresolved parent qualifier conflicts" in text


def test_bounded_escaped_display_keeps_complete_original_instances(card):
    instance = structure(card)["qualifiers"]["ligands"][0]["instances"][0]
    instance["asym_id"] = "<script>unsafe</script>" + "x" * 3000
    instance["contacts"].extend(deepcopy(instance["contacts"]) * 40)
    view = card.explore().view("ligand_instances")
    html = view._repr_html_()
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "x" * 3000 not in html
    assert view.items()[0].cells["value"].value == instance
    assert len(view.items()[0].open().native_payload["contacts"]) == 123
