"""Agent display selection over public TcTIM; altered cases are synthetic."""

import importlib
import json
import socket
import subprocess
import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
import pyunitwizard as puw
from pyunitwizard import QuantityRecord
from pyunitwizard.record import RecordError

import sabueso
from sabueso.core.card import Card
from sabueso.core.errors import ArgumentError, StorageError
from sabueso.core.snapshot import canonical_json

PUBLIC = Path("temp_data/frozen_cards/schema_0.3.9__P52270.json")


def forbidden(*args, **kwargs):
    raise AssertionError("No source request or new scientific execution allowed")


@pytest.fixture(autouse=True)
def no_queries(monkeypatch):
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


@pytest.fixture
def explorer():
    return Card.from_dict(json.loads(PUBLIC.read_text(encoding="utf-8"))).explore()


def pages(selection, **kwargs):
    frames, cursor = [], None
    while True:
        frame = selection.page(cursor=cursor, **kwargs)
        assert len(canonical_json(frame).encode("utf-8")) <= kwargs.get(
            "max_bytes", 65536
        )
        frames.append(frame)
        cursor = frame["page"]["next_cursor"]
        if cursor is None:
            return frames


def refs(selection):
    return [
        i["item_ref"]
        for p in pages(selection, limit=2, max_bytes=8192)
        for i in p["items"]
    ]


def request(selection):
    return selection._access._resolve(selection._context_location)[0]["request"]


def test_filters_order_and_original_human_result_are_shared(explorer, monkeypatch):
    human = explorer.view("structures")
    sci = importlib.import_module("sabueso.core.card_scientific_access")
    monkeypatch.setattr(sci, "materialize", forbidden)
    expected = human.filter("resolution", equals=puw.quantity(2.0, "angstrom")).sort(
        "coverage", descending=True
    )
    selected = explorer.access.select(
        "structures",
        fields=["structure_ref", "resolution"],
        where={"resolution": puw.quantity(0.2, "nanometer")},
        order_by={"column": "coverage", "descending": True},
    )
    assert selected.result_ref == human.result_ref
    assert refs(selected) == [i.item_ref for i in expected.items()]
    spec = request(selected)["selection"]
    assert spec["format"] == "structure_access_selection@1"
    assert spec["underlying_count"] == len(human.items())
    assert spec["selected_count"] == selected.count
    assert (
        spec["where"]["resolution"]["manifest"]["field"]
        == "relationships.has_structure.resolution"
    )
    assert len(spec["display_exclusions"]) + selected.count == len(human.items())
    for frame in pages(selected, max_bytes=8192):
        assert frame["outcome"] == selected._scientific.wire["outcome"]
        assert frame["coverage"]["inspection_required"]
        for item in frame["items"]:
            assert item["interpretation"]["structure_kind"] == "experimental"
            assert explorer.access.explain(item["item_ref"]).count > 0


def test_membership_intersects_where_and_does_not_order_or_change_identity(explorer):
    base = explorer.access.select("structures")
    all_refs = refs(base)
    chosen = all_refs[1::2]
    first = explorer.access.select("structures", fields=[], item_refs=chosen)
    second = explorer.access.select("structures", fields=[], item_refs=chosen[::-1])
    assert first is second
    assert refs(first) == chosen
    assert first.result_ref == base.result_ref
    assert first.selection_ref != base.selection_ref
    assert explorer.access.selection(first.selection_ref) is first
    sample = first.page(max_bytes=8192)["items"][0]
    name = sample["label"]
    intersection = explorer.access.select(
        "structures", item_refs=chosen, where={"structure_ref": name}
    )
    assert refs(intersection) == [sample["item_ref"]]
    assert request(first)["selection"]["members"] == chosen
    assert first.page(max_bytes=8192)["items"][0]["cells"] == {}


def test_display_empty_is_distinct_from_empty_scientific_result(explorer):
    full = explorer.access.select("structures")
    empty = explorer.access.select("structures", item_refs=[])
    assert empty.count == 0
    assert empty.result_ref == full.result_ref
    assert empty.page()["page"]["complete"]
    assert empty.page()["outcome"] == full.page()["outcome"]
    assert request(empty)["selection"]["underlying_count"] == full.count
    assert all(
        x["reasons"] == [{"kind": "membership"}]
        for x in request(empty)["selection"]["display_exclusions"]
    )
    assert explorer.access.select("structures", where={}) is full


@pytest.mark.parametrize("descending", [False, True])
def test_sort_matches_human_missing_last_and_retries_are_stable(explorer, descending):
    human = explorer.view("structures").sort(
        "resolution", descending=descending, unit="nanometer"
    )
    selected = explorer.access.select(
        "structures",
        order_by={
            "column": "resolution",
            "descending": descending,
            "unit": "nanometer",
        },
    )
    assert refs(selected) == [i.item_ref for i in human.items()]
    first = selected.page(limit=1, max_bytes=8192)
    cursor = first["page"]["next_cursor"]
    assert selected.page(limit=2, max_bytes=8192, cursor=cursor) == selected.page(
        limit=2, max_bytes=8192, cursor=cursor
    )
    with pytest.raises(ArgumentError):
        explorer.access.select("structures").page(cursor=cursor)
    assert refs(selected) == refs(selected)


@pytest.mark.parametrize("skip", [False, True])
@pytest.mark.parametrize(
    "bad",
    [
        {"where": []},
        {"where": {"unknown": 1}},
        {"where": {"coverage": True}},
        {"where": {"coverage": float("nan")}},
        {"where": {"resolution": 2}},
        {"where": {"resolution": puw.quantity(2, "second")}},
        {"where": {"method": None}},
        {"where": {"chains": "A"}},
        {"where": {"state": {"bad": object()}}},
        {"item_refs": "XI_" + "0" * 64},
        {"item_refs": ["foreign"]},
        {"item_refs": ["XI_" + "0" * 64] * 2},
        {"order_by": []},
        {"order_by": {}},
        {"order_by": {"column": "chains"}},
        {"order_by": {"column": "state"}},
        {"order_by": {"column": "unknown"}},
        {"order_by": {"column": puw.quantity([1, 2], "angstrom")}},
        {"order_by": {"column": "method", "unit": "angstrom"}},
        {"order_by": {"column": "resolution", "unit": "second"}},
        {"order_by": {"column": "resolution", "unit": " "}},
        {"order_by": {"column": "resolution", "descending": 1}},
        {"order_by": {"column": "resolution", "extra": True}},
    ],
)
def test_invalid_grammar_is_an_argument_error_before_materialization(
    explorer, monkeypatch, skip, bad
):
    monkeypatch.setattr(
        importlib.import_module("sabueso.core.card_scientific_access"),
        "materialize",
        forbidden,
    )
    with pytest.raises(ArgumentError):
        explorer.access.select("structures", skip_digestion=skip, **bad)


def test_foreign_members_and_foreign_scientific_scope_are_errors(explorer):
    with pytest.raises(ArgumentError):
        explorer.access.select("structures", item_refs=["XI_" + "0" * 64])
    ref = refs(explorer.access.select("structures"))[0]
    with pytest.raises(ArgumentError):
        explorer.access.select(
            "structures", options={"region": [1, 10]}, item_refs=[ref]
        )


def test_ties_do_not_depend_on_input_entry_order(explorer):
    from sabueso.core.card_structure_selection_v1 import evaluate, normalize

    result = explorer.access.select("structures")._scientific
    query = normalize(None, None, {"column": "kind", "descending": True})
    first, spec = evaluate(result, query)
    other, rebound = evaluate(replace(result, entries=result.entries[::-1]), query)
    assert [e.key for e in first] == [e.key for e in other]
    assert spec == rebound


def test_unknown_cells_are_excluded_and_sort_last_in_both_directions():
    card = Card.from_dict(json.loads(PUBLIC.read_text(encoding="utf-8")))
    rel = next(
        r for r in card.relationships("has_structure") if r["object_ref"] == "pdb:1SUX"
    )
    del rel["qualifiers"]["resolution"]  # Synthetic missing retained qualifier.
    access = card.access()
    for descending in (False, True):
        ordered = access.select(
            "structures", order_by={"column": "resolution", "descending": descending}
        )
        assert (
            list(pages(ordered, max_bytes=8192))[-1]["items"][-1]["label"] == "pdb:1SUX"
        )
    selected = access.select(
        "structures", where={"resolution": puw.quantity(2.0, "angstrom")}
    )
    excluded = request(selected)["selection"]["display_exclusions"]
    assert any(
        reason.get("cell_state") == "unknown"
        for item in excluded
        for reason in item["reasons"]
    )


def test_quantity_policy_and_caller_mutation_do_not_change_captured_selection(explorer):
    where = {"resolution": puw.quantity(0.2, "nanometer")}
    order = {"column": "resolution", "unit": "nanometer"}
    with puw.context(standard_units=["nm", "ps", "K", "mole", "gram"]):
        selection = explorer.access.select("structures", where=where, order_by=order)
        before = selection.page(max_bytes=8192)
        where["resolution"] = puw.quantity(9, "angstrom")
        order["unit"] = "second"
        assert selection.page(max_bytes=8192) == before
        assert all(
            QuantityRecord.from_dict(i["cells"]["resolution"]["value"]).to_quantity(
                field="relationships.has_structure.resolution", unit="angstrom"
            )
            is not None
            for i in before["items"]
        )


def test_catalog_declares_actual_selection_policy_without_changing_native_schema(
    explorer,
):
    catalog = explorer.access.catalog().page()["items"]
    location = next(i["location"] for i in catalog if i["key"] == "structures")
    columns = explorer.access.read(location).page()["items"]
    values = {i["key"]: i.get("value") for i in columns}
    assert values["machine_filter"] is True
    assert values["machine_order"] is True
    assert values["machine_membership"] is True
    assert values["selection_policy"] == "structure_access_selection@1"
    native = explorer.access.select("structures")._scientific.wire["schema"]
    assert native["adapter"] == "structure_exploration@1"
    assert (
        native["machine_filter"] is False
    )  # Original adapter declaration stays frozen.


def test_saved_filtered_request_is_exact_and_keeps_full_underlying_result(
    explorer, tmp_path, monkeypatch
):
    selected = explorer.access.select(
        "structures",
        fields=["resolution"],
        where={"resolution": puw.quantity(2.0, "angstrom")},
        order_by={"column": "coverage", "descending": True},
    )
    original_refs = refs(selected)
    path = tmp_path / "selection.json"
    selected.save(path)
    monkeypatch.setattr(Card, "from_dict", forbidden)
    monkeypatch.setattr(
        importlib.import_module("sabueso.core.card_scientific_access"),
        "materialize",
        forbidden,
    )
    saved = sabueso.read_exploration(path)
    assert saved.validation["verified_selection_policies"] == [
        "structure_access_selection@1"
    ]
    access = saved.explorer.access
    same = access.select(
        "structures",
        fields=["resolution"],
        where={"resolution": puw.quantity(2.0, "angstrom")},
        order_by={"column": "coverage", "descending": True},
    )
    assert same.selection_ref == selected.selection_ref
    assert refs(same) == original_refs
    assert len(saved.native_payload["items"]) > same.count
    assert (
        access.select("structures", fields=["resolution"]).page()["outcome"]["status"]
        == "not_saved"
    )
    assert (
        access.select("structures", fields=["resolution"], item_refs=[]).page()[
            "outcome"
        ]["status"]
        == "not_saved"
    )
    assert saved.explorer.view("structures").outcome["status"] == "not_saved"
    assert "structures" in saved.explorer.capabilities["not_saved_topics"]
    again = tmp_path / "again.json"
    same.save(again)
    assert (
        refs(
            sabueso.read_exploration(again).explorer.access.selection(
                same.selection_ref
            )
        )
        == original_refs
    )


def test_independent_saved_reader_forbids_current_selection_and_scientific_helpers(
    explorer, tmp_path
):
    selected = explorer.access.select(
        "structures", fields=[], order_by={"column": "resolution", "unit": "nanometer"}
    )
    path = tmp_path / "independent.json"
    selected.save(path)
    script = """
import importlib,sys
import sabueso
from sabueso.core.card import Card
def forbidden(*a, **k): raise AssertionError('Current producer forbidden')
Card.from_dict=forbidden
m=importlib.import_module('sabueso.core.card_scientific_access')
for name in ['materialize','validate_equality','equal_values','sorted_entries']:
 setattr(m,name,forbidden)
view=sabueso.read_exploration(sys.argv[1])
selection=view.explorer.access.select('structures',fields=[],order_by={'column':'resolution','unit':'nanometer'})
assert selection.selection_ref==sys.argv[2]
assert selection.count==7
assert selection.page(max_bytes=8192)['context']['mode']=='saved'
"""
    completed = subprocess.run(
        [sys.executable, "-c", script, str(path.resolve()), selected.selection_ref],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


@pytest.mark.parametrize("operand", [1, 1.0])
def test_saved_lookup_preserves_canonical_numeric_request_identity(
    explorer, tmp_path, operand
):
    selected = explorer.access.select("structures", where={"coverage": operand})
    path = tmp_path / "typed-request.json"
    selected.save(path)
    access = sabueso.read_exploration(path).explorer.access
    assert (
        access.select("structures", where={"coverage": operand}).selection_ref
        == selected.selection_ref
    )
    other = float(operand) if type(operand) is int else int(operand)
    # Python 1 == 1.0 cannot identify distinct canonical XA requests.
    assert (
        access.select("structures", where={"coverage": other}).page()["outcome"][
            "status"
        ]
        == "not_saved"
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "members",
        "exclusions",
        "policy",
        "quantity",
        "duplicate_projection",
        "unknown_projection",
    ],
)
def test_rebound_selector_decisions_are_refused(explorer, mutation):
    selected = explorer.access.select(
        "structures", where={"resolution": puw.quantity(2.0, "angstrom")}
    )
    from sabueso.core.card_structure_selection_v1 import selection_ref

    obj = deepcopy(selected._access._resolve(selected._context_location)[0])
    spec = obj["request"]["selection"]
    if mutation == "members":
        spec["members"] = []
    elif mutation == "exclusions":
        spec["display_exclusions"] = []
    elif mutation == "policy":
        spec["format"] = "structure_access_selection@999"
    elif mutation == "quantity":
        spec["where"]["resolution"] = QuantityRecord.from_quantity(
            puw.quantity(2.0, "angstrom"), field="wrong.field", unit="angstrom"
        ).to_dict()
    else:
        obj["request"]["fields"] = (
            ["method", "method"]
            if mutation == "duplicate_projection"
            else ["invented_column"]
        )
    # The isolated historical checker below must reject the coherent request even
    # when its handle and resolved context are valid. The public reader's outer
    # seal is separately exercised by the historical exploration tests.
    fake = replace(
        selected,
        _fields=tuple(obj["request"]["fields"]),
        _selection_ref=selection_ref(
            selected._scientific, tuple(obj["request"]["fields"]), spec
        ),
        _context_location=selected._access._object_location(obj),
    )
    from sabueso.core.card_exploration import CardView
    from sabueso.core.card_exploration_science import _verify_selection
    from sabueso.core.card_exploration_storage import _explorer

    view = CardView(
        _explorer(fake._access, {"views": {}, "explanations": {}, "links": {}}),
        fake,
        fake._entries,
        "Synthetic rebound request",
    )
    with pytest.raises((StorageError, RecordError)):
        _verify_selection(view)
