"""Original literal support survives intake, storage and refresh without curation."""

import json
from copy import deepcopy
from pathlib import Path

import ackredit
import pytest

import sabueso
from sabueso._private.smonitor.warnings import AttributionTrackingWarning
from sabueso.core import attribution as adapter
from sabueso.core.card import CARD_SCHEMA_VERSION, Card
from sabueso.core.errors import ArgumentError, SchemaError, StorageError
from sabueso.resolver import EntityResolver, FixtureUniProtClient

DATA = Path("temp_data")


@pytest.fixture(autouse=True)
def workflow():
    with ackredit.session("literal intake test"):
        yield


def extract(text="α UniProt:P60174", identifier="P60174"):
    return sabueso.extract_literature_mentions(
        text, identifier, "pubmed:40832834", "Synthetic test fragment"
    )


def build(identifier="P60174", **options):
    return sabueso.resolve(
        identifier, resolver=EntityResolver(FixtureUniProtClient(DATA)), **options
    )[0]


def test_intake_explanation_original_occurrences_terms_and_idempotency(tmp_path):
    result = extract()
    original = deepcopy(result)
    card = build()
    with sabueso.attribution() as observed, ackredit.capture("host intake") as host:
        event = card.add_literature_extraction(result)
    assert event["original_extraction"] == result["extraction_trace"]
    assert event["card_ref"] == card.pinned_ref()
    assert event["provider"]["status"] == "available"
    assert observed.literature == [event]
    assert host.attribution.to_dict()["items"]
    uses = event["provider"]["attribution"]["uses"]
    reused = [u for u in uses if u["roles"] == ["reused_reference"]]
    original_uses = result["extraction_trace"]["provider"]["attribution"]["uses"]
    assert [u["context"]["original_use"] for u in reused] == original_uses
    for assertion in result["source_assertions"]:
        assert card.source_assertion_store.get(assertion["id"]) == assertion
    explanation = card.explain_literature("pubmed:40832834")
    assert explanation["status"] == "on_card"
    supported = explanation["links"][0]["source_assertions"]
    assert all(a["acquisition"]["method"] == "rule_extraction" for a in supported)
    publication = explanation["publication"]
    assert publication["curated"] == []
    assert publication["mentions"][0]["locations"][0]["start"] == 2
    assert sabueso.CurationStore(tmp_path / "curations.jsonl").save(card)["added"] == 0
    payload = deepcopy(card.to_dict())
    card.add_literature_extraction(result)
    assert card.to_dict() == payload and result == original
    assert "original_extraction" not in json.dumps(card.to_dict())
    assert "ackredit.attribution@1" not in json.dumps(card.to_dict())
    terms = card.terms("redistribution")
    assert "Literature" in terms["sources"]


def test_store_readers_are_inert_and_explicit_replay_preserves_original_attribution(
    tmp_path,
):
    result = extract()
    store = sabueso.ExtractionStore(tmp_path / "extractions.jsonl")
    identifier = store.save(result)
    first_bytes = store.path.read_bytes()
    assert store.save(result) == identifier and store.path.read_bytes() == first_bytes
    with ackredit.session("independent receiver"):
        before = ackredit.get_attribution().to_dict()
        records = sabueso.ExtractionStore(store.path).records()
        saved = ackredit.Attribution.from_dict(
            records[0]["extraction_trace"]["provider"]["attribution"]
        )
        assert saved.to_dict() == result["extraction_trace"]["provider"]["attribution"]
        assert ackredit.get_attribution().to_dict() == before
        card = build(extractions=store.path)
        assert (
            card.literature_intake_traces[0]["original_extraction"]
            == result["extraction_trace"]
        )
        assert any(
            "reused_reference" in u["roles"]
            for u in ackredit.get_attribution().to_dict()["uses"]
        )
    records[0]["extraction_trace"]["producer"]["version"] = "modified copy"
    assert store.records() == [result]


def test_loaded_card_refresh_preserves_original_support_and_explicit_sidecar_gap(
    tmp_path, monkeypatch
):
    result = extract()
    card = build()
    card.add_literature_extraction(result)
    knowledge = sabueso.KnowledgeStore(tmp_path / "knowledge.db")
    pin = knowledge.save(card)
    with ackredit.session("saved reader"):
        before = ackredit.get_attribution().to_dict()
        loaded = knowledge.load(pin)
        assert loaded.to_dict() == card.to_dict()
        assert loaded.literature_intake_traces == []
        assert ackredit.get_attribution().to_dict() == before
    monkeypatch.setattr(
        sabueso,
        "extract_literature_mentions",
        lambda *a, **k: pytest.fail("refresh must not extract"),
    )
    refreshed, _ = sabueso.refresh_card(
        loaded, resolver=EntityResolver(FixtureUniProtClient(DATA)), store=knowledge
    )
    for assertion in result["source_assertions"]:
        assert refreshed.source_assertion_store.get(assertion["id"]) == assertion
    assert (
        refreshed.quality["literature_extractions"]
        == loaded.quality["literature_extractions"]
    )
    event = refreshed.literature_intake_traces[0]
    assert event["route"] == "stored_support"
    assert event["provider"]["status"] == "not_recorded"
    assert event["original_extraction"] is None
    assert refreshed.quality["migration"][-1]["refresh_of"] == pin
    assert knowledge.load(pin).to_dict() == card.to_dict()


def test_refresh_with_original_store_reuses_receipts_and_preserves_first_support(
    tmp_path,
):
    first = extract()
    first["extraction_trace"]["started_at"] = "2026-10-04T01:00:00+00:00"
    for a in first["source_assertions"]:
        a["retrieved_at"] = first["extraction_trace"]["started_at"]
    card = build()
    card.add_literature_extraction(first)
    later = extract()
    extractions = sabueso.ExtractionStore(tmp_path / "extractions.jsonl")
    extractions.save(later)
    loaded = Card.from_dict(card.to_dict())
    with sabueso.attribution() as observed:
        refreshed, _ = sabueso.refresh_card(
            loaded,
            extractions=extractions,
            resolver=EntityResolver(FixtureUniProtClient(DATA)),
        )
    assert (
        refreshed.source_assertion_store.get(first["source_assertions"][0]["id"])
        == first["source_assertions"][0]
    )
    assert len(observed.literature) == 1
    assert (
        refreshed.literature_intake_traces[0]["original_extraction"]
        == later["extraction_trace"]
    )
    assert refreshed.literature_intake_traces[0]["provider"]["status"] == "available"


def test_alternative_fragments_retain_all_support_and_location_forms():
    first, second = extract(), extract("ββ UniProtKB:P60174")
    card = build()
    card.add_literature_extraction(first)
    card.add_literature_extraction(second)
    (rel,) = card.relationships("mentioned_in", "pubmed:40832834")
    assert set(rel["source_assertion_ids"]) == {
        a["id"] for data in (first, second) for a in data["source_assertions"]
    }
    assert rel["qualifier_conflicts"]["locations"] == [
        first["relationships"][0]["qualifiers"]["locations"],
        second["relationships"][0]["qualifiers"]["locations"],
    ]
    refreshed, _ = sabueso.refresh_card(
        Card.from_dict(card.to_dict()),
        resolver=EntityResolver(FixtureUniProtClient(DATA)),
    )
    assert refreshed.relationships("mentioned_in", "pubmed:40832834") == [rel]


def test_empty_result_is_fragment_scoped_and_other_subject_is_never_merged(tmp_path):
    empty = extract("No explicit accession in this synthetic fragment")
    card = build()
    card.add_literature_extraction(empty)
    assert card.relationships("mentioned_in", "pubmed:40832834") == []
    record = card.quality["literature_extractions"][0]
    assert record["source_assertion_ids"] == []
    assert record["terms"]["scope"] == "supplied_text_fragment"
    before = deepcopy(card.to_dict())
    with pytest.raises(SchemaError, match="exact UniProt"):
        card.add_literature_extraction(extract("UniProt:P52270", "P52270"))
    assert card.to_dict() == before
    extractions = sabueso.ExtractionStore(tmp_path / "all.jsonl")
    extractions.save(extract("UniProt:P52270", "P52270"))
    assert extractions.apply(card) == []


@pytest.mark.parametrize(
    "change",
    [
        lambda data: data["relationships"][0]["source_assertion_ids"].append(
            "SA_missing"
        ),
        lambda data: data["source_assertions"][0]["acquisition"].update(
            method="curation"
        ),
        lambda data: data["extraction_trace"].update(rule="unknown@1"),
        lambda data: data["source_assertions"][0]["asserted_value"].update(start=-1),
        lambda data: data["extraction_trace"].update(input_sha256="0" * 64),
        lambda data: data["source_assertions"][0].update(id="SA_forged"),
    ],
)
def test_inconsistent_intake_is_rejected_before_mutation(change):
    result = extract()
    change(result)
    card = build()
    before = deepcopy(card.to_dict())
    with pytest.raises(SchemaError):
        card.add_literature_extraction(result)
    assert card.to_dict() == before and card.literature_intake_traces == []


def test_provider_failure_preserves_support_and_unknown_original_credit(monkeypatch):
    result = extract()
    monkeypatch.setattr(
        adapter,
        "_load_backend",
        lambda: (_ for _ in ()).throw(RuntimeError("provider unavailable")),
    )
    card = Card(
        meta={"card_id": "sabueso:protein:uniprot:P60174", "entity_type": "protein"}
    )
    with pytest.warns(AttributionTrackingWarning):
        event = card.add_literature_extraction(result)
    assert event["provider"]["status"] == "failed"
    assert card.source_assertion_store.get(result["source_assertions"][0]["id"])
    result["extraction_trace"]["provider"]["attribution"] = None
    event = card.add_literature_extraction(result)
    assert event["provider"]["status"] == "unavailable"


def test_migration_is_explicit_and_does_not_claim_original_extraction(tmp_path):
    original = json.loads(
        (DATA / "frozen_cards/schema_0.3.11__P60174.json").read_text()
    )
    older = Card.from_dict(original)
    with pytest.raises(SchemaError, match="Migrate"):
        older.add_literature_extraction(extract())
    assert older.to_dict() == original
    current = sabueso.migrate_card(original)
    assert current.meta["schema_version"] == CARD_SCHEMA_VERSION
    assert "literature_extractions" not in current.quality
    assert current.quality["migration"][-1]["steps"][0]["gaps"] == [
        {
            "introduced_in": "0.3.13",
            "path": path,
            "filled_by": "refresh",
            "kind": "missing",
        }
        for path in (
            "annotations.activity_regulation",
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
        )
    ] + [
        {
            "introduced_in": "0.3.14",
            "path": "relationships.has_structure.derivation",
            "filled_by": "structures",
            "kind": "missing",
        }
    ]
    current.add_literature_extraction(extract())


def test_corrupt_store_and_public_argument_types_are_rejected(tmp_path):
    path = tmp_path / "extractions.jsonl"
    store = sabueso.ExtractionStore(path)
    store.save(extract())
    lines = path.read_text().splitlines()
    row = json.loads(lines[1])
    row["id"] = "sha256:" + "0" * 64
    path.write_text(lines[0] + "\n" + json.dumps(row) + "\n")
    with pytest.raises(StorageError, match="content address"):
        store.records()
    with pytest.raises(ArgumentError):
        sabueso.ExtractionStore(None)
    with pytest.raises(ArgumentError):
        build(extractions=[])
    with pytest.raises(ArgumentError):
        build().add_literature_extraction("invalid")


@pytest.mark.parametrize("missing", ["assertion", "relationship"])
def test_refresh_reports_missing_historical_support_without_reconstruction(missing):
    result = extract()
    card = build()
    card.add_literature_extraction(result)
    if missing == "assertion":
        del card.source_assertion_store.store[result["source_assertions"][0]["id"]]
    else:
        del card.relationship_store.store[result["relationships"][0]["id"]]
    before = deepcopy(card.to_dict())
    with pytest.raises(SchemaError, match="missing original"):
        sabueso.refresh_card(card, resolver=EntityResolver(FixtureUniProtClient(DATA)))
    assert card.to_dict() == before


def test_unknown_fragment_terms_do_not_bypass_an_explicit_terms_profile():
    result = extract()
    card = build(terms="non_commercial")
    before = deepcopy(card.to_dict())
    with pytest.raises(SchemaError, match="terms-profile"):
        card.add_literature_extraction(result)
    assert card.to_dict() == before
    source = build()
    source.add_literature_extraction(result)
    with pytest.raises(SchemaError, match="terms-profile"):
        sabueso.refresh_card(
            source,
            terms="non_commercial",
            resolver=EntityResolver(FixtureUniProtClient(DATA)),
        )
