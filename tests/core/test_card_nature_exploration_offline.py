"""Public nature-specific journeys; deliberately altered inputs are synthetic."""

import importlib
import json
import socket
from pathlib import Path

import ackredit
import pytest
import pyunitwizard as puw
from argdigest import UnknownArgumentError

from sabueso.core.card import Card
from sabueso.core.errors import ArgumentError
from sabueso.core.relationship_store import make_relationship
from sabueso.core.source_assertion_store import make_source_assertion
from sabueso.tools.card.disease import resolve_disease_card
from sabueso.tools.card.small_molecule import single_molecule_card
from sabueso.tools.db.chembl import FixtureChEMBLClient
from sabueso.tools.db.mondo import FixtureMONDOClient


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Captured exploration must not query sources")

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


@pytest.fixture
def protein():
    return Card.from_dict(
        json.loads(Path("temp_data/frozen_cards/schema_0.3.9__P52270.json").read_text())
    )


def pick(view, label):
    return view.filter("label", equals=label).items()[0]


def test_public_molecule_opening_identity_property_original_source_and_return(molecule):
    original = molecule.to_dict()
    explorer = molecule.explore()
    opening = explorer.overview()
    assert opening.items()[0].label == "Chemical identity"
    assert "CULUWZNBISUWAS-UHFFFAOYSA-N" in repr(opening)
    chemistry = opening.items()[0].open()
    assert chemistry.back() is opening
    identities = [
        item for item in chemistry.items() if item.kind == "identity_statement"
    ]
    assert len(identities) == 1
    assert identities[0].open().native_payload == molecule.relationships("same_as")[0]
    assert identities[0].support[0]["basis"] == "relationship_level"
    assert identities[0].explain().items()
    properties = explorer.answer("property_context")
    assert properties.result_ref == explorer.view("properties").result_ref
    selected = properties.filter("label", equals="Molecular weight")
    weight = selected.items()[0]
    assert weight.cells["type"].value == "quantity"
    assert puw.get_value(weight.cells["value"].value, to_unit="dalton") == 260.25
    assert weight.open().native_payload["unit"] == "dalton"
    explanation = weight.explain()
    source = explanation.items()[0].open()
    assert source.native_payload["asserted_value"] == "260.25"
    assert source.native_payload["source_metadata"] == {"unit": "Da"}
    assert source.native_payload["source"]["version"] == "ChEMBL_37"
    assert source.back() is explanation and explanation.back() is selected
    assert source.request == properties.request
    assert "260.25 dalton" in repr(properties)
    assert "selected-source method: ALogP" in repr(properties)
    assert "method not stated in selected support" in repr(selected)
    assert molecule.to_dict() == original


def test_quantity_expectations_and_nondefault_policy_do_not_change_molecular_values(
    molecule,
):
    with puw.context(standard_units=["nm", "ps", "K", "mole", "gram"]):
        explorer = molecule.explore()
        view = explorer.view("properties")
        weight = pick(view, "Molecular weight")
        area = pick(view, "Topological polar surface area")
        assert puw.get_value(weight.cells["value"].value, to_unit="dalton") == 260.25
        assert (
            puw.get_value(area.cells["value"].value, to_unit="angstrom ** 2") == 90.06
        )
        expectation = view.schema["quantity_expectations"][
            "properties.physchem.molecular_weight"
        ]
        assert expectation == {
            "field": "properties.physchem.molecular_weight",
            "unit": "dalton",
        }
        machine = explorer.access.read(
            {
                **weight.payload_location,
                "segments": [
                    *weight.payload_location["segments"],
                    {"type": "Key", "value": "value"},
                ],
            }
        )
        frame = machine.page()["items"][0]
        assert (
            frame["quantity_context"]["field"] == "properties.physchem.molecular_weight"
        )
        assert frame["quantity_context"]["record"]["manifest"]["unit"] == "dalton"
        assert "260.25 dalton" in view._repr_html_()


def test_property_alternatives_and_conflicts_do_not_replace_selected_support(molecule):
    path = "properties.physchem.logp"
    selected_ids = molecule.get(path)["source_assertion_ids"][:]
    alternative = make_source_assertion(
        path, 2.0, "Synthetic source", "synthetic", "synthetic"
    )
    alternative["source_metadata"] = {"method": "synthetic alternative method"}
    molecule.source_assertion_store.add(alternative)
    molecule.quality["conflicts"] = [{"field": path, "values": [1.11, 2.0]}]
    molecule.quality["alternatives"] = [
        {"field": path, "reason": "synthetic selection context"}
    ]
    explorer = molecule.explore()
    item = pick(explorer.view("properties"), "logP")
    assert item.cells["value"].value == 1.11
    assert item.cells["value"].state == "conflicting"
    explanation = item.explain()
    assert (
        explanation.native_payload["support"][0]["source_assertion_ids"] == selected_ids
    )
    assert (
        explanation.native_payload["stored_alternatives"]
        == molecule.quality["alternatives"]
    )
    records = [row.open().native_payload for row in explanation.items()]
    assert {row["id"] for row in records} == {*selected_ids, alternative["id"]}
    assert next(row for row in records if row["id"] == alternative["id"]) == alternative
    assert "synthetic alternative method" not in repr(item.back())
    explanation.native_payload["stored_conflicts"].clear()
    assert item.explain().native_payload["stored_conflicts"]


def test_property_literal_keys_and_empty_values_keep_exact_locations(molecule):
    molecule.sections["properties"]["physchem"]["synthetic.dot"] = {
        "value": False,
        "source_assertion_ids": ["SA_SYNTHETIC_NOT_RETAINED"],
    }
    explorer = molecule.explore()
    item = pick(explorer.view("properties"), "synthetic.dot (retained property field)")
    assert item.cells["value"].value is False
    assert item.payload_location["segments"][-1] == {
        "type": "Key",
        "value": "synthetic.dot",
    }
    assert item.open().native_payload["value"] is False
    assert (
        item.explain().native_payload["support"][0]["statements"][0]["state"]
        == "not_retained"
    )


def test_public_disease_definition_parents_and_identity_are_separate(disease):
    original = disease.to_dict()
    explorer = disease.explore()
    assert explorer.overview().items()[0].label == "Disease definition"
    assert explorer.questions().items()[0].label == "What does this disease term mean?"
    assert "exact synonym" in repr(explorer)
    assert disease.get("names.synonyms")["value"][0]["kind"] == "exact_synonym"
    definition = explorer.answer("meaning")
    text = pick(definition, "Ontology definition")
    assert (
        text.cells["value"].value["text"]
        == disease.get("annotations.definition")["value"]["text"]
    )
    assert text.explain().items()[0].open().native_payload["source"]["name"] == "MONDO"
    parents = explorer.answer("classification")
    assert parents.result_ref == explorer.view("classification").result_ref
    assert len(parents.items()) == 4
    selected = parents.filter("object_ref", equals="mondo:MONDO:0002908")
    edge = selected.items()[0]
    assert edge.cells["predicate"].value == "subclass_of"
    assert edge.open().native_payload in disease.relationships("subclass_of")
    assert (
        edge.explain().items()[0].open().native_payload["field_path"]
        == "relationships.subclass_of"
    )
    assert edge.open().request == parents.request
    assert edge.explain().back() is selected
    assert "explorer.view('identity')" in repr(parents)
    identity = explorer.view("identity")
    equivalents = (
        pick(identity, "Source-stated equivalent identifiers").cells["value"].value
    )
    related = (
        pick(identity, "Related identifiers (not equivalence)").cells["value"].value
    )
    assert "OMIM:615512" in equivalents and "GARD:0005287" in related
    assert all(
        item.cells["predicate"].value == "subclass_of" for item in parents.items()
    )
    assert disease.to_dict() == original


@pytest.mark.parametrize("shape", [None, False, []])
def test_unrecognized_property_container_is_distinct_from_missing(molecule, shape):
    molecule.sections["properties"]["physchem"] = shape
    explorer = molecule.explore()
    view = explorer.view("properties")
    assert view.outcome["status"] == "empty"
    assert view.native_payload["field_gaps"][0]["state"] == "unrecognized_shape"
    location = view.native_payload["field_gaps"][0]["location"]
    assert explorer.inspect(locator=location).native_payload == shape


def test_classification_does_not_admit_other_subjects_or_turn_equivalence_into_edges(
    disease,
):
    disease.relationship_store.add(
        make_relationship(
            "mondo:MONDO:0002908",
            "subclass_of",
            "mondo:MONDO:OTHER",
            source_assertion_ids=["SA_SYNTHETIC_NOT_RETAINED"],
        )
    )
    explorer = disease.explore(related_cards=[Card(meta={"entity_type": "disease"})])
    view = explorer.view("classification")
    assert len(view.items()) == 4
    assert (
        len(explorer.inspect(locator=explorer._location("relationship_store")).items())
        == 5
    )
    assert view.context["used_captures"] == [explorer.context["inputs"][0]]
    assert not view.filter("object_ref", equals="OMIM:615512").items()
    assert "parent" not in view.native_payload or not view.native_payload["parent"]


@pytest.mark.parametrize("fixture", ["protein", "molecule", "disease"])
def test_coverage_native_result_and_scoped_explanation_are_exact(request, fixture):
    card = request.getfixturevalue(fixture)
    original = card.to_dict()
    baseline = card.knowledge_state()
    explorer = card.explore()
    view = explorer.view("coverage")
    assert view.native_payload == baseline
    assert view.coverage["rows"] == baseline["rows"]
    assert len(view.items()) == len(baseline["rows"])
    item = view.items()[0]
    row = item.open().native_payload
    assert row == baseline["rows"][0]
    explanation = item.explain()
    assert explanation.native_payload == card.explain_knowledge_state(
        row["area"], row["source"]
    )
    assert explanation.native_payload["rule"]["rule"] == "knowledge_state_explanation@2"
    assert item.support[0]["rule"] == baseline["rule"]
    assert explanation.back() is view
    assert card.to_dict() == original
    assert explorer.view("quality").native_payload == original["quality"]
    assert "no global completeness" in repr(view)


def test_coverage_capture_cache_and_lazy_explanation_do_not_rerun_on_navigation(
    protein, monkeypatch
):
    state = importlib.import_module("sabueso.core.knowledge_state")
    explanations = importlib.import_module("sabueso.core.knowledge_state_explanation")
    serialized, calls = protein.to_dict, []
    monkeypatch.setattr(
        protein, "to_dict", lambda: (calls.append("capture"), serialized())[1]
    )
    explorer = protein.explore()
    original = state.knowledge_state
    monkeypatch.setattr(
        state,
        "knowledge_state",
        lambda *a, **k: (calls.append("state"), original(*a, **k))[1],
    )
    view = explorer.view("coverage")
    assert calls == ["capture", "state"]
    item = view.items()[0]
    captured = explorer._coverage_result
    original_explain = captured.explanation_factory
    monkeypatch.setattr(
        captured,
        "explanation_factory",
        lambda *a, **k: (calls.append("explain"), original_explain(*a, **k))[1],
    )
    explanation = item.explain()

    def forbidden(*a, **k):
        pytest.fail("A materialized result/explanation must not rerun")

    monkeypatch.setattr(state, "knowledge_state", forbidden)
    monkeypatch.setattr(explanations, "knowledge_state", forbidden)
    monkeypatch.setattr(explanations, "explain_knowledge_state", forbidden)
    protein.sections.clear()
    assert explorer.view("coverage").result_ref == view.result_ref
    assert item.explain().result_ref == explanation.result_ref
    assert view.sort("state").back() is view
    assert item.open().back() is view
    assert item.cells["area"].value == view.native_payload["rows"][0]["area"]
    view.table()._repr_html_()
    assert calls == ["capture", "state", "explain"]


@pytest.mark.parametrize(
    "report,expected",
    [
        ({"source": "ChEMBL", "status": "error"}, "unavailable"),
        ({"source": "ChEMBL", "status": "not_queried"}, "not_queried"),
        ({"source": "ChEMBL", "status": "added", "count": 0}, "not_stated"),
        (
            {"source": "ChEMBL", "status": "added", "count": 2, "truncated": True},
            "partial",
        ),
        ({"source": "ChEMBL", "status": "added"}, "known"),
    ],
)
def test_coverage_source_states_and_unknown_counts_are_not_reclassified(
    report, expected
):
    card = Card(
        meta={
            "entity_type": "small_molecule",
            "card_id": "sabueso:small_molecule:inchikey:CULUWZNBISUWAS-UHFFFAOYSA-N",
        },
        quality={"enrichments": [report]},
    )
    view = card.explore().view("coverage")
    selected = view.filter("source", equals="ChEMBL").filter("area", equals="records")
    assert len(selected.items()) == 1
    assert selected.items()[0].cells["state"].value == expected
    assert selected.coverage == view.coverage
    count = selected.items()[0].cells["count"]
    if "count" not in report:
        assert count.state == "unknown" and count.value is None
        assert len(selected.filter("count", equals=0).items()) == 0
    assert (
        selected.items()[0].explain().native_payload["rows"][0]["row"]["state"]
        == expected
    )


@pytest.mark.parametrize(
    "nature,topics,questions",
    [
        ("protein", {"function", "structures"}, {"function", "region_coverage"}),
        (
            "small_molecule",
            {"chemistry", "properties"},
            {"chemical_identity", "property_context"},
        ),
        (
            "disease",
            {"definition", "classification", "identity"},
            {"meaning", "classification"},
        ),
    ],
)
def test_profiles_advertise_only_their_own_routes_and_missing_identity_is_explicit(
    nature, topics, questions
):
    explorer = Card(meta={"entity_type": nature}).explore()
    assert set(explorer.capabilities["scientific_topics"]) == topics | {"coverage"}
    assert set(explorer.capabilities["question_keys"]) == questions
    missing = explorer.view("coverage")
    assert missing.outcome["status"] == "missing_prerequisite" and not missing.items()
    assert missing.coverage["classification"] == "not_evaluated"
    assert missing.filter("source", equals="anything").outcome == missing.outcome
    if nature == "disease":
        assert (
            explorer.view("classification").outcome["status"] == "missing_prerequisite"
        )


@pytest.mark.parametrize(
    "topic",
    ["chemistry", "properties", "definition", "identity", "classification", "coverage"],
)
@pytest.mark.parametrize("skip", [False, True])
def test_panel_options_are_never_silently_ignored(protein, topic, skip):
    with pytest.raises(ArgumentError):
        protein.explore().view(topic, options={"typo": True}, skip_digestion=skip)


def test_wrong_profile_questions_and_bad_record_selection_are_argument_errors(
    molecule, disease
):
    with pytest.raises(ArgumentError):
        molecule.explore().answer("meaning")
    with pytest.raises(ArgumentError):
        disease.explore().answer("chemical_identity")
    with pytest.raises(ArgumentError):
        disease.explore().answer("meaning", options={"region": [1]})
    with pytest.raises(UnknownArgumentError):
        molecule.explore().answer("property_context", typo=True)
    coverage = molecule.explore().view("coverage")
    with pytest.raises(ArgumentError):
        coverage.filter("count", equals=True)
    with pytest.raises(ArgumentError):
        coverage.filter("state", equals={})
    with pytest.raises(ArgumentError):
        coverage.sort("count", unit="dalton")
    assert disease.explore().view("chemistry").outcome["status"] == "not_applicable"


def test_unrecognized_selected_support_is_preserved_without_inventing_selection(
    molecule,
):
    molecule.get("properties.physchem.logp")["source_assertion_ids"] = None
    explorer = molecule.explore()
    item = pick(explorer.view("properties"), "logP")
    support = item.explain()
    assert support.native_payload["selection_support_state"] == "unrecognized"
    assert support.native_payload["alternative_source_assertions"] == []
    assert support.native_payload["unclassified_field_source_assertions"]
    assert (
        support.items()[0].open().native_payload["field_path"]
        == "properties.physchem.logp"
    )
    assert item.open().native_payload["source_assertion_ids"] is None


def test_skipped_option_digestion_still_rejects_array_before_comparing_values(molecule):
    import numpy as np

    with pytest.raises(ArgumentError, match="mapping"):
        molecule.explore().view(
            "properties", options=np.array([1, 2]), skip_digestion=True
        )


def test_all_views_remain_inert_defensive_and_bounded(molecule, disease, monkeypatch):
    with ackredit.session("inert nature exploration"):
        before = ackredit.get_attribution().to_dict()
        for card, topic in (
            (molecule, "properties"),
            (disease, "definition"),
            (disease, "classification"),
            (molecule, "coverage"),
        ):
            view = card.explore().view(topic)
            monkeypatch.setattr(
                type(view),
                "rows",
                lambda *a: pytest.fail("Preview materialized all rows"),
            )
            assert len(repr(view)) < 10000
            assert "<script>" not in view._repr_html_()
            original = view.items()[0].open().native_payload
            copy = view.items()[0].open().native_payload
            copy.clear()
            assert view.items()[0].open().native_payload == original
            view.context.clear()
            view.items()[0].support.clear()
            view.items()[0].explain()
        assert ackredit.get_attribution().to_dict() == before
