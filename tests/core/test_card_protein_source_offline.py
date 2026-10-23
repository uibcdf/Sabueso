"""Public source-oriented protein routes; altered variants are synthetic."""

import importlib
import json
import socket
import subprocess
import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
import pyunitwizard as puw

import sabueso
from sabueso.core.card import Card
from sabueso.core.errors import ArgumentError, StorageError


def forbidden(*args, **kwargs):
    raise AssertionError("No acquisition, live interpretation or recapture")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


@pytest.fixture
def card():
    return Card.from_dict(
        json.loads(Path("temp_data/frozen_cards/schema_0.3.9__P52270.json").read_text())
    )


def pick(view, label):
    return view.filter("label", equals=label).items()[0]


def test_sequence_source_fields_quantities_and_feature_locations(card):
    original = card.to_dict()
    explorer = card.explore()
    view = explorer.answer("sequence_annotations")
    assert view.result_ref == explorer.view("sequence").result_ref
    assert (
        pick(view, "Primary sequence").cells["value"].value
        == card.get("sequence.primary")["value"]
    )
    mass = pick(view, "Sequence molecular weight").cells["value"].value
    assert (
        puw.get_value(mass, to_unit="dalton")
        == card.get("sequence.molecular_weight")["value"]
    )
    active = pick(view, "Active sites")
    assert active.open().native_payload == card.get("features_positional.active_site")
    annotations = pick(active.open(), "Annotations").open()
    assert len(annotations.items()) == 2
    assert "Electrophile" in annotations.items()[0].label
    assert "UniProt:P52270" in repr(annotations)
    assert "96–96" in repr(annotations) and "1-based" in repr(annotations)
    assert active.explain().back() is active.back()
    assert (
        view.schema["quantity_expectations"]["sequence.molecular_weight"]["unit"]
        == "dalton"
    )
    assert card.to_dict() == original


def test_predicted_model_is_a_complete_original_relationship_with_direct_support(card):
    explorer = card.explore()
    model = explorer.answer("predicted_models").items()[0]
    assert model.kind == "predicted_model"
    assert "alphafold:AF-P52270-F1" in model.label
    assert (
        model.open().native_payload == card.relationships("has_predicted_structure")[0]
    )
    text = repr(model.back())
    assert (
        "97.31" in text
        and "1–251" in text
        and "Recorded sequence-match flag: True" in text
    )
    assert "No experimental equivalence" in text
    assert "coverage" not in model.cells["value"].value["qualifiers"]
    source = model.explain().items()[0].open()
    assert source.native_payload["source"]["name"] == "AlphaFold DB"
    assert source.back().back() is model.back()
    assert len(explorer.view("structures").items()) == 7


def test_sites_keep_annotation_fields_and_aggregate_contact_statements_separate(card):
    view = card.explore().answer("retained_sites")
    fields = [item for item in view.items() if item.kind == "field"]
    contacts = [item for item in view.items() if item.kind == "contact_relationship"]
    assert {item.label for item in fields} == {
        "Active sites",
        "Binding sites",
        "Family-model sites",
    }
    assert len(contacts) == 8
    ligand = next(
        item
        for item in contacts
        if item.open().native_payload["object_ref"] == "pdb.ligand:BTS"
    )
    assert "numbering: uniprot" in repr(ligand.back())
    assert ligand.open().native_payload["qualifiers"]["residues"][0]["observed_in"]
    assert "Aggregated contacts are not ligand instances" in repr(view)
    assert "no site overlap" in repr(view)
    assert len(view.items()) == 11 and "showing 10" in repr(view)
    assert ligand.explain().items()[0].label.startswith("Relationship support")
    assert ligand.related().back().back() is view


def test_foreign_subjects_never_enter_model_or_contact_panels(card):
    for predicate in ("has_predicted_structure", "has_ligand_site"):
        row = deepcopy(card.relationships(predicate)[0])
        row["id"] += "_SYNTHETIC_FOREIGN"
        row["subject_ref"] = "uniprot:P60174"
        card.relationship_store.add(row)
    explorer = card.explore()
    assert len(explorer.view("predicted_structures").items()) == 1
    assert len(explorer.view("sites").items()) == 11


@pytest.mark.parametrize("mode", ["missing", "conflicting", "wrong"])
def test_unknown_identity_is_not_an_empty_source_result(card, mode):
    if mode == "missing":
        card.meta.pop("card_id")
    elif mode == "wrong":
        card.get("identifiers.uniprot")["value"] = "P60174"
    else:
        card.quality["conflicts"] = [
            {"field": "identifiers.uniprot", "values": ["P52270", "P60174"]}
        ]
    view = card.explore().view("predicted_structures")
    assert view.outcome["status"] == "missing_prerequisite" and not view.items()
    assert view.native_payload["field_gaps"][0]["state"] == "missing_prerequisite"


@pytest.mark.parametrize("topic", ["sequence", "predicted_structures", "sites"])
def test_other_natures_do_not_get_protein_science(topic):
    view = Card(meta={"entity_type": "small_molecule"}).explore().view(topic)
    assert view.outcome["status"] == "not_applicable" and not view.items()


def test_original_axes_modifiers_and_literal_feature_keys_are_preserved(card):
    data = deepcopy(card.get("features_positional.active_site"))
    axis = data["value"][0]["location"]["sequence"]
    axis["sequence_id"] = "UniProt:synthetic-other-isoform"
    axis["start_modifier"] = "LESS_THAN"
    axis.pop("indexing")
    card.sections["features_positional"]["annotation.with.dot"] = data
    view = card.explore().view("sequence")
    item = next(row for row in view.items() if "annotation.with.dot" in row.label)
    text = repr(view)
    assert "synthetic-other-isoform" in text or "synthetic-other-isoform" in repr(
        item.open()
    )
    assert "LESS_THAN" in repr(pick(item.open(), "Annotations").open())
    assert "indexing not stated" in repr(pick(item.open(), "Annotations").open())
    assert item.payload_location["segments"][-1]["value"] == "annotation.with.dot"


@pytest.mark.parametrize(
    "topic,question",
    [
        ("sequence", "sequence_annotations"),
        ("predicted_structures", "predicted_models"),
        ("sites", "retained_sites"),
    ],
)
def test_new_panels_save_and_reopen_inertly_with_exact_original_requests(
    card, topic, question, tmp_path, monkeypatch
):
    view = card.explore().answer(question)
    path = tmp_path / "original.json"
    receipt = view.save(path)
    original = path.read_bytes()
    expected_labels = [item.label for item in view.items()]
    card.sections.clear()
    monkeypatch.setattr(Card, "from_dict", forbidden)
    monkeypatch.setattr(
        importlib.import_module("sabueso.core.card_exploration_profiles"),
        "field_entries",
        forbidden,
    )
    saved = sabueso.read_exploration(path, expected_digest=receipt["bundle_digest"])
    assert saved.explorer.answer(question).view_ref == view.view_ref
    assert [item.label for item in saved.items()] == expected_labels
    assert saved.explorer.view(topic).outcome["status"] == "ok"
    assert saved.items()[0].explain().back() is saved
    assert path.read_bytes() == original


def test_saved_model_panel_rejects_lost_original_membership(card, tmp_path):
    view = card.explore().view("predicted_structures")
    bad = replace(view, _selected=(), _selection=replace(view._selection, _entries=()))
    with pytest.raises(StorageError, match="membership"):
        bad.save(tmp_path / "invalid.json")


@pytest.mark.parametrize("topic", ["sequence", "predicted_structures", "sites"])
def test_source_panels_reject_undeclared_scientific_options(card, topic):
    with pytest.raises(ArgumentError):
        card.explore().view(topic, options={"guess_numbering": True})


def test_independent_saved_reader_uses_no_live_card_or_scientific_reader(
    card, tmp_path
):
    view = card.explore().view("sites")
    path = tmp_path / "sites.json"
    view.save(path)
    script = """
import sys
from unittest.mock import patch
import sabueso
from sabueso.core.card import Card
def fail(*a,**k): raise AssertionError('No live interpretation or source query')
with patch.object(Card,'from_dict',fail),patch.object(Card,'ligand_sites',fail),patch.object(Card,'predicted_structures',fail),patch('socket.socket.connect',fail):
    saved=sabueso.read_exploration(sys.argv[1])
    assert len(saved.items())==11
    assert saved.explorer.view('sites').view_ref==saved.view_ref
    assert saved.items()[0].explain().back() is saved
"""
    subprocess.run([sys.executable, "-c", script, str(path)], check=True)


def test_untrusted_feature_text_is_escaped_bounded_and_still_complete(card):
    record = card.get("features_positional.active_site")["value"][0]
    record["description"] = "<script>source</script>" + "x" * 3000
    view = card.explore().view("sequence")
    text = view.table()._repr_html_()
    assert "<script>" not in text and "&lt;script&gt;" in text
    assert "x" * 3000 not in text
    assert (
        pick(view, "Active sites").cells["value"].value[0]["description"]
        == record["description"]
    )


def test_zero_metric_false_match_and_unknown_isoform_do_not_become_absence(card):
    rel = card.relationship_store.get(
        card.relationships("has_predicted_structure")[0]["id"]
    )
    rel["qualifiers"]["mean_plddt"] = 0.0
    rel["qualifiers"]["sequence_matches"] = False
    rel["qualifiers"]["isoform"] = "synthetic-isoform"
    view = card.explore().view("predicted_structures")
    assert "Source mean pLDDT: 0.0" in repr(view)
    assert "Recorded sequence-match flag: False" in repr(view)
    assert "synthetic-isoform" in repr(view)
    assert "coverage" not in view.items()[0].cells["value"].value["qualifiers"]


def test_model_band_preview_does_not_traverse_the_unshown_tail():
    from sabueso.core.card_protein_source_render import relationship

    class Bands(dict):
        def items(self):
            for index in range(4):
                yield str(index), index / 10
            raise AssertionError("A bounded preview must not visit unshown bands")

    bands = Bands({str(index): index / 10 for index in range(5)})
    text = relationship(
        "predicted_structures", {"qualifiers": {"plddt_fractions": bands}}
    )
    assert "0=0.0" in text and "3=0.3" in text and "5 bands" in text


def test_recorded_match_flag_is_not_attributed_to_the_original_alphafold_record(card):
    view = card.explore().view("predicted_structures")
    item = view.items()[0]
    source = item.explain().items()[0].open().native_payload
    assert "sequence_matches" not in source["asserted_value"]["model"]
    assert item.open().native_payload["qualifiers"]["sequence_matches"] is True
    assert "Recorded sequence-match flag: True" in repr(view)
    assert "not attributed as direct source claims" in repr(view)
    assert "Source sequence match" not in repr(view)
