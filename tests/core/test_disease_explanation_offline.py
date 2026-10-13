"""Disease groups expose exact stored support without acquiring new knowledge."""

from copy import deepcopy

import ackredit
import argdigest
import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.core.errors import ArgumentError, StorageError
from sabueso.core.relationship_store import make_relationship
from sabueso.core.source_assertion_store import make_source_assertion
from sabueso.mappings.mondo import map_hierarchy
from sabueso.resolver import EntityResolver, FixtureUniProtClient
from sabueso.tools.db.clinvar import FixtureClinVarClient
from sabueso.tools.db.diseases import FixtureDISEASESClient
from sabueso.tools.db.medgen import FixtureMedGenClient
from sabueso.tools.db.mondo import FixtureMONDOClient
from sabueso.tools.db.open_targets import FixtureOpenTargetsClient
from sabueso.tools.db.orphadata import FixtureOrphadataClient

TERM = "mondo:MONDO:0014221"


@pytest.fixture(scope="module")
def public_card():
    with pytest.warns(Warning):  # declared public ClinVar/Open Targets fixture cuts
        card, _ = sabueso.resolve(
            "P60174",
            resolver=EntityResolver(FixtureUniProtClient("temp_data")),
            diseases={},
            diseases_client=FixtureDISEASESClient("temp_data"),
            open_targets={},
            open_targets_client=FixtureOpenTargetsClient("temp_data"),
            orphadata=True,
            orphadata_client=FixtureOrphadataClient("temp_data"),
            clinvar={},
            clinvar_client=FixtureClinVarClient("temp_data"),
            medgen=True,
            medgen_client=FixtureMedGenClient("temp_data"),
            disease_identity=True,
            mondo_client=FixtureMONDOClient("temp_data"),
        )
    return card


def relationships(answer):
    for row in answer["statements"] + answer["ungrouped_context"]["statements"]:
        if row["input"]["basis"] == "relationship":
            yield row["input"]
        for path in row["identity"]:
            yield from path["links"]
            yield from path["alternatives"]
        for path in row["hierarchy"]:
            yield from path["links"]


def test_public_group_retains_each_source_and_exact_annotation_members(
    public_card, monkeypatch
):
    from sabueso.tools.db import _http

    monkeypatch.setattr(
        _http, "_urlopen", lambda *a, **k: pytest.fail("no acquisition")
    )
    before = public_card.to_dict()
    with ackredit.session("inert explanation"):
        credited = ackredit.get_attribution().to_dict()
        answer = public_card.explain_disease(TERM)
        assert ackredit.get_attribution().to_dict() == credited
    assert answer["status"] == "on_card" and not answer["gaps"]
    assert answer["rule"]["rule"] == "disease_group_explanation@3"
    assert answer["rule"]["inputs"] == [public_card.pinned_ref()]
    assert answer["grouping_rule"]["rule"] == "disease_grouping@3"
    assert answer["group"] == next(
        g for g in public_card.diseases()["diseases"] if g["mondo"] == "MONDO:0014221"
    )
    assert answer["group"]["sources"] == [
        "ClinVar",
        "DISEASES",
        "Open Targets",
        "Orphanet",
        "UniProt",
    ]
    for row in answer["statements"]:
        basis = row["input"]
        assert basis["source_assertions"] and all(
            a["found"] for a in basis["source_assertions"]
        )
        if basis["basis"] == "selected_annotation_member":
            assert all(
                a["asserted_value"] in basis["members"]
                for a in basis["source_assertions"]
            )
            if row["statement"]["kind"] == "clinvar_condition":
                assert {a["record"] for a in basis["source_assertions"]} == {
                    row["statement"]["variant"]
                }
    chains = [
        path
        for row in answer["statements"]
        for path in row["identity"]
        if len(path["links"]) == 2
    ]
    assert chains and {
        r["relationship"]["qualifiers"]["source"] for r in chains[0]["links"]
    } == {"MedGen", "MONDO"}
    assert {
        row["statement"]["reason"] for row in answer["ungrouped_context"]["statements"]
    } >= {"condition_not_provided", "no_id_stated", "no_stated_equivalence"}
    answer["group"]["names"].clear()
    answer["statements"][0]["input"]["source_assertions"].clear()
    assert public_card.to_dict() == before


def test_historical_explanation_keeps_every_relationship_and_assertion_pin(
    public_card, tmp_path
):
    store = sabueso.KnowledgeStore(tmp_path / "knowledge.db")
    pin = store.save(public_card)
    expected = public_card.explain_disease(TERM)
    later = Card.from_dict(public_card.to_dict())
    later.meta["later_observation"] = True
    store.save(later)
    assert store.load(pin).explain_disease(TERM) == expected
    for link in relationships(expected):
        assert store.relationship(link["relationship_ref"]) == link["relationship"]
        for assertion in link["source_assertions"]:
            assert (
                store.source_assertion(assertion["source_assertion_ref"])[
                    "asserted_value"
                ]
                == assertion["asserted_value"]
            )


@pytest.mark.parametrize("route", ["association", "identity", "annotation"])
def test_missing_assertion_support_is_partial(public_card, route):
    subject = Card.from_dict(public_card.to_dict())
    explanation = subject.explain_disease(TERM)
    if route == "annotation":
        row = next(
            r
            for r in explanation["statements"]
            if r["input"]["basis"] == "selected_annotation_member"
        )
        identifier = row["input"]["source_assertions"][0]["id"]
    else:
        row = next(
            r
            for r in relationships(explanation)
            if r["relationship"]["predicate"]
            == ("associated_with" if route == "association" else "same_as")
        )
        identifier = row["source_assertions"][0]["id"]
    subject.source_assertion_store.store.pop(identifier)
    answer = subject.explain_disease(TERM)
    assert answer["status"] == "partial"
    assert any(g["reason"] == "missing_source_assertion" for g in answer["gaps"])


def synthetic(conditions, equivalents=(), hierarchy=()):
    card = Card(
        meta={"card_id": "sabueso:protein:uniprot:P60174", "entity_type": "protein"},
        quality={
            "enrichments": [{"source": "MONDO", "status": "added", "ungrouped": []}]
        },
    )
    item = {"accession": "VCV_SYNTHETIC", "conditions": conditions}
    assertion = make_source_assertion(
        "annotations.clinical_variants",
        item,
        "ClinVar",
        item["accession"],
        "2026-01-01",
    )
    card.source_assertion_store.add(assertion)
    card.set("annotations.clinical_variants", [item], [assertion["id"]])
    for subject, obj in equivalents:
        assertion = make_source_assertion(
            "relationships.same_as",
            {"mondo": obj},
            "MONDO",
            obj,
            "2026-01-01",
            subject_ref=subject,
        )
        card.source_assertion_store.add(assertion)
        card.relationship_store.add(
            make_relationship(
                subject,
                "same_as",
                f"mondo:{obj}",
                qualifiers={"source": "MONDO"},
                source_assertion_ids=[assertion["id"]],
            )
        )
    if hierarchy:
        mapped = map_hierarchy(
            [
                [
                    {
                        "term": a,
                        "parent": b,
                        "retrieved_at": "2026-01-01",
                        "version": "synthetic",
                    }
                    for a, b in zip(hierarchy, hierarchy[1:])
                ]
            ]
        )
        for assertion in mapped["source_assertions"]:
            card.source_assertion_store.add(assertion)
        for rel in mapped["relationships"]:
            card.relationship_store.add(rel)
    return card


def test_stated_hierarchy_is_explained_with_every_step_and_rule():
    path = ["MONDO:0000003", "MONDO:0000005", "MONDO:0000009"]
    subject = synthetic(
        [{"name": "synthetic condition", "xrefs": [path[0], "Orphanet:9"]}],
        [("Orphanet:9", path[-1])],
        path,
    )
    answer = subject.explain_disease(f"mondo:{path[-1]}")
    assert answer["status"] == "on_card"
    (step,) = answer["statements"][0]["hierarchy"]
    assert step["path"] == path
    (link,) = step["links"]
    assert link["relationship"]["derivation"]["rule"] == "mondo_hierarchy@1"
    assert len(link["source_assertions"]) == 2


def test_identity_conflicts_are_ungrouped_never_silently_selected():
    subject = synthetic(
        [{"name": "synthetic condition", "xrefs": ["MONDO:0000001", "OMIM:1"]}],
        [("OMIM:1", "MONDO:0000002")],
    )
    answer = subject.explain_disease("MONDO:0000001")
    assert answer["status"] == "not_on_card" and answer["group"] is None
    (row,) = answer["ungrouped_context"]["statements"]
    assert row["statement"]["reason"] == "conflicting_identity"
    assert set(row["statement"]["terms"]) == {"MONDO:0000001", "MONDO:0000002"}
    assert row["input"]["source_assertions"][0]["found"]


def test_lookup_alternatives_and_qualifier_conflicts_remain_visible():
    subject = synthetic(
        [{"name": "synthetic condition", "xrefs": ["OMIM:1"]}],
        [("OMIM:1", "MONDO:0000001"), ("OMIM:1", "MONDO:0000002")],
    )
    rel = subject.relationships("same_as")[-1]
    rel["qualifier_conflicts"] = {
        "mondo_name": ["synthetic name", "synthetic alternative"]
    }
    answer = subject.explain_disease(
        "MONDO:0000002", grouping_rule="disease_grouping@1"
    )
    assert answer["status"] == "partial"
    (path,) = answer["statements"][0]["identity"]
    assert len(path["links"]) == len(path["alternatives"]) == 1
    assert (
        path["links"][0]["relationship"]["qualifier_conflicts"]
        == rel["qualifier_conflicts"]
    )
    assert path["alternatives"][0]["selected"] is False
    assert any(g["reason"] == "ambiguous_stored_identity" for g in answer["gaps"])


def test_field_selection_alternatives_are_context_not_selected_members(public_card):
    subject = Card.from_dict(public_card.to_dict())
    node = subject.get("annotations.disease")
    alternative = deepcopy(
        subject.source_assertion_store.get(node["source_assertion_ids"][0])
    )
    alternative["id"] += "_synthetic_alternative"
    alternative["asserted_value"]["name"] = "synthetic competing annotation"
    subject.source_assertion_store.add(alternative)
    subject.quality.setdefault("conflicts", []).append(
        {"field": "annotations.disease", "synthetic_alternative": alternative["id"]}
    )
    answer = subject.explain_disease(TERM)
    field = next(
        f
        for f in answer["field_context"]["fields"]
        if f["field_path"] == "annotations.disease"
    )
    assert field["alternatives"][0]["id"] == alternative["id"]
    assert field["conflicts"][0]["synthetic_alternative"] == alternative["id"]
    assert alternative["id"] not in {
        a["id"] for r in answer["statements"] for a in r["input"]["source_assertions"]
    }


def test_missing_group_unqueried_identity_and_argument_validation(public_card):
    answer = public_card.explain_disease("MONDO:9999999")
    assert (answer["status"], answer["reason"]) == (
        "not_on_card",
        "no_stored_disease_group",
    )
    subject = synthetic([{"name": "synthetic condition", "xrefs": ["OMIM:1"]}])
    subject.quality.clear()
    assert (
        subject.explain_disease("MONDO:0000001")["ungrouped_context"]["statements"][0][
            "statement"
        ]["reason"]
        == "identity_not_queried"
    )
    assert public_card.explain_disease(
        " mondo:mondo:0014221 "
    ) == public_card.explain_disease(TERM)
    for invalid in (None, "doid:DOID:0050884", "MONDO:1", "TPI deficiency", 14221):
        with pytest.raises(ArgumentError):
            public_card.explain_disease(invalid)
    with pytest.raises(argdigest.UnknownArgumentError):
        public_card.explain_disease(TERM, surprise=True)
    with pytest.raises(StorageError):
        Card().explain_disease(TERM)


def add_identity(card, subject, target, source="MedGen", version="synthetic"):
    assertion = make_source_assertion(
        "relationships.same_as",
        {"target": target, "version": version},
        source,
        target,
        "2026-01-01",
        subject_ref=subject,
    )
    assertion["source"]["version"] = version
    card.source_assertion_store.add(assertion)
    card.relationship_store.add(
        make_relationship(
            subject,
            "same_as",
            target,
            qualifiers={"source": source},
            source_assertion_ids=[assertion["id"]],
        )
    )
    return assertion["id"]


@pytest.mark.parametrize("hierarchy", [(), ("MONDO:0000001", "MONDO:0000002")])
def test_multiple_targets_of_one_id_stay_conflicting_in_every_storage_order(hierarchy):
    pairs = [("OMIM:1", "MONDO:0000001"), ("OMIM:1", "MONDO:0000002")]
    cards = [
        synthetic([{"xrefs": ["OMIM:1"]}], order, hierarchy)
        for order in (pairs, pairs[::-1])
    ]
    assert cards[0].diseases() == cards[1].diseases()
    for card in cards:
        before = card.to_dict()
        answer = card.explain_disease("MONDO:0000001")
        assert answer["status"] == "not_on_card" and answer["group"] is None
        (row,) = answer["ungrouped_context"]["statements"]
        assert row["statement"]["reason"] == "conflicting_identity"
        assert {p["term"] for p in row["identity"][0]["paths"]} == {p[1] for p in pairs}
        links = row["identity"][0]["links"]
        assert len(links) == 2 and all(not r["selected"] for r in links)
        assert all(r["source_assertions"][0]["found"] for r in links)
        assert card.to_dict() == before


@pytest.mark.parametrize(
    "targets",
    [
        ("MONDO:0000001", "MONDO:0000002"),
        ("MONDO:0000001", "MONDO:0000001"),
        ("MONDO:0000001", None),
    ],
)
def test_every_medgen_branch_is_retained_without_selecting_a_uid(targets):
    cards = []
    for order in ((0, 1), (1, 0)):
        card = synthetic([{"xrefs": ["MEDGEN:C1"]}])
        for i in order:
            uid = f"MEDGEN:{i + 1}"
            add_identity(card, "MEDGEN:C1", uid)
            if targets[i]:
                add_identity(card, uid, f"mondo:{targets[i]}", "MONDO")
        cards.append(card)
    assert cards[0].diseases() == cards[1].diseases()
    answer = cards[0].explain_disease("MONDO:0000001")
    rows = answer["statements"] or answer["ungrouped_context"]["statements"]
    paths = rows[0]["identity"][0]["paths"]
    assert len(paths) == 2 and {p["term"] for p in paths} == set(targets)
    assert all(len(p["links"]) == (2 if p["term"] else 1) for p in paths)
    if len(set(targets)) == 1:
        assert answer["status"] == "on_card"
    else:
        assert answer["group"] is None
        assert rows[0]["statement"]["reason"] == (
            "incomplete_identity" if None in targets else "conflicting_identity"
        )


def test_direct_naming_does_not_hide_a_contradictory_stored_equivalence():
    card = synthetic(
        [{"xrefs": ["MONDO:0000001"]}], [("MONDO:0000001", "MONDO:0000002")]
    )
    (row,) = card.diseases()["ungrouped"]
    assert row["reason"] == "conflicting_identity"
    assert {p["basis"] for p in row["identity_paths"]} == {"named_directly", "same_as"}
    assert (
        card.diseases(grouping_rule="disease_grouping@1")["diseases"][0]["mondo"]
        == "MONDO:0000001"
    )


def test_ambiguous_mondo_targets_after_a_single_medgen_hop_keep_both_chains():
    card = synthetic([{"xrefs": ["MEDGEN:C1"]}])
    add_identity(card, "MEDGEN:C1", "MEDGEN:1")
    for term in ("MONDO:0000001", "MONDO:0000002"):
        add_identity(card, "MEDGEN:1", f"mondo:{term}", "MONDO")
    answer = card.explain_disease("MONDO:0000001")
    (row,) = answer["ungrouped_context"]["statements"]
    assert row["statement"]["reason"] == "conflicting_identity"
    (identity,) = row["identity"]
    assert len(identity["links"]) == 3
    assert {p["term"] for p in identity["paths"]} == {"MONDO:0000001", "MONDO:0000002"}
    assert all(len(p["links"]) == 2 for p in identity["paths"])


@pytest.mark.parametrize("source", ["MONDO", "Unrelated source"])
def test_source_and_version_do_not_silently_select_an_identity(source):
    cards = []
    ids = set()
    for order in ((0, 1), (1, 0)):
        card = synthetic([{"xrefs": ["OMIM:1"]}])
        for i in order:
            ids.add(
                add_identity(
                    card,
                    "OMIM:1",
                    f"mondo:MONDO:000000{i + 1}",
                    "MONDO" if i == 0 else source,
                    f"202{i}",
                )
            )
        cards.append(card)
    assert cards[0].diseases() == cards[1].diseases()
    answer = cards[0].explain_disease("MONDO:0000001")
    if source == "MONDO":
        assert answer["group"] is None
        supported = [
            a
            for r in relationships(answer)
            for a in r["source_assertions"]
            if a["id"] in ids
        ]
        assert {a["version"] for a in supported} == {"2020", "2021"}
    else:
        assert answer["status"] == "on_card"
        assert len(answer["statements"][0]["identity"][0]["paths"]) == 1


def test_converging_versions_and_source_qualifier_conflicts_keep_every_support():
    cards = []
    for sources in (("Unrelated source", "MONDO"), ("MONDO", "Unrelated source")):
        card = synthetic([{"xrefs": ["OMIM:1"]}])
        for source in sources:
            for version in ("older", "newer"):
                add_identity(card, "OMIM:1", "mondo:MONDO:0000001", source, version)
        cards.append(card)
    assert cards[0].diseases() == cards[1].diseases()
    for card in cards:
        answer = card.explain_disease("MONDO:0000001")
        (link,) = answer["statements"][0]["identity"][0]["links"]
        assert answer["status"] == "on_card" and len(link["source_assertions"]) == 4
        assert set(link["relationship"]["qualifier_conflicts"]["source"]) == {
            "MONDO",
            "Unrelated source",
        }


def test_name_conflicts_are_retained_without_choosing_a_label():
    card = synthetic([{"xrefs": ["OMIM:1"]}], [("OMIM:1", "MONDO:0000001")])
    rel = card.relationships("same_as")[0]
    rel["qualifiers"]["mondo_name"] = "first label"
    rel["qualifier_conflicts"] = {"mondo_name": ["first label", "second label"]}
    (group,) = card.diseases()["diseases"]
    assert group["mondo_names"] == ["first label", "second label"]
    assert "mondo_name" not in group
    rel["qualifiers"]["mondo_name"] = "second label"
    rel["qualifier_conflicts"]["mondo_name"].reverse()
    assert card.diseases()["diseases"] == [group]


def test_hierarchy_path_alternatives_are_preserved_in_group_and_explanation():
    narrow, broad = "MONDO:0000001", "MONDO:0000009"
    card = synthetic([{"xrefs": [narrow, broad]}], hierarchy=[narrow, broad])
    rel = card.relationships("subclass_of")[0]
    alternatives = [[narrow, broad], [narrow, "MONDO:0000005", broad]]
    rel["qualifier_conflicts"] = {"path": alternatives}
    expected = card.diseases()
    answer = card.explain_disease(broad)
    assert answer["statements"][0]["hierarchy"][0]["paths"] == sorted(alternatives)
    rel["qualifiers"]["path"] = alternatives[-1]
    rel["qualifier_conflicts"]["path"] = alternatives[::-1]
    assert card.diseases() == expected


def test_explicit_legacy_view_and_explanation_survive_historical_storage(tmp_path):
    card = synthetic(
        [{"xrefs": ["OMIM:1"]}],
        [("OMIM:1", "MONDO:0000001"), ("OMIM:1", "MONDO:0000002")],
    )
    store = sabueso.KnowledgeStore(tmp_path / "rules.db")
    before = card.to_dict()
    pin = store.save(card)
    legacy = card.explain_disease("MONDO:0000002", grouping_rule="disease_grouping@1")
    current = card.explain_disease("MONDO:0000002")
    assert legacy["rule"]["rule"] == "disease_group_explanation@1"
    assert legacy["group"]["mondo"] == "MONDO:0000002" and legacy["status"] == "partial"
    assert (
        current["group"] is None
        and current["rule"]["rule"] == "disease_group_explanation@3"
    )
    loaded = store.load(pin)
    assert (
        loaded.explain_disease("MONDO:0000002", grouping_rule="disease_grouping@1")
        == legacy
    )
    assert loaded.explain_disease("MONDO:0000002") == current
    for link in relationships(current):
        assert store.relationship(link["relationship_ref"]) == link["relationship"]
        for assertion in link["source_assertions"]:
            assert (
                store.source_assertion(assertion["source_assertion_ref"])[
                    "asserted_value"
                ]
                == assertion["asserted_value"]
            )
    assert card.to_dict() == before and card.pinned_ref() == pin


@pytest.mark.parametrize("invalid", [None, "disease_grouping@4", "@2", 2, []])
def test_grouping_rule_arguments_refuse_unknown_versions(invalid):
    card = synthetic([])
    with pytest.raises(ArgumentError):
        card.diseases(grouping_rule=invalid)
    with pytest.raises(ArgumentError):
        card.explain_disease("MONDO:0000001", grouping_rule=invalid)
