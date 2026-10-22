"""Saved original science over public inputs; altered cases are synthetic."""

import gzip
import hashlib
import importlib
import json
import socket
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
import pyunitwizard as puw

import sabueso
from sabueso.core.card import Card
from sabueso.core.card_exploration_science import _result_ref, _verify_objects
from sabueso.core.card_exploration_storage import _seal
from sabueso.core.errors import ArgumentError, StorageError

PUBLIC = Path("temp_data/frozen_cards/schema_0.3.9__P52270.json")


def forbidden(*args, **kwargs):
    raise AssertionError("Current scientific readers/source requests are forbidden")


@pytest.fixture(autouse=True)
def no_queries(monkeypatch):
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


@pytest.fixture
def card():
    return Card.from_dict(json.loads(PUBLIC.read_text(encoding="utf-8")))


@pytest.fixture(scope="module")
def bundles(tmp_path_factory):
    folder = tmp_path_factory.mktemp("original-science")
    result = {}
    for topic in ("structures", "coverage"):
        card = Card.from_dict(json.loads(PUBLIC.read_text(encoding="utf-8")))
        view = card.explore().view(topic)
        path = folder / f"{topic}.json"
        view.save(path)
        result[topic] = json.loads(path.read_text(encoding="utf-8"))
    return result


def read_bundle(bundle, tmp_path):
    path = tmp_path / "reading.json"
    path.write_text(json.dumps(_seal(deepcopy(bundle))), encoding="utf-8")
    return sabueso.read_exploration(path)


@pytest.mark.parametrize("topic", ["structures", "coverage"])
def test_public_original_results_and_saved_topic_closure(bundles, topic, tmp_path):
    view = read_bundle(bundles[topic], tmp_path)
    assert view.explorer.mode == "saved"
    assert view.validation["verifier"] == "scientific_exploration_binding@1"
    assert topic in view.explorer.capabilities["scientific_topics"]
    assert view.explorer.view(topic).result_ref == view.result_ref
    assert len(view.items()) == (7 if topic == "structures" else 93)
    assert view.capabilities["save"]
    for item in view.items():
        assert item.explain().back() is view
    path = tmp_path / "again.json"
    view.save(path)
    again = sabueso.read_exploration(path)
    assert again.view_ref == view.view_ref
    assert (
        again.validation["scientific_classifications"]
        == view.validation["scientific_classifications"]
    )


def test_structural_selection_quantity_detail_sources_and_return(card, tmp_path):
    full = card.explore().view("structures")
    selected = (
        full.sort("resolution", unit="angstrom")
        .filter("structure_ref", equals="pdb:1SUX")
        .table()
    )
    path = tmp_path / "structures.json"
    selected.save(path)
    card.sections.clear()
    saved = sabueso.read_exploration(path)
    assert saved.view_ref == selected.view_ref
    assert len(saved.items()) == 1
    assert len(saved.native_payload["items"]) == 7
    item = saved.items()[0]
    assert puw.get_value(item.cells["resolution"].value, to_unit="angstrom") == 2.0
    detail = item.open()
    assert detail.back() is saved
    assert detail.native_payload["relationship_id"] == item._entry.key
    assert puw.get_value(detail.native_payload["resolution"], to_unit="angstrom") == 2.0
    source = item.explain()
    assert source.back() is saved
    assert source.native_payload["rule"]["rule"] == "structure_inventory_explanation@1"
    assert source.native_payload["card_ref"] == saved.context["card_ref"]
    assert any(i.cells["role"].value == "source" for i in item.related().items())
    detail.save(tmp_path / "detail.json")
    restored_detail = sabueso.read_exploration(tmp_path / "detail.json")
    assert restored_detail.presentation == "detail"
    assert restored_detail.back().view_ref == saved.view_ref


def test_machine_original_projection_pages_and_missing_variants(card, tmp_path):
    selection = card.access().select(
        "structures", fields=["structure_ref", "resolution"]
    )
    first = selection.page(limit=1)
    path = tmp_path / "machine.json"
    selection.save(path)
    saved = sabueso.read_exploration(path)
    access = saved.explorer.access
    restored = access.selection(selection.selection_ref)
    assert (
        access.select("structures", fields=["structure_ref", "resolution"]) is restored
    )
    assert restored.page(limit=1)["context"]["mode"] == "saved"
    assert restored.page(limit=1)["selection_ref"] == first["selection_ref"]
    with pytest.raises(ArgumentError):
        restored.page(cursor=first["page"]["next_cursor"])
    assert (
        access.select("structures", fields=["method"]).page()["outcome"]["status"]
        == "not_saved"
    )
    assert (
        access.select("structures", options={"region": [1, 2]}).page()["outcome"][
            "status"
        ]
        == "not_saved"
    )
    assert "structures" in access.capabilities["scientific_topics"]


def test_region_original_request_and_exact_retained_lookup(card, tmp_path):
    options = {"sequence_ref": "uniprot:P52270", "region": [10, 11, 12]}
    view = card.explore().answer("region_coverage", options=options)
    path = tmp_path / "region.json"
    view.save(path)
    saved = sabueso.read_exploration(path)
    assert saved.request == view.request
    assert (
        saved.explorer.answer("region_coverage", options=options).result_ref
        == saved.result_ref
    )
    assert (
        saved.explorer.answer(
            "region_coverage", options={**options, "region": [20]}
        ).outcome["status"]
        == "not_saved"
    )
    assert saved.explorer.view("structures").outcome["status"] == "not_saved"
    assert (
        saved.items()[0].open().native_payload["missing_in_region"]
        == view.items()[0].open().native_payload["missing_in_region"]
    )


@pytest.mark.parametrize(
    "options,status",
    [
        ({}, "missing_prerequisite"),
        (
            {"sequence_ref": "uniprot:synthetic-unsupported", "region": [1]},
            "unsupported",
        ),
    ],
)
def test_saved_region_prerequisites_remain_explicit(card, tmp_path, options, status):
    view = card.explore().answer("region_coverage", options=options)
    assert view.outcome["status"] == status
    path = tmp_path / "missing-scope.json"
    view.save(path)
    saved = sabueso.read_exploration(path)
    assert saved.outcome == view.outcome
    assert saved.request == view.request
    assert (
        saved.explorer.answer("region_coverage", options=options).outcome
        == view.outcome
    )
    assert not saved.items()


def test_resolution_filter_and_nondefault_quantity_policy_survive(card, tmp_path):
    with puw.context(standard_units=["nm", "ps", "K", "mole", "gram"]):
        root = card.explore().view("structures")
        view = root.filter("resolution", equals=puw.quantity(0.2, "nanometer")).sort(
            "resolution", unit="nanometer"
        )
        path = tmp_path / "physical-filter.json"
        view.save(path)
        saved = sabueso.read_exploration(path)
        assert [item.item_ref for item in saved.items()] == [
            item.item_ref for item in view.items()
        ]
        assert all(
            puw.get_value(item.cells["resolution"].value, to_unit="angstrom") == 2.0
            for item in saved.items()
        )
        assert saved.filter("resolution", equals=puw.quantity(2, "angstrom")).items()


def test_original_literal_v1_bytes_remain_readable():
    path = Path("tests/core/data/card_exploration_literal_v1.json")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == "6e5ffae0e24884c05805e772d221f78955926a60c4898622146790f09932ccb5"
    saved = sabueso.read_exploration(path)
    assert saved.validation["verifier"] == "literal_exploration_binding@1"
    assert saved.native_payload is False


@pytest.mark.parametrize("topic", ["structures", "coverage"])
def test_frozen_scientific_producer_bytes_read_without_live_rules(
    topic, tmp_path, monkeypatch
):
    data = Path("tests/core/data/card_exploration_science_v2.json.gz").read_bytes()
    assert (
        hashlib.sha256(data).hexdigest()
        == "5e8e83fd2defd8ad1d67df683518f7922e45ce0f9c9afa89c1528d8cc352a443"
    )
    original = gzip.decompress(data)
    assert (
        hashlib.sha256(original).hexdigest()
        == "b0a15a369938c5ba663835f15d2075a21c8b6f86355d25e8be0dcca2bea7c1a4"
    )
    path = tmp_path / "original-scientific-reading.json"
    path.write_bytes(original)
    monkeypatch.setattr(Card, "from_dict", forbidden)
    monkeypatch.setattr(
        importlib.import_module("sabueso.core.card_scientific_access"),
        "materialize",
        forbidden,
    )
    monkeypatch.setattr(
        importlib.import_module("sabueso.core.knowledge_state"),
        "knowledge_state",
        forbidden,
    )
    saved = sabueso.read_exploration(path).explorer.view(topic)
    assert len(saved.items()) == (7 if topic == "structures" else 93)
    assert saved.native_payload["rule"]["sabueso_version"] == "0.14.0+77.g5b20ffa"
    assert {"knowledge_state@5", "structure_inventory@1"} <= set(
        saved.validation["verified_scientific_rules"]
    )
    assert saved.items()[0].explain().back() is saved


def test_generic_extension_scientific_lookalikes_stay_literal(tmp_path, monkeypatch):
    from sabueso.core import card_exploration_adapter_v1

    card = Card()
    card.unknown_stored.update(
        question="region_coverage",
        options="arbitrary literal text",
        rule={"rule": "knowledge_state@5"},
    )
    view = card.explore().inspect()
    monkeypatch.setattr(card_exploration_adapter_v1, "_v1_region_request", forbidden)
    path = tmp_path / "literal-lookalikes.json"
    view.save(path)
    saved = sabueso.read_exploration(path)
    assert saved.native_payload == view.native_payload
    assert saved.validation["verifier"] == "literal_exploration_binding@1"


@pytest.mark.parametrize("change", ["value", "field", "unit"])
def test_valid_resealed_resolution_keeps_original_field_and_source(
    bundles, change, tmp_path
):
    from pyunitwizard import QuantityRecord

    bundle = deepcopy(bundles["structures"])
    wire = bundle["objects"][next(iter(bundle["scientific_results"]))]
    row = next(row for row in wire["items"].values() if row["resolution"] is not None)
    field = (
        "synthetic.wrong_field"
        if change == "field"
        else "relationships.has_structure.resolution"
    )
    unit = "second" if change == "unit" else "angstrom"
    row["resolution"] = QuantityRecord.from_quantity(
        puw.quantity(999 if change == "value" else 2, unit), field=field, unit=unit
    ).to_dict()
    with pytest.raises(StorageError):
        read_bundle(bundle, tmp_path)


@pytest.mark.parametrize("change", ["state", "coverage", "membership", "exclusion"])
def test_historical_structure_decisions_reject_rebound_result(card, change):
    access = card.access()
    result = access.select("structures")._scientific
    wire = deepcopy(result.wire)
    row = wire["native_payload"]["items"][0]
    key = row["relationship_id"]
    if change == "state":
        row["state"]["sequence"] = wire["items"][key]["state"]["sequence"] = "mutant"
    elif change == "coverage":
        row["coverage"] = wire["items"][key]["coverage"] = 0.111
    elif change == "membership":
        wire["native_payload"]["items"].pop(0)
        for member in ("items", "support", "interpretations", "explanations"):
            wire[member].pop(key)
    else:
        wire["native_payload"]["excluded"] = {card.id: [row["structure_ref"]]}
    ref = _result_ref(access, wire)
    bundle = {
        "objects": {ref: wire},
        "scientific_results": {ref: {"focal": access._focal_key}},
    }
    with pytest.raises(StorageError, match="historical"):
        _verify_objects(bundle, {access._focal_key: access})


def test_scientific_result_stays_bound_to_focal_card_with_supplied_context(
    card, tmp_path
):
    related = Card.from_dict(
        json.loads(
            Path("temp_data/frozen_cards/schema_0.3.13__P60174.json").read_text(
                encoding="utf-8"
            )
        )
    )
    view = card.explore(related_cards=[related]).view("structures")
    path = tmp_path / "context.json"
    view.save(path)
    saved = sabueso.read_exploration(path)
    assert saved.context["card_ref"] == card.pinned_ref()
    assert saved.context["used_captures"] == [view._explorer.access._focal_key]
    subject = next(
        item
        for item in saved.items()[0].related().items()
        if item.cells["role"].value == "subject"
    )
    destination = subject.open()
    restored = destination.explorer.access.select("structures")
    assert restored.selection_ref == view._selection.selection_ref
    assert restored.page(limit=1)["context"]["card_ref"] == saved.context["card_ref"]
    bundle = json.loads(path.read_text(encoding="utf-8"))
    assert len(bundle["cards"]) == 2
    foreign = next(
        key
        for key, value in bundle["cards"].items()
        if value["card_ref"].startswith(related.id + "@")
    )
    next(iter(bundle["scientific_results"].values()))["focal"] = foreign
    with pytest.raises(StorageError):
        read_bundle(bundle, tmp_path)


def test_synthetic_exclusions_conflicts_and_missing_support_are_retained(
    card, tmp_path
):
    data = card.to_dict()
    rel = next(
        row for row in data["relationship_store"] if row["predicate"] == "has_structure"
    )
    rel["qualifiers"]["coverage"] = 0.1
    rel["qualifier_conflicts"] = {"coverage": [0.1, 0.9]}
    lost = rel["source_assertion_ids"][0]
    data["source_assertion_store"] = [
        row for row in data["source_assertion_store"] if row["id"] != lost
    ]
    view = Card.from_dict(data).explore().view("structures")
    path = tmp_path / "synthetic.json"
    view.save(path)
    saved = sabueso.read_exploration(path)
    assert saved.exclusions == view.exclusions
    excluded = next(
        row for row in saved.exclusions if row["structure_ref"] == rel["object_ref"]
    )
    assert excluded["explanation"]["reason"] == "fragment_or_peptide"
    assert excluded["explanation"]["item"]["qualifier_conflicts"] == {
        "coverage": [0.1, 0.9]
    }
    assert any(
        not source["found"]
        for member in excluded["explanation"]["members"]
        for source in member["source_assertions"]
    )


@pytest.mark.parametrize("nature", ["small_molecule", "disease", "anonymous_protein"])
def test_saved_coverage_respects_nature_and_missing_identity(nature, tmp_path):
    if nature == "small_molecule":
        from sabueso.tools.card.small_molecule import single_molecule_card
        from sabueso.tools.db.chembl import FixtureChEMBLClient

        card = single_molecule_card(
            chembl=FixtureChEMBLClient("temp_data").molecules(["CHEMBL110"])
        )
    elif nature == "disease":
        from sabueso.tools.card.disease import resolve_disease_card
        from sabueso.tools.db.mondo import FixtureMONDOClient

        card = resolve_disease_card(
            "MONDO:0014221", mondo_client=FixtureMONDOClient("temp_data")
        )[0]
    else:
        card = Card(meta={"entity_type": "protein"})
    view = card.explore().view("coverage")
    path = tmp_path / "nature.json"
    view.save(path)
    saved = sabueso.read_exploration(path)
    assert saved.native_payload == view.native_payload
    assert saved.outcome == view.outcome
    assert saved.explorer.profile == card.meta["entity_type"]


def test_save_coverage_uses_original_classification_and_catalog(
    card, tmp_path, monkeypatch
):
    state = importlib.import_module("sabueso.core.knowledge_state")
    explanation = importlib.import_module("sabueso.core.knowledge_state_explanation")
    registry = importlib.import_module("sabueso.enrichers")
    view = card.explore().view("coverage")
    original = deepcopy(view.native_payload)
    monkeypatch.setattr(state, "knowledge_state", forbidden)
    monkeypatch.setattr(explanation, "knowledge_state", forbidden)
    monkeypatch.setattr(explanation, "explain_knowledge_state", forbidden)
    monkeypatch.setattr(registry, "count_by_area", forbidden)
    monkeypatch.setattr(registry, "not_queried_details_by_area", forbidden)
    path = tmp_path / "coverage.json"
    view.save(path)
    saved = sabueso.read_exploration(path)
    assert saved.native_payload == original
    assert saved.items()[0].explain().native_payload["state_rule"] == original["rule"]


@pytest.mark.parametrize("topic", ["structures", "coverage"])
def test_independent_reader_uses_no_current_rules_or_card_factory(
    bundles, topic, tmp_path
):
    path = tmp_path / "original.json"
    path.write_text(json.dumps(bundles[topic]), encoding="utf-8")
    reader = """
import importlib, socket, sys
import sabueso
from sabueso.core.card import Card
def forbidden(*args, **kwargs): raise AssertionError('live scientific operation')
socket.create_connection = socket.socket.connect = forbidden
Card.from_dict = Card.to_dict = forbidden
for name, attributes in {
 'structures': ['structure_inventory', 'structures_view', 'coverage_class', '_sequence_state'],
 'knowledge_state': ['knowledge_state', '_enrichment_counts', '_enrichment_row'],
 'structure_explanation': ['explain_structure_inventory'],
 'knowledge_state_explanation': ['explain_knowledge_state'],
 'card_scientific_access': ['materialize'],
 'card_coverage_exploration': ['view', 'explain'],
}.items():
 module = importlib.import_module('sabueso.core.' + name)
 for attribute in attributes: setattr(module, attribute, forbidden)
registry = importlib.import_module('sabueso.enrichers')
registry.knowledge_areas = registry.count_by_area = registry.not_queried_details_by_area = forbidden
profiles = importlib.import_module('sabueso.core.card_exploration_profiles')
profiles.RECORD_COLUMNS['coverage'] = ('synthetic_future_column',)
profiles.record_label = forbidden
importlib.import_module('sabueso.core.card_scientific_access').COLUMNS = ('synthetic_future_column',)
view = sabueso.read_exploration(sys.argv[1])
assert view.explorer.mode == 'saved'
for item in view.items():
 item.cells
 assert item.explain().back() is view
view.table()._repr_html_()
assert view.explorer.view(sys.argv[2]).result_ref == view.result_ref
new = view.explorer.start_new()
assert new.mode == 'live' and view.explorer.mode == 'saved'
print('original scientific reading verified without current readers')
"""
    result = subprocess.run(
        [sys.executable, "-c", reader, str(path.resolve()), topic],
        cwd="/tmp",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "original scientific reading verified" in result.stdout


@pytest.mark.parametrize("mutation", ["state", "count", "row_missing", "rule"])
def test_historical_state_decision_rejects_coherent_payload_changes(card, mutation):
    view = card.explore().view("coverage")
    native = deepcopy(view.native_payload)
    if mutation == "state":
        native["rows"][0]["state"] = "not_stated"
    elif mutation == "count":
        native["rows"][0]["count"] = 424242
    elif mutation == "row_missing":
        native["rows"].pop()
    else:
        native["rule"]["rule"] = "knowledge_state@999"
    payload = {
        "adapter": "knowledge_coverage_exploration@1",
        "context": view.explorer.context,
        "native_payload": native,
    }
    bundle = {
        "objects": {"synthetic_rebound_metadata": payload},
        "scientific_results": {},
    }
    with pytest.raises(StorageError, match="historical"):
        _verify_objects(bundle, {view.explorer.access._focal_key: view.explorer.access})


@pytest.mark.parametrize(
    "mutation",
    [
        "state",
        "count",
        "scope",
        "quantity",
        "membership",
        "missing_support",
        "unknown_verifier",
        "native_payload",
        "closure",
    ],
)
def test_public_reader_refuses_rehashed_scientific_changes(bundles, mutation, tmp_path):
    bundle = deepcopy(bundles["structures"])
    ref = next(iter(bundle["scientific_results"]))
    wire = bundle["objects"][ref]
    row = next(iter(wire["items"].values()))
    root = bundle["views"][bundle["root_navigation_ref"]]
    if mutation == "state":
        row["state"]["sequence"] = "invented"
    elif mutation == "count":
        wire["coverage"]["rows"][0]["count"] = 424242
    elif mutation == "scope":
        wire["context"]["options"]["region"] = [42]
    elif mutation == "quantity":
        key = next(
            key for key, item in wire["items"].items() if item["resolution"] is not None
        )
        wire["items"][key]["resolution"]["manifest"]["unit"] = "second"
    elif mutation == "membership":
        root["selection"]["entries"].pop()
    elif mutation == "missing_support":
        next(iter(wire["support"].values()))["source_assertion_ids"] = []
    elif mutation == "unknown_verifier":
        bundle["producer"]["verifier"] = "scientific_exploration_binding@999"
    elif mutation == "native_payload":
        root["native_payload"]["items"].pop()
    else:
        bundle["navigation"]["explanations"].clear()
    with pytest.raises(StorageError):
        read_bundle(bundle, tmp_path)
