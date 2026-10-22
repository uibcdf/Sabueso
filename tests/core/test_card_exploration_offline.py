"""Human literal navigation; synthetic content is not scientific source knowledge."""

import json
import socket
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
import pyunitwizard as puw
from argdigest import UnknownArgumentError

from sabueso.core.card import Card
from sabueso.core.card_exploration import CardView, Cell
from sabueso.core.errors import ArgumentError


@pytest.fixture(autouse=True)
def forbid_queries(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Human literal exploration must not acquire source data")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def _card(data=None, nature=None):
    card = Card(meta={"entity_type": nature} if nature else {})
    card.unknown_stored["synthetic"] = {} if data is None else data
    return card


def _child(view, label):
    return next(item for item in view.items() if item.label == label)


def _synthetic(explorer):
    return _child(explorer.inspect(), "synthetic").open()


@pytest.mark.parametrize(
    "nature", [None, "protein", "small_molecule", "disease", "other"]
)
def test_generic_capture_once_and_shared_machine_context(nature, monkeypatch):
    card = _card({"nested": {"x": [False, 0, None]}}, nature)
    serialize = card.to_dict
    calls = []

    def counted():
        calls.append(True)
        return serialize()

    monkeypatch.setattr(card, "to_dict", counted)
    explorer = card.explore(related_cards=[card])
    assert calls == [True]
    assert explorer.mode == "live"
    assert explorer.profile == (
        nature if nature in ("protein", "small_molecule", "disease") else "generic"
    )
    assert explorer.context == explorer.access.context
    root = explorer.inspect()
    machine = explorer.access.read(explorer.access.root_location)
    assert root.result_ref == machine.result_ref
    assert [i.item_ref for i in root.items()] == [
        i["item_ref"] for i in machine.page()["items"]
    ]
    card.unknown_stored["synthetic"].clear()
    assert _synthetic(explorer).native_payload == {"nested": {"x": [False, 0, None]}}
    assert calls == [True]


def test_public_values_are_defensive_and_objects_read_only():
    explorer = _card({"x": [1, 2]}).explore()
    view = _synthetic(explorer)
    item = view.items()[0]
    item.cells["value"].value.clear()
    item.support.clear()
    item.payload_location.clear()
    view.native_payload.clear()
    view.context.clear()
    rows = view.rows()
    rows[0]["cells"]["value"]["value"].clear()
    assert item.cells["value"].value == [1, 2]
    for obj, key, value in (
        (view, "title", "bad"),
        (item, "label", "bad"),
        (explorer, "profile", "bad"),
        (item.cells["value"], "state", "unknown"),
    ):
        with pytest.raises((AttributeError, FrozenInstanceError)):
            setattr(obj, key, value)
    with pytest.raises(TypeError):
        item.cells["value"] = Cell(42)


def test_complete_inspection_literal_dots_unicode_and_empty_values():
    values = {
        "a.b": [False, 0, None, "", {}, [], "α🧬"],
        "value": "kept",
        "unit": "invented",
    }
    explorer = _card(values).explore()
    view = _synthetic(explorer)
    assert view.native_payload == values
    dotted = _child(view, "a.b")
    assert dotted.payload_location["segments"][-1] == {"type": "Key", "value": "a.b"}
    children = dotted.open().items()
    assert len(children) == 7
    for index, item in enumerate(children):
        assert item.cells["value"].value == values["a.b"][index]
        assert item.cells["value"].state == "present"
        assert (
            explorer.access.read(item.payload_location).page()["node"]["owner"][
                "snapshot_id"
            ]
            == explorer.context["snapshot_id"]
        )
        assert item.open().native_payload == values["a.b"][index]
    assert children[4].open().outcome["status"] == "empty"
    assert children[2].open().outcome["status"] == "ok"
    assert len(children[-2:]) == 2
    with pytest.raises(IndexError):
        children[99]


def test_navigation_preserves_selection_and_hidden_item_identity():
    explorer = _card({"b": 2, "a": 1, "c": 3}).explore()
    view = _synthetic(explorer)
    assert view.back().at_root
    assert view.back().back() is view.back()
    ordered = view.sort("label", descending=True)
    assert [item.label for item in ordered.items()] == ["c", "b", "a"]
    assert ordered.back() is view
    selected = ordered.filter("label", equals="b")
    item = selected.items()[0]
    assert item.back() is selected
    assert item.open().back() is selected
    assert item.explain().back() is selected
    assert selected.back() is ordered
    assert selected.result_ref == ordered.result_ref == view.result_ref
    assert selected.view_ref != ordered.view_ref
    assert ordered.items()[1].item_ref == item.item_ref
    hidden = selected.item(ordered.items()[0].item_ref)
    assert hidden.label == "c" and not hidden.is_selected
    assert selected.summary().result_ref == selected.table().result_ref
    assert selected.summary().view_ref != selected.table().view_ref
    empty = selected.filter("kind", equals="route")
    assert len(empty.items()) == 0 and empty.outcome["status"] == "empty"
    assert empty.coverage == selected.coverage
    assert empty.back() is selected


def test_only_delivered_topics_are_advertised_and_route_open_has_origin():
    explorer = _card().explore()
    topics = explorer.topics()
    assert len(topics.items()) == 3
    assert explorer.capabilities["scientific_topics"] == []
    assert explorer.capabilities["scientific_questions"] is False
    assert topics.items()[0].kind == "route"
    assert topics.items()[0].open().back() is topics
    assert explorer.view("sources").native_payload == []
    quality = explorer.view("coverage")
    assert quality.coverage["classification"] == "not_evaluated"
    assert explorer.questions().outcome["status"] == "unsupported"
    assert len(explorer.questions().items()) == 0
    with pytest.raises(ArgumentError):
        explorer.view("made-up")


def test_unicode_search_all_hits_and_original_locations():
    explorer = _card({f"key{i}": "Straße α🧬" for i in range(25)}).explore()
    view = explorer.search("STRASSE")
    assert len(view.items()) == 25
    assert view.native_payload["synthetic"]["key24"] == "Straße α🧬"
    assert [i.payload_location for i in view.items()] == [
        i.payload_location for i in explorer.search("STRASSE").items()
    ]
    assert view.result_ref == explorer.search("STRASSE").result_ref
    assert explorer.search("nothing matching").outcome["status"] == "empty"
    for item in view.items():
        assert item.open().native_payload == "Straße α🧬"
        assert item.open().back() is view
    key_matches = explorer.search("key24")
    assert len(key_matches.items()) == 1
    assert "24" in key_matches.items()[0].label


def test_bounded_inert_rendering_does_not_copy_rows_or_large_values(monkeypatch):
    explorer = _card(
        {
            f"<script>{i}</script>": "<img onerror=evil()>" + "z" * 10000
            for i in range(35)
        }
    ).explore()
    view = _synthetic(explorer)

    def forbidden(*args, **kwargs):
        pytest.fail("Implicit rendering must not materialize rows or Cell values")

    monkeypatch.setattr(CardView, "rows", forbidden)
    monkeypatch.setattr(Cell, "value", property(forbidden))
    text, html = repr(view), view._repr_html_()
    assert "showing 10, 25 more" in text
    assert len(text) < 4000 and len(html) < 5000
    assert "<script>" not in html and "<img " not in html
    assert "&lt;script&gt;" in html
    assert len(view.items()) == 35


def test_quantity_cells_preserve_units_under_a_different_session_default():
    card = Card(
        sections={
            "properties": {
                "physchem": {
                    "molecular_weight": {
                        "value": 260.25,
                        "unit": "dalton",
                        "source_assertion_ids": [],
                    }
                }
            }
        }
    )
    explorer = card.explore()
    with puw.context(standard_units=["nm", "ps", "K", "mole", "gram"]):
        parent = explorer.inspect("properties.physchem")
        item = parent.items()[0]
        quantity = item.cells["value"].value
        assert puw.get_value(quantity, to_unit="dalton") == pytest.approx(260.25)
        assert str(puw.get_unit(quantity)) == "dalton"
    assert item.open().native_payload["unit"] == "dalton"
    assert "dalton" in repr(parent)
    extension = _synthetic(
        _card({"lookalike": {"value": 3, "unit": "fictional"}}).explore()
    )
    assert extension.items()[0].cells["value"].value == {
        "value": 3,
        "unit": "fictional",
    }


def test_source_support_record_locations_missing_support_and_stored_conflict():
    card = _card()
    card.sections = {
        "names": {
            "canonical_name": {
                "value": "selected",
                "source_assertion_ids": ["SA_missing"],
            }
        }
    }
    card.quality = {
        "conflicts": [
            {
                "field": "names.canonical_name",
                "values": ["selected", "alternative"],
                "source_assertion_ids": [["SA_missing"], ["SA_other"]],
            }
        ]
    }
    explorer = card.explore()
    item = explorer.inspect("names").items()[0]
    assert item.cells["value"].state == "conflicting"
    assert item.cells["value"].value["value"] == "selected"
    explanation = item.explain().native_payload
    assert explanation["stored_conflicts"] == card.quality["conflicts"]
    assert explanation["support"][0]["statements"][0]["state"] == "not_retained"
    assert "Stored conflicts" in repr(explorer)


def test_public_tctim_opening_and_exact_original_support():
    path = Path("temp_data/frozen_cards/schema_0.3.9__P52270.json")
    original = path.read_bytes()
    card = Card.from_dict(json.loads(original))
    explorer = card.explore()
    assert "Triosephosphate isomerase, glycosomal" in repr(explorer)
    sources = explorer.view("sources")
    assert len(sources.items()) == len(card.source_assertion_store.to_list())
    assert any("UniProt" in item.label for item in sources.items())
    assert sources.items()[0].payload_location["segments"][-1]["type"] == "Record"
    item = explorer.inspect("names").filter("label", equals="canonical_name").items()[0]
    support = item.explain().native_payload["support"][0]
    assert support["basis"] == "original_field_support"
    for statement in support["statements"]:
        record = explorer.inspect(locator=statement["location"]).native_payload
        assert record["id"] == statement["id"]
        assert (
            "original_assertion"
            in explorer.inspect(locator=statement["location"])
            .items()[0]
            .support[0]["basis"]
        )
    assert path.read_bytes() == original


def test_supplied_related_capture_does_not_silently_switch_profile():
    focal, related = _card({"x": 1}, "protein"), _card({"x": 2}, "disease")
    explorer = focal.explore(related_cards=[related])
    capture = explorer.access._captures[explorer.context["inputs"][1]]
    location = {
        "format": "card_access_location@1",
        "kind": "card",
        "card_ref": capture.pin,
        "snapshot_id": capture.snapshot,
        "segments": [],
    }
    assert explorer.access.read(location).count > 0
    with pytest.raises(ArgumentError, match="focal capture"):
        explorer.inspect(locator=location)


@pytest.mark.parametrize("skip", [False, True])
@pytest.mark.parametrize(
    "call",
    [
        lambda e, s: e.inspect("names..x", skip_digestion=s),
        lambda e, s: e.inspect(42, skip_digestion=s),
        lambda e, s: e.inspect("names", locator={}, skip_digestion=s),
        lambda e, s: e.inspect(locator={}, skip_digestion=s),
        lambda e, s: e.search("", skip_digestion=s),
        lambda e, s: e.view("invalid", skip_digestion=s),
        lambda e, s: e.inspect().filter("value", equals=1, skip_digestion=s),
        lambda e, s: e.inspect().filter("label", equals=1, skip_digestion=s),
        lambda e, s: e.inspect().sort("label", descending=1, skip_digestion=s),
        lambda e, s: e.inspect().item("XI_" + "f" * 64, skip_digestion=s),
    ],
)
def test_bad_arguments_are_errors_not_empty_knowledge(call, skip):
    with pytest.raises(ArgumentError):
        call(_card().explore(), skip)


def test_unknown_options_do_not_become_ignored_filters():
    with pytest.raises(UnknownArgumentError):
        _card().explore().inspect(surprise=True)


def test_table_presentation_is_bounded_escaped_and_retains_result():
    view = _synthetic(_card({"<name>": "<value>"}).explore())
    table = view.table()
    assert table.back() is view
    assert table.result_ref == view.result_ref
    assert "<table>" in table._repr_html_()
    assert "&lt;name&gt;" in table._repr_html_()
    assert "<value>" not in table._repr_html_()
    assert "Index | Label | Value" in repr(table)
    assert table.rows() == view.rows()


def test_extension_support_lookalikes_do_not_become_source_lineage():
    explorer = _card(
        {"lookalike": {"value": "literal", "source_assertion_ids": ["SA_fake"]}}
    ).explore()
    item = _synthetic(explorer).items()[0]
    assert item.support[0]["basis"] == "stored_literal"
    assert "statements" not in item.support[0]
    card = Card(
        sections={
            "annotations": {
                "synthetic": {
                    "value": {"value": "nested", "source_assertion_ids": ["SA_fake"]},
                    "source_assertion_ids": ["SA_original"],
                }
            }
        }
    )
    item = card.explore().inspect("annotations.synthetic.value").items()[0]
    assert item.support[0]["source_assertion_ids"] == ["SA_original"]


def test_relationship_qualifiers_retain_only_relationship_level_support():
    from sabueso.core.relationship_store import make_relationship

    relationship = make_relationship(
        "uniprot:P52270",
        "has_structure",
        "pdb:1SUX",
        qualifiers={
            "synthetic": {"value": "literal", "source_assertion_ids": ["SA_fake"]}
        },
        source_assertion_ids=["SA_original"],
        derivation={"rule": "synthetic_test@1", "inputs": ["original-input"]},
    )
    explorer = Card(relationship_store=[relationship]).explore()
    item = _child(explorer.inspect(), "Relationships").open().items()[0]
    assert "pdb:1SUX" in item.label
    assert item.support[0]["basis"] == "relationship_level"
    assert item.support[0]["derivation"] == relationship["derivation"]
    qualifiers = _child(item.open(), "qualifiers").open()
    qualifier = qualifiers.items()[0]
    assert qualifier.support[0]["source_assertion_ids"] == ["SA_original"]
    assert (
        qualifier.explain().native_payload["support"][0]["derivation"]["rule"]
        == "synthetic_test@1"
    )


def test_unhashable_topic_with_skipped_digestion_is_an_argument_error():
    with pytest.raises(ArgumentError):
        _card().explore().view([], skip_digestion=True)


def test_display_selection_cannot_relabel_an_unsupported_operation():
    view = _card().explore().questions()
    selected = view.filter("label", equals="anything")
    assert selected.outcome == view.outcome
    assert selected.back() is view
    assert selected.sort("label").outcome == view.outcome


def test_unrecognized_retained_name_and_quality_shapes_remain_inspectable():
    card = Card(
        sections={"names": "unrecognized", "other": {"value": False}},
        quality={"conflicts": None},
    )
    explorer = card.explore()
    assert "Card overview" in repr(explorer)
    assert explorer.inspect("names").native_payload == "unrecognized"
    assert explorer.inspect("other").items()[0].cells["value"].state == "present"
