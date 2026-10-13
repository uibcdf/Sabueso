"""Observed comparative executions stay separate from their original science."""

import json
import subprocess
import sys
from contextvars import Context
from pathlib import Path

import ackredit
import pytest

import sabueso
from sabueso._private.smonitor.warnings import AttributionTrackingWarning
from sabueso.core import attribution
from sabueso.core.card import Card
from sabueso.core.source_assertion_store import make_source_assertion
from sabueso.resolver import EntityResolver, FixtureUniProtClient
from sabueso.tools.db import _http
from sabueso.tools.db.gnomad import FixtureGnomADClient
from sabueso.tools.db.gtex import FixtureGTExClient
from sabueso.tools.db.uniref import FixtureUniRefClient


@pytest.fixture(scope="module")
def cards():
    with ackredit.session("public comparative fixture producer"):
        resolver = EntityResolver(FixtureUniProtClient("temp_data"))
        return {
            accession: sabueso.resolve(accession, resolver=resolver, **options)[0]
            for accession, options in (
                (
                    "P52270",
                    {"uniref": True, "uniref_client": FixtureUniRefClient("temp_data")},
                ),
                ("Q4DV43", {}),
                (
                    "P60174",
                    {
                        "gnomad": {},
                        "exon_usage": True,
                        "gtex": True,
                        "gnomad_client": FixtureGnomADClient("temp_data"),
                        "gtex_client": FixtureGTExClient("temp_data"),
                    },
                ),
            )
        }


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(
        _http, "_urlopen", lambda *a, **k: pytest.fail("No acquisition")
    )
    with ackredit.session("comparative operation test"):
        yield


def call(cards, operation, legacy=False):
    if operation == "sequence_differences":
        return cards["P52270"].sequence_differences(cards["Q4DV43"])
    options = {"threshold": 0.2}
    if legacy:
        options["usage_rule"] = (
            "pext_at_variant@1"
            if operation.startswith("variant")
            else "isoform_exon_usage@2"
        )
    return getattr(cards["P60174"], operation)(**options)


@pytest.mark.parametrize(
    "operation,legacy",
    [
        ("sequence_differences", False),
        ("variant_tissue_usage", False),
        ("variant_tissue_usage", True),
        ("isoform_tissue_usage", False),
        ("isoform_tissue_usage", True),
    ],
)
def test_observed_views_keep_exact_science_and_credit_only_their_inputs(
    cards, operation, legacy
):
    before = {key: c.to_dict() for key, c in cards.items()}
    baseline = call(cards, operation, legacy)
    with sabueso.attribution() as run:
        result = call(cards, operation, legacy)
    assert result == baseline
    assert {key: c.to_dict() for key, c in cards.items()} == before
    assert not run.records and not run.acquisitions
    (record,) = run.operations
    assert record["format"] == "sabueso.comparative_operation@2"
    assert record["operation"] == operation and record["status"] == "completed"
    assert record["rule"] == result["rule"]
    assert record["provider"]["status"] == "available"
    expected = (
        {"UniProt"}
        if operation == "sequence_differences"
        else {"UniProt", "gnomAD", "GTEx"}
        if operation.startswith("isoform")
        else {"gnomAD", "GTEx"}
    )
    assert {r["source"]["name"] for r in record["resources"]} == expected
    assert all(
        "source_assertion_ref" in use for r in record["resources"] for use in r["uses"]
    )
    roles = {
        role
        for use in record["provider"]["attribution"]["uses"]
        for role in use["roles"]
    }
    assert roles == {
        "executed_software",
        "stored_knowledge",
        "resource_description",
    } | ({"method_description"} if operation != "sequence_differences" else set())
    assert record["acquisition"] == "not_performed"


def test_plain_views_and_explanations_keep_their_inert_contract(cards, monkeypatch):
    def forbidden(*a, **k):
        pytest.fail("Unobserved readers must not load the provider")

    monkeypatch.setattr(attribution, "_load_backend", forbidden)
    for operation in (
        "sequence_differences",
        "variant_tissue_usage",
        "isoform_tissue_usage",
    ):
        call(cards, operation)
    with sabueso.attribution() as run:
        cards["P52270"].explain_sequence_differences(cards["Q4DV43"])
        cards["P60174"].explain_variant_tissue_usage()
        cards["P60174"].explain_isoform_tissue_usage()
    assert not run.operations and not run.records and not run.acquisitions


def test_tissue_term_join_records_its_actual_nested_rule_and_bibliography_gaps(cards):
    with sabueso.attribution() as run:
        answer = call(cards, "variant_tissue_usage")
    record = run.operations[0]
    assert record["applied_rules"] == [answer["rule"], answer["tissue_terms"]["rule"]]
    assert record["applied_rules"][1]["rule"] == "gtex_tissue_key@1"
    assert not record["support_gaps"] and record["support_status"] == "available"
    assert record["bibliography_gaps"]


def test_repeated_nested_calls_own_detached_records_and_workflow_credit(cards):
    with ackredit.capture("application") as workflow:
        with sabueso.attribution() as outer:
            with sabueso.attribution() as inner:
                result = call(cards, "sequence_differences")
            again = call(cards, "sequence_differences")
    first, second = outer.operations
    assert first == inner.operations[0]
    assert result == again and first["result_id"] == second["result_id"]
    assert first["execution_id"] != second["execution_id"]
    assert {item["id"] for item in workflow.attribution.to_dict()["items"]} == {
        item["id"] for item in first["provider"]["attribution"]["items"]
    }
    first["inputs"].clear()
    assert outer.operations[0]["inputs"] and inner.operations[0]["inputs"]


@pytest.mark.parametrize("first", ["packet", "comparison"])
def test_packet_and_comparative_execution_keep_their_distinct_records_in_one_workflow(
    cards, first
):
    with ackredit.capture("mixed knowledge workflow") as workflow:
        with sabueso.attribution() as run:
            if first == "comparison":
                call(cards, "sequence_differences")
            packet = sabueso.compose_packet(
                sabueso.KnowledgeQuery("P52270", aspects=["identity"]), cards["P52270"]
            )
            if first == "packet":
                call(cards, "sequence_differences")
    assert len(run.records) == len(run.operations) == 1
    assert packet.attribution == run.records[0]
    assert (
        run.records[0]["provider"]["status"]
        == run.operations[0]["provider"]["status"]
        == "available"
    )
    expected = {
        item["id"]
        for record in [*run.records, *run.operations]
        for item in record["provider"]["attribution"]["items"]
    }
    assert {item["id"] for item in workflow.attribution.to_dict()["items"]} == expected


@pytest.mark.parametrize("other", [None, "AC", "ACD"])
def test_empty_missing_and_unequal_sequences_are_completed_knowledge_limits(other):
    left, right = (
        Card(meta={"card_id": "sabueso:protein:uniprot:P60174"}),
        Card(meta={"card_id": "sabueso:protein:uniprot:P52270"}),
    )
    for c, value in ((left, "ACE"), (right, other)):
        if value is not None:
            assertion = make_source_assertion(
                "sequence.primary", value, "UniProt", c.id, "public synthetic"
            )
            c.source_assertion_store.add(assertion)
            c.set("sequence.primary", value, [assertion["id"]])
    with sabueso.attribution() as run:
        answer = left.sequence_differences(right)
    (record,) = run.operations
    assert record["status"] == "completed"
    assert record["result_basis"] == answer.get("basis")
    if other is not None:
        assert record["support_gaps"] == []
    else:
        assert any(g["reason"] == "input_not_stated" for g in record["support_gaps"])
    assert record["provider"]["status"] == "available"


@pytest.mark.parametrize("failure", ["import", "after_credit"])
def test_provider_failure_keeps_the_completed_result_and_host_record(
    cards, monkeypatch, failure
):
    baseline = call(cards, "sequence_differences")

    def broken(*a, **k):
        raise RuntimeError("public synthetic provider failure")

    if failure == "import":
        monkeypatch.setattr(attribution, "_load_backend", broken)
    else:
        monkeypatch.setattr(ackredit, "track_item", broken)
    with pytest.warns(AttributionTrackingWarning):
        with sabueso.attribution() as run:
            result = call(cards, "sequence_differences")
    assert result == baseline
    assert run.operations[0]["status"] == "completed"
    assert run.operations[0]["provider"]["status"] == "failed"
    assert run.operations[0]["provider"]["attribution"] is None


def test_scientific_failure_is_re_raised_and_never_receives_completed_credit(
    cards, monkeypatch
):
    from sabueso.core import sequences

    error = ValueError("public synthetic scientific failure")

    def broken(*a, **k):
        raise error

    monkeypatch.setattr(sequences, "sequence_differences_view", broken)
    monkeypatch.setattr(
        attribution,
        "_load_backend",
        lambda: pytest.fail("Failed computation gets no credit"),
    )
    with sabueso.attribution() as run:
        with pytest.raises(ValueError) as raised:
            call(cards, "sequence_differences")
    assert raised.value is error
    assert run.operations[0]["status"] == "failed"
    assert run.operations[0]["provider"]["status"] == "not_attempted"
    assert run.operations[0]["result_id"] is None


def test_context_isolation_and_rejected_arguments_do_not_record_execution(cards):
    with sabueso.attribution() as run:
        Context().run(call, cards, "sequence_differences")
        with pytest.raises(sabueso.core.errors.ArgumentError):
            cards["P60174"].variant_tissue_usage(threshold=2)
    assert not run.operations


def test_isoform_text_uses_all_stored_statements_even_without_a_selected_field():
    c = Card(meta={"card_id": "sabueso:protein:uniprot:P60174"})
    from sabueso.core.tissue_usage import TISSUE_TEXT

    assertion = make_source_assertion(
        TISSUE_TEXT, "public synthetic tissue", "UniProt", "P60174", "synthetic"
    )
    c.source_assertion_store.add(assertion)
    with sabueso.attribution() as run:
        c.isoform_tissue_usage()
    uses = [u for r in run.operations[0]["resources"] for u in r["uses"]]
    assert any(
        u["source_assertion_ref"].endswith("#" + assertion["id"])
        and u["support_basis"] == "all_stored_tissue_specificity_statements"
        for u in uses
    )


@pytest.mark.parametrize("defect", ["missing", "field", "value"])
def test_invalid_input_support_is_explicit_and_gets_no_false_resource_credit(defect):
    left, right = (
        Card(meta={"card_id": "sabueso:protein:uniprot:P60174"}),
        Card(meta={"card_id": "sabueso:protein:uniprot:P52270"}),
    )
    assertion = make_source_assertion(
        "other.field" if defect == "field" else "sequence.primary",
        "XXX" if defect == "value" else "ACE",
        "ChEMBL",
        "synthetic",
        "synthetic",
    )
    if defect != "missing":
        left.source_assertion_store.add(assertion)
    left.set("sequence.primary", "ACE", [assertion["id"]])
    right.set("sequence.primary", "ACD", [])
    baseline = left.sequence_differences(right)
    with sabueso.attribution() as run:
        assert left.sequence_differences(right) == baseline
    record = run.operations[0]
    assert record["support_status"] == "partial" and record["support_gaps"]
    assert record["resources"] == []
    assert {
        r for u in record["provider"]["attribution"]["uses"] for r in u["roles"]
    } == {"executed_software"}


def test_missing_bibliography_and_original_source_labels_stay_separate_from_support():
    c = Card(meta={"card_id": "sabueso:protein:uniprot:P60174"})
    assertion = make_source_assertion(
        "sequence.primary", "ACE", "Unregistered source", "synthetic", "original"
    )
    assertion["source"]["version"] = "original label"
    c.source_assertion_store.add(assertion)
    c.set("sequence.primary", "ACE", [assertion["id"]])
    with sabueso.attribution() as run:
        c.sequence_differences(c)
    record = run.operations[0]
    assert record["support_status"] == "available" and not record["support_gaps"]
    assert (
        record["bibliography_gaps"][0]["reason"] == "description_citation_not_declared"
    )
    resource = record["resources"][0]
    assert resource["source"]["version"] == "original label"
    assert resource["version_basis"] == "stored_source_assertion_label"


@pytest.mark.parametrize("defect", ["missing_pin", "changed_input"])
def test_unbound_or_changed_input_keeps_science_and_refuses_credit(
    cards, monkeypatch, defect
):
    from sabueso.core import sequences

    left = Card.from_dict(cards["P52270"].to_dict())
    right = cards["Q4DV43"]
    baseline = left.sequence_differences(right)
    if defect == "missing_pin":

        def broken_pin():
            raise ValueError("synthetic input pin unavailable")

        monkeypatch.setattr(left, "pinned_ref", broken_pin)
    else:
        original = sequences.sequence_differences_view

        def changed(a, b):
            result = original(a, b)
            a.meta["synthetic_later_state"] = True
            return result

        monkeypatch.setattr(sequences, "sequence_differences_view", changed)
    monkeypatch.setattr(
        attribution,
        "_load_backend",
        lambda: pytest.fail("Unbound input gets no credit"),
    )
    with pytest.warns(AttributionTrackingWarning):
        with sabueso.attribution() as run:
            assert left.sequence_differences(right) == baseline
    assert run.operations[0]["status"] == "completed"
    assert run.operations[0]["support_status"] == "unavailable"
    assert run.operations[0]["provider"]["status"] == "not_attempted"


def test_genuine_provider_absence_is_lazy_and_preserves_the_completed_result(tmp_path):
    script = """
import importlib.abc, json, sys, warnings
from pathlib import Path
class Absent(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'ackredit' or fullname.startswith('ackredit.'):
            raise ModuleNotFoundError('Ackredit absent in this process', name=fullname)
sys.meta_path.insert(0, Absent())
import sabueso
from sabueso.core.card import Card
c = Card.from_dict(json.loads(Path(sys.argv[1]).read_text()))
with sabueso.attribution() as empty:
    pass
assert not empty.operations
assert 'ackredit' not in sys.modules
assert 'sabueso.core.attribution_bibliography' not in sys.modules
baseline = c.sequence_differences(c)
with warnings.catch_warnings(record=True) as diagnosed:
    warnings.simplefilter('always')
    with sabueso.attribution() as run:
        result = c.sequence_differences(c)
assert result == baseline and diagnosed
assert run.operations[0]['provider']['status'] == 'failed'
assert 'ModuleNotFoundError' in run.operations[0]['provider']['reason']
assert run.operations[0]['inputs'] and run.operations[0]['bibliography']
assert 'ackredit' not in sys.modules
"""
    fixture = Path("temp_data/frozen_cards/schema_0.3.10__P60174.json").resolve()
    result = subprocess.run(
        [sys.executable, "-c", script, str(fixture)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_fresh_saved_reader_uses_original_pins_rules_and_bibliography_without_execution(
    cards, tmp_path
):
    store = sabueso.KnowledgeStore(tmp_path / "cards.db")
    for card in cards.values():
        store.save(card)
    with sabueso.attribution() as run:
        results = [
            call(cards, op)
            for op in (
                "sequence_differences",
                "variant_tissue_usage",
                "isoform_tissue_usage",
            )
        ]
    document = {"results": results, "operations": run.operations}
    report = tmp_path / "original.json"
    report.write_text(json.dumps(document))
    script = """
import json, sys
from pathlib import Path
import ackredit, sabueso
from sabueso.core import attribution
from sabueso.core.card import Card
from sabueso.core.snapshot import canonical_json, digest
def forbidden(*a, **k):
    raise AssertionError('Reader cannot acquire, derive or create credit')
attribution._load_backend = forbidden
ackredit.register_item = ackredit.track_item = forbidden
sabueso.resolve = forbidden
for name in ('sequence_differences', 'variant_tissue_usage', 'isoform_tissue_usage', 'explain_sequence_differences', 'explain_variant_tissue_usage', 'explain_isoform_tissue_usage'):
    setattr(Card, name, forbidden)
sabueso.__version__ = '999.reader'
directory = Path(sys.argv[1])
original = (directory / 'original.json').read_bytes()
data = json.loads(original)
store = sabueso.KnowledgeStore(directory / 'cards.db')
with ackredit.session('independent inert reader'):
    credit = ackredit.get_attribution().to_dict()
    with sabueso.attribution() as run:
        for result, record in zip(data['results'], data['operations'], strict=True):
            assert record['rule'] == result['rule']
            assert record['result_id'] == digest(canonical_json(result))
            for scope in record['inputs']:
                card = store.load(scope['card_ref'])
                assert card.pinned_ref() == scope['card_ref']
                for field in scope['fields']:
                    for ref in field['source_assertion_refs']:
                        assert store.source_assertion(ref)['id'] == ref.split('#')[1]
            saved = ackredit.Attribution.from_dict(record['provider']['attribution'])
            assert saved.to_dict() == record['provider']['attribution']
            for format in ('text', 'csl-json', 'bibtex'):
                assert '999.reader' not in saved.report(format=format)
        assert not run.operations and not run.records and not run.acquisitions
    assert ackredit.get_attribution().to_dict() == credit
assert (directory / 'original.json').read_bytes() == original
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
