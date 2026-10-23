"""Readable structural support over public data; altered variants are synthetic."""

import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.core.errors import StorageError


def forbidden(*args, **kwargs):
    raise AssertionError("No source query or new scientific interpretation")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


@pytest.fixture
def card():
    return Card.from_dict(
        json.loads(Path("temp_data/frozen_cards/schema_0.3.9__P52270.json").read_text())
    )


def selected(card):
    return card.explore().view("structures").filter("structure_ref", equals="pdb:1SUX")


def relationship(card):
    return card.relationships("has_structure", object_ref="pdb:1SUX")[0]


def test_public_structural_support_opens_real_sources_and_retains_exact_science(card):
    view = selected(card)
    item = view.items()[0]
    original = item.open().native_payload
    explanation = item.explain()
    native = explanation.native_payload
    assert native["structure_ref"] == "pdb:1SUX"
    assert native["item"] == original
    refs = relationship(card)["source_assertion_ids"]
    assert [row._entry.key for row in explanation.items()] == list(dict.fromkeys(refs))
    assert explanation.items()
    for row in explanation.items():
        assert row.label.startswith("Relationship support · ")
        record = row.open()
        assert record.native_payload == card.source_assertion_store.get(row._entry.key)
        assert record.back() is explanation
    text = repr(explanation)
    for content in (
        "Why this structure is shown: pdb:1SUX",
        "grouped by retained structural state",
        "structure_inventory_explanation@1",
        "Sequence state: reference",
        "Complex state: False",
        "not individual qualifiers or the derived grouping",
        "does not establish coordinate completeness",
        "Open a source record below",
    ):
        assert content in text
    assert explanation.back() is view
    assert explanation.native_payload == native


def test_readable_support_does_not_rerun_readers_or_copy_original_body(
    card, monkeypatch
):
    import sabueso.core.structure_explanation as explainers
    import sabueso.core.structures as readers

    view = selected(card)
    monkeypatch.setattr(explainers, "explain_structure_inventory", forbidden)
    monkeypatch.setattr(readers, "structure_inventory", forbidden)
    explanation = view.items()[0].explain()
    monkeypatch.setattr(type(explanation), "native_payload", property(forbidden))
    assert "Why this structure" in repr(explanation)
    assert "Why this structure" in explanation.table()._repr_html_()


@pytest.mark.parametrize("remove_all", [False, True])
def test_missing_relationship_sources_are_visible_without_fabricated_rows(
    card, remove_all
):
    refs = relationship(card)["source_assertion_ids"]
    drop = set(refs if remove_all else refs[:1])
    for ref in drop:
        card.source_assertion_store.store.pop(ref)
    view = selected(card)
    explanation = view.items()[0].explain()
    assert "relationship source records not retained" in repr(explanation)
    assert not any(row._entry.key in drop for row in explanation.items())
    assert bool(explanation.items()) is not remove_all
    assert explanation.back() is view


def test_undeclared_relationship_source_list_is_not_source_absence(card):
    rel = relationship(card)
    rel["source_assertion_ids"] = []
    card.relationship_store.store[rel["id"]] = rel
    explanation = selected(card).items()[0].explain()
    assert "No source references are declared" in repr(explanation)
    assert not explanation.items()


def test_literal_explanation_lookalike_never_gets_scientific_presentation(card):
    from copy import deepcopy

    view = selected(card)
    original = deepcopy(
        view._selection._scientific.wire["explanations"][view.items()[0]._entry.key]
    )
    generic = Card(meta={"entity_type": "other"})
    generic.unknown_stored["lookalike"] = original
    view = generic.explore().inspect()
    lookalike = view.filter("label", equals="lookalike").items()[0].open()
    assert "Why this structure" not in repr(lookalike)
    assert {item.label for item in lookalike.items()} >= {"card_id", "rule", "members"}


def test_new_saved_support_reopens_inertly_with_complete_original_sources(
    card, tmp_path
):
    view = selected(card)
    explanation = view.items()[0].explain()
    path = tmp_path / "support.json"
    receipt = explanation.save(path)
    original = path.read_bytes()
    saved = sabueso.read_exploration(path, expected_digest=receipt["bundle_digest"])
    assert [row.label for row in saved.items()] == [
        row.label for row in explanation.items()
    ]
    assert "Why this structure is shown" in repr(saved)
    assert saved.back().view_ref == view.view_ref
    script = """
import socket, sys
from unittest.mock import patch
import sabueso
from sabueso.core.card import Card
def forbidden(*args, **kwargs):
    raise AssertionError('No source acquisition, Card construction or scientific reading')
with patch.object(Card, 'from_dict', forbidden), patch.object(Card, 'structures', forbidden), patch('socket.socket.connect', forbidden):
    view=sabueso.read_exploration(sys.argv[1], expected_digest=sys.argv[2])
    assert 'Why this structure is shown' in repr(view)
    assert view.items()[0].open().native_payload['source']
    assert view.back().items()[0].explain().view_ref == view.view_ref
"""
    subprocess.run(
        [sys.executable, "-c", script, str(path), receipt["bundle_digest"]], check=True
    )
    assert path.read_bytes() == original


def test_saved_support_cannot_silently_drop_an_original_source(card, tmp_path):
    view = selected(card).items()[0].explain()
    assert view.items()
    from dataclasses import replace

    # A locally constructed invalid presentation must fail before replacing output.
    changed = replace(
        view, _selected=(), _selection=replace(view._selection, _entries=())
    )
    with pytest.raises(StorageError, match="assertion membership"):
        changed.save(tmp_path / "invalid.json")


def test_source_text_is_bounded_and_escaped_in_the_structural_explanation(card):
    ref = relationship(card)["source_assertion_ids"][0]
    record = card.source_assertion_store.get(ref)
    record["source"]["record_id"] = "<script>untrusted</script>" + "x" * 2000
    view = selected(card).items()[0].explain().table()
    html = view._repr_html_()
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "x" * 2000 not in html
    assert any(
        "x" * 2000 in row.open().native_payload["source"]["record_id"]
        for row in view.items()
    )


def test_region_explanation_keeps_its_question_and_effective_scientific_options(card):
    answer = card.explore().answer(
        "region_coverage",
        options={"sequence_ref": "uniprot:P52270", "region": [(1, 10)]},
    )
    view = answer.filter("structure_ref", equals="pdb:1SUX")
    explanation = view.items()[0].explain()
    text = repr(explanation)
    assert "Question: region_coverage" in text
    assert "canonical region positions 1, 2, 3" in text
    assert explanation.request == answer.request
    assert explanation.back() is view


def test_frozen_historical_explanation_keeps_its_recorded_items(
    card, tmp_path, monkeypatch
):
    import gzip

    data = Path("tests/core/data/card_exploration_science_v2.json.gz").read_bytes()
    path = tmp_path / "original.json"
    original = gzip.decompress(data)
    path.write_bytes(original)
    monkeypatch.setattr(Card, "from_dict", forbidden)
    root = sabueso.read_exploration(path)
    view = root.explorer.view("structures").filter("structure_ref", equals="pdb:1SUX")
    explanation = view.items()[0].explain()
    assert {row.label for row in explanation.items()} >= {"card_id", "members", "rules"}
    text = repr(explanation)
    assert "Why this structure is shown: pdb:1SUX" in text
    assert "related() links to follow original sources" in text
    assert explanation.back() is view
    assert path.read_bytes() == original
