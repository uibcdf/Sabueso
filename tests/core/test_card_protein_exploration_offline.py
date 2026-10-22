"""Human protein journey over public captured data; negative variants are synthetic."""

import json
import socket
from pathlib import Path

import pytest
from argdigest import UnknownArgumentError

from sabueso.core.card import Card
from sabueso.core.errors import ArgumentError

PUBLIC = Path("temp_data/frozen_cards/schema_0.3.9__P52270.json")


@pytest.fixture(autouse=True)
def no_queries(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Human exploration must remain within its captured data")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


@pytest.fixture
def card():
    return Card.from_dict(json.loads(PUBLIC.read_text()))


def pick(view, label):
    return view.filter("label", equals=label).items()[0]


def test_opening_question_function_original_source_and_exact_return(card, monkeypatch):
    original = PUBLIC.read_bytes()
    serialize, calls = card.to_dict, []
    monkeypatch.setattr(card, "to_dict", lambda: (calls.append(True), serialize())[1])
    explorer = card.explore()
    opening = explorer.overview()
    text = repr(opening)
    for fact in (
        "Trypanosoma cruzi",
        "P52270",
        "251 residues",
        "EC: 5.3.1.1",
        "UniProt",
    ):
        assert fact in text
    assert "Function description: not retained" in text
    assert "current sources have not been queried" in text
    assert opening.items()[0].label == "Protein function"
    function = opening.items()[0].open()
    assert function.back() is opening
    questions = explorer.questions()
    answer = questions.items()[0].open()
    assert answer.back() is questions
    assert answer.request == {
        "question": "function",
        "topic": "function",
        "options": {},
    }
    assert answer.result_ref == function.result_ref
    selected = answer.filter("label", equals="Catalytic activity")
    item = selected.items()[0]
    assert item.cells["value"].value[0]["ec_number"] == "5.3.1.1"
    assert item.kind == "field"
    assert item.cells["type"].value == "array"
    assert item.open().request == answer.request
    assert (
        item.open().native_payload == card.sections["annotations"]["catalytic_activity"]
    )
    explanation = item.explain()
    assert explanation.back() is selected
    assert explanation.request == answer.request
    source = explanation.items()[0]
    assert "UniProt" in source.label
    record = source.open().native_payload
    assert record["field_path"] == "annotations.catalytic_activity"
    assert record["asserted_value"] in item.cells["value"].value
    assert record == next(
        row
        for row in card.source_assertion_store.to_list()
        if row["id"] == record["id"]
    )
    assert source.open().back() is explanation
    assert source.open().request == answer.request
    assert explanation.back().back() is answer
    card.sections.clear()
    assert "Trypanosoma cruzi" in repr(opening)
    assert explorer.answer("function").result_ref == answer.result_ref
    assert calls == [True]
    assert PUBLIC.read_bytes() == original


def test_explicit_region_question_reuses_native_result_and_machine_selection(
    card, monkeypatch
):
    import sabueso.core.structures as readers

    explorer = card.explore()
    options = {"sequence_ref": "uniprot:P52270", "region": [[170, 180]]}
    answer = explorer.answer("region_coverage", options=options)
    expected = explorer.view("structures", options={"region": list(range(170, 181))})
    assert answer.result_ref == expected.result_ref
    assert answer.native_payload == expected.native_payload
    assert (
        explorer.access.select(
            "structures", options={"region": [[170, 180]]}
        ).result_ref
        == answer.result_ref
    )
    assert answer.request["options"]["region"] == list(range(170, 181))
    assert answer.request["options"]["include_fragments"] is False
    assert "region coordinate annotations not retained" in repr(answer)
    assert "Requested region" in answer.table()._repr_html_()
    assert "does not establish coordinate completeness" in repr(answer)
    monkeypatch.setattr(
        readers, "structure_inventory", lambda *a, **k: pytest.fail("Reader rerun")
    )
    selected = answer.filter("structure_ref", equals="pdb:1SUX")
    assert selected.request == answer.request
    assert selected.view_ref != expected.view_ref
    item = selected.items()[0]
    assert item.open().back() is selected and item.explain().back() is selected
    assert item.explain().request == answer.request
    assert item.open().native_payload["missing_in_region"] == {"A": [], "B": []}
    assert item.open().native_payload["complete_chains"] == ["A", "B"]
    assert (
        explorer.answer("region_coverage", options=options).result_ref
        == answer.result_ref
    )
    options["region"].clear()
    request = answer.request
    request["options"].clear()
    assert answer.request["options"]["region"] == list(range(170, 181))


@pytest.mark.parametrize(
    "options,status",
    [
        ({}, "missing_prerequisite"),
        ({"region": [1]}, "missing_prerequisite"),
        ({"sequence_ref": "uniprot:P52270"}, "missing_prerequisite"),
        ({"sequence_ref": "uniprot:P60174", "region": [1]}, "unsupported"),
        ({"sequence_ref": "uniprot:P52270-1", "region": [1]}, "unsupported"),
        ({"sequence_ref": "pdb:1SUX:A", "region": [1]}, "unsupported"),
    ],
)
def test_missing_or_foreign_scope_never_runs_reader(card, monkeypatch, options, status):
    import sabueso.core.structures as readers

    monkeypatch.setattr(
        readers, "structure_inventory", lambda *a, **k: pytest.fail("Unscoped reader")
    )
    explorer = card.explore()
    result = explorer.answer("region_coverage", options=options)
    assert result.outcome["status"] == status
    assert not result.items()
    assert result.coverage["classification"] == "not_evaluated"
    assert result.filter("label", equals="anything").outcome == result.outcome
    assert result.native_payload["options"] == result.request["options"]
    if options:
        assert result.result_ref != explorer.answer("region_coverage").result_ref
    assert (
        explorer.questions().items()[1].open().outcome["status"]
        == "missing_prerequisite"
    )


@pytest.mark.parametrize("mutation", ["identity", "sequence", "length", "conflict"])
def test_inconsistent_canonical_context_is_a_prerequisite_gap(card, mutation):
    if mutation == "identity":
        card.meta["card_id"] = "sabueso:protein:uniprot:OTHER"
    elif mutation == "sequence":
        card.sections["sequence"].pop("primary")
    elif mutation == "length":
        card.sections["sequence"]["length"]["value"] = 250
    else:
        card.quality["conflicts"] = [
            {"field": "sequence.primary", "values": ["synthetic-a", "synthetic-b"]}
        ]
    result = card.explore().answer(
        "region_coverage", options={"sequence_ref": "uniprot:P52270", "region": [1]}
    )
    assert result.outcome["status"] == "missing_prerequisite"


@pytest.mark.parametrize(
    "options",
    [
        [],
        {"sequence_ref": [], "region": [1]},
        {"sequence_ref": "uniprot:P52270", "region": []},
        {"sequence_ref": "uniprot:P52270", "region": [0]},
        {"sequence_ref": "uniprot:P52270", "region": [252]},
        {"sequence_ref": "uniprot:P52270", "region": [True]},
        {"sequence_ref": "uniprot:P52270", "region": [1], "include_fragments": 1},
        {"sequence_ref": "uniprot:P52270", "region": [1], "typo": True},
    ],
)
@pytest.mark.parametrize("skip", [False, True])
def test_question_scope_errors_are_not_empty_scientific_answers(card, options, skip):
    with pytest.raises(ArgumentError):
        card.explore().answer("region_coverage", options=options, skip_digestion=skip)


@pytest.mark.parametrize("nature", [None, "small_molecule", "disease", "other"])
def test_protein_routes_do_not_leak_into_other_natures(nature):
    explorer = Card(meta={"entity_type": nature} if nature else {}).explore()
    assert "function" not in explorer.capabilities["question_keys"]
    assert "region_coverage" not in explorer.capabilities["question_keys"]
    if nature not in ("small_molecule", "disease"):
        assert explorer.capabilities["scientific_questions"] is False
        assert explorer.questions().outcome["status"] == "unsupported"
    assert explorer.view("function").outcome["status"] == "not_applicable"
    with pytest.raises(ArgumentError):
        explorer.answer("function")


def test_empty_null_conflicting_and_missing_function_are_distinct(card):
    field = {"value": None, "source_assertion_ids": ["SA_SYNTHETIC_NOT_RETAINED"]}
    card.sections["annotations"]["function"] = field
    card.quality["conflicts"] = [
        {
            "field": "annotations.catalytic_activity",
            "values": ["synthetic-a", "synthetic-b"],
        }
    ]
    explorer = card.explore()
    view = explorer.answer("function")
    assert pick(view, "Function description").cells["value"].state == "unknown"
    assert pick(view, "Catalytic activity").cells["value"].state == "conflicting"
    missing = pick(view, "Function description").explain()
    assert len(missing.items()) == 0
    assert (
        missing.native_payload["support"][0]["statements"][0]["state"] == "not_retained"
    )
    assert view.coverage["classification"] == "not_evaluated"
    card.sections["annotations"]["function"]["value"] = []
    empty = pick(card.explore().answer("function"), "Function description")
    assert empty.cells["value"].value == [] and empty.cells["value"].state == "present"
    card.sections["annotations"].pop("function")
    gaps = card.explore().answer("function").native_payload["field_gaps"]
    assert any(row["field"] == "annotations.function" for row in gaps)


def test_sources_and_unknown_shapes_remain_literal_not_generated_function(card):
    card.sections["annotations"]["function"] = "unrecognized retained text"
    explorer = card.explore()
    assert "Function description: unrecognized retained field" in repr(explorer)
    assert (
        explorer.inspect("annotations.function").native_payload
        == "unrecognized retained text"
    )
    assert not any(
        item.label == "Function description"
        for item in explorer.view("function").items()
    )
    gap = next(
        row
        for row in explorer.view("function").native_payload["field_gaps"]
        if row["field"] == "annotations.function"
    )
    assert gap["state"] == "unrecognized_shape"
    assert (
        explorer.inspect(locator=gap["location"]).native_payload
        == "unrecognized retained text"
    )
    with pytest.raises(ArgumentError):
        explorer.answer("function", options={"region": [1]})
    with pytest.raises(ArgumentError):
        explorer.answer([], skip_digestion=True)
    with pytest.raises(ArgumentError):
        explorer.answer("invented_question")
    with pytest.raises(UnknownArgumentError):
        explorer.answer("function", typo=True)


def test_html_is_inert_and_escaped_and_preview_does_not_materialize_rows(
    card, monkeypatch
):
    card.sections["annotations"]["function"] = {
        "value": "<script>" + "α" * 10000,
        "source_assertion_ids": [],
    }
    explorer = card.explore()
    view = explorer.view("function")
    monkeypatch.setattr(
        type(view), "rows", lambda *a: pytest.fail("Full row materialization")
    )
    assert "<script>" not in view._repr_html_()
    assert "&lt;script&gt;" in view._repr_html_()
    assert len(repr(explorer)) < 5000
    value = pick(view, "Function description").cells["value"].value
    assert len(value) == 10008
    assert "source attribution not retained" in repr(view)


def test_missing_source_metadata_does_not_become_retained_null(card):
    record = card.source_assertion_store.to_list()[0]
    record["source"].pop("version", None)
    record.pop("retrieved_at", None)
    raw = card.to_dict()
    raw["source_assertion_store"][0] = record
    explorer = Card.from_dict(raw).explore()
    sources = explorer.view("sources")
    item = next(item for item in sources.items() if item._entry.key == record["id"])
    selected = sources.filter("label", equals=item.label)
    assert "source version unknown" in repr(selected)
    assert "retrieved unknown" in repr(selected)
    assert "version" not in item.open().native_payload["source"]
