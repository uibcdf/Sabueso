"""Shared captured structural adapter; synthetic variants are not source knowledge."""

import json
import socket
from pathlib import Path

import pytest
import pyunitwizard as puw
from argdigest import UnknownArgumentError
from pyunitwizard import QuantityRecord
from pyunitwizard.record import RecordError

from sabueso.core.card import Card
from sabueso.core.errors import ArgumentError
from sabueso.core.snapshot import canonical_json

PUBLIC = Path("temp_data/frozen_cards/schema_0.3.9__P52270.json")


@pytest.fixture(autouse=True)
def no_queries(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Scientific exploration must not query sources")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


@pytest.fixture
def card():
    return Card.from_dict(json.loads(PUBLIC.read_text()))


def _pick(view, ref="pdb:1SUX"):
    return view.filter("structure_ref", equals=ref).items()[0]


def _walk(access, location):
    selection = access.read(location)
    first = selection.page(max_bytes=8192)
    frames, cursor = [first], first["page"]["next_cursor"]
    while cursor:
        page = selection.page(max_bytes=8192, cursor=cursor)
        frames.append(page)
        cursor = page["page"]["next_cursor"]
    items = [i for frame in frames for i in frame["items"]]
    kind = first["node"]["node_type"]
    if kind == "object":
        return {i["key"]: _walk(access, i["location"]) for i in items}
    if kind == "array":
        return [
            _walk(access, i["location"])
            for i in sorted(items, key=lambda i: i["ordinal"])
        ]
    if kind == "string" and not items[0]["value_included"]:
        return "".join(
            access.read(
                location,
                text_slice={
                    "start": start,
                    "stop": min(start + 2048, first["node"]["size"]),
                },
            ).page(max_bytes=8192)["items"][0]["value"]
            for start in range(0, first["node"]["size"], 2048)
        )
    return items[0]["value"]


def test_public_native_result_and_original_explanation_match_existing_reader(card):
    from sabueso.core.deck import Deck
    from sabueso.core.structure_explanation import explain_structure_inventory

    original = PUBLIC.read_bytes()
    baseline = Deck([card]).structure_inventory()
    explorer = card.explore()
    view = explorer.view("structures")
    assert view.capabilities["scientific_adapter"]
    assert len(view.items()) == len(baseline["items"]) == 7
    item = _pick(view)
    assert item.label == "pdb:1SUX"
    assert item.kind == "structure"
    assert item.cells["method"].value == "X-ray"
    assert item.cells["chains"].value == ["A", "B"]
    assert item.cells["coverage"].value == 1.0
    assert puw.get_value(item.cells["resolution"].value, to_unit="angstrom") == 2.0
    native = item.open().native_payload
    expected = next(i for i in baseline["items"] if i["structure_ref"] == "pdb:1SUX")
    assert native == expected
    explanation = item.explain().native_payload
    assert explanation == explain_structure_inventory(
        [card], card.id, "pdb:1SUX", baseline
    )
    assert explanation["rule"]["rule"] == "structure_inventory_explanation@1"
    assert item.open().back() is item.back()
    assert PUBLIC.read_bytes() == original


def test_single_capture_single_result_and_no_reader_calls_after_materialization(
    card, monkeypatch
):
    from importlib import import_module

    import sabueso.core.structure_explanation as explainers
    import sabueso.core.structures as readers

    knowledge_module = import_module("sabueso.core.knowledge_state")
    calls = []
    original = card.to_dict
    monkeypatch.setattr(
        card, "to_dict", lambda: (calls.append("capture"), original())[1]
    )
    explorer = card.explore()
    inventory = readers.structure_inventory
    monkeypatch.setattr(
        readers,
        "structure_inventory",
        lambda *a, **kw: (calls.append("inventory"), inventory(*a, **kw))[1],
    )
    view = explorer.view("structures")
    assert calls == ["capture", "inventory"]

    def forbidden(*args, **kwargs):
        pytest.fail("Scientific reader rerun")

    monkeypatch.setattr(readers, "structure_inventory", forbidden)
    monkeypatch.setattr(readers, "structures_view", forbidden)
    monkeypatch.setattr(explainers, "explain_structure_inventory", forbidden)
    monkeypatch.setattr(knowledge_module, "knowledge_state", forbidden)
    card.sections.clear()
    card.relationship_store = type(card.relationship_store)()
    item = _pick(view)
    assert item.open().native_payload["structure_ref"] == "pdb:1SUX"
    assert item.explain().native_payload["structure_ref"] == "pdb:1SUX"
    assert view.sort("resolution", unit="nanometer").back() is view
    assert explorer.view("structures").result_ref == view.result_ref
    machine = explorer.access.select("structures", fields=["resolution"])
    assert machine.result_ref == view.result_ref
    assert (
        machine.page(max_bytes=8192)["items"][0]["cells"]["resolution"]["value"][
            "manifest"
        ]["unit"]
        == "angstrom"
    )
    assert explorer.access.explain(item.item_ref).page()["page"]["total"] > 0
    assert calls == ["capture", "inventory"]


def test_machine_projection_and_human_item_ids_share_result(card):
    e = card.explore()
    a = e.access.select("structures", fields=[])
    v = e.view("structures")
    frame = a.page(max_bytes=8192)
    assert a.result_ref == v.result_ref
    assert frame["context"]["adapter"] == "structure_exploration@1"
    assert frame["coverage"]["inspection_required"]
    assert frame["items"][0]["cells"] == {}
    assert frame["items"][0]["interpretation"]["structure_kind"] == "experimental"
    assert (
        frame["items"][0]["interpretation"]["coordinate_completeness"]
        == "not_established_by_coverage"
    )
    human = [i.item_ref for i in v.items()]
    cursor = None
    ids = []
    while True:
        page = a.page(limit=2, max_bytes=8192, cursor=cursor)
        assert len(canonical_json(page).encode()) <= 8192
        ids.extend(i["item_ref"] for i in page["items"])
        cursor = page["page"]["next_cursor"]
        if cursor is None:
            break
    assert ids == human
    assert e.access.select("structures").selection_ref != a.selection_ref
    assert e.access.select("structures", fields=[]).selection_ref == a.selection_ref
    first = _pick(v)
    explanation = e.access.explain(first.item_ref)
    encoded = _walk(e.access, explanation._target["location"])
    assert encoded["structure_ref"] == "pdb:1SUX"
    assert encoded["rule"]["rule"] == "structure_inventory_explanation@1"
    assert _walk(e.access, first.payload_location)["structure_ref"] == "pdb:1SUX"


def test_quantities_are_field_bound_and_preserved_under_nondefault_policy(card):
    with puw.context(standard_units=["nm", "ps", "K", "mole", "gram"]):
        e = card.explore()
        v = e.view("structures")
        item = _pick(v)
        q = item.cells["resolution"].value
        assert puw.get_value(q, to_unit="angstrom") == 2.0
        frame = e.access.select("structures", fields=["resolution"]).page(
            max_bytes=8192
        )
        record = frame["items"][0]["cells"]["resolution"]["value"]
        assert (
            QuantityRecord.from_dict(record).to_quantity(
                field="relationships.has_structure.resolution", unit="angstrom"
            )
            is not None
        )
        with pytest.raises(RecordError):
            QuantityRecord.from_dict(record).to_quantity(
                field="wrong.field", unit="angstrom"
            )
        assert (
            len(v.filter("resolution", equals=puw.quantity(0.2, "nanometer")).items())
            >= 1
        )
        ordered = v.sort("resolution", unit="nanometer")
        values = [
            puw.get_value(i.cells["resolution"].value, to_unit="angstrom")
            for i in ordered.items()
        ]
        assert values == sorted(values)
        assert "2.0 angstrom" in repr(v)


def test_display_navigation_filter_sort_and_original_payload(card):
    e = card.explore()
    root = e.topics()
    route = next(i for i in root.items() if i.label == "Experimental structures")
    v = route.open()
    selected = v.filter("structure_ref", equals="pdb:1SUX")
    i = selected.items()[0]
    assert v.back() is root
    assert i.open().back() is selected and i.explain().back() is selected
    assert selected.back() is v
    assert selected.native_payload == v.native_payload
    assert selected.result_ref == v.result_ref
    assert selected.table().rows() == selected.rows()
    assert selected.summary().view_ref != selected.table().view_ref
    assert "<table>" in selected.table()._repr_html_()
    assert "<th>Resolution</th>" in selected.table()._repr_html_()
    assert "Sequence coverage" in repr(selected.table())
    empty = v.filter("structure_ref", equals="pdb:XXXX")
    assert empty.outcome["status"] == "empty" and empty.coverage == v.coverage
    assert empty.back() is v
    assert not empty.item(i.item_ref).is_selected


def test_options_are_normalized_distinct_and_exclusions_are_scientific(card):
    rel = next(
        r for r in card.relationships("has_structure") if r["object_ref"] == "pdb:1SUX"
    )
    rel["qualifiers"]["coverage"] = 0.1  # synthetic variant of a public record
    # The store's find method returns its actual record; the explorer captures it.
    e = card.explore()
    a = e.view("structures")
    b = e.view("structures", options={"include_fragments": True})
    assert a.result_ref != b.result_ref
    assert len(a.items()) == 6 and len(b.items()) == 7
    excluded = next(x for x in a.exclusions if x["structure_ref"] == "pdb:1SUX")
    assert excluded["reason"] == "fragment_or_peptide"
    assert excluded["explanation"]["status"] == "excluded"
    x = e.access.select("structures", options={"region": [[2, 4], 1]})
    y = e.access.select(
        "structures", options={"region": [4, 3, 2, 1], "include_fragments": False}
    )
    assert x is y and x.result_ref != a.result_ref
    assert x._scientific.options["region"] == [1, 2, 3, 4]
    assert _pick(b).open().native_payload["coverage_class"] == "fragment_or_peptide"


def test_empty_unsupported_and_missing_identity_have_distinct_outcomes():
    anonymous = Card(meta={"entity_type": "protein"}).explore()
    missing = anonymous.view("structures")
    assert missing.outcome["status"] == "missing_prerequisite"
    assert missing.filter("label", equals="x").outcome == missing.outcome
    generic = Card().explore()
    unsupported = generic.view("structures")
    assert unsupported.outcome["status"] == "not_applicable"
    assert generic.capabilities["scientific_topics"] == []
    assert "structures" not in generic.capabilities["topics"]
    empty = (
        Card(
            meta={"entity_type": "protein", "card_id": "sabueso:protein:uniprot:P52270"}
        )
        .explore()
        .view("structures")
    )
    assert empty.outcome["status"] == "empty"
    assert any(row["state"] == "not_queried" for row in empty.coverage["rows"])


def test_conflicting_qualifiers_and_unretained_support_remain_explicit(card):
    rel = next(
        r for r in card.relationships("has_structure") if r["object_ref"] == "pdb:1SUX"
    )
    rel["qualifier_conflicts"] = {"method": ["X-ray", "NMR"]}
    rel["source_assertion_ids"].append("SA_NOT_RETAINED")
    e = card.explore()
    item = _pick(e.view("structures"))
    assert item.cells["method"].state == "conflicting"
    assert item.cells["method"].value == "X-ray"
    assert item.support[0]["basis"] == "relationship_level"
    assert item.support[0]["source_assertions"][-1]["state"] == "not_retained"
    assert item.explain().native_payload["members"][0]["relationship"][
        "qualifier_conflicts"
    ] == {"method": ["X-ray", "NMR"]}
    frame = e.access.select("structures", fields=[]).page(max_bytes=8192)
    row = next(r for r in frame["items"] if r["label"] == "pdb:1SUX")
    assert row["interpretation"]["qualifier_conflicts"] == {"method": ["X-ray", "NMR"]}


def test_whole_value_and_interpretation_are_deferred_together(card):
    rel = next(
        r for r in card.relationships("has_structure") if r["object_ref"] == "pdb:1SUX"
    )
    rel["qualifier_conflicts"] = {"method": ["X-ray", "unknown" + "z" * 20000]}
    a = card.access()
    s = a.select("structures", fields=["method"])
    cursor = None
    frames = []
    while True:
        p = s.page(limit=2, max_bytes=4096, cursor=cursor)
        frames.append(p)
        assert len(canonical_json(p).encode()) <= 4096
        assert not p["page"]["blocked"]
        cursor = p["page"]["next_cursor"]
        if cursor is None:
            break
    rows = [r for p in frames for r in p["items"]]
    deferred = next(
        row
        for row in rows
        if a._resolve(row["payload_location"])[0]["structure_ref"] == "pdb:1SUX"
    )
    assert not deferred["value_included"]
    assert "interpretation" not in deferred
    assert deferred["inspection_required"]
    assert deferred["cells"]["method"]["state"] == "conflicting"
    assert not deferred["cells"]["method"]["value_included"]
    assert "value" not in deferred["cells"]["method"]
    assert _walk(a, deferred["interpretation_location"])["qualifier_conflicts"][
        "method"
    ][1].endswith("z" * 20000)
    assert _walk(a, deferred["value_location"])["structure_ref"] == "pdb:1SUX"
    assert any(not p["page"]["values_complete"] for p in frames)


def test_metadata_and_store_order_do_not_change_semantic_result(card, monkeypatch):
    import sabueso

    first = card.access().select("structures")
    data = card.to_dict()
    data["relationship_store"].reverse()
    data["source_assertion_store"].reverse()
    monkeypatch.setattr(sabueso, "__version__", "synthetic-producer-metadata")
    other = Card.from_dict(data).access().select("structures")
    assert first.result_ref == other.result_ref
    assert [e.location for e in first._entries] == [e.location for e in other._entries]


@pytest.mark.parametrize("skip", [False, True])
@pytest.mark.parametrize(
    "call",
    [
        lambda e, s: e.access.select(
            "structures", fields=["missing"], skip_digestion=s
        ),
        lambda e, s: e.access.select(
            "structures", fields=["method", "method"], skip_digestion=s
        ),
        lambda e, s: e.access.select("structures", fields=123, skip_digestion=s),
        lambda e, s: e.access.select(
            "structures", options={"unknown": 1}, skip_digestion=s
        ),
        lambda e, s: e.access.select(
            "structures", options={"include_fragments": 1}, skip_digestion=s
        ),
        lambda e, s: e.access.select(
            "structures", options={"region": [0]}, skip_digestion=s
        ),
        lambda e, s: e.view("content", options={"region": [1]}, skip_digestion=s),
        lambda e, s: e.access.select("made-up", skip_digestion=s),
        lambda e, s: e.access.explain("XI_" + "f" * 64, skip_digestion=s),
        lambda e, s: e.view("structures").filter(
            "coverage", equals=True, skip_digestion=s
        ),
        lambda e, s: e.view("structures").filter("method", equals=2, skip_digestion=s),
        lambda e, s: e.view("structures").filter(
            "resolution", equals=2, skip_digestion=s
        ),
        lambda e, s: e.view("structures").sort(
            "resolution", unit="second", skip_digestion=s
        ),
    ],
)
def test_bad_scientific_arguments_fail_explicitly(card, call, skip):
    with pytest.raises(ArgumentError):
        call(card.explore(), skip)


def test_unsupported_machine_grammar_and_foreign_refs_do_not_succeed(card):
    a = card.access()
    with pytest.raises(UnknownArgumentError):
        a.select("structures", aggregate="method")
    e = card.explore()
    i = _pick(e.view("structures"))
    with pytest.raises(ArgumentError):
        a.explain(i.item_ref)
    assert "structures" in e.access.capabilities["scientific_topics"]


def test_missing_resolution_sorts_last_and_dimension_checks_apply_to_empty_views(card):
    rel = next(
        r for r in card.relationships("has_structure") if r["object_ref"] == "pdb:1SUX"
    )
    del rel["qualifiers"]["resolution"]  # synthetic missing retained qualifier
    view = card.explore().view("structures")
    assert _pick(view).cells["resolution"].state == "unknown"
    for descending in (False, True):
        ordered = view.sort("resolution", descending=descending, unit="nanometer")
        assert ordered.items()[-1].label == "pdb:1SUX"
    empty = view.filter("structure_ref", equals="not-retained")
    with pytest.raises(ArgumentError):
        empty.sort("resolution", unit="second")
    with pytest.raises(ArgumentError):
        empty.filter("resolution", equals=puw.quantity(1, "second"))
    with pytest.raises(ArgumentError):
        empty.filter("resolution", equals=puw.quantity([1, 2], "angstrom"))


def test_original_failed_source_scope_and_unknown_state_survive_projection():
    from sabueso.core.relationship_store import make_relationship

    c = Card(
        meta={"entity_type": "protein", "card_id": "sabueso:protein:uniprot:P52270"},
        relationship_store=[
            make_relationship(
                "uniprot:P52270",
                "has_structure",
                "pdb:1SUX",
                qualifiers={"method": "X-ray", "coverage": 1.0},
                source_assertion_ids=["SA_SYNTHETIC_NOT_RETAINED"],
            )
        ],
        quality={
            "enrichments": [
                {"source": "RCSB PDB", "structure": "1SUX", "status": "error"}
            ]
        },
    )
    e = c.explore()
    v = e.view("structures")
    assert any(
        row["source"] == "RCSB PDB" and row["state"] == "unavailable"
        for row in v.coverage["rows"]
    )
    i = v.items()[0]
    assert i.explain().native_payload["reason"] == "error"
    frame = e.access.select("structures", fields=["method"]).page(max_bytes=8192)
    interpretation = frame["items"][0]["interpretation"]
    assert interpretation["state"]["sequence"] is None
    assert interpretation["inventory_status"] == "not_inventoried"
    assert interpretation["inventory_reason"] == "error"
    assert "unavailable" in repr(v)


def test_results_and_native_explanations_are_defensive(card):
    e = card.explore()
    v = e.view("structures")
    i = _pick(v)
    i.open().native_payload["chains"].clear()
    i.cells["chains"].value.clear()
    i.support[0].clear()
    v.coverage.clear()
    v.context.clear()
    i.explain().native_payload["members"].clear()
    assert i.cells["chains"].value == ["A", "B"]
    assert i.explain().native_payload["members"]
    page = e.access.select("structures").page(max_bytes=8192)
    page["items"][0]["interpretation"].clear()
    assert e.access.select("structures").page(max_bytes=8192)["items"][0][
        "interpretation"
    ]
