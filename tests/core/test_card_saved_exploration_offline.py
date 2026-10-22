"""Portable captured reading; synthetic changes test integrity, not source claims."""

import json
import socket
from pathlib import Path

import pytest
import pyunitwizard as puw

import sabueso
from sabueso.core.card import Card
from sabueso.core.card_exploration import CardView
from sabueso.core.card_exploration_storage import _seal
from sabueso.core.errors import ArgumentError, StorageError
from sabueso.tools.card.disease import resolve_disease_card
from sabueso.tools.card.small_molecule import single_molecule_card
from sabueso.tools.db.chembl import FixtureChEMBLClient
from sabueso.tools.db.mondo import FixtureMONDOClient


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Saved exploration must not acquire source data")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


@pytest.fixture
def molecule():
    return single_molecule_card(
        chembl=FixtureChEMBLClient("temp_data").molecules(["CHEMBL110"])
    )


@pytest.fixture
def disease():
    return resolve_disease_card(
        "MONDO:0014221", mondo_client=FixtureMONDOClient("temp_data")
    )[0]


def custom():
    card = Card()
    card.unknown_stored["synthetic"] = {
        "a.b": [False, 0, None, "", "α🧬"],
        "long": "x" * 20000,
    }
    return card


def child(view, label):
    return next(item for item in view.items() if item.label == label)


def reopen(view, tmp_path):
    path = tmp_path / "exploration.json"
    receipt = view.save(path)
    result = sabueso.read_exploration(path, expected_digest=receipt["bundle_digest"])
    assert isinstance(result, CardView)
    assert result.explorer is None or result.explorer.mode == "saved"
    assert result.view_ref == view.view_ref
    return result, path, receipt


def test_literal_root_complete_values_mutation_and_saved_mode(tmp_path):
    card = custom()
    original = card.to_dict()
    view = card.explore().inspect()
    saved, path, receipt = reopen(view, tmp_path)
    card.unknown_stored.clear()
    assert saved.native_payload == original
    assert saved.context["mode"] == "saved"
    assert saved.explorer.access.context["mode"] == "saved"
    assert child(saved, "synthetic").open().native_payload == original["synthetic"]
    assert saved.back() is saved and saved.at_root
    assert (
        saved.explorer.access.export_card(tmp_path / "card.json")["snapshot_id"]
        == saved.context["snapshot_id"]
    )
    assert json.loads((tmp_path / "card.json").read_text(encoding="utf-8")) == original
    assert path.exists() and receipt["bundle_digest"].startswith("sha256:")


def test_filtered_ordered_view_preserves_full_result_hidden_items_and_trail(tmp_path):
    explorer = custom().explore()
    full = child(explorer.inspect(), "synthetic").open()
    sorted_view = full.sort("label", descending=True)
    selected = sorted_view.filter("label", equals="a.b").table()
    saved, _, _ = reopen(selected, tmp_path)
    assert len(saved.items()) == 1
    assert saved.native_payload == full.native_payload
    assert [i.label for i in saved.back().back().items()] == ["long", "a.b"]
    assert saved.back().back().back().native_payload == full.native_payload
    hidden = saved.item(child(full, "long").item_ref)
    assert not hidden.is_selected and hidden.open().native_payload == "x" * 20000
    assert saved.sort("label").back() is saved
    assert "<table>" in saved._repr_html_()


def test_public_molecule_properties_units_original_sources_and_question(
    tmp_path, molecule
):
    explorer = molecule.explore()
    properties = explorer.answer("property_context")
    weight = properties.filter("label", equals="Molecular weight")
    saved, _, _ = reopen(weight, tmp_path)
    mass = saved.items()[0]
    assert puw.get_value(mass.cells["value"].value, to_unit="dalton") == 260.25
    assert mass.open().native_payload["unit"] == "dalton"
    with puw.context(standard_units=["nm", "ps", "K", "mole", "gram"]):
        assert puw.get_value(mass.cells["value"].value, to_unit="dalton") == 260.25
    support = mass.explain()
    assert support.back() is saved
    assert support.items()[0].open().native_payload["asserted_value"] == "260.25"
    assert saved.explorer.answer("property_context").request == properties.request
    assert saved.explorer.answer("property_context").result_ref == properties.result_ref
    assert (
        saved.explorer.answer("property_context").native_payload
        == properties.native_payload
    )
    assert saved.explorer.view("properties").result_ref == properties.result_ref
    assert saved.explorer.view("chemistry").outcome["status"] == "not_saved"
    assert "260.25 dalton" in repr(saved)


def test_public_disease_hierarchy_retained_parent_card_links_and_back(
    tmp_path, disease
):
    parent = resolve_disease_card(
        "MONDO:0003689", mondo_client=FixtureMONDOClient("temp_data")
    )[0]
    explorer = disease.explore(related_cards=[parent])
    selected = explorer.view("classification").filter(
        "object_ref", equals="mondo:MONDO:0003689"
    )
    links = selected.items()[0].related()
    target = links.filter("role", equals="object")
    destination = target.items()[0].open()
    saved, _, _ = reopen(destination, tmp_path)
    assert saved.explorer.profile == "disease"
    assert saved.context["card_ref"] == parent.pinned_ref()
    assert saved.back().back().back().back().native_payload == selected.native_payload
    assert saved.back().items()[0].open().context == saved.context
    restored_parent = saved.back().back().back().back()
    assert restored_parent.items()[0].explain().items()
    assert saved.explorer.view("coverage").outcome["status"] == "not_saved"


def test_missing_context_keeps_null_focal_identity_after_read(tmp_path, disease):
    selected = disease.explore().view("classification")
    target = selected.items()[0].related().filter("role", equals="object")
    missing = target.items()[0].open()
    saved, _, _ = reopen(missing, tmp_path)
    assert saved.explorer is None and saved.context["card_ref"] is None
    assert saved.context["snapshot_id"] is None
    assert saved.outcome["status"] == "context_not_supplied"
    assert saved.back().schema["kind"] == "link"
    assert saved.items()[0].open().explorer is None


def test_new_interpretation_is_explicit_and_does_not_serialize_caller_cards(
    tmp_path, molecule, monkeypatch
):
    saved, _, _ = reopen(molecule.explore().view("properties"), tmp_path)
    original = saved.native_payload

    def forbidden(*args, **kwargs):
        pytest.fail("Starting a new interpretation must not recapture caller Cards")

    monkeypatch.setattr(Card, "to_dict", forbidden)
    live = saved.explorer.start_new()
    assert live.mode == "live"
    assert live.context["snapshot_id"] == saved.context["snapshot_id"]
    assert live.view("properties").outcome["status"] == "ok"
    assert saved.native_payload == original and saved.explorer.mode == "saved"


def test_inert_reading_forbids_scientific_readers_and_live_join(
    tmp_path, molecule, monkeypatch
):
    view = molecule.explore().view("properties")
    path = tmp_path / "saved.json"
    receipt = view.save(path)

    def forbidden(*args, **kwargs):
        pytest.fail("Saved reading must not execute scientific readers or live joins")

    monkeypatch.setattr("sabueso.core.card_scientific_access.materialize", forbidden)
    monkeypatch.setattr("sabueso.core.knowledge_state.knowledge_state", forbidden)
    monkeypatch.setattr(
        "sabueso.core.card_context_navigation._resolve_target", forbidden
    )
    saved = sabueso.read_exploration(path, expected_digest=receipt["bundle_digest"])
    repr(saved)
    saved._repr_html_()
    saved.items()[0].open()
    saved.items()[0].explain()
    saved.items()[0].related()
    assert saved.explorer.view("coverage").outcome["status"] == "not_saved"
    assert saved.explorer.view("structures").outcome["status"] == "not_saved"
    assert (
        saved.explorer.access.select("structures").page()["outcome"]["status"]
        == "not_saved"
    )


def test_machine_selection_reopens_exact_request_and_issues_fresh_cursors(tmp_path):
    access = custom().access()
    selection = access.read(access.root_location)
    old = selection.page(limit=1)["page"]["next_cursor"]
    path = tmp_path / "machine.json"
    receipt = selection.save(path)
    saved = sabueso.read_exploration(path, expected_digest=receipt["bundle_digest"])
    exact = saved.explorer.access.selection(selection.selection_ref)
    assert (
        exact.selection_ref == selection.selection_ref
        and exact.result_ref == selection.result_ref
    )
    assert exact.page(limit=1)["context"]["mode"] == "saved"
    with pytest.raises(ArgumentError):
        exact.page(limit=1, cursor=old)
    first = exact.page(limit=1)
    second = exact.page(limit=1, cursor=first["page"]["next_cursor"])
    assert second["page"]["offset"] == 1


@pytest.mark.parametrize("topic", ["structures", "coverage"])
def test_unavailable_historical_validation_preserves_destination(
    tmp_path, topic, monkeypatch
):
    protein = Card.from_dict(
        json.loads(
            Path("temp_data/frozen_cards/schema_0.3.9__P52270.json").read_text(
                encoding="utf-8"
            )
        )
    )
    view = protein.explore().view(topic)
    assert view.capabilities["save"] is True
    from sabueso.core import card_exploration_science

    def unavailable(*args, **kwargs):
        raise StorageError("Required historical verifier is unavailable.")

    monkeypatch.setattr(card_exploration_science, "_verify_objects", unavailable)
    path = tmp_path / "keep.json"
    path.write_text("original", encoding="utf-8")
    with pytest.raises(StorageError, match="historical verifier"):
        view.save(path, overwrite=True)
    assert path.read_text(encoding="utf-8") == "original"


def test_atomic_no_clobber_overwrite_and_read_validation_failure(tmp_path):
    view = custom().explore().inspect()
    path = tmp_path / "saved.json"
    first = view.save(path)
    original = path.read_bytes()
    with pytest.raises(StorageError):
        view.save(path)
    assert path.read_bytes() == original
    second = view.save(path, overwrite=True)
    assert first["root_view_ref"] == second["root_view_ref"]
    assert not list(tmp_path.glob(".sabueso-exploration-*"))


def mutate(path, function):
    data = json.loads(path.read_text(encoding="utf-8"))
    function(data)
    path.write_text(json.dumps(_seal(data)), encoding="utf-8")


@pytest.mark.parametrize(
    "part", ["value", "state", "support", "entry", "membership", "verifier", "input"]
)
def test_coherently_rehashed_changes_fail_against_original_bindings(
    tmp_path, molecule, part
):
    _, path, _ = reopen(molecule.explore().view("properties"), tmp_path)

    def change(data):
        root = data["views"][data["root_navigation_ref"]]
        rows = root["state"]["items"]
        row = next(row for row in rows.values() if row["label"] == "Molecular weight")
        if part == "value":
            row["cells"]["value"]["value"] = 999
            row["cells"]["value"]["encoding"] = "json"
        elif part == "state":
            row["cells"]["value"]["state"] = "unknown"
        elif part == "support":
            row["cells"]["value"]["support"] = []
        elif part == "entry":
            root["selection"]["entries"][0]["value"] = {"value": "forged"}
        elif part == "membership":
            root["selected"] = root["selected"][:1]
        elif part == "verifier":
            data["producer"]["verifier"] = "unknown_verifier@999"
        else:
            first = next(iter(data["cards"].values()))
            first["data"]["sections"]["names"]["canonical_name"]["value"] = "forged"

    mutate(path, change)
    with pytest.raises(StorageError):
        sabueso.read_exploration(path)


def test_digest_pin_missing_member_and_duplicate_json_are_refused(tmp_path):
    _, path, receipt = reopen(custom().explore().inspect(), tmp_path)
    original = path.read_text(encoding="utf-8")
    with pytest.raises(StorageError):
        sabueso.read_exploration(path, expected_digest="sha256:" + "0" * 64)
    path.write_text('{"format":"one","format":"two"}', encoding="utf-8")
    with pytest.raises(StorageError, match="Duplicate"):
        sabueso.read_exploration(path)
    path.write_text(original, encoding="utf-8")
    mutate(path, lambda data: data["views"].pop(data["root_navigation_ref"]))
    with pytest.raises(StorageError):
        sabueso.read_exploration(path, expected_digest=receipt["bundle_digest"])


@pytest.mark.parametrize("skip", [False, True])
def test_argument_guards_remain_active(tmp_path, skip):
    view = custom().explore().inspect()
    with pytest.raises(ArgumentError):
        view.save(tmp_path / "bad.json", overwrite=1, skip_digestion=skip)
    with pytest.raises(ArgumentError):
        sabueso.read_exploration(
            tmp_path / "bad.json", expected_digest="bad", skip_digestion=skip
        )
    with pytest.raises(StorageError):
        sabueso.read_exploration(tmp_path / "missing.json", skip_digestion=skip)


def test_reopened_destination_explorer_keeps_its_transition_origin(tmp_path, disease):
    parent = resolve_disease_card(
        "MONDO:0003689", mondo_client=FixtureMONDOClient("temp_data")
    )[0]
    explorer = disease.explore(related_cards=[parent])
    selection = explorer.view("classification").filter(
        "object_ref", equals="mondo:MONDO:0003689"
    )
    target = selection.items()[0].related().filter("role", equals="object")
    destination = target.items()[0].open()
    definition = destination.explorer.view("definition")
    saved, _, _ = reopen(definition, tmp_path)
    again = saved.explorer.view("definition")
    assert again.back().view_ref == target.view_ref
    assert saved.explorer.view("coverage").back().view_ref == target.view_ref


def test_missing_context_child_and_repeated_save_remain_portable(tmp_path, disease):
    missing = (
        disease.explore()
        .view("classification")
        .items()[0]
        .related()
        .filter("role", equals="object")
        .items()[0]
        .open()
    )
    detail = child(missing, "subject_ref").open()
    saved, _, _ = reopen(detail, tmp_path)
    assert saved.explorer is None and saved.native_payload == detail.native_payload
    destination = tmp_path / "again.json"
    receipt = saved.save(destination)
    again = sabueso.read_exploration(
        destination, expected_digest=receipt["bundle_digest"]
    )
    assert again.native_payload == detail.native_payload and again.explorer is None


def test_empty_filter_and_literal_search_survive(tmp_path):
    explorer = custom().explore()
    matches = explorer.search("α🧬")
    saved, _, _ = reopen(matches, tmp_path)
    assert [i.payload_location for i in saved.items()] == [
        i.payload_location for i in matches.items()
    ]
    empty = saved.filter("label", equals="none")
    receipt = empty.save(tmp_path / "empty.json")
    loaded = sabueso.read_exploration(
        tmp_path / "empty.json", expected_digest=receipt["bundle_digest"]
    )
    assert len(loaded.items()) == 0 and loaded.outcome["status"] == "empty"
    assert loaded.back().view_ref == saved.view_ref


def test_independent_process_reader_with_scientific_engines_forbidden(
    tmp_path, molecule
):
    import os
    import subprocess
    import sys

    _, path, receipt = reopen(molecule.explore().view("properties"), tmp_path)
    script = """
import socket, sys
import sabueso
import pyunitwizard as puw
from sabueso.core.card import Card
import sabueso.core.card_scientific_access as scientific
import sabueso.core.card_context_navigation as navigation

def forbidden(*args, **kwargs):
    raise AssertionError("No acquisition, Card reconstruction or scientific reader")
socket.create_connection = forbidden
socket.socket.connect = forbidden
Card.from_dict = forbidden
Card.knowledge_state = forbidden
Card.structures = forbidden
scientific.materialize = forbidden
navigation._resolve_target = forbidden
view = sabueso.read_exploration(sys.argv[1], expected_digest=sys.argv[2])
assert view.explorer.mode == "saved"
weight = view.filter("label", equals="Molecular weight").items()[0]
assert puw.get_value(weight.cells["value"].value, to_unit="dalton") == 260.25
assert weight.explain().items()[0].open().native_payload["asserted_value"] == "260.25"
assert view.explorer.view("coverage").outcome["status"] == "not_saved"
assert view.explorer.start_new().mode == "live"
print("PASS independent inert reader")
"""
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, "-c", script, str(path), receipt["bundle_digest"]],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS independent inert reader" in result.stdout


def test_literal_scientific_projection_retains_verifiable_original_context(tmp_path):
    protein = Card.from_dict(
        json.loads(
            Path("temp_data/frozen_cards/schema_0.3.9__P52270.json").read_text(
                encoding="utf-8"
            )
        )
    )
    explorer = protein.explore()
    structures = explorer.view("structures")
    literal_science = explorer.access.read(structures.items()[0].payload_location)
    assert literal_science.capabilities["save"] is True
    literal_science.save(tmp_path / "projection.json")
    projection = sabueso.read_exploration(tmp_path / "projection.json")
    assert projection.validation["verifier"] == "scientific_exploration_binding@1"
    explorer.view("coverage").items()[0].explain()
    # Actually materialized scientific variants retain their historical checks;
    # literal projection never drops their original input/support context.
    supported = explorer.view("function")
    saved, path, _ = reopen(supported, tmp_path)
    objects = json.loads(path.read_text(encoding="utf-8"))["objects"]
    assert any(
        value.get("adapter") == "knowledge_coverage_exploration@1"
        for value in objects.values()
        if isinstance(value, dict)
    )
    assert saved.explorer.view("structures").outcome["status"] == "ok"


@pytest.mark.parametrize(
    "mutation", ["result_ref", "selection_ref", "literal_membership"]
)
def test_rehashed_literal_request_identity_and_membership_are_verified(
    tmp_path, mutation
):
    _, path, _ = reopen(custom().explore().inspect(), tmp_path)

    def change(data):
        root = data["views"][data["root_navigation_ref"]]
        if mutation == "literal_membership":
            root["selection"]["entries"] = []
            root["state"]["items"] = {}
            root["selected"] = []
        else:
            root["selection"][mutation] = (
                "XR_" if mutation == "result_ref" else "XA_"
            ) + "0" * 64

    mutate(path, change)
    with pytest.raises(StorageError):
        sabueso.read_exploration(path)


def test_required_explanation_closure_cannot_be_downgraded(tmp_path, molecule):
    _, path, _ = reopen(molecule.explore().view("properties"), tmp_path)

    def change(data):
        root = data["views"][data["root_navigation_ref"]]
        item = root["selected"][0]
        binding = json.dumps(
            [root["focal"], item], ensure_ascii=False, separators=(",", ":")
        )
        data["navigation"]["explanations"].pop(binding)

    mutate(path, change)
    with pytest.raises(StorageError, match="closure"):
        sabueso.read_exploration(path)


def test_optional_presentation_metadata_and_machine_resave(tmp_path):
    access = custom().access()
    selection = access.read(access.root_location)
    path = tmp_path / "first.json"
    selection.save(path)
    mutate(
        path,
        lambda data: data["presentation_metadata"].update(
            {"future_optional": {"label": "kept"}}
        ),
    )
    saved = sabueso.read_exploration(path)
    exact = saved.explorer.access.selection(selection.selection_ref)
    second = tmp_path / "second.json"
    receipt = exact.save(second)
    loaded = sabueso.read_exploration(second, expected_digest=receipt["bundle_digest"])
    assert loaded._machine_ref == selection.selection_ref
    assert json.loads(second.read_text(encoding="utf-8"))["presentation_metadata"] == {
        "future_optional": {"label": "kept"}
    }


def test_empty_missing_and_null_field_values_are_not_reinterpreted(tmp_path):
    card = Card(
        sections={
            "names": {"canonical_name": {"value": None, "source_assertion_ids": []}}
        }
    )
    view = child(card.explore().inspect(), "Knowledge").open()
    saved, _, _ = reopen(view, tmp_path)
    assert child(saved, "names").open().native_payload == card.sections["names"]
    raw = saved.explorer.inspect("names").items()[0]
    assert raw.cells["value"].value == {"value": None, "source_assertion_ids": []}


def test_explicit_validation_scope_is_readonly_and_new_interpretation_is_separate(
    tmp_path,
):
    saved, _, _ = reopen(custom().explore().inspect(), tmp_path)
    report = saved.validation
    assert report["integrity"] == "verified" and report["independent_expected_digest"]
    assert report["scientific_classifications"] == "not_supported_by_this_saved_slice"
    report.clear()
    assert saved.validation
    assert saved.explorer.start_new().inspect().validation is None


def test_ambiguous_public_parent_snapshots_stay_explicit_after_read(tmp_path, disease):
    parent = resolve_disease_card(
        "MONDO:0003689", mondo_client=FixtureMONDOClient("temp_data")
    )[0]
    variant = Card.from_dict(parent.to_dict())
    variant.unknown_stored["synthetic_navigation_revision"] = True
    explorer = disease.explore(related_cards=[variant, parent, parent])
    edge = (
        explorer.view("classification")
        .filter("object_ref", equals="mondo:MONDO:0003689")
        .items()[0]
    )
    choices = edge.related().filter("role", equals="object").items()[0].open()
    saved, _, _ = reopen(choices, tmp_path)
    assert saved.outcome["status"] == "ambiguous"
    assert len(saved.items()) == 2
    assert {item.open().context["card_ref"] for item in saved.items()} == {
        parent.pinned_ref(),
        variant.pinned_ref(),
    }
    assert len(saved.context["inputs"]) == 4 and len(saved.context["captures"]) == 3


@pytest.mark.parametrize("alter", ["target", "drop", "owner"])
def test_rehashed_navigation_target_membership_and_node_owner_fail(
    tmp_path, disease, alter
):
    view = disease.explore().view("classification").items()[0].related()
    _, path, _ = reopen(view, tmp_path)

    def change(data):
        root = data["views"][data["root_navigation_ref"]]
        if alter == "owner":
            root["selection"]["target"]["owner"] = {"result_ref": "XR_" + "0" * 64}
        else:
            entry = next(
                entry
                for entry in root["selection"]["entries"]
                if entry["value"]["role"] == "object"
            )
            if alter == "target":
                entry["value"]["target_ref"] = "mondo:synthetic-forged"
            else:
                root["selection"]["entries"].remove(entry)

    mutate(path, change)
    with pytest.raises(StorageError):
        sabueso.read_exploration(path)


def test_new_literal_nodes_do_not_promise_unretained_explanations_or_save(tmp_path):
    saved, _, _ = reopen(custom().explore().inspect(), tmp_path)
    cold = child(child(saved, "synthetic").open(), "a.b").open()
    assert cold.native_payload == [False, 0, None, "", "α🧬"]
    assert cold.capabilities["explain"] is False
    assert cold.capabilities["save"] is False
    assert cold.items()[0].explain().outcome["status"] == "not_saved"
    with pytest.raises(StorageError):
        cold.save(tmp_path / "no-closure.json")


def test_machine_unicode_slice_is_exact_after_save(tmp_path):
    access = custom().access()
    root = access.read(access.root_location)
    synthetic = next(
        item for item in root.page()["items"] if item["key"] == "synthetic"
    )
    long_text = next(
        item
        for item in access.read(synthetic["location"]).page()["items"]
        if item["key"] == "long"
    )
    selection = access.read(long_text["location"], text_slice={"start": 10, "stop": 20})
    path = tmp_path / "slice.json"
    receipt = selection.save(path)
    restored = sabueso.read_exploration(path, expected_digest=receipt["bundle_digest"])
    exact = restored.explorer.access.selection(selection.selection_ref)
    assert exact.page()["items"][0]["value"] == "x" * 10


@pytest.mark.parametrize("change", ["value", "unit", "field"])
def test_valid_resealed_provider_quantity_cannot_change_source_binding(
    tmp_path, molecule, change
):
    from pyunitwizard import QuantityRecord

    _, path, _ = reopen(molecule.explore().view("properties"), tmp_path)

    def alter(data):
        root = data["views"][data["root_navigation_ref"]]
        row = next(
            row
            for row in root["state"]["items"].values()
            if row["label"] == "Molecular weight"
        )
        cell = row["cells"]["value"]
        unit = "nanometer" if change == "unit" else "dalton"
        field = (
            "properties.physchem.synthetic_wrong_field"
            if change == "field"
            else cell["field"]
        )
        value = 999.0 if change == "value" else 260.25
        cell["value"] = QuantityRecord.from_quantity(
            puw.quantity(value, unit), field=field, unit=unit
        ).to_dict()
        cell["unit"], cell["field"] = unit, field

    mutate(path, alter)
    with pytest.raises(StorageError):
        sabueso.read_exploration(path)


def test_unknown_required_adapter_is_not_treated_as_optional_metadata(tmp_path):
    _, path, _ = reopen(custom().explore().inspect(), tmp_path)

    def change(data):
        root = data["views"][data["root_navigation_ref"]]
        root["state"]["context"]["adapter"] = "unknown_adapter@999"

    mutate(path, change)
    with pytest.raises(StorageError, match="adapter"):
        sabueso.read_exploration(path)


@pytest.mark.parametrize("part", ["key", "ordinal"])
def test_rehashed_literal_keys_and_ordinals_are_bound_to_original_locations(
    tmp_path, part
):
    _, path, _ = reopen(custom().explore().inspect(), tmp_path)

    def change(data):
        root = data["views"][data["root_navigation_ref"]]
        root["selection"]["entries"][0][part] = (
            999 if part == "ordinal" else "forged-key"
        )

    mutate(path, change)
    with pytest.raises(StorageError):
        sabueso.read_exploration(path)
