"""The glossary of molecular entities a card mentions (uibcdf/sabueso#52)."""

import json

import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.resolver import EntityResolver, FixtureRCSBClient, FixtureUniProtClient
from sabueso.tools.db.chembl import FixtureChEMBLClient
from sabueso.tools.db.pdb_ccd import FixtureCCDClient
from sabueso.tools.db.pdbe_kb import FixturePDBeKBClient
from sabueso.tools.db.unichem import FixtureUniChemClient

BTS = "inchikey:XBNHRNFODJOFRU-UHFFFAOYSA-N"


@pytest.fixture(scope="module")
def clients():
    return dict(
        chembl_client=FixtureChEMBLClient("temp_data"),
        ccd_client=FixtureCCDClient("temp_data"),
        unichem_client=FixtureUniChemClient("temp_data"),
    )


@pytest.fixture
def resolver():
    return EntityResolver(
        FixtureUniProtClient("temp_data"), rcsb_client=FixtureRCSBClient("temp_data")
    )


@pytest.fixture
def tctim(resolver, clients):
    card, _ = sabueso.resolve(
        "P52270",
        resolver=resolver,
        structures=["1SUX", "3Q37"],
        chembl={},
        chembl_client=clients["chembl_client"],
        ligand_sites=True,
        interfaces=True,
        pdbe_kb_client=FixturePDBeKBClient("temp_data"),
    )
    return card


@pytest.mark.parametrize("malformed", [17, "bad", [None, 42, "bad"]])
def test_malformed_ligand_declarations_remain_stored_without_false_entities(
    tctim, malformed
):
    # Synthetic shape damage must not erase the original declaration or break
    # capture of the remaining knowledge. No entity is inferred from it.
    row = next(
        row
        for row in tctim.relationship_store.store.values()
        if row["predicate"] == "has_structure"
    )
    row["qualifiers"]["ligands"] = malformed
    stored = tctim.to_dict()
    original = next(
        item for item in stored["relationship_store"] if item["id"] == row["id"]
    )
    assert original["qualifiers"]["ligands"] == malformed
    assert "pdb.ligand:bad" not in stored["entities"]


def test_each_entity_appears_once_with_where_the_card_mentions_it(tctim):
    entities = tctim.entities()
    subject = entities["uniprot:P52270"]
    assert subject["entity_type"] == "protein" and "subject" in subject["appears_in"]
    bts = tctim.entity("pdb.ligand:BTS")
    assert {"has_structure", "has_ligand_site"} <= set(bts["appears_in"])


def test_records_stay_apart_until_a_source_states_their_identity(tctim, clients):
    # No source on the protein card says the PDB component BTS is the measured
    # molecule CHEMBL1161789 (PDBe-KB leaves ChEMBL ids empty for TIM ligands).
    assert (
        tctim.entity("pdb.ligand:BTS")["key"]
        != tctim.entity("chembl:CHEMBL1161789")["key"]
    )
    # A resolved identity says so, and they become one entity.
    bts, _ = sabueso.resolve("pdb.ligand:BTS", **clients)
    tctim.add_literature_bioactivity(
        bts, "IC50", "33 uM", "pubmed:35189560", "curator-a", "direct"
    )
    assert (
        tctim.entity("pdb.ligand:BTS")["key"]
        == tctim.entity("chembl:CHEMBL1161789")["key"]
        == BTS
    )


def test_records_merge_only_where_a_source_states_they_are_one(tctim):
    entities = tctim.entities()
    all_records = [r for e in entities.values() for r in e["records"]]
    assert len(all_records) == len(set(all_records))  # no record in two entities
    # Two different measured molecules stay two entities.
    assert (
        tctim.entity("chembl:CHEMBL110")["key"] != tctim.entity("pdb.ligand:BTS")["key"]
    )


def test_a_chimera_partner_and_a_protein_without_uniprot_are_listed(tctim):
    assert tctim.entity("uniprot:P04789")["entity_type"] == "protein"


def test_structures_publications_and_terms_are_not_entities(tctim):
    refs = set(tctim.entities())
    refs |= {r for e in tctim.entities().values() for r in e["records"]}
    assert not {
        r for r in refs if r.startswith(("pdb:", "pubmed:", "go:", "interpro:"))
    }


def test_a_curated_molecule_anchors_its_entity_and_states_no_records(tctim, clients):
    bts, _ = sabueso.resolve("pdb.ligand:BTS", **clients)
    record = tctim.add_literature_bioactivity(
        bts, "IC50", "33 uM", "pubmed:35189560", "curator-a", "direct"
    )
    entry = tctim.entity("pubchem:162569")
    assert entry["key"] == BTS and entry["identity"]["by"] == "curation"
    assert {"chembl:CHEMBL1161789", "pdb.ligand:BTS"} <= set(entry["records"])
    rel = tctim.relationship_store.get(record["relationship_id"])
    assert rel["qualifiers"]["molecule_ref"] == BTS
    stated = tctim.source_assertion_store.get(record["source_assertion_id"])
    assert "records" not in stated["asserted_value"]["molecule"]


def test_the_curated_id_does_not_depend_on_the_records_unichem_links(tctim, clients):
    bts, _ = sabueso.resolve("pdb.ligand:BTS", **clients)
    first = tctim.add_literature_bioactivity(
        bts, "IC50", "33 uM", "pubmed:35189560", "curator-a", "direct"
    )
    # The same statement, with UniChem knowing one more record some other day.
    other_day = {
        "inchikey": BTS.split(":", 1)[1],
        "records": ["chembl:CHEMBL1161789", "pubchem:162569", "chebi:99999"],
        "as_given": None,
    }
    again = tctim.add_literature_bioactivity(
        other_day, "IC50", "33 uM", "pubmed:35189560", "curator-a", "direct"
    )
    assert again["source_assertion_id"] == first["source_assertion_id"]


def test_the_glossary_round_trips(tctim, clients):
    bts, _ = sabueso.resolve("pdb.ligand:BTS", **clients)
    tctim.add_literature_bioactivity(
        bts, "IC50", "33 uM", "pubmed:35189560", "curator-a", "direct"
    )
    data = json.loads(json.dumps(tctim.to_dict()))
    loaded = Card.from_dict(data)
    assert loaded.entities() == tctim.entities() == data["entities"]


def test_a_card_without_a_glossary_still_loads():
    data = json.loads(
        open(
            "temp_data/frozen_cards/schema_0.3.0__P52270.json", encoding="utf-8"
        ).read()
    )
    card = Card.from_dict(data)
    assert card.entity("uniprot:P52270")["anchor"] == "uniprot:P52270"
