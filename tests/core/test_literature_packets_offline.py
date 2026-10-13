"""Literature indexes cite both mention kinds and keep honest acquisition gaps."""

import json
from pathlib import Path

import pytest

import sabueso
from sabueso._private.smonitor.warnings import (
    EnrichmentFailedWarning,
    EnrichmentTruncatedWarning,
)
from sabueso.core.card import Card
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.packets import KnowledgePacket
from sabueso.mappings.europepmc import STRUCTURE_MENTION_RULE
from sabueso.resolver import EntityResolver, FixtureUniProtClient
from sabueso.tools.db.europepmc import FixtureEuropePMCClient

ARTICLE = "PMC:PMC12400196"


def resolver():
    return EntityResolver(FixtureUniProtClient("temp_data"))


def query(detail="index"):
    return sabueso.KnowledgeQuery("P60174", aspects=["literature"], detail=detail)


def card(articles=ARTICLE, **options):
    return sabueso.resolve(
        "P60174",
        resolver=resolver(),
        europepmc={"article_ids": articles},
        europepmc_client=FixtureEuropePMCClient("temp_data"),
        **options,
    )[0]


def mention_rows(packet):
    return {
        r["area"]: r
        for r in packet.unknowns["subject"]["rows"]
        if r["source"] == "Europe PMC"
    }


def test_automatic_literature_acquisition_searches_bibliography_without_article_ids():
    class BibliographyOnly(FixtureEuropePMCClient):
        def __init__(self):
            super().__init__("temp_data")
            self.requests = []

        def mentions(self, accession, limit):
            self.requests.append((accession, limit))
            return super().mentions(accession, limit)

        def annotations(self, articles):
            pytest.fail("Automatic packets cannot guess article ids")

    assert query().options() == query("full").options() == {"europepmc": {}}
    client = BibliographyOnly()
    with pytest.warns(EnrichmentTruncatedWarning):
        packet = sabueso.knowledge_packet(
            query(), resolver=resolver(), europepmc_client=client
        )
    assert client.requests == [("P60174", 5000)]
    areas = packet.facts["literature"]["subject"]["areas"]
    assert areas["relationships.mentioned_in"]["count"] == 25
    assert areas["relationships.mentioned_in"]["by_source"] == {"Europe PMC": 25}
    assert "relationships.structure_mentioned_in" not in areas
    rows = mention_rows(packet)
    assert rows["relationships.mentioned_in"]["state"] == "partial"
    assert rows["relationships.mentioned_in"]["basis"]["truncated_for"] == ["P60174"]
    assert rows["relationships.structure_mentioned_in"]["state"] == "not_queried"
    assert (
        "explicit article_ids"
        in rows["relationships.structure_mentioned_in"]["basis"]["detail"]
    )


def test_prebuilt_card_mentions_are_indexed_separately_and_read_at_historical_pins(
    tmp_path,
):
    subject = card()
    store = sabueso.KnowledgeStore(tmp_path / "knowledge.db")
    store.save(subject)
    index = sabueso.compose_packet(query(), subject)
    full = sabueso.compose_packet(query("full"), subject)
    assert index.to_dict()["aspect_mapping"] == "packet_aspects@7"
    assert index.unknowns == full.unknowns
    facts = index.facts["literature"]["subject"]
    assert facts["full_rules"] == [STRUCTURE_MENTION_RULE]
    assert facts["full_views"] == ["literature", "claims"]
    for predicate in ("mentioned_in", "structure_mentioned_in"):
        area = facts["areas"][f"relationships.{predicate}"]
        (relationship,) = subject.relationships(predicate)
        assert area["count"] == 1
        assert area["by_source"] == {"Europe PMC": 1}
        assert area["relationship_ids"] == [relationship["id"]]
        assert index.item("subject", relationship["id"], store) == relationship
    publication = next(
        p
        for p in full.facts["literature"]["subject"]["publications"]["publications"]
        if p["publication_ref"] == "pubmed:40832834"
    )
    assert len(publication["mentions"]) == len(publication["structure_mentions"]) == 1
    assert (
        publication["structure_mentions"][0]["derivation"]["rule"]
        in facts["full_rules"]
    )
    (structure_mention,) = subject.relationships("structure_mentioned_in")
    context = structure_mention["qualifiers"]["structure_context"]
    # The index itself holds no quote fragments or copies of structural context.
    assert '"exact"' not in json.dumps(facts)
    assert "structure_context" not in json.dumps(facts)
    store.save_packet(index, "literature")
    assert store.load_packet(index.ref).to_dict() == index.to_dict()
    later = card("MED:18562316")  # A new acquisition has no located mentions.
    store.save(later)
    assert not later.relationships("structure_mentioned_in")
    assert store.load_packet(index.ref).to_dict() == index.to_dict()
    assert index.item("subject", structure_mention["id"], store) == structure_mention
    for identifier in (
        structure_mention["source_assertion_ids"] + context["source_assertion_ids"]
    ):
        assert index.item(
            "subject", identifier, store
        ) == subject.source_assertion_store.get(identifier)
    for identifier in context["relationship_ids"]:
        assert index.item(
            "subject", identifier, store
        ) == subject.relationship_store.get(identifier)


@pytest.mark.parametrize("detail", ["full", "index"])
def test_composing_a_bare_card_exposes_both_not_queried_areas(detail):
    subject, _ = sabueso.resolve("P60174", resolver=resolver())
    packet = sabueso.compose_packet(query(detail), subject)
    rows = mention_rows(packet)
    assert {r["state"] for r in rows.values()} == {"not_queried"}
    assert set(rows) == {
        "relationships.mentioned_in",
        "relationships.structure_mentioned_in",
    }


@pytest.mark.parametrize(
    "articles,state",
    [
        ("MED:18562316", "not_stated"),
        ("MED:1", "unavailable"),
        ([ARTICLE, "MED:1"], "partial"),
    ],
)
def test_empty_failed_and_partial_article_answers_remain_distinct_in_both_details(
    articles, state
):
    if state == "not_stated":
        subject = card(articles)
    else:
        with pytest.warns(EnrichmentFailedWarning):
            subject = card(articles)
    index = sabueso.compose_packet(query(), subject)
    full = sabueso.compose_packet(query("full"), subject)
    assert full.unknowns == index.unknowns
    rows = mention_rows(index)
    assert set(rows) == {
        "relationships.mentioned_in",
        "relationships.structure_mentioned_in",
    }
    assert {r["state"] for r in rows.values()} == {state}
    if state == "partial":
        assert all(r["basis"]["unavailable_for"] == ["MED:1"] for r in rows.values())


def test_terms_excluded_annotations_are_not_presented_as_an_empty_answer():
    subject = card(terms="commercial")
    rows = mention_rows(sabueso.compose_packet(query(), subject))
    assert {r["state"] for r in rows.values()} == {"not_queried"}
    assert all("terms_per_record" in r["basis"]["detail"] for r in rows.values())


def test_missing_search_fixture_is_unavailable_and_a_source_stated_zero_is_not_stated():
    with pytest.raises(ConnectorError, match="No saved Europe PMC search response"):
        FixtureEuropePMCClient("temp_data").mentions("P52270")
    missing = sabueso.KnowledgeQuery("P52270", aspects=["literature"], detail="index")
    with pytest.warns(EnrichmentFailedWarning):
        packet = sabueso.knowledge_packet(
            missing,
            resolver=resolver(),
            europepmc_client=FixtureEuropePMCClient("temp_data"),
        )
    assert mention_rows(packet)["relationships.mentioned_in"]["state"] == "unavailable"

    class SourceStatedZero:
        def mentions(self, accession, limit):
            raise RecordNotFoundError("The source returned zero hits", version="6.9")

    packet = sabueso.knowledge_packet(
        query(), resolver=resolver(), europepmc_client=SourceStatedZero()
    )
    assert mention_rows(packet)["relationships.mentioned_in"]["state"] == "not_stated"
    assert mention_rows(packet)["relationships.mentioned_in"]["release"] == "6.9"


def test_the_frozen_previous_mapping_reads_unchanged_and_is_not_compared(tmp_path):
    document = json.loads(
        Path(
            "temp_data/frozen_packets/packet_aspects_5__literature_index__P60174.json"
        ).read_text()
    )
    historical = KnowledgePacket(document)
    assert (
        historical.snapshot_id()
        == "sha256:ae66464608dd98a34f8e7520afbf2a794280a6d91681cb0dcde005afeabb4bc2"
    )
    assert historical.to_dict()["aspect_mapping"] == "packet_aspects@5"
    assert historical.unknowns["subject"]["rule"]["rule"] == "knowledge_state@4"
    subject = Card.from_dict(
        json.loads(
            Path("temp_data/frozen_cards/schema_0.3.10__P60174.json").read_text()
        )
    )
    assert historical.entities["subject"]["ref"] == subject.pinned_ref()
    store = sabueso.KnowledgeStore(tmp_path / "knowledge.db")
    store.save(subject)
    store.save_packet(historical, "literature")
    assert store.load_packet(historical.ref).to_dict() == document
    current = sabueso.compose_packet(query(), subject)
    assert current.unknowns["subject"]["rule"]["rule"] == "knowledge_state@5"
    assert store.load_packet(historical.ref).unknowns == document["unknowns"]
    assert current.same_knowledge(historical) is None
    assert historical.same_knowledge(current) is None
    assert set(historical.facts["literature"]["subject"]["areas"]) == {
        "relationships.described_in"
    }
    assert (
        "relationships.mentioned_in" in current.facts["literature"]["subject"]["areas"]
    )
    store.save_packet(current, "literature")
    assert [r["knowledge_changed"] for r in store.packet_history("literature")] == [
        None,
        None,
    ]
    full = sabueso.compose_packet(query("full"), subject)
    store.save_packet(full, "literature")
    assert [r["knowledge_changed"] for r in store.packet_history("literature")] == [
        None,
        None,
        None,
    ]
    assert store.load_packet(historical.ref).to_dict() == document
    rel_id = historical.facts["literature"]["subject"]["areas"][
        "relationships.described_in"
    ]["relationship_ids"][0]
    assert historical.item("subject", rel_id, store)["predicate"] == "described_in"


@pytest.mark.parametrize(
    "change,expected", [("retrieval_time", False), ("answer", True)]
)
def test_history_within_one_scope_distinguishes_new_observation_from_changed_knowledge(
    tmp_path, change, expected
):
    subject = card()
    if change == "retrieval_time":
        data = subject.to_dict()
        for assertion in data["source_assertion_store"]:
            assertion["retrieved_at"] = "a later test observation"
        later = Card.from_dict(data)
    else:
        later = card("MED:18562316")
    first = sabueso.compose_packet(query(), subject)
    second = sabueso.compose_packet(query(), later)
    assert second.same_knowledge(first) is not expected
    store = sabueso.KnowledgeStore(tmp_path / "knowledge.db")
    for observed, packet in ((subject, first), (later, second)):
        store.save(observed)
        store.save_packet(packet, "literature")
    assert [r["knowledge_changed"] for r in store.packet_history("literature")] == [
        None,
        expected,
    ]
