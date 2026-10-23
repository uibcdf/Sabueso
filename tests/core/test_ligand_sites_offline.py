"""Ligand binding sites crossed with annotated sites (uibcdf/sabueso#28).

TcTIM (P52270) and HsTIM (P60174): UniProt annotations, PDBe-KB ligand sites and RCSB
per-instance ligand neighbours of 1SUX (TcTIM with BTS) and 1HTI (HsTIM with PGA), all
retrieved on 2026-09-23.
"""

import json
import random
from pathlib import Path

import pytest

from sabueso import ligand_deck, resolve_protein_card
from sabueso._private.smonitor.warnings import EnrichmentFailedWarning
from sabueso.core.card import Card
from sabueso.core.ligand_sites import ligand_sites_view
from sabueso.mappings.rcsb_structures import map_structure_entities
from sabueso.mappings.uniprot import map_protein
from sabueso.resolver import EntityResolver, FixtureRCSBClient, FixtureUniProtClient
from sabueso.tools.db.chembl import FixtureChEMBLClient
from sabueso.tools.db.pdb_ccd import FixtureCCDClient
from sabueso.tools.db.pdbe_kb import FixturePDBeKBClient


@pytest.fixture(scope="module")
def resolver():
    return EntityResolver(
        FixtureUniProtClient("temp_data"), rcsb_client=FixtureRCSBClient("temp_data")
    )


def _card(resolver, accession, structures=(), **kwargs):
    card, _ = resolve_protein_card(
        accession,
        resolver,
        structures=list(structures),
        ligand_sites=True,
        pdbe_kb_client=FixturePDBeKBClient("temp_data"),
        **kwargs,
    )
    return card


def _sites(card):
    return {i["ligand_ref"]: i for i in card.ligand_sites()["items"]}


def test_uniprot_binding_sites_keep_their_ligand():
    human = map_protein(
        json.loads(Path("temp_data/P60174.json").read_text(encoding="utf-8")), "x"
    )
    sites = human["features"]["features_positional.binding_site"]
    assert [s["ligand"] for s in sites] == [{"name": "substrate"}] * 2
    # Hexokinase has two ATP sites: the label keeps their residues apart.
    hexokinase = map_protein(
        json.loads(Path("temp_data/P52789.json").read_text(encoding="utf-8")), "x"
    )
    atp = {
        s["ligand"]["label"]
        for s in hexokinase["features"]["features_positional.binding_site"]
        if s["ligand"].get("name") == "ATP"
    }
    assert atp == {"1", "2"}


def test_pdbe_kb_sites_are_supported_relationships(resolver):
    card = _card(resolver, "P52270")
    (enrichment,) = card.quality["enrichments"]
    assert enrichment == {
        "source": "PDBe-KB",
        "request_options": True,
        "data": "ligand_sites",
        "identifier": "P52270",
        "status": "added",
        "count": 6,
    }
    (bts,) = card.relationships("has_ligand_site", object_ref="pdb.ligand:BTS")
    assert bts["qualifiers"]["numbering"] == "uniprot"
    assert [r["start"] for r in bts["qualifiers"]["residues"]] == [71, 75, 102]
    (sa_id,) = bts["source_assertion_ids"]
    assertion = card.source_assertion_store.get(sa_id)
    assert (assertion["source"]["name"], assertion["subject_ref"]) == (
        "PDBe-KB",
        "uniprot:P52270",
    )


def test_two_sources_agree_on_the_human_active_site(resolver):
    view = _card(resolver, "P60174", structures=["1HTI"]).ligand_sites()
    assert [(a["kind"], a["start"]) for a in view["annotated_sites"]] == [
        ("binding_site", 12),
        ("binding_site", 14),
        ("active_site", 96),
        ("active_site", 166),
    ]
    assert view["annotated_sites"][0]["evidence"] == ["ECO:0000255", "ECO:0000269"]
    pga = {i["ligand_ref"]: i for i in view["items"]}["pdb.ligand:PGA"]
    # 2-phosphoglycolate, a transition-state analogue, contacts every annotated residue.
    assert [o["start"] for o in pga["annotated_overlap"]] == [12, 14, 96, 166]
    assert pga["site_class"] == "overlaps_annotated_site"
    assert view["classification"]["rule"] == "annotated_site_overlap@2"


def test_bts_binds_away_from_the_annotated_site_and_across_chains(resolver):
    card = _card(resolver, "P52270", structures=["1SUX"])
    bts = _sites(card)["pdb.ligand:BTS"]
    assert bts["site_class"] == "no_annotated_overlap"
    assert bts["positions"] == [71, 75, 102]
    # One BTS instance contacts Arg71 and Phe75 of chain A and Tyr102 of chain B.
    assert bts["instances"] == [
        {
            "structure_ref": "pdb:1SUX",
            "relationship_id": card.relationships(
                "has_structure", object_ref="pdb:1SUX"
            )[0]["id"],
            "sequence_ref": "uniprot:P52270",
            "asym_id": "J",
            "chains": ["A", "B"],
            "chain_scope": "recorded",
            "positions": [71, 75, 102],
            "unplaced_contacts": [],
        }
    ]
    assert bts["spans_chains"] == ["pdb:1SUX"]
    assert bts["subject_of_investigation"] == {"pdb:1SUX": True}


def test_aggregated_chains_never_imply_one_ligand_spans_them(resolver):
    # PDBe-KB attributes Asn12 of 1HTI to chain B and His96 to chain A, but the only PGA
    # instance of 1HTI contacts chain B alone. Aggregated chains are not instance data.
    pga_record = json.loads(
        Path("temp_data/pdbe_kb/ligand_sites__P60174.json").read_text(encoding="utf-8")
    )
    pga = next(d for d in pga_record["data"] if d["accession"] == "PGA")
    chains_1hti = {
        e["chainIds"]
        for r in pga["residues"]
        for e in r["interactingPDBEntries"]
        if e["pdbId"] == "1hti"
    }
    assert chains_1hti == {"A", "B"}
    site = _sites(_card(resolver, "P60174", structures=["1HTI"]))["pdb.ligand:PGA"]
    assert site["spans_chains"] == []
    # Without instance-level data, spanning is unknown, not "no".
    unknown = _sites(_card(resolver, "P60174"))["pdb.ligand:PGA"]
    assert (unknown["instances"], unknown["spans_chains"]) == ([], None)


def test_rcsb_contacts_are_mapped_to_uniprot_numbering():
    entry = json.loads(Path("temp_data/rcsb/1HTI.json").read_text(encoding="utf-8"))
    (rel,) = map_structure_entities(entry, "x")["relationships"]
    (pga,) = rel["qualifiers"]["ligands"]
    (instance,) = pga["instances"]
    first = instance["contacts"][0]
    # The construct lacks the initiator Met: structure residue 11 is UniProt Asn12.
    assert (first["seq_id"], first["position"], first["residue"]) == (11, 12, "ASN")
    assert first["uniprot"] == "P60174"
    shuffled = json.loads(json.dumps(entry))
    random.Random(7).shuffle(shuffled["polymer_entities"])
    assert map_structure_entities(shuffled, "x") == map_structure_entities(entry, "x")


def test_both_relevance_statements_are_kept_apart(resolver):
    sites = _sites(_card(resolver, "P52270", structures=["1SUX"]))
    # PDBe-KB does not flag glycerol or sulfate as solvents; the PDB flag says sulfate is
    # not what 1SUX studies. Neither statement overrides the other.
    assert sites["pdb.ligand:GOL"]["is_solvent"] is False
    assert sites["pdb.ligand:SO4"]["is_solvent"] is False
    assert sites["pdb.ligand:SO4"]["subject_of_investigation"] == {"pdb:1SUX": False}


def test_a_card_without_annotated_sites_says_so():
    card = Card(meta={"card_id": "sabueso:protein:uniprot:X"})
    assert ligand_sites_view(card)["items"] == []
    stub = Card(
        meta={"card_id": "sabueso:protein:uniprot:P52270"},
        relationship_store=_card_relationships(),
    )
    (item,) = ligand_sites_view(stub)["items"]
    assert item["site_class"] == "no_annotated_sites"


def _card_relationships():
    from sabueso.core.relationship_store import make_relationship

    return [
        make_relationship(
            "uniprot:P52270",
            "has_ligand_site",
            "pdb.ligand:BTS",
            qualifiers={
                "numbering": "uniprot",
                "residues": [{"start": 71, "end": 71, "residue": "ARG"}],
            },
            source_assertion_ids=["SA_x"],
        )
    ]


def test_outcomes_are_recorded(resolver):
    absent, _ = resolve_protein_card(
        "P60174",
        resolver,
        ligand_sites=True,
        pdbe_kb_client=FixturePDBeKBClient("/nonexistent"),
    )
    assert absent.quality["enrichments"][0]["status"] == "not_found"
    with pytest.warns(EnrichmentFailedWarning, match="PDBe-KB could not be consulted"):
        failing, _ = resolve_protein_card(
            "P60174",
            resolver,
            ligand_sites=True,
            pdbe_kb_client=FixturePDBeKBClient("temp_data", failing={"P60174"}),
        )
    assert failing.quality["enrichments"][0]["status"] == "error"
    assert failing.relationships("has_ligand_site") == []


def test_sites_reach_the_ligand_deck_and_its_crossing(resolver):
    chembl = FixtureChEMBLClient("temp_data")
    card = _card(
        resolver, "P52270", structures=["1SUX"], chembl={}, chembl_client=chembl
    )
    deck = ligand_deck(
        card, chembl_client=chembl, ccd_client=FixtureCCDClient("temp_data")
    )
    excluded = {e["ref"]: e["reason"] for e in deck.meta["excluded_structure_ligands"]}
    # PDBe-KB ligands from structures the card has not fetched: flag unknown, listed.
    assert excluded["pdb.ligand:GOL"] == "subject_of_investigation_unknown"
    assert excluded["pdb.ligand:SO4"] == "not_subject_of_investigation"
    bts = next(
        i for i in card.ligands(deck)["items"] if "pdb.ligand:BTS" in i["records"]
    )
    assert bts["bioactivity"]["class"] == "weak"  # IC50 33 uM
    assert bts["sites"] == [
        {
            "ligand_ref": "pdb.ligand:BTS",
            "positions": [71, 75, 102],
            "site_class": "no_annotated_overlap",
            "spans_chains": ["pdb:1SUX"],
        }
    ]


# InterPro family sites: positioned by the source on each protein's own sequence.


def _with_family_sites(resolver, accession, structures=()):
    from sabueso.tools.db.interpro import FixtureInterProClient

    return _card(
        resolver,
        accession,
        structures=structures,
        family_sites=True,
        interpro_client=FixtureInterProClient("temp_data"),
    )


def test_family_sites_are_placed_on_each_sequence_by_the_source(resolver):
    def triad(card):
        return next(
            a["positions"]
            for a in card.ligand_sites()["annotated_sites"]
            if a["description"] == "catalytic triad"
        )

    human = _with_family_sites(resolver, "P60174")
    parasite = _with_family_sites(resolver, "P52270")
    # One CDD model (cd00311), placed by InterPro on each sequence: the parasite
    # enzyme's catalytic glutamate is residue 168, the human one's 166.
    assert (triad(human), triad(parasite)) == ([14, 96, 166], [14, 96, 168])
    enrichment = next(
        e for e in human.quality["enrichments"] if e["source"] == "InterPro"
    )
    assert (enrichment["status"], enrichment["version"], enrichment["count"]) == (
        "added",
        "110.0",
        3,
    )
    (sa_id,) = [
        i
        for i in human.get("features_positional.family_site")["source_assertion_ids"]
        if human.source_assertion_store.get(i)["asserted_value"]["description"]
        == "catalytic triad"
    ]
    assertion = human.source_assertion_store.get(sa_id)
    assert (
        assertion["subject_ref"] == "uniprot:P60174"
    )  # InterPro keys proteins by UniProt
    assert assertion["source_metadata"] == {
        "member_database": "cdd",
        "signature": "cd00311",
    }


def test_each_overlap_names_its_annotation_and_source(resolver):
    sites = _sites(_with_family_sites(resolver, "P52270", structures=["1SUX"]))
    sulfate = {
        (o["source"], o["description"] or o["kind"]): o["matched"]
        for o in sites["pdb.ligand:SO4"]["annotated_overlap"]
    }
    # Sulfate sits in the phosphate-binding part of the substrate site.
    assert sulfate[("InterPro", "substrate binding site")] == [14, 174, 214, 235, 236]
    # BTS touches no annotation, including the family's dimer interface.
    assert sites["pdb.ligand:BTS"]["annotated_overlap"] == []


def test_no_site_residues_is_not_found():
    from sabueso.core.errors import RecordNotFoundError
    from sabueso.tools.db.interpro import FixtureInterProClient

    with pytest.raises(RecordNotFoundError, match="does not know it"):
        FixtureInterProClient("temp_data").site_residues("P00000")
