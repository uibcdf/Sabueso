"""Ligand crossings/site classes retain original multi-card source support (#91)."""

from copy import deepcopy

import ackredit
import argdigest
import pytest
import pyunitwizard as puw

import sabueso
from sabueso.core.card import Card
from sabueso.core.deck import Deck
from sabueso.core.errors import ArgumentError
from sabueso.core.quantities import normalized_measurement
from sabueso.core.relationship_store import make_relationship
from sabueso.core.source_assertion_store import make_source_assertion
from sabueso.resolver import EntityResolver, FixtureRCSBClient, FixtureUniProtClient
from sabueso.tools.db.chembl import FixtureChEMBLClient
from sabueso.tools.db.pdb_ccd import FixtureCCDClient
from sabueso.tools.db.pdbe_kb import FixturePDBeKBClient

ANCHOR = "inchikey:ABCDEFGHIJKLMN-AAAAAAAAAA-N"
MOLECULE = f"sabueso:small_molecule:{ANCHOR}"
CHEMBL = "chembl:CHEMBL_SYNTHETIC"


def assertion(card, path, value, source="synthetic", record="synthetic"):
    sa = make_source_assertion(path, deepcopy(value), source, record, "2026-01-01")
    sa["source"]["version"] = "original-release"
    card.source_assertion_store.add(sa)
    return sa["id"]


def relationship(
    card,
    predicate,
    obj,
    qualifiers,
    source="synthetic",
    *,
    subject="uniprot:P52270",
    record="synthetic",
):
    sa = assertion(card, f"relationships.{predicate}", qualifiers, source, record)
    rel = make_relationship(subject, predicate, obj, qualifiers, [sa])
    card.relationship_store.add(rel)
    return card.relationship_store.get(rel["id"])


def synthetic(
    *,
    numbering="uniprot",
    position=71,
    annotation=True,
    instances=True,
    bioactivity=True,
):
    card = Card(
        meta={"card_id": "sabueso:protein:uniprot:P52270", "entity_type": "protein"}
    )
    molecule = Card(meta={"card_id": MOLECULE, "entity_type": "small_molecule"})
    for source_ref in (CHEMBL, "pdb.ligand:BTS"):
        relationship(
            molecule,
            "same_as",
            ANCHOR,
            {"source": "synthetic", "name": "Synthetic ligand"},
            subject=source_ref,
            record=source_ref,
        )
    if annotation:
        path = "features_positional.active_site"
        site = {
            "location": {"sequence": {"start": 71, "end": 71}},
            "description": "Synthetic annotated site",
        }
        card.set(path, [site], [assertion(card, path, site, "UniProt")])
    relationship(
        card,
        "has_structure",
        "pdb:1SUX",
        {
            "ligands": [
                {
                    "comp_id": "BTS",
                    "subject_of_investigation": False,
                    "instances": [
                        {
                            "asym_id": "L",
                            "chains": ["A", "B"],
                            "contacts": [{"position": 71, "uniprot": "P52270"}],
                        }
                    ]
                    if instances
                    else [],
                }
            ]
        },
        "RCSB PDB",
    )
    relationship(
        card,
        "has_ligand_site",
        "pdb.ligand:BTS",
        {
            "numbering": numbering,
            "residues": [{"start": position, "end": position, "residue": "ARG"}],
            "is_solvent": False,
            "significance": "synthetic significance",
            "structures": ["pdb:1SUX"],
        },
        "PDBe-KB",
    )
    if bioactivity:
        relationship(
            card,
            "has_bioactivity",
            CHEMBL,
            {
                "activity_id": 1,
                "source": "ChEMBL",
                "measurement": {
                    "type": "IC50",
                    "value": 5000,
                    "units": "nM",
                    "relation": "=",
                    "normalized": normalized_measurement(5000, "nM"),
                },
                "assay": {"relationship_type": "D"},
                "document": {"pubmed": "1"},
            },
            "ChEMBL",
        )
    deck = Deck()
    deck.add(molecule, basis={"rule": "synthetic-membership", "source": "synthetic"})
    return card, molecule, deck


@pytest.fixture(
    scope="module", params=[("P52270", "1SUX", "BTS"), ("P60174", "1HTI", "PGA")]
)
def public(request):
    accession, structure, ligand = request.param
    chembl = FixtureChEMBLClient("temp_data")
    ccd = FixtureCCDClient("temp_data")
    card = sabueso.resolve_protein_card(
        accession,
        resolver=EntityResolver(
            FixtureUniProtClient("temp_data"),
            rcsb_client=FixtureRCSBClient("temp_data"),
        ),
        structures=[structure],
        chembl={},
        chembl_client=chembl,
        ligand_sites=True,
        pdbe_kb_client=FixturePDBeKBClient("temp_data"),
    )[0]
    molecule = sabueso.resolve_molecule_card(
        f"pdb.ligand:{ligand}", ccd_client=ccd, chembl_client=chembl
    )[0]
    deck = Deck()
    deck.add(molecule, basis={"source": "public frozen fixture"})
    return card, molecule, deck


def test_public_site_and_crossing_match_native_views_with_distinct_pins(public):
    card, molecule, deck = public
    item = card.ligands(deck)["items"][0]
    answer = card.explain_ligand(molecule.id, deck)
    assert answer["status"] == "on_card" and not answer["gaps"]
    assert answer["items"][0]["item"] == item
    assert answer["items"][0]["molecule_card_ref"] == molecule.pinned_ref()
    assert answer["card_ref"] == card.pinned_ref()
    assert answer["deck"]["snapshot_id"] == deck.snapshot_id()
    assert answer["deck"]["membership"] == deck.explain(molecule.id)
    for site in card.ligand_sites()["items"]:
        explained = card.explain_ligand_site(site["relationship_id"])
        assert explained["item"] == site
        assert explained["classification"]["rule"] == "annotated_site_overlap@2"
        assert explained["site"]["relationship"]["id"] == site["relationship_id"]
        assert explained["rule"]["rule"] == "ligand_site_explanation@1"
        assert explained["status"] == "on_card"


@pytest.mark.parametrize(
    "numbering,position,annotation,expected",
    [
        ("uniprot", 71, True, "overlaps_annotated_site"),
        ("uniprot", 72, True, "no_annotated_overlap"),
        ("uniprot", 71, False, "no_annotated_sites"),
        ("author", 71, True, "numbering_not_comparable"),
    ],
)
def test_site_classes_expose_exact_stored_inputs_without_negative_assertions(
    numbering, position, annotation, expected
):
    card, _, _ = synthetic(
        numbering=numbering, position=position, annotation=annotation
    )
    site = card.ligand_sites()["items"][0]
    answer = card.explain_ligand_site(site["relationship_id"])
    assert answer["item"]["site_class"] == expected
    assert answer["classification_inputs"]["numbering"] == numbering
    assert answer["classification_inputs"]["annotated_site_count"] == int(annotation)
    assert answer["classification_inputs"]["fields"][0]["stored"] == annotation
    assert answer["site"]["source_assertions"][0]["version"] == "original-release"
    assert answer["status"] == "on_card" and not answer["gaps"]


@pytest.mark.parametrize("instances", [False, True])
def test_instance_contacts_and_relevance_sources_remain_separate(instances):
    card, _, _ = synthetic(instances=instances)
    site = card.ligand_sites()["items"][0]
    answer = card.explain_ligand_site(site["relationship_id"])
    assert answer["item"]["spans_chains"] == (["pdb:1SUX"] if instances else None)
    assert answer["item"]["subject_of_investigation"] == {"pdb:1SUX": False}
    assert answer["item"]["is_solvent"] is False
    structure = next(
        link
        for link in answer["context"]["relationships"]
        if link["relationship"]["predicate"] == "has_structure"
    )
    assert structure["source_assertions"][0]["source"] == "RCSB PDB"
    assert answer["site"]["source_assertions"][0]["source"] == "PDBe-KB"


def test_missing_annotation_match_retains_field_support_and_is_partial():
    card, _, _ = synthetic()
    node = card.get("features_positional.active_site")
    card.source_assertion_store.get(node["source_assertion_ids"][0])[
        "asserted_value"
    ] = {"different": "synthetic"}
    site = card.ligand_sites()["items"][0]
    answer = card.explain_ligand_site(site["relationship_id"])
    assert answer["status"] == "partial"
    assert answer["item"]["site_class"] == "overlaps_annotated_site"
    assert answer["classification_inputs"]["fields"][0]["source_assertions"]
    assert any(
        g["reason"] == "no_matching_annotation_assertion" for g in answer["gaps"]
    )


def test_selected_annotation_alternatives_conflicts_and_versions_are_preserved():
    card, _, _ = synthetic()
    path = "features_positional.active_site"
    alternative = assertion(card, path, {"different": "alternative"}, "InterPro")
    card.quality["conflicts"] = [{"field": path, "source_assertion_ids": [alternative]}]
    site = card.ligand_sites()["items"][0]
    field = card.explain_ligand_site(site["relationship_id"])["classification_inputs"][
        "fields"
    ][0]
    assert field["conflicts"] == card.quality["conflicts"]
    assert field["alternatives"][0]["id"] == alternative
    assert field["source_assertions"][0]["source"] == "UniProt"


def test_missing_conflict_support_is_partial_without_discarding_site_class():
    card, _, _ = synthetic()
    card.quality["conflicts"] = [
        {
            "field": "features_positional.active_site",
            "source_assertion_ids": [["SA_missing"]],
        }
    ]
    site = card.ligand_sites()["items"][0]
    answer = card.explain_ligand_site(site["relationship_id"])
    assert answer["status"] == "partial"
    assert answer["item"]["site_class"] == "overlaps_annotated_site"
    assert not answer["classification_inputs"]["fields"][0][
        "conflict_source_assertions"
    ][0]["found"]


def test_crossing_exposes_actual_identity_class_selection_and_quantity_policy():
    card, molecule, deck = synthetic()
    before = (card.to_dict(), molecule.to_dict(), deepcopy(deck.meta))
    policy = {"active_max": puw.quantity(1, "micromolar")}
    answer = card.explain_ligand(MOLECULE, deck, thresholds=policy)
    (explained,) = answer["items"]
    assert explained["item"]["bioactivity"]["class"] == "weak"
    assert explained["crossing_inputs"]["best_class_ref"] == CHEMBL
    assert set(explained["crossing_inputs"]["records"]) == {CHEMBL, "pdb.ligand:BTS"}
    assert len(explained["identity"]["used_relationship_ids"]) == 2
    assert explained["bioactivities"][0]["rule"]["parameters"]["thresholds"][
        "active_max"
    ] == {"value": 1, "unit": "micromolar"}
    assert explained["sites"][0]["item"]["site_class"] == "overlaps_annotated_site"
    assert answer["rule"]["rule"] == "ligand_deck_explanation@2"
    assert before == (card.to_dict(), molecule.to_dict(), deck.meta)


def test_name_fallback_and_selected_name_retain_exact_support():
    card, molecule, deck = synthetic()
    answer = card.explain_ligand(MOLECULE, deck)["items"][0]
    assert answer["crossing_inputs"]["name_basis"] == "same_as_name"
    used = answer["crossing_inputs"]["name_relationship_id"]
    assert used in {link["relationship"]["id"] for link in answer["identity"]["links"]}
    path = "names.canonical_name"
    molecule.set(path, "Selected name", [assertion(molecule, path, "Selected name")])
    answer = card.explain_ligand(MOLECULE, deck)["items"][0]
    assert answer["item"]["name"] == "Selected name"
    assert answer["crossing_inputs"]["name_basis"] == path
    assert answer["name"]["source_assertions"][0]["asserted_value"] == "Selected name"


def test_missing_molecular_identity_support_is_partial_without_changing_the_crossing():
    card, molecule, deck = synthetic()
    molecule.relationships("same_as")[0]["source_assertion_ids"] = ["SA_missing"]
    answer = card.explain_ligand(MOLECULE, deck)
    assert answer["status"] == "partial"
    assert answer["items"][0]["item"] == card.ligands(deck)["items"][0]
    assert any(g["reason"] == "missing_source_assertion" for g in answer["gaps"])


@pytest.mark.parametrize("legacy", [False, True])
def test_ligand_counter_separates_groups_from_records_and_copies_stay_copies(legacy):
    card, _, deck = synthetic()
    q = deepcopy(card.relationships("has_bioactivity")[0]["qualifiers"])
    q.update(
        source="PubChem", activity_id=2, copy_of={"source": "ChEMBL", "activity_id": 1}
    )
    relationship(card, "has_bioactivity", CHEMBL, q, "PubChem", record="copy")
    rule = f"ligand_measurement_count@{1 if legacy else 2}"
    answer = card.explain_ligand(MOLECULE, deck, counting_rule=rule)
    (measured,) = answer["items"][0]["bioactivities"]
    assert measured["item"]["measurement_count"] == 1
    assert measured["item"]["record_count"] == 2
    item = answer["items"][0]
    assert item["item"]["bioactivity"]["measurements"] == (2 if legacy else 1)
    assert item["item"]["bioactivity"]["records"] == 2
    assert answer["measurement_counting"]["rule"] == rule
    assert len(item["crossing_inputs"]["measurement_group_ids"]) == 1
    assert len(item["crossing_inputs"]["measurement_record_ids"]) == 2
    assert (
        answer["rule"]["parameters"]["bioactivity_measurements"]
        == answer["measurement_counting"]["parameters"]["measurements"]
    )
    assert len(measured["groups"][0]["voters"]) == 1


def add_measurement(
    card,
    activity,
    *,
    source="ChEMBL",
    molecule=CHEMBL,
    value=5000,
    assignment="D",
    copy_of=None,
    parent=None,
):
    q = {
        "activity_id": activity,
        "source": source,
        "measurement": {
            "type": "IC50",
            "value": value,
            "units": "nM",
            "relation": "=",
            "normalized": normalized_measurement(value, "nM"),
        },
        "assay": {"relationship_type": assignment},
        "document": {"pubmed": "1"},
    }
    if copy_of:
        q["copy_of"] = copy_of
    if parent:
        q["parent_molecule"] = parent
    return relationship(
        card, "has_bioactivity", molecule, q, source, record=str(activity)
    )


@pytest.mark.parametrize(
    "mode", ["statement", "same_source", "ambiguous", "discordant", "copy_only"]
)
def test_group_count_preserves_statement_ambiguity_independence_and_class_policy(mode):
    card, _, deck = synthetic(bioactivity=mode != "copy_only")
    if mode == "copy_only":
        add_measurement(
            card, 2, source="PubChem", copy_of={"source": "ChEMBL", "activity_id": 1}
        )
    else:
        add_measurement(
            card,
            2,
            source="ChEMBL" if mode == "same_source" else "BindingDB",
            value=1000000 if mode == "discordant" else 5000,
        )
        if mode == "ambiguous":
            add_measurement(card, 3)
    native = card.bioactivities()["items"][0]
    expected_groups = {
        "statement": 1,
        "same_source": 2,
        "ambiguous": 3,
        "discordant": 2,
        "copy_only": 1,
    }[mode]
    answer = card.explain_ligand(MOLECULE, deck)
    item = answer["items"][0]
    assert native["measurement_count"] == expected_groups
    assert item["item"]["bioactivity"] == {
        "class": native["class"],
        "best_pchembl": native["best_pchembl"],
        "measurements": expected_groups,
        "records": native["record_count"],
    }
    assert item["bioactivities"][0]["item"] == native
    if mode == "statement":
        assert item["bioactivities"][0]["groups"][0]["joins"][0]["basis"] == "statement"
    elif mode == "ambiguous":
        assert item["bioactivities"][0]["measurement_identity"]["ambiguous"]
    elif mode == "discordant":
        assert native["discordant"]
    elif mode == "copy_only":
        assert item["bioactivities"][0]["groups"][0]["basis"] == "copies_only"


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("parent", [False, True])
def test_a_group_crossing_matched_molecule_items_is_counted_once(parent, legacy):
    card, molecule, deck = synthetic(bioactivity=False)
    original_ref = "chembl:SALT" if parent else CHEMBL
    original = add_measurement(
        card, 1, molecule=original_ref, parent=CHEMBL if parent else None
    )
    alternate = "pubchem:2"
    copied = add_measurement(
        card,
        2,
        source="PubChem",
        molecule=alternate,
        copy_of={"source": "ChEMBL", "activity_id": 1},
    )
    relationship(molecule, "same_as", ANCHOR, {}, subject=alternate, record=alternate)
    native = card.bioactivities()
    assert len(native["items"]) == 2
    assert sum(i["measurement_count"] for i in native["items"]) == 2
    assert len({m["group"] for i in native["items"] for m in i["measurements"]}) == 1
    rule = f"ligand_measurement_count@{1 if legacy else 2}"
    answer = card.explain_ligand(MOLECULE, deck, counting_rule=rule)
    item = answer["items"][0]
    assert item["item"] == card.ligands(deck, counting_rule=rule)["items"][0]
    assert item["item"]["bioactivity"]["measurements"] == (2 if legacy else 1)
    assert item["item"]["bioactivity"]["records"] == 2
    assert item["crossing_inputs"]["measurement_record_ids"] == sorted(
        [original["id"], copied["id"]]
    )
    assert len(item["crossing_inputs"]["measurement_group_ids"]) == 1
    assert {
        m["relationship_id"]
        for i in item["bioactivities"]
        for m in i["item"]["measurements"]
    } == {original["id"], copied["id"]}


@pytest.mark.parametrize("include_indirect", [False, True])
def test_counts_only_include_records_admitted_by_the_selected_assay_scope(
    include_indirect,
):
    card, _, deck = synthetic()
    add_measurement(card, 2, assignment="H", value=1000000)
    view = card.ligands(deck, include_indirect=include_indirect)
    item = view["items"][0]
    assert (
        item["bioactivity"]["measurements"]
        == item["bioactivity"]["records"]
        == 1 + int(include_indirect)
    )
    assert item["excluded_measurements"] == int(not include_indirect)
    assert view["scope"]["target_assignment"] == ("any" if include_indirect else "D")


@pytest.mark.parametrize("legacy", [False, True])
def test_comparison_uses_the_same_counting_policy_and_distinct_input_pins(legacy):
    card, _, deck = synthetic()
    other, _, other_deck = synthetic()
    add_measurement(
        card, 2, source="PubChem", copy_of={"source": "ChEMBL", "activity_id": 1}
    )
    rule = f"ligand_measurement_count@{1 if legacy else 2}"
    answer = card.compare_ligands(deck, other, other_deck, counting_rule=rule)
    (item,) = answer["shared"]
    assert item["self"]["bioactivity"]["measurements"] == (2 if legacy else 1)
    assert item["self"]["bioactivity"]["records"] == 2
    assert (
        item["other"]["bioactivity"]["measurements"]
        == item["other"]["bioactivity"]["records"]
        == 1
    )
    for side, protein in (("self", card), ("other", other)):
        assert answer["measurement_counting"][side]["rule"] == rule
        assert answer["measurement_counting"][side]["inputs"][0] == protein.pinned_ref()


@pytest.mark.parametrize("legacy", [False, True])
def test_historical_counting_preserves_original_group_record_and_assertion_support(
    tmp_path, monkeypatch, legacy
):
    from sabueso.tools.db import _http

    card, molecule, deck = synthetic()
    add_measurement(
        card, 2, source="PubChem", copy_of={"source": "ChEMBL", "activity_id": 1}
    )
    rule = f"ligand_measurement_count@{1 if legacy else 2}"
    store = sabueso.KnowledgeStore(tmp_path / "counting.db")
    pin = store.save(card)
    deck_pin = store.save_deck(deck, "ligands")
    expected = card.explain_ligand(MOLECULE, deck, counting_rule=rule)
    add_measurement(card, 3)
    store.save(card)
    monkeypatch.setattr(
        _http, "_urlopen", lambda *a, **k: pytest.fail("no acquisition")
    )
    with ackredit.session("historical counting"):
        credit = ackredit.get_attribution().to_dict()
        old = store.load(pin)
        old_deck = store.load_deck(deck_pin)
        restored = old.explain_ligand(MOLECULE, old_deck, counting_rule=rule)
        assert restored == expected
        assert ackredit.get_attribution().to_dict() == credit
    assert restored["measurement_counting"]["inputs"] == [pin, molecule.pinned_ref()]
    for record in restored["items"][0]["bioactivities"][0]["records"]:
        for sa in record["source_assertions"]:
            assert (
                store.source_assertion(sa["source_assertion_ref"])["source"]["version"]
                == "original-release"
            )


@pytest.mark.parametrize("method", ["ligands", "compare_ligands", "explain_ligand"])
@pytest.mark.parametrize("value", [None, "ligand_measurement_count@3", []])
def test_counting_rule_is_digested_at_every_public_crossing(method, value):
    card, _, deck = synthetic()
    args = (
        (MOLECULE, deck)
        if method == "explain_ligand"
        else (deck, card, deck)
        if method == "compare_ligands"
        else (deck,)
    )
    with pytest.raises(ArgumentError):
        getattr(card, method)(*args, counting_rule=value)


def test_duplicate_deck_members_are_retained_without_selecting_a_snapshot():
    card, molecule, deck = synthetic()
    other = Card.from_dict(molecule.to_dict())
    other.set(
        "names.canonical_name",
        "Another stored name",
        [assertion(other, "names.canonical_name", "Another stored name")],
    )
    deck.add(other)
    answer = card.explain_ligand(MOLECULE, deck)
    assert answer["status"] == "partial" and len(answer["items"]) == 2
    assert {i["molecule_card_ref"] for i in answer["items"]} == {
        molecule.pinned_ref(),
        other.pinned_ref(),
    }
    assert any(g["reason"] == "multiple_deck_members" for g in answer["gaps"])


def test_historical_protein_and_deck_restore_original_multi_card_support(tmp_path):
    card, molecule, deck = synthetic()
    store = sabueso.KnowledgeStore(tmp_path / "ligands.db")
    pin = store.save(card)
    deck_pin = store.save_deck(deck, "original-ligands")
    expected = card.explain_ligand(MOLECULE, deck)
    molecule.set(
        "names.canonical_name",
        "Later name",
        [assertion(molecule, "names.canonical_name", "Later name")],
    )
    store.save_deck(deck, "original-ligands")
    restored = store.load(pin).explain_ligand(MOLECULE, store.load_deck(deck_pin))
    assert restored == expected
    for link in restored["items"][0]["identity"]["links"]:
        assert store.relationship(link["relationship_ref"]) == link["relationship"]
        for sa in link["source_assertions"]:
            assert (
                store.source_assertion(sa["source_assertion_ref"])["source"]["version"]
                == "original-release"
            )


def test_readers_fetch_nothing_add_no_credit_and_return_detached_support(monkeypatch):
    from sabueso.tools.db import _http

    card, molecule, deck = synthetic()
    before = (card.to_dict(), molecule.to_dict(), deepcopy(deck.meta))
    monkeypatch.setattr(
        _http, "_urlopen", lambda *a, **k: pytest.fail("no acquisition")
    )
    with ackredit.session("inert ligand explanations"):
        credited = ackredit.get_attribution().to_dict()
        answer = card.explain_ligand(MOLECULE, deck)
        assert ackredit.get_attribution().to_dict() == credited
    answer["items"][0]["identity"]["links"][0]["relationship"]["qualifiers"].clear()
    answer["deck"]["meta"].clear()
    assert before == (card.to_dict(), molecule.to_dict(), deck.meta)


def test_missing_native_items_and_unrelated_deck_cards_are_not_absence():
    card, molecule, deck = synthetic(bioactivity=False)
    assert card.explain_ligand_site("REL_missing")["status"] == "not_on_card"
    assert (
        card.explain_ligand("sabueso:small_molecule:inchikey:UNKNOWN", deck)["reason"]
        == "not_in_deck"
    )
    unrelated = Card(meta={"card_id": "sabueso:protein:uniprot:OTHER"})
    answer = unrelated.explain_ligand(molecule.id, deck)
    assert (
        answer["status"] == "not_on_card"
        and answer["reason"] == "no_stored_relation_to_protein"
    )


@pytest.mark.parametrize(
    "value", [None, "pdb.ligand:BTS", "MG_0123456789abcdef", "REL_x#SA_y"]
)
def test_site_selector_is_digested(value):
    with pytest.raises(ArgumentError):
        synthetic()[0].explain_ligand_site(value)


def test_crossing_arguments_use_existing_digesters():
    card, _, deck = synthetic()
    with pytest.raises(ArgumentError):
        card.explain_ligand(None, deck)
    with pytest.raises(ArgumentError):
        card.explain_ligand(CHEMBL, deck)
    with pytest.raises(ArgumentError):
        card.explain_ligand(MOLECULE, [])
    with pytest.raises(ArgumentError):
        card.explain_ligand(MOLECULE, deck, include_indirect="yes")
    with pytest.raises(ArgumentError):
        card.explain_ligand(MOLECULE, deck, thresholds={"active_max": 1})
    with pytest.raises(argdigest.UnknownArgumentError):
        card.explain_ligand_site("REL_missing", surprise=True)
