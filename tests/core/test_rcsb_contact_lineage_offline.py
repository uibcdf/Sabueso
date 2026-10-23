"""Contact rule/input binding; deliberately synthetic cases test ambiguity."""

import json
import socket
from copy import deepcopy
from pathlib import Path

import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.core.ligand_sites import _chain_spans
from sabueso.core.migration import _has
from sabueso.mappings.rcsb_ligand_contacts_v1 import RULE, map_contacts
from sabueso.mappings.rcsb_structures import map_structure_entities


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("No source acquisition")

    monkeypatch.setattr(socket.socket, "connect", forbidden)


def neighbor(identifier="L", *, distance=3.0, seq_id=5):
    return {
        "ligand_comp_id": "LIG",
        "ligand_asym_id": identifier,
        "seq_id": seq_id,
        "comp_id": "ARG",
        "distance": distance,
        "ligand_is_bound": True,
    }


def entry():
    return {
        "rcsb_id": "SYNTHETIC",
        "polymer_entities": [
            {
                "rcsb_polymer_entity_container_identifiers": {
                    "entity_id": "1",
                    "auth_asym_ids": ["A", "B"],
                    "uniprot_ids": ["SYNTHETIC"],
                },
                "rcsb_polymer_entity_align": [
                    {
                        "reference_database_name": "UniProt",
                        "reference_database_accession": "SYNTHETIC",
                        "aligned_regions": [
                            {
                                "entity_beg_seq_id": 1,
                                "ref_beg_seq_id": 101,
                                "length": 20,
                            }
                        ],
                    }
                ],
                "polymer_entity_instances": [
                    {
                        "rcsb_polymer_entity_instance_container_identifiers": {
                            "auth_asym_id": chain
                        },
                        "rcsb_ligand_neighbors": [neighbor()],
                    }
                    for chain in ("A", "B")
                ],
            }
        ],
        "nonpolymer_entities": [
            {
                "rcsb_nonpolymer_entity_container_identifiers": {
                    "nonpolymer_comp_id": "LIG"
                },
                "rcsb_nonpolymer_entity": {"pdbx_description": "Synthetic ligand"},
            }
        ],
    }


def rows(data):
    return [
        instance["rcsb_ligand_neighbors"]
        for instance in data["polymer_entities"][0]["polymer_entity_instances"]
    ]


def mapped(data):
    result = map_structure_entities(data, "2026-10-23")
    relation = result["relationships"][0]
    return result, relation, relation["qualifiers"]["ligands"][0]["instances"]


def test_original_inputs_and_scoped_rule_reproduce_contacts_without_current_card():
    data = entry()
    original = deepcopy(data)
    result, relation, instances = mapped(data)
    derivation = relation["derivation"]
    assert derivation["rule"] == RULE
    assert derivation["parameters"]["qualifier_paths"] == ["ligands[].instances"]
    assertion = next(
        row
        for row in result["source_assertions"]
        if row["id"] == derivation["inputs"][0]
    )
    value = assertion["asserted_value"]
    assert (
        value["ligand_contact_inputs"]["polymer_entities"] == data["polymer_entities"]
    )
    assert "instances" not in value["nonpolymer_entities"][0]
    assert "min_distance" not in json.dumps(value["ligand_contact_inputs"])
    assert "sabueso_version" in derivation
    assert data == original
    data["polymer_entities"].clear()
    _, replayed, diagnostics = map_contacts(
        value["ligand_contact_inputs"]["polymer_entities"]
    )
    assert replayed["LIG"] == instances
    assert diagnostics == derivation["parameters"]["diagnostics"]
    contact = instances[0]["contacts"][0]
    assert (contact["position"], contact["seq_id"]) == (105, 5)
    assert contact["min_distance"] == {"value": 3.0, "unit": "angstrom"}


@pytest.mark.parametrize("missing", [None, "", 17])
def test_missing_instance_identity_never_joins_contacts_across_chains(missing):
    data = entry()
    for neighbors in rows(data):
        neighbors[0]["ligand_asym_id"] = missing
    _, relation, instances = mapped(data)
    assert len(instances) == 2
    assert [row["asym_id"] for row in instances] == [None, None]
    assert [row["chains"] for row in instances] == [["A"], ["B"]]
    assert (
        len(
            relation["derivation"]["parameters"]["diagnostics"][
                "unidentified_neighbors"
            ]
        )
        == 2
    )
    assert (
        _chain_spans([{**row, "structure_ref": "pdb:SYNTHETIC"} for row in instances])
        is None
    )


def test_unknown_occurrences_in_one_chain_are_not_claimed_to_be_one_instance():
    data = entry()
    rows(data)[0][:] = [neighbor(None), neighbor(None, seq_id=6)]
    _, _, instances = mapped(data)
    assert len(instances) == 3
    assert sorted(len(row["contacts"]) for row in instances) == [1, 1, 1]


def test_known_source_instance_can_span_chains_and_repeated_neighbors_take_minimum():
    data = entry()
    rows(data)[0].extend([neighbor(distance=2.0), neighbor(distance=4.0)])
    _, relation, instances = mapped(data)
    assert len(instances) == 1 and instances[0]["chains"] == ["A", "B"]
    assert len(instances[0]["contacts"]) == 2
    assert instances[0]["contacts"][0]["min_distance"]["value"] == 2.0
    assert not relation["derivation"]["parameters"]["diagnostics"][
        "unidentified_neighbors"
    ]
    assert _chain_spans([{**instances[0], "structure_ref": "pdb:SYNTHETIC"}]) == [
        "pdb:SYNTHETIC"
    ]


def test_conflicting_source_alignments_do_not_choose_the_first_accession():
    data = entry()
    entity = data["polymer_entities"][0]
    other = deepcopy(entity["rcsb_polymer_entity_align"][0])
    other["reference_database_accession"] = "OTHER_SYNTHETIC"
    entity["rcsb_polymer_entity_align"].append(other)
    _, relation, instances = mapped(data)
    assert all(
        row["position"] is None and row["uniprot"] is None
        for row in instances[0]["contacts"]
    )
    rejected = relation["derivation"]["parameters"]["diagnostics"]["ambiguous_mappings"]
    assert len(rejected) == 2
    assert {candidate["uniprot"] for candidate in rejected[0]["candidates"]} == {
        "SYNTHETIC",
        "OTHER_SYNTHETIC",
    }


def test_equal_chain_labels_and_residue_numbers_in_different_source_entities_do_not_merge():
    data = entry()
    data["polymer_entities"][0]["polymer_entity_instances"] = data["polymer_entities"][
        0
    ]["polymer_entity_instances"][:1]
    entity = deepcopy(data["polymer_entities"][0])
    entity["rcsb_polymer_entity_container_identifiers"]["entity_id"] = "2"
    entity["polymer_entity_instances"][0]["rcsb_ligand_neighbors"][0]["distance"] = 1.0
    data["polymer_entities"].append(entity)
    _, _, instances = mapped(data)
    assert len(instances[0]["contacts"]) == 2
    assert sorted(row["min_distance"]["value"] for row in instances[0]["contacts"]) == [
        1.0,
        3.0,
    ]


def test_conflicting_bound_flags_are_unknown_with_all_source_values_retained():
    data = entry()
    rows(data)[1][0]["ligand_is_bound"] = False
    _, relation, instances = mapped(data)
    assert instances[0]["is_bound"] is None
    conflict = relation["derivation"]["parameters"]["diagnostics"]["bound_conflicts"][0]
    assert set(conflict["values"]) == {True, False}
    assert len(conflict["origins"]) == 2


@pytest.mark.parametrize("state", ["not_retained", "retained_null", "retained_empty"])
def test_input_scope_distinguishes_unasked_null_and_empty_neighbors(state):
    data = entry()
    instance = data["polymer_entities"][0]["polymer_entity_instances"][0]
    if state == "not_retained":
        instance.pop("rcsb_ligand_neighbors")
    else:
        instance["rcsb_ligand_neighbors"] = None if state == "retained_null" else []
    _, relation, _ = mapped(data)
    scope = relation["derivation"]["parameters"]["diagnostics"]["neighbor_scope"]
    assert scope[0]["state"] == state and scope[1]["state"] == "retained"


def test_missing_chains_stay_unknown_and_do_not_become_a_literal_none_chain():
    data = entry()
    for instance in data["polymer_entities"][0]["polymer_entity_instances"]:
        instance["rcsb_polymer_entity_instance_container_identifiers"].pop(
            "auth_asym_id"
        )
    _, relation, instances = mapped(data)
    assert instances[0]["chains"] == [] and len(instances[0]["contacts"]) == 2
    assert (
        len(relation["derivation"]["parameters"]["diagnostics"]["missing_chains"]) == 2
    )


def test_historical_anonymous_chain_span_is_not_treated_as_a_known_span():
    assert (
        _chain_spans(
            [{"structure_ref": "pdb:SYNTHETIC", "asym_id": None, "chains": ["A", "B"]}]
        )
        is None
    )
    assert _chain_spans([]) is None


@pytest.mark.parametrize("reference", [None, "P60174"])
def test_native_instance_positions_never_mix_equal_numbers_from_foreign_or_unknown_axes(
    reference,
):
    card = Card.from_dict(
        json.loads(Path("temp_data/frozen_cards/schema_0.3.9__P52270.json").read_text())
    )
    relationship = next(
        row
        for row in card.relationship_store.store.values()
        if row["predicate"] == "has_structure" and row["object_ref"] == "pdb:1SUX"
    )
    ligand = next(
        row for row in relationship["qualifiers"]["ligands"] if row["comp_id"] == "BTS"
    )
    ligand["instances"][0]["contacts"][0]["uniprot"] = reference
    before = card.to_dict()
    item = next(
        row
        for row in card.ligand_sites()["items"]
        if row["ligand_ref"] == "pdb.ligand:BTS"
    )
    instance = next(
        row for row in item["instances"] if row["structure_ref"] == "pdb:1SUX"
    )
    assert item["instance_rule"] == "ligand_instance_scope@1"
    assert instance["sequence_ref"] == "uniprot:P52270" and instance["positions"] == [
        75,
        102,
    ]
    assert instance["unplaced_contacts"][0]["position"] == 71
    assert instance["unplaced_contacts"][0]["uniprot"] == reference
    instance["unplaced_contacts"].clear()
    instance["chains"].clear()
    assert card.to_dict() == before


@pytest.mark.parametrize(
    "damage", ["scope", "raw_inputs", "foreign_structure", "missing_input"]
)
def test_migration_does_not_credit_unrelated_or_missing_contact_basis(damage):
    result, relation, _ = mapped(entry())
    stored = {
        "relationship_store": result["relationships"],
        "source_assertion_store": result["source_assertions"],
    }
    assert _has(stored, "relationships.has_structure.derivation")
    if damage == "scope":
        relation["derivation"]["parameters"]["qualifier_paths"] = ["other"]
    elif damage == "raw_inputs":
        result["source_assertions"][0]["asserted_value"]["ligand_contact_inputs"] = {}
    elif damage == "foreign_structure":
        result["source_assertions"][0]["subject_ref"] = "pdb:OTHER"
    else:
        relation["derivation"]["inputs"] = ["SA_MISSING"]
    assert not _has(stored, "relationships.has_structure.derivation")


def test_migration_marks_legacy_gap_without_creating_historical_provenance():
    original = json.loads(
        Path("temp_data/frozen_cards/schema_0.3.9__P52270.json").read_text()
    )
    before = deepcopy(original)
    migrated = sabueso.migrate_card(original)
    record = migrated.quality["migration"][0]
    gaps = [gap for step in record["steps"] for gap in step["gaps"]]
    assert any(gap["path"] == "relationships.has_structure.derivation" for gap in gaps)
    assert migrated.to_dict()["relationship_store"] == original["relationship_store"]
    assert original == before


def test_public_current_rule_and_legacy_scope_remain_separate_through_saved_reading(
    tmp_path, monkeypatch
):
    original = json.loads(
        Path("temp_data/frozen_cards/schema_0.3.9__P52270.json").read_text()
    )
    old = Card.from_dict(original)
    assert not _has(original, "relationships.has_structure.derivation")
    data = json.loads(Path("temp_data/rcsb/1SUX.json").read_text())
    mapping = map_structure_entities(data, "2026-10-23", subjects=["P52270"])
    card = Card(
        meta={"entity_type": "protein", "card_id": "sabueso:protein:uniprot:P52270"}
    )
    card.set("identifiers.uniprot", "P52270", source_assertion_ids=[])
    for row in mapping["source_assertions"]:
        card.source_assertion_store.add(row)
    for row in mapping["relationships"]:
        card.relationship_store.add(row)
    assert _has(card.to_dict(), "relationships.has_structure.derivation")
    assert _has(Card().to_dict(), "relationships.has_structure.derivation")
    view = card.explore().answer("structure_ligands")
    assert view.items()[0].support[0]["derivation"]["rule"] == RULE
    path = tmp_path / "new.json"
    view.save(path)
    monkeypatch.setattr(
        Card, "from_dict", lambda *a, **k: pytest.fail("No live reconstruction")
    )
    saved = sabueso.read_exploration(path)
    assert saved.items()[0].support[0]["derivation"]["rule"] == RULE
    assert old.to_dict()["relationship_store"] == original["relationship_store"]
