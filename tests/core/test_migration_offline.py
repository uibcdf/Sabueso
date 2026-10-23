"""Honest migration of stored cards, completed by a refresh (uibcdf/sabueso#51)."""

import copy
import json
from pathlib import Path

import pytest

import sabueso
from sabueso.core import migration
from sabueso.core.card import CARD_SCHEMA_VERSION, Card
from sabueso.core.errors import StorageError
from sabueso.core.snapshot import snapshot_id
from sabueso.resolver import EntityResolver, FixtureRCSBClient, FixtureUniProtClient
from sabueso.tools.db.chembl import FixtureChEMBLClient

FROZEN = sorted(Path("temp_data/frozen_cards").glob("schema_*__*.json"))


def _data(name="schema_0.3.0__P52270.json"):
    return json.loads(Path("temp_data/frozen_cards", name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", FROZEN, ids=[p.name for p in FROZEN])
def test_every_published_card_migrates_and_its_original_is_kept(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    before = copy.deepcopy(data)
    card = sabueso.migrate_card(data)
    assert card.meta["schema_version"] == CARD_SCHEMA_VERSION
    (record,) = card.quality["migration"]
    assert record["rule"] == "card_migration@1"
    assert record["original_schema"] == before["meta"]["schema_version"]
    assert record["original_snapshot"] == snapshot_id(before)
    assert data == before  # the original is never changed
    assert (
        Card.from_dict(json.loads(json.dumps(card.to_dict()))).to_dict()
        == card.to_dict()
    )


def test_gaps_say_what_a_refresh_would_bring_and_what_can_be_asked_for():
    (step,) = sabueso.migrate_card(_data()).quality["migration"][0]["steps"]
    kinds = {g["path"]: g["kind"] for g in step["gaps"]}
    assert kinds["annotations.taxon_id"] == "missing"  # a fresh build states it
    assert kinds["annotations.taxonomy"] == "available"  # an enrichment to ask for
    assert "relationships.engages" not in kinds  # only a curator adds it
    recent = sabueso.migrate_card(_data("schema_0.3.3__P60174.json"))
    gaps = [g for s in recent.quality["migration"][0]["steps"] for g in s["gaps"]]
    # Since 0.3.4, UniProt's other names: a refresh brings them.
    assert {g["path"] for g in gaps if g["kind"] == "missing"} == {
        "names.synonyms",
        "names.abbreviations",
        "names.gene_names",
        "relationships.has_structure.construct",
        "relationships.has_structure.author_numbering",  # since 0.3.5
        "relationships.has_structure.derivation",  # scoped RCSB contact basis, 0.3.14
        "identifiers.ensembl_transcripts",  # since 0.3.10
        "annotations.isoforms",  # since 0.3.6
        "annotations.alternative_products",
        "features_positional.alternative_sequence",
        "features_positional.secondary_structure",
        "relationships.has_structure.secondary_structure",
        "source_assertion_store[].acquisition",  # since 0.3.7: how each entered
        "annotations.activity_regulation",  # since 0.3.13: native UniProt statements
        "annotations.domain_notes",
        "annotations.similarity",
        "annotations.source_cautions",
        "annotations.miscellaneous",
        "features_positional.domains",
        "features_positional.chain",
        "features_positional.lipidation",
        "features_positional.motif",
        "features_positional.region",
        "features_positional.sequence_conflict",
        "features_positional.topological_domain",
        "features_positional.transmembrane",
    }


def test_the_store_keeps_the_original_and_the_migrated_card(tmp_path):
    store = sabueso.KnowledgeStore(tmp_path / "k.db")
    card = sabueso.migrate_card(_data(), store=store)
    history = store.history(card.id)
    assert [h["schema_version"] for h in history] == ["0.3.0", CARD_SCHEMA_VERSION]
    assert store.load(history[0]["ref"]).meta["schema_version"] == "0.3.0"


def test_what_cannot_be_migrated_is_refused():
    newer = _data()
    newer["meta"]["schema_version"] = "9.0.0"
    with pytest.raises(StorageError, match="newer"):
        sabueso.migrate_card(newer)
    other_line = _data()
    other_line["meta"]["schema_version"] = "0.2.0"
    with pytest.raises(
        StorageError, match="No migration from card schema line 0.2 to 0.3"
    ):
        sabueso.migrate_card(other_line)
    with pytest.raises(StorageError, match="migrate_card"):
        Card.from_dict(other_line)


def test_steps_between_lines_chain_and_record_what_they_did(monkeypatch):
    # A constructed step: a 0.2 card stored its SourceAssertions under another key.
    def step(data):
        data = dict(data)
        data["source_assertion_store"] = data.pop("evidence_store")
        return data, {
            "converted": ["evidence_store → source_assertion_store"],
            "gaps": [
                {"path": "quantities of 0.2", "kind": "missing", "filled_by": "refresh"}
            ],
        }

    monkeypatch.setitem(migration.STEPS, ("0.2", "0.3"), step)
    old = _data()
    old["meta"]["schema_version"] = "0.2.0"
    old["evidence_store"] = old.pop("source_assertion_store")
    card = sabueso.migrate_card(old)
    steps = card.quality["migration"][0]["steps"]
    assert [(s["from"], s["to"], s["step"]) for s in steps] == [
        ("0.2.0", "0.3.0", "between_lines"),
        ("0.3.0", CARD_SCHEMA_VERSION, "within_line"),
    ]
    assert steps[0]["converted"] == ["evidence_store → source_assertion_store"]
    assert card.source_assertion_store.to_list()


def test_a_refresh_completes_the_gaps_and_reapplies_curations(tmp_path):
    resolver = EntityResolver(
        FixtureUniProtClient("temp_data"), rcsb_client=FixtureRCSBClient("temp_data")
    )
    curated, _ = sabueso.resolve("P52270", resolver=resolver)
    curated.add_literature_assertion(
        "annotations.subunit", "Homodimer", "pubmed:9761683", "curator-a"
    )
    curations = sabueso.CurationStore(tmp_path / "curation.jsonl")
    curations.save(curated)

    card = sabueso.migrate_card(_data())
    store = sabueso.KnowledgeStore(tmp_path / "k.db")
    from sabueso._private.smonitor.warnings import EnrichmentTruncatedWarning

    with pytest.warns(EnrichmentTruncatedWarning):  # the card was built with limit 25
        refreshed, _ = sabueso.refresh_card(
            card,
            curations=curations,
            store=store,
            resolver=resolver,
            chembl_client=FixtureChEMBLClient("temp_data"),
        )
    record = refreshed.quality["migration"][-1]
    assert record["refresh_of"] == card.pinned_ref()
    assert record["options"] == ["chembl", "structures"]  # as the card was built
    assert {
        "annotations.taxon_id",
        "annotations.lineage",
        "identifiers.gene_loci",
    } <= set(record["completed"])
    assert (
        "annotations.disease" in record["not_stated"]
    )  # UniProt states none for TcTIM
    assert refreshed.quality["curation_store"]["applied"] == 1
    assert len(refreshed.relationships("has_bioactivity")) == 25  # the recorded limit
    assert store.history(card.id)[-1]["note"] == "refreshed from the sources"


def test_every_schema_version_says_what_it_added():
    from sabueso.core.schema_version import parse

    versions = sorted(
        (p.stem.split("_")[-1] for p in Path("schemas").glob("card_schema_0.3.*.yaml")),
        key=parse,
    )
    missing = [
        v for v in versions if v != "0.3.0" and v not in migration.SCHEMA_CHANGES
    ]
    assert missing == [], "add what these versions added to migration.SCHEMA_CHANGES"
    assert versions[-1] == CARD_SCHEMA_VERSION
