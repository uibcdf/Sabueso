"""Mapping @8 declares new instance scope; @6/@7 retain their original projection."""

import json
from pathlib import Path

import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.core.packets import KnowledgePacket, _facts, full_rules


@pytest.mark.parametrize("mapping", ["packet_aspects@6", "packet_aspects@7"])
@pytest.mark.parametrize("detail", ["full", "index"])
def test_current_and_historical_instance_scopes_never_silently_change(
    tmp_path, monkeypatch, mapping, detail
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
    # Explicitly synthetic foreign-axis contact: old projection used all positions.
    ligand["instances"][0]["contacts"][0]["uniprot"] = "P60174"
    ligand["instances"][0]["asym_id"] = None
    store = sabueso.KnowledgeStore(tmp_path / "history.db")
    store.save(card)
    query = sabueso.KnowledgeQuery("P52270", aspects=["ligand_sites"], detail=detail)
    current = sabueso.compose_packet(query, card)
    assert current.to_dict()["aspect_mapping"] == "packet_aspects@8"
    current_terms = current.terms("commercial_product", store=store)
    assert any(
        item.get("predicate") == "has_structure"
        for item in current_terms["scope"]["subject"]["items"]
    )
    assert "RCSB PDB" in current_terms["sources"]
    assert full_rules()["ligand_sites"] == [
        "annotated_site_overlap@2",
        "ligand_instance_scope@1",
    ]
    payload = current.to_dict()
    payload["aspect_mapping"] = mapping
    native_current = _facts("ligand_sites", card)
    native_legacy = _facts("ligand_sites", card, mapping=mapping)

    def bts(native):
        return next(
            row for row in native["items"] if row["ligand_ref"] == "pdb.ligand:BTS"
        )

    assert bts(native_current)["instances"][0]["positions"] == [75, 102]
    assert bts(native_legacy)["instances"][0]["positions"] == [71, 75, 102]
    assert "instance_rule" not in bts(native_legacy)
    assert bts(native_current)["spans_chains"] is None
    assert bts(native_legacy)["spans_chains"] == ["pdb:1SUX"]
    assert full_rules(mapping=mapping)["ligand_sites"] == ["annotated_site_overlap@2"]
    if detail == "full":
        payload["facts"]["ligand_sites"]["subject"] = native_legacy
    else:
        payload["facts"]["ligand_sites"]["subject"]["full_rules"] = full_rules(
            mapping=mapping
        )["ligand_sites"]
    legacy = KnowledgePacket(payload)
    assert current.same_knowledge(legacy) is None
    before = legacy.to_dict()
    pin = store.save_packet(legacy, "legacy")
    loaded = store.load_packet(pin)
    assert loaded.to_dict() == before

    # Historical terms/index reconstruction must never substitute the new reader.
    monkeypatch.setattr(
        Card,
        "ligand_sites",
        lambda *a, **k: pytest.fail("No current instance interpretation"),
    )
    assert (
        loaded.terms("commercial_product", store=store)["packet_rule"]
        == "packet_terms@1"
    )
    assert loaded.to_dict() == before


@pytest.mark.parametrize("detail", ["full", "index"])
def test_structure_flags_keep_source_support_even_without_instance_rows(
    tmp_path, detail
):
    card = Card.from_dict(
        json.loads(Path("temp_data/frozen_cards/schema_0.3.9__P52270.json").read_text())
    )
    for row in list(card.relationship_store.store.values()):
        if (
            row["predicate"] == "has_ligand_site"
            and row["object_ref"] != "pdb.ligand:BTS"
        ):
            del card.relationship_store.store[row["id"]]
        if row["predicate"] == "has_structure":
            for ligand in row.get("qualifiers", {}).get("ligands", []):
                ligand["instances"] = []
    store = sabueso.KnowledgeStore(tmp_path / "flags.db")
    store.save(card)
    packet = sabueso.compose_packet(
        sabueso.KnowledgeQuery("P52270", aspects=["ligand_sites"], detail=detail), card
    )
    report = packet.terms("commercial_product", store=store)
    assert "RCSB PDB" in report["sources"]
    assert any(
        row.get("predicate") == "has_structure"
        for row in report["scope"]["subject"]["items"]
    )
