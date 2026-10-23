"""Selected-method preview over public inputs and deliberately malformed variants."""

import socket

import pytest

import sabueso
from sabueso.core.source_assertion_store import make_source_assertion
from sabueso.tools.card.small_molecule import single_molecule_card
from sabueso.tools.db.chembl import FixtureChEMBLClient


def forbidden(*args, **kwargs):
    raise AssertionError("No source query or method lookup for malformed selection")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


@pytest.fixture
def molecule():
    return single_molecule_card(
        chembl=FixtureChEMBLClient("temp_data").molecules(["CHEMBL110"])
    )


INVALID = [
    None,
    False,
    True,
    0,
    1,
    1.5,
    "",
    "selected_id",
    {"selected_id": "synthetic"},
    [0],
    [False],
    [{}],
]


@pytest.mark.parametrize("refs", INVALID)
def test_malformed_selection_renders_unknown_without_method_or_partial_attribution(
    molecule, refs
):
    molecule.get("properties.physchem.logp")["source_assertion_ids"] = refs
    original = molecule.to_dict()
    view = molecule.explore().view("properties").filter("label", equals="logP")
    text, html = repr(view), view.table()._repr_html_()
    assert "selected-source method unknown: unrecognized selection references" in text
    assert "selected-source method unknown" in html
    assert "ALogP" not in text and "ALogP" not in html
    assert "source attribution unknown" in text
    item = view.items()[0]
    assert item.cells["value"].value == 1.11
    assert item.open().native_payload["source_assertion_ids"] == refs
    assert "Selection role unknown" in repr(item.explain())
    assert molecule.to_dict() == original


@pytest.mark.parametrize("position", [0, 1, 4])
def test_mixed_reference_list_is_unknown_as_a_whole_including_beyond_preview(
    molecule, position, monkeypatch
):
    good = molecule.get("properties.physchem.logp")["source_assertion_ids"][0]
    refs = [good] * 5
    refs[position] = {"synthetic": "invalid"}
    molecule.get("properties.physchem.logp")["source_assertion_ids"] = refs
    explorer = molecule.explore()
    view = explorer.view("properties").filter("label", equals="logP")
    monkeypatch.setattr(type(explorer), "_statement", forbidden)
    text = repr(view)
    assert "method unknown: unrecognized selection references" in text
    assert "source attribution unknown" in text and "ALogP" not in text


def test_missing_selection_and_declared_empty_selection_are_distinct(molecule):
    field = molecule.get("properties.physchem.logp")
    field.pop("source_assertion_ids")
    missing = molecule.explore().view("properties").filter("label", equals="logP")
    assert "method unknown: selection references not retained" in repr(missing)
    assert "Selection role unknown" in repr(missing.items()[0].explain())
    field["source_assertion_ids"] = []
    empty = molecule.explore().view("properties").filter("label", equals="logP")
    assert "method not stated in selected support" in repr(empty)
    assert "Alternative statement" in repr(empty.items()[0].explain())


def test_valid_public_method_and_original_unit_are_preserved(molecule):
    view = molecule.explore().view("properties")
    assert "selected-source method: ALogP" in repr(view)
    weight = view.filter("label", equals="Molecular weight")
    assert "method not stated in selected support" in repr(weight)
    assert "260.25 dalton" in repr(weight)


def test_missing_selected_record_does_not_establish_missing_method(molecule):
    molecule.get("properties.physchem.logp")["source_assertion_ids"] = [
        "SA_SYNTHETIC_NOT_RETAINED"
    ]
    view = molecule.explore().view("properties").filter("label", equals="logP")
    assert "method unknown: supporting records not retained" in repr(view)
    assert "method not stated" not in repr(view)


def test_partial_support_keeps_known_method_and_explicit_gap(molecule):
    molecule.get("properties.physchem.logp")["source_assertion_ids"].append(
        "SA_SYNTHETIC_NOT_RETAINED"
    )
    view = molecule.explore().view("properties").filter("label", equals="logP")
    assert "selected-source method: ALogP" in repr(view)
    assert "some supporting records not retained" in repr(view)


@pytest.mark.parametrize("known_first", [False, True])
def test_preview_limit_never_claims_absence_beyond_inspected_references(
    molecule, known_first
):
    refs = []
    for index in range(5):
        row = make_source_assertion(
            "properties.physchem.logp", 1.11, "Synthetic", str(index), "synthetic"
        )
        if index == 4 or (known_first and index == 0):
            row["source_metadata"] = {"method": "Synthetic retained method"}
        molecule.source_assertion_store.add(row)
        refs.append(row["id"])
    molecule.get("properties.physchem.logp")["source_assertion_ids"] = refs
    view = molecule.explore().view("properties").filter("label", equals="logP")
    text = repr(view)
    assert "4 of 5 references" in text and "method not stated" not in text
    assert ("selected-source method: Synthetic retained method" in text) is known_first
    assert len(view.items()[0].explain().items()) >= 5


@pytest.mark.parametrize("refs", [{"synthetic": "invalid"}, 1, ["original", {}]])
def test_saved_malformed_selection_keeps_unknown_preview_and_literal_detail(
    molecule, refs, tmp_path
):
    molecule.get("properties.physchem.logp")["source_assertion_ids"] = refs
    view = molecule.explore().view("properties").filter("label", equals="logP")
    path = tmp_path / "malformed.json"
    view.save(path)
    original = path.read_bytes()
    saved = sabueso.read_exploration(path)
    assert "selected-source method unknown" in repr(saved)
    assert "ALogP" not in repr(saved)
    assert saved.items()[0].open().native_payload["source_assertion_ids"] == refs
    assert "Selection role unknown" in repr(saved.items()[0].explain())
    assert path.read_bytes() == original
