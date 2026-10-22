"""Captured navigation; synthetic identities test joins, never scientific claims."""

import json
import socket
from pathlib import Path

import pytest
from argdigest import UnknownArgumentError

from sabueso.core.card import Card
from sabueso.core.errors import ArgumentError
from sabueso.core.relationship_store import make_relationship
from sabueso.core.source_assertion_store import make_source_assertion
from sabueso.tools.card.disease import resolve_disease_card
from sabueso.tools.db.mondo import FixtureMONDOClient


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Context navigation must not query sources")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def card(ref="uniprot:synthetic-A", nature="protein", name="Synthetic"):
    return Card(
        meta={"card_id": f"sabueso:{nature}:{ref}", "entity_type": nature},
        sections={
            "names": {"canonical_name": {"value": name, "source_assertion_ids": []}}
        },
    )


def edge(owner, target, predicate="associated_with", *, missing=False):
    source = make_source_assertion(
        "relationships." + predicate,
        target,
        "Synthetic",
        "navigation",
        "2026-10-22",
        subject_ref=owner.meta["card_id"].split(":", 2)[2],
    )
    if not missing:
        owner.source_assertion_store.add(source)
    rel = make_relationship(
        source["subject_ref"], predicate, target, source_assertion_ids=[source["id"]]
    )
    owner.relationship_store.add(rel)
    return rel


def relation(explorer, ref=None):
    view = explorer.inspect()
    store = next(item for item in view.items() if item.label == "Relationships").open()
    return next(item for item in store.items() if ref is None or item._entry.key == ref)


def role(links, key):
    return links.filter("role", equals=key).items()[0]


def test_public_disease_parent_missing_preserves_retained_context_and_return():
    disease = resolve_disease_card(
        "MONDO:0014221", mondo_client=FixtureMONDOClient("temp_data")
    )[0]
    view = disease.explore().view("classification").sort("object_ref")
    selected = view.filter("object_ref", equals="mondo:MONDO:0002908")
    item = selected.items()[0]
    links = item.related()
    assert links.back().native_payload == item.open().native_payload
    assert links.back().back() is selected
    assert links.schema["kind"] == "link"
    assert len(links.filter("role", equals="source").items()) > 0
    target = role(links, "object")
    assert target.cells["availability"].value == "context_not_supplied"
    context = target.open()
    assert context.explorer is None
    assert (
        context.context["card_ref"] is None and context.context["snapshot_id"] is None
    )
    assert context.context["subject_ref"] == "mondo:MONDO:0002908"
    assert context.native_payload["link"]["support"][0]["basis"] == "relationship_level"
    assert context.outcome["status"] == "context_not_supplied"
    assert context.back() is target.back()
    assert "explorer is None" in repr(context)
    assert "No destination Card supplied" in context._repr_html_()
    nested = context.items()[0].open()
    assert nested.explorer is None and nested.context == context.context
    assert context.coverage["classification"] == "not_evaluated"
    assert context.coverage["quality_location"] is None


@pytest.mark.parametrize(
    "nature,ref",
    [
        ("protein", "uniprot:synthetic-B"),
        ("small_molecule", "inchikey:synthetic-B"),
        ("disease", "mondo:synthetic-B"),
        ("other", "custom:synthetic-B"),
    ],
)
def test_supplied_destination_switches_own_profile_and_returns(nature, ref):
    source, target = card(), card(ref, nature)
    edge(source, ref)
    explorer = source.explore(related_cards=[target])
    original_inputs = explorer.context["inputs"]
    links = relation(explorer).related()
    dest = role(links, "object").open()
    assert dest.explorer.profile == (nature if nature != "other" else "generic")
    assert dest.context["card_ref"] == target.pinned_ref()
    assert dest.context["inputs"] == original_inputs
    assert dest.back().back().back().back().explorer is explorer
    assert dest.explorer.view("content").back() is dest.back()
    assert explorer.profile == "protein"
    assert links.follow(role(links, "object").item_ref).context == dest.context


def test_revision_choices_are_explicit_stable_and_never_latest():
    source, first = card(), card("mondo:synthetic-B", "disease", "first")
    second = card("mondo:synthetic-B", "disease", "second")
    edge(source, "mondo:synthetic-B")
    explorer = source.explore(related_cards=[second, first, first])
    assert (
        len(explorer.context["captures"]) == 3 and len(explorer.context["inputs"]) == 4
    )
    target = role(relation(explorer).related(), "object")
    assert target.cells["availability"].value == "ambiguous"
    choices = target.open()
    assert choices.outcome["status"] == "ambiguous"
    assert len(choices.items()) == 2
    assert {i.open().context["card_ref"] for i in choices.items()} == {
        first.pinned_ref(),
        second.pinned_ref(),
    }
    assert choices.back() is target.back()
    assert all(item.open().back() is choices for item in choices.items())
    assert choices.filter("label", equals="absent").outcome["status"] == "empty"
    assert choices.sort("target_ref").outcome["status"] == "ambiguous"


def test_exact_pin_and_record_reference_never_fall_back():
    source, target = card(), card("mondo:synthetic-B", "disease")
    asserted = edge(target, "mondo:synthetic-C", "subclass_of")
    pin = target.pinned_ref()
    edge(source, pin + "#" + asserted["id"])
    explorer = source.explore(related_cards=[target])
    detail = role(relation(explorer).related(), "object").open()
    assert detail.native_payload == asserted
    assert detail.context["card_ref"] == pin
    edge(source, target.meta["card_id"] + "@sha256:" + "0" * 64)
    missing = relation(
        source.explore(related_cards=[target]), source.relationships()[-1]["id"]
    ).related()
    assert role(missing, "object").open().outcome["status"] == "context_not_supplied"


def test_source_links_missing_support_and_literal_text_are_not_joins():
    source = card()
    rel = edge(source, "mondo:synthetic-B", missing=True)
    explorer = source.explore()
    links = relation(explorer, rel["id"]).related()
    assert role(links, "source").open().outcome["status"] == "missing_prerequisite"
    assert (
        role(links, "source").explain().native_payload["rule"]
        == "retained_context_links@1"
    )
    ordinary = explorer.inspect("names").items()[0]
    assert len(ordinary.related().items()) == 0
    with pytest.raises(ArgumentError):
        explorer.inspect().follow(ordinary.item_ref)
    with pytest.raises(ArgumentError):
        links.follow("XI_" + "0" * 64)
    with pytest.raises(UnknownArgumentError):
        links.follow(role(links, "object").item_ref, pretend=True)


def test_source_assertion_link_opens_original_record_and_its_subject():
    source = card()
    edge(source, "mondo:synthetic-B")
    links = relation(source.explore()).related()
    original = role(links, "source").open()
    assert original.native_payload == source.to_dict()["source_assertion_store"][0]
    assert original.back().result_ref == links.result_ref
    subject = next(item for item in original.items() if item.label == "subject_ref")
    assert (
        role(subject.related(), "subject").open().context["card_ref"]
        == source.pinned_ref()
    )


def test_supported_identity_graph_retains_agreeing_paths_and_conflicts():
    source, one, two = (
        card(),
        card("inchikey:synthetic-X", "small_molecule"),
        card("inchikey:synthetic-Y", "small_molecule"),
    )
    edge(source, "chembl:synthetic-X")
    a = edge(one, "chembl:synthetic-X", "same_as")
    edge(two, "chembl:synthetic-X", "same_as")
    target = role(
        relation(source.explore(related_cards=[one, two])).related(), "object"
    )
    assert target.cells["availability"].value == "ambiguous"
    paths = target._entry.value["paths"]
    assert len(paths) == 2 and all(path["source_assertions"] for path in paths)
    assert paths[0]["location"]["segments"][-1]["value"] in {
        a["id"],
        two.relationships("same_as")[0]["id"],
    }
    assert len(target.open().items()) == 2


@pytest.mark.parametrize(
    "predicate,missing",
    [("same_as", True), ("possibly_same_as", False), ("ortholog_of", False)],
)
def test_unsupported_identity_cannot_join(predicate, missing):
    source, target = card(), card("inchikey:synthetic-X", "small_molecule")
    edge(source, "chembl:synthetic-X")
    edge(target, "chembl:synthetic-X", predicate, missing=missing)
    dest = role(
        relation(source.explore(related_cards=[target])).related(), "object"
    ).open()
    assert dest.explorer is None
    assert dest.outcome["status"] == (
        "missing_prerequisite" if predicate == "same_as" else "context_not_supplied"
    )


def test_capture_once_mutation_and_cycles_do_not_recapture(monkeypatch):
    source, target = card(), card("mondo:synthetic-B", "disease")
    edge(source, "mondo:synthetic-B")
    edge(target, "uniprot:synthetic-A", "subclass_of")
    explorer = source.explore(related_cards=[target, source])

    def forbidden():
        pytest.fail("Navigation must reuse captured values")

    monkeypatch.setattr(Card, "to_dict", lambda self: forbidden())
    target.sections.clear()
    dest = role(relation(explorer).related(), "object").open()
    assert "Synthetic" in repr(dest)
    back = role(
        dest.explorer.view("classification").items()[0].related(), "object"
    ).open()
    assert back.context["card_ref"] == explorer.context["card_ref"]
    assert back.explorer is not explorer
    assert len(back.context["captures"]) == 2


def test_structural_sources_and_scientific_cache_stay_bound_to_focal_capture():
    source = Card.from_dict(
        json.loads(Path("temp_data/frozen_cards/schema_0.3.9__P52270.json").read_text())
    )
    target = card("uniprot:synthetic-B")
    rel = edge(source, "uniprot:synthetic-B")
    explorer = source.explore(related_cards=[target])
    structures = explorer.view("structures")
    assert (
        len(structures.items()[0].related().filter("role", equals="source").items()) > 0
    )
    other = role(relation(explorer, rel["id"]).related(), "object").open().explorer
    empty = other.view("structures")
    assert empty.context["card_ref"] == target.pinned_ref()
    assert empty.result_ref != structures.result_ref
    assert len(empty.items()) == 0
    assert explorer.view("structures").result_ref == structures.result_ref
    coverage = other.view("coverage")
    assert coverage.context["used_captures"] == [target.pinned_ref()]
    page = other.access.read(structures.items()[0].payload_location).page()
    assert page["context"]["card_ref"] == target.pinned_ref()


def test_link_rows_are_defensive_and_bounded_escaped():
    source = card()
    edge(source, "custom:<script>evil</script>")
    links = relation(source.explore()).related()
    before = links.native_payload
    rows = links.rows()
    rows[0]["support"].clear()
    assert links.native_payload == before
    assert "&lt;script&gt;" in links.table()._repr_html_()
    assert "<script>" not in links._repr_html_()
    assert links.capabilities["follow"] is True
    assert links.schema["columns"] == links.capabilities["filter"]


def test_generic_discovery_describes_literal_quality_without_scientific_claim():
    explorer = Card().explore()
    coverage = next(i for i in explorer.topics().items() if i._entry.key == "coverage")
    assert "not evaluated" in coverage._entry.value["description"]
    assert explorer.capabilities["cross_card_navigation"] is True


def test_agreeing_paths_and_cycles_keep_all_support_without_duplicate_destination():
    source, target = card(), card("inchikey:synthetic-X", "small_molecule")
    edge(source, "chembl:synthetic-X")
    edge(target, "chembl:synthetic-X", "same_as")
    bridge = card("pubchem:synthetic-X", "small_molecule")
    edge(bridge, "chembl:synthetic-X", "same_as")
    edge(bridge, "inchikey:synthetic-X", "same_as")
    explorer = source.explore(related_cards=[target, bridge])
    link = role(relation(explorer).related(), "object")
    assert len(link._entry.value["paths"]) == 3
    assert len(link._entry.value["candidates"]) == 2
    # Remove the bridge's own global Card identity: its explicitly retained edges
    # remain usable source support, without inventing a join to an anonymous Card.
    bridge.meta.pop("card_id")
    link = role(
        relation(source.explore(related_cards=[target, bridge])).related(), "object"
    )
    assert len(link._entry.value["paths"]) == 3
    assert len(link._entry.value["candidates"]) == 1
    assert link.open().context["card_ref"] == target.pinned_ref()


def test_equal_names_and_sequences_are_not_identity_paths():
    source, target = card(), card("uniprot:synthetic-B")
    for item in (source, target):
        item.sections["sequence"] = {
            "primary": {"value": "SAME", "source_assertion_ids": []}
        }
    edge(source, "uniprot:synthetic-C")
    context = role(
        relation(source.explore(related_cards=[target])).related(), "object"
    ).open()
    assert (
        context.explorer is None and context.outcome["status"] == "context_not_supplied"
    )


def test_input_order_does_not_choose_or_change_identity_candidate_result():
    source, one, two = (
        card(),
        card("inchikey:synthetic-X", "small_molecule"),
        card("inchikey:synthetic-Y", "small_molecule"),
    )
    edge(source, "chembl:synthetic-X")
    edge(one, "chembl:synthetic-X", "same_as")
    edge(two, "chembl:synthetic-X", "same_as")
    results = [
        role(relation(source.explore(related_cards=cards)).related(), "object").open()
        for cards in ([one, two], [two, one])
    ]
    assert results[0].result_ref == results[1].result_ref
    assert [i.label for i in results[0].items()] == [
        i.label for i in results[1].items()
    ]


def test_pinned_assertion_and_wrong_item_pin_do_not_switch_to_other_revision():
    source, target = card(), card("mondo:synthetic-B", "disease")
    edge(target, "mondo:synthetic-C", "subclass_of")
    assertion = target.to_dict()["source_assertion_store"][0]
    edge(source, target.pinned_ref() + "#" + assertion["id"])
    assert (
        role(relation(source.explore(related_cards=[target])).related(), "object")
        .open()
        .native_payload
        == assertion
    )
    edge(source, target.pinned_ref() + "#SA_missing")
    result = role(
        relation(
            source.explore(related_cards=[target]), source.relationships()[-1]["id"]
        ).related(),
        "object",
    ).open()
    assert result.explorer is None
    assert result.outcome["status"] == "missing_prerequisite"


def test_exact_source_node_links_remain_accessible_and_source_roles_are_declared():
    source = card()
    rel = edge(source, "mondo:synthetic-B")
    explorer = source.explore()
    links = relation(explorer).related()
    source_link = role(links, "source")
    detail = source_link.open()
    statement = source.to_dict()["source_assertion_store"][0]
    assert detail.native_payload == statement
    assert source_link.cells["role"].value == "source"
    assert source_link.cells["availability"].value == "available"
    assert source_link.kind == "link"
    assert links.context["adapter"] == "retained_context_links@1"
    assert links.native_payload["rule"] == "retained_context_links@1"
    # Opening a subfield of the original relationship retains its endpoint roles.
    subsection = next(
        i
        for i in relation(explorer, rel["id"]).open().items()
        if i.label == "predicate"
    )
    assert len(subsection.related().filter("role", equals="object").items()) == 1


def test_entity_glossary_entry_uses_declared_reference_only():
    source = card()
    edge(source, "uniprot:synthetic-B", "interacts_with")
    explorer = source.explore()
    glossary = next(
        i for i in explorer.inspect().items() if i.label == "Entity records"
    ).open()
    entity = next(i for i in glossary.items() if i.label == "uniprot:synthetic-B")
    target = role(entity.related(), "entity").open()
    assert target.explorer is None
    assert target.native_payload["entity"] == entity._entry.value


@pytest.mark.parametrize("skip", [False, True])
def test_follow_guards_foreign_result_and_non_link_reference(skip):
    source = card()
    edge(source, "mondo:synthetic-B")
    explorer = source.explore()
    item = relation(explorer)
    links = item.related()
    with pytest.raises(ArgumentError):
        links.follow(item.item_ref, skip_digestion=skip)
    with pytest.raises(ArgumentError):
        links.follow(None, skip_digestion=skip)


def test_related_catalog_entry_never_executes_a_scientific_topic(monkeypatch):
    explorer = card().explore()

    def forbidden(*args, **kwargs):
        pytest.fail("Catalog links must not execute scientific topic readers")

    monkeypatch.setattr(type(explorer), "_topic", forbidden)
    monkeypatch.setattr(type(explorer), "_answer", forbidden)
    for catalog in (explorer.topics(), explorer.questions()):
        for item in catalog.items():
            links = item.related()
            assert links.outcome["status"] == "empty"
            assert links.back().native_payload == item._entry.value
            assert links.back().back() is catalog
