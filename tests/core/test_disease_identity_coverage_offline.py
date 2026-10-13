"""Identifier-scoped disease coverage; public synthetic statements and inert readers."""

from copy import deepcopy

import ackredit
import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.core.relationship_store import make_relationship
from sabueso.core.source_assertion_store import make_source_assertion
from sabueso.tools.db import _http


def card(refs, records=(), links=()):
    result = Card(
        meta={"card_id": "sabueso:protein:uniprot:P60174", "entity_type": "protein"},
        quality={"enrichments": deepcopy(list(records))},
    )
    item = {
        "accession": "VCV_SYNTHETIC",
        "conditions": [{"name": "synthetic", "xrefs": refs}],
    }
    assertion = make_source_assertion(
        "annotations.clinical_variants", item, "ClinVar", "VCV_SYNTHETIC", "synthetic"
    )
    result.source_assertion_store.add(assertion)
    result.set("annotations.clinical_variants", [item], [assertion["id"]])
    identifier = make_source_assertion(
        "identifiers.uniprot", "P60174", "UniProt", "P60174", "synthetic"
    )
    result.source_assertion_store.add(identifier)
    result.set("identifiers.uniprot", "P60174", [identifier["id"]])
    for source, subject, target in links:
        assertion = make_source_assertion(
            "relationships.same_as",
            {"target": target},
            source,
            subject,
            "synthetic",
            subject_ref=subject,
        )
        result.source_assertion_store.add(assertion)
        result.relationship_store.add(
            make_relationship(
                subject,
                "same_as",
                target,
                qualifiers={"source": source},
                source_assertion_ids=[assertion["id"]],
            )
        )
    return result


def record(status, curie=None, reason="no_stated_equivalence", source="MONDO"):
    return {
        "source": source,
        "status": status,
        "ungrouped": [] if curie is None else [{"curie": curie, "reason": reason}],
    }


def only(result):
    return result.diseases()["ungrouped"][0]


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(
        _http, "_urlopen", lambda *a, **k: pytest.fail("No source access allowed")
    )
    with ackredit.session("public disease coverage"):
        yield


@pytest.mark.parametrize(
    "status,reason",
    [
        ("not_queried", "identity_not_queried"),
        ("not_applicable", "identity_not_queried"),
        ("error", "identity_unavailable"),
        ("unavailable", "identity_unavailable"),
        ("added", "identity_scope_unknown"),
        ("not_found", "identity_scope_unknown"),
    ],
)
def test_request_record_without_identifier_answer_never_establishes_absence(
    status, reason
):
    result = card(["OMIM:123"], [record(status)])
    before = result.to_dict()
    assert only(result)["reason"] == reason
    coverage = only(result)["identity_coverage"]
    assert coverage["rule"]["rule"] == "disease_identity_coverage@1"
    assert coverage["rows"][0]["steps"][0]["scope"] == "not_recorded"
    assert result.diseases()["rule"]["rule"] == "disease_grouping@3"
    assert result.to_dict() == before


@pytest.mark.parametrize("status", ["added", "not_found"])
@pytest.mark.parametrize("outcome", ["no_stated_equivalence", "obsolete_term"])
def test_explicit_completed_identifier_diagnostics_retain_native_outcomes(
    status, outcome
):
    result = card(["OMIM:123"], [record(status, "OMIM:123", outcome)])
    assert only(result)["reason"] == outcome
    row = only(result)["identity_coverage"]["rows"][0]
    assert row["steps"][0]["scope"] == "identifier_diagnostic"
    assert row["steps"][0]["enrichment_indexes"] == [0]


@pytest.mark.parametrize("status", ["not_queried", "error", "unavailable"])
def test_failed_or_blocked_records_cannot_turn_a_diagnostic_into_source_absence(status):
    result = card(["OMIM:123"], [record(status, "OMIM:123")])
    assert only(result)["reason"] != "no_stated_equivalence"


@pytest.mark.parametrize("counter", [0, 1, 999])
def test_global_counts_and_another_identifiers_answer_do_not_establish_coverage(
    counter,
):
    source = record("added", "OMIM:456")
    source["ids"] = counter
    result = card(["OMIM:123"], [source])
    assert only(result)["reason"] == "identity_scope_unknown"


@pytest.mark.parametrize("mondo_status", ["added", "not_found", "not_queried", "error"])
def test_medgen_concept_without_uid_blocks_mondo_independently_of_other_queries(
    mondo_status,
):
    result = card(["MEDGEN:C123"], [record(mondo_status, "OMIM:456")])
    assert only(result)["reason"] == "identity_not_queried"
    row = only(result)["identity_coverage"]["rows"][0]
    assert row["steps"][-1]["scope"] == "missing_prerequisite"


def test_native_missing_medgen_uid_is_not_a_mondo_equivalence_answer():
    result = card(
        ["MEDGEN:C123"],
        [{"source": "MedGen", "status": "not_found", "missing": ["C123"]}],
    )
    row = only(result)["identity_coverage"]["rows"][0]
    assert only(result)["reason"] == "identity_not_queried"
    assert row["steps"][0]["state"] == "not_stated"
    assert row["steps"][-1]["state"] == "not_queried"


@pytest.mark.parametrize(
    "status,reason",
    [
        ("not_queried", "identity_not_queried"),
        ("error", "identity_unavailable"),
        ("added", "identity_scope_unknown"),
    ],
)
def test_unfinished_stored_uid_branch_preserves_its_actual_mondo_coverage(
    status, reason
):
    result = card(
        ["MEDGEN:C123"], [record(status)], [("MedGen", "MEDGEN:C123", "MEDGEN:123")]
    )
    assert only(result)["reason"] == reason
    path = only(result)["identity_paths"][0]
    assert path["reason"] == reason and path["relationship_ids"]


def test_uid_answer_scope_is_not_confused_with_the_original_concept():
    result = card(
        ["MEDGEN:C123"],
        [record("not_found", "MEDGEN:123")],
        [("MedGen", "MEDGEN:C123", "MEDGEN:123")],
    )
    assert only(result)["reason"] == "no_stated_equivalence"


def test_mixed_identifier_coverage_is_reported_without_discarding_native_answers():
    result = card(["OMIM:123", "OMIM:456"], [record("added", "OMIM:123")])
    assert only(result)["reason"] == "mixed_identity_coverage"
    assert {r["state"] for r in only(result)["identity_coverage"]["rows"]} == {
        "not_stated",
        "unknown",
    }


def test_conflicting_native_negative_diagnostics_are_preserved():
    result = card(
        ["OMIM:123"],
        [record("added", "OMIM:123"), record("not_found", "OMIM:123", "obsolete_term")],
    )
    assert only(result)["reason"] == "mixed_identity_coverage"
    assert only(result)["identity_coverage"]["rows"][0]["state"] == "mixed"


@pytest.mark.parametrize(
    "refs,reason",
    [
        ([], "no_id_stated"),
        (["HP:123"], "namespace_not_mapped"),
        (["MEDGEN:C3661900"], "condition_not_provided"),
    ],
)
def test_local_condition_limits_stay_distinct_from_source_absence(refs, reason):
    assert only(card(refs, [record("added")]))["reason"] == reason


def test_positive_stored_identity_is_retained_despite_an_unavailable_refresh():
    result = card(
        ["OMIM:123"], [record("error")], [("MONDO", "OMIM:123", "mondo:MONDO:0000001")]
    )
    before = result.to_dict()
    (group,) = result.diseases()["diseases"]
    assert group["mondo"] == "MONDO:0000001"
    assert (
        group["statements"][0]["identity_coverage"]["rows"][0]["state"]
        == "identity_stated"
    )
    assert result.to_dict() == before


@pytest.mark.parametrize("with_uid", [False, True])
def test_direct_stored_concept_identity_does_not_require_an_indirect_uid(with_uid):
    links = [("MONDO", "MEDGEN:C123", "mondo:MONDO:0000001")]
    if with_uid:
        links.append(("MedGen", "MEDGEN:C123", "MEDGEN:123"))
    result = card(["MEDGEN:C123"], [record("error")], links)
    before = result.to_dict()
    view = result.diseases()
    statement = (
        view["ungrouped"][0] if with_uid else view["diseases"][0]["statements"][0]
    )
    row = statement["identity_coverage"]["rows"][0]
    assert row["state"] == ("mixed" if with_uid else "identity_stated")
    direct = [
        s
        for s in row["steps"]
        if s["source"] == "MONDO" and s["identifier"] == "MEDGEN:C123"
    ]
    assert len(direct) == 1
    assert direct[0]["state"] == "identity_stated"
    assert direct[0]["relationship_ids"]
    if with_uid:
        assert statement["reason"] == "incomplete_identity"
        assert any(
            s["identifier"] == "MEDGEN:123" and s["state"] == "unavailable"
            for s in row["steps"]
        )
    assert result.to_dict() == before


def test_explicit_historical_rules_and_pins_are_inert_and_keep_old_classification(
    tmp_path, monkeypatch
):
    result = card(["MEDGEN:C123"], [record("not_queried")])
    historical = {
        n: result.diseases(grouping_rule=f"disease_grouping@{n}") for n in (1, 2)
    }
    assert all(
        v["ungrouped"][0]["reason"] == "no_stated_equivalence"
        for v in historical.values()
    )
    before = result.to_dict()
    store = sabueso.KnowledgeStore(tmp_path / "cards.db")
    pin = store.save(result)
    current = result.explain_disease("MONDO:0000001")
    assert current["rule"]["rule"] == "disease_group_explanation@3"
    assert (
        current["ungrouped_context"]["statements"][0]["statement"]["reason"]
        == "identity_not_queried"
    )
    assert current["coverage_context"]["card_ref"] == pin
    from sabueso.core import attribution, source_acquisition

    monkeypatch.setattr(
        attribution, "_credit", lambda *a: pytest.fail("No fresh credit")
    )
    monkeypatch.setattr(
        source_acquisition, "_credit", lambda *a: pytest.fail("No fresh credit")
    )
    credits = ackredit.get_attribution().to_dict()
    with sabueso.attribution() as trace:
        loaded = store.load(pin)
        assert loaded.to_dict() == before and loaded.pinned_ref() == pin
        assert loaded.explain_disease("MONDO:0000001") == current
        for n in (1, 2):
            assert (
                loaded.diseases(grouping_rule=f"disease_grouping@{n}") == historical[n]
            )
    assert not trace.acquisitions and not trace.records
    assert ackredit.get_attribution().to_dict() == credits


@pytest.mark.parametrize("rule", ["disease_grouping@1", "disease_grouping@2"])
def test_both_historical_explanation_versions_remain_explicit(rule):
    result = card(["OMIM:123"], [record("not_queried")])
    explanation = result.explain_disease("MONDO:0000001", grouping_rule=rule)
    assert explanation["rule"]["rule"] == rule.replace(
        "disease_grouping", "disease_group_explanation"
    )
    assert "coverage_context" not in explanation
    assert (
        explanation["ungrouped_context"]["statements"][0]["statement"]["reason"]
        == "no_stated_equivalence"
    )


@pytest.mark.parametrize("detail", ["full", "index"])
def test_packet_mapping_versions_and_terms_preserve_historical_scopes(tmp_path, detail):
    from sabueso.core.packets import KnowledgePacket, _facts, full_rules

    result = card(["OMIM:123"], [record("not_queried")])
    store = sabueso.KnowledgeStore(tmp_path / "packets.db")
    store.save(result)
    query = sabueso.KnowledgeQuery(
        "P60174", aspects=["disease_association"], detail=detail
    )
    current = sabueso.compose_packet(query, result)
    assert current.to_dict()["aspect_mapping"] == "packet_aspects@7"
    legacy_data = current.to_dict()
    legacy_data["aspect_mapping"] = "packet_aspects@6"
    if detail == "full":
        current_statement = current.facts["disease_association"]["subject"]["grouped"][
            "ungrouped"
        ][0]
        assert current_statement["reason"] == "identity_not_queried"
        assert current_statement["identity_coverage"]["rows"]
        legacy_data["facts"]["disease_association"]["subject"] = _facts(
            "disease_association", result, mapping="packet_aspects@6"
        )
        legacy_statement = legacy_data["facts"]["disease_association"]["subject"][
            "grouped"
        ]["ungrouped"][0]
        assert legacy_statement["reason"] == "no_stated_equivalence"
        assert "identity_coverage" not in legacy_statement
    else:
        legacy_data["facts"]["disease_association"]["subject"]["full_rules"] = (
            full_rules(mapping="packet_aspects@6")["disease_association"]
        )
        assert legacy_data["facts"]["disease_association"]["subject"]["full_rules"] == [
            "disease_grouping@2"
        ]
    legacy = KnowledgePacket(legacy_data)
    assert current.same_knowledge(legacy) is None
    for name, packet in (("legacy", legacy), ("current", current)):
        before = packet.to_dict()
        pin = store.save_packet(packet, name)
        loaded = store.load_packet(pin)
        assert loaded.to_dict() == before
        report = loaded.terms("commercial_product", store=store)
        assert report["aspect_mapping"] == before["aspect_mapping"]
        assert loaded.to_dict() == before


def test_failed_obsolete_diagnostic_cannot_remove_an_upstream_named_identifier():
    result = card(
        ["MONDO:0000001"], [record("error", "MONDO:0000001", "obsolete_term")]
    )
    assert result.diseases(grouping_rule="disease_grouping@2")["diseases"] == []
    assert result.diseases()["diseases"][0]["mondo"] == "MONDO:0000001"
