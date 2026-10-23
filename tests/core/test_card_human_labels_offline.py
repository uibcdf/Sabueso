"""Human wording over public inputs; altered support/ontology cases are synthetic."""

import socket
import subprocess
import sys

import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.core.relationship_store import make_derivation, make_relationship
from sabueso.core.source_assertion_store import make_source_assertion
from sabueso.tools.card.disease import resolve_disease_card
from sabueso.tools.card.small_molecule import single_molecule_card
from sabueso.tools.db.chembl import FixtureChEMBLClient
from sabueso.tools.db.mondo import FixtureMONDOClient


def forbidden(*args, **kwargs):
    raise AssertionError("No source query or new scientific interpretation allowed")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
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


def property_item(molecule):
    return (
        molecule.explore().view("properties").filter("label", equals="logP").items()[0]
    )


def alternative(molecule):
    row = make_source_assertion(
        "properties.physchem.logp",
        "2.0",
        "Synthetic alternative",
        "synthetic",
        "2026-10-22",
    )
    row["source_metadata"] = {"method": "synthetic alternative method"}
    molecule.source_assertion_store.add(row)
    return row


def test_selected_and_alternative_statements_have_distinct_original_roles(molecule):
    alt = alternative(molecule)
    molecule.quality["conflicts"] = [
        {"field": "properties.physchem.logp", "values": [1.11, 2.0]}
    ]
    molecule.quality["alternatives"] = [
        {"field": "properties.physchem.logp", "reason": "synthetic"}
    ]
    original = molecule.to_dict()
    item = property_item(molecule)
    explanation = item.explain()
    labels = [row.label for row in explanation.items()]
    assert any(label.startswith("Selected support · ChEMBL") for label in labels)
    assert any(
        label.startswith("Alternative statement · Synthetic alternative")
        for label in labels
    )
    text = repr(explanation.table())
    assert "method: ALogP" in text and "synthetic alternative method" in text
    assert "Stored conflicts remain unresolved" in text
    assert "not source reliability" in text
    assert "stored_alternatives" in text
    assert (
        item.cells["value"].value == 1.11 and item.cells["value"].state == "conflicting"
    )
    assert "synthetic alternative method" not in repr(item.back())
    assert (
        next(
            row.open().native_payload
            for row in explanation.items()
            if row._entry.key == alt["id"]
        )
        == alt
    )
    assert explanation.back() is item.back()
    assert molecule.to_dict() == original


@pytest.mark.parametrize("refs", [None, False, "unrecognized", {}])
def test_unrecognized_selection_does_not_assign_source_roles(molecule, refs):
    alternative(molecule)
    field = molecule.get("properties.physchem.logp")
    if refs is None:
        field.pop("source_assertion_ids")
    else:
        field["source_assertion_ids"] = refs
    view = property_item(molecule).explain()
    assert all(row.label.startswith("Selection role unknown") for row in view.items())
    assert "no assigned selection role" in repr(view)
    assert "Selected support" not in repr(view)
    assert "Alternative statement" not in repr(view)


def test_declared_empty_selection_keeps_other_assertions_as_alternatives(molecule):
    molecule.get("properties.physchem.logp")["source_assertion_ids"] = []
    view = property_item(molecule).explain()
    assert view.items() and all(
        row.label.startswith("Alternative statement") for row in view.items()
    )
    assert view.native_payload["selection_support_state"] == "declared"


def test_missing_support_and_source_unit_method_are_explicit(molecule):
    field = molecule.get("properties.physchem.molecular_weight")
    field["source_assertion_ids"].append("SA_SYNTHETIC_NOT_RETAINED")
    view = (
        molecule.explore()
        .view("properties")
        .filter("label", equals="Molecular weight")
        .items()[0]
        .explain()
    )
    text = repr(view)
    assert "1 supporting source records not retained" in text
    assert "260.25" in text and "source unit: Da" in text
    assert "method not stated" in text
    assert (
        view.native_payload["support"][0]["statements"][-1]["id"]
        == "SA_SYNTHETIC_NOT_RETAINED"
    )
    assert view.items()[0].open().native_payload["source_metadata"] == {"unit": "Da"}


def test_source_catalog_does_not_invent_a_selection_role(molecule):
    view = molecule.explore().view("sources")
    assert all(
        not row.label.startswith(("Selected support", "Alternative statement"))
        for row in view.items()
    )
    assert "not source reliability" not in repr(view)


def test_saved_label_filter_uses_recorded_wording_not_current_live_labels(
    molecule, tmp_path, monkeypatch
):
    from sabueso.core.card_exploration import CardItem

    original_label = CardItem.label
    with monkeypatch.context() as producer:
        # Synthetic earlier wording, not a regenerated historical producer capsule.
        producer.setattr(
            CardItem,
            "label",
            property(
                lambda item: (
                    "Earlier source wording"
                    if item._entry.location["segments"]
                    and item._entry.location["segments"][0].get("value")
                    == "source_assertion_store"
                    else original_label.fget(item)
                )
            ),
        )
        selected = (
            property_item(molecule)
            .explain()
            .filter("label", equals="Earlier source wording")
        )
        assert len(selected.items()) == 1
        path = tmp_path / "earlier-wording.json"
        selected.save(path)
    saved = sabueso.read_exploration(path)
    assert saved.items()[0].label == "Earlier source wording"
    assert len(saved.filter("label", equals="Earlier source wording").items()) == 1
    assert not saved.filter("label", equals="Selected support").items()
    assert saved.items()[0].open().native_payload["source"]["name"] == "ChEMBL"


def test_source_extension_lookalikes_remain_literal_and_do_not_gain_roles():
    card = Card(
        sections={
            "extension": {
                "basis": "stored_literal",
                "support": "unrecognized",
                "asserted_value": "synthetic",
                "source": {"name": "Synthetic"},
            }
        }
    )
    view = card.explore().inspect("extension")
    assert "Selected support" not in repr(view)
    assert "source version" not in repr(view)
    assert view.native_payload["support"] == "unrecognized"
    assert "Source roles" not in repr(view.items()[0].explain())


@pytest.mark.parametrize(
    "scope, label",
    [
        ("exact_synonym", "exact synonym"),
        ("related_synonym", "related synonym"),
        ("broad_synonym", "broad synonym"),
        ("narrow_synonym", "narrow synonym"),
        ("synthetic_scope", "synthetic_scope"),
        (None, "scope not retained"),
        ({"unknown": "shape"}, "1 fields"),
    ],
)
def test_synonym_scope_is_readable_without_changing_original_values(
    disease, scope, label
):
    disease.get("names.synonyms")["value"] = [{"name": "Synthetic term", "kind": scope}]
    explorer = disease.explore()
    view = explorer.view("definition")
    item = view.filter("label", equals="Scoped synonyms").items()[0]
    assert label in repr(view) and label in repr(explorer.overview())
    assert "do not establish disease identity" in repr(view)
    assert item.cells["value"].value == [{"name": "Synthetic term", "kind": scope}]
    assert item.open().native_payload["value"][0]["kind"] == scope


@pytest.mark.parametrize(
    "basis, label",
    [
        ("direct", "Source-supported broader term"),
        ("derived", "Derived broader term"),
        ("missing", "support not retained"),
        ("none", "basis not retained"),
        ("incomplete", "derivation incomplete"),
        ("unversioned", "derivation incomplete"),
    ],
)
def test_hierarchy_basis_is_original_not_guessed_from_path_or_names(
    disease, basis, label
):
    source = make_source_assertion(
        "relationships.subclass_of",
        {"parent": "MONDO:SYNTHETIC"},
        "Synthetic",
        "synthetic",
        "2026-10-22",
    )
    disease.source_assertion_store.add(source)
    rel = make_relationship(
        "mondo:MONDO:0014221",
        "subclass_of",
        "mondo:MONDO:SYNTHETIC",
        source_assertion_ids=["SA_SYNTHETIC_NOT_RETAINED"]
        if basis == "missing"
        else [source["id"]],
        qualifiers={"path": ["synthetic", "path", "does not determine derivation"]},
    )
    if basis == "none":
        # Deliberately malformed retained data; the public maker refuses this.
        rel["source_assertion_ids"] = []
    if basis == "derived":
        rel["derivation"] = make_derivation(
            "mondo_hierarchy@1", parameters={"steps": 2}
        )
    elif basis in ("incomplete", "unversioned"):
        rel["derivation"] = (
            {} if basis == "incomplete" else {"rule": "synthetic_unversioned"}
        )
    disease.relationship_store.add(rel)
    original = disease.to_dict()
    view = (
        disease.explore()
        .view("classification")
        .filter("object_ref", equals="mondo:MONDO:SYNTHETIC")
    )
    item = view.items()[0]
    assert label in item.label and label in repr(view.table())
    assert "Basis" in view.table()._repr_html_()
    if basis == "derived":
        assert "mondo_hierarchy@1" in repr(view)
    assert item.cells["predicate"].value == "subclass_of"
    assert item.cells["object_ref"].value == rel["object_ref"]
    assert item.open().native_payload == rel
    assert disease.to_dict() == original


def test_hierarchy_statement_support_is_not_selected_field_support(disease):
    edge = disease.explore().view("classification").items()[0]
    assert all(
        row.label.startswith("Relationship support") for row in edge.explain().items()
    )


def test_long_untrusted_text_is_bounded_escaped_and_fully_reachable(molecule):
    row = alternative(molecule)
    actual = molecule.source_assertion_store.get(row["id"])
    actual["source_metadata"]["method"] = "<script>synthetic</script>" + "long" * 10000
    actual["asserted_value"] = "<img src=x>" + "long" * 10000
    view = property_item(molecule).explain()
    html = view.table()._repr_html_()
    assert "<script>" not in html and "<img" not in html
    assert "&lt;script&gt;" in html and len(html) < 12000
    assert len(repr(view)) < 12000
    assert (
        len(
            next(
                item.open().native_payload
                for item in view.items()
                if item._entry.key == row["id"]
            )["asserted_value"]
        )
        > 40000
    )


def test_saved_roles_labels_and_original_sources_survive_inert_independent_reading(
    molecule, tmp_path
):
    alternative(molecule)
    view = property_item(molecule).explain()
    path = tmp_path / "roles.json"
    receipt = view.save(path)
    original = path.read_bytes()
    program = """
import socket, sys
import sabueso
from sabueso.core.card import Card
from sabueso.core.card_exploration import CardItem
def forbidden(*args, **kwargs):
    raise AssertionError("No Card construction, live explanation or source query")
socket.create_connection = forbidden
socket.socket.connect = forbidden
Card.from_dict = forbidden
CardItem._live_explain = forbidden
saved = sabueso.read_exploration(sys.argv[1], expected_digest=sys.argv[2])
text = repr(saved.table())
assert "Selected support" in text and "Alternative statement" in text
assert "method: ALogP" in text
assert saved.items()[0].open().native_payload["source"]["name"] == "ChEMBL"
assert saved.explorer.mode == "saved"
print("PASS: independent inert source-role reading")
"""
    result = subprocess.run(
        [sys.executable, "-c", program, str(path), receipt["bundle_digest"]],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    saved = sabueso.read_exploration(path)
    assert [row.label for row in saved.items()] == [row.label for row in view.items()]
    saved.save(tmp_path / "resaved.json")
    assert path.read_bytes() == original
