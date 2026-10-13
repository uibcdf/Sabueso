"""Disease cards: one disease across terminologies, joined only through MONDO's stated
equivalences (#90). Frozen MONDO terms of release v2026-09-01."""

import json

import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.core.errors import ArgumentError
from sabueso.tools.db.mondo import (
    FixtureMONDOClient,
    get_term,
    normalize,
    parse_release,
)

TPI_DEFICIENCY = "sabueso:disease:mondo:MONDO:0014221"


@pytest.fixture(scope="module")
def mondo():
    return FixtureMONDOClient("temp_data")


def _resolve(query, mondo, **options):
    return sabueso.resolve(query, mondo_client=mondo, **options)


@pytest.mark.parametrize(
    "query",
    [
        "mondo:MONDO:0014221",
        "MONDO:0014221",
        "MONDO_0014221",
        "doid:DOID:0050884",
        "DOID:0050884",
        "orphanet:868",
        "ORPHA:868",
        "omim:615512",
        "mesh:C566029",
    ],
)
def test_every_stated_equivalent_resolves_to_one_disease(query, mondo):
    card, resolution = _resolve(query, mondo)
    assert resolution.status == "resolved"
    assert card.id == TPI_DEFICIENCY
    assert resolution.decision["route"]["entity_type"] == "disease"
    if not query.upper().startswith("MONDO"):
        identity = resolution.decision["identity"]
        assert identity["rule"] == "mondo_equivalence@1"
        assert (identity["stated_by"], identity["release"]) == ("MONDO", "2026-09-01")
        assert identity["mondo"] == "MONDO:0014221"


def test_the_card_holds_what_mondo_states(mondo):
    card, _ = _resolve("ORPHA:868", mondo)
    assert card.meta["entity_type"] == "disease"
    assert card.get("names.canonical_name")["value"] == (
        "triosephosphate isomerase deficiency"
    )
    equivalent = card.get("identifiers.equivalent_ids")["value"]
    assert {"DOID:0050884", "Orphanet:868", "OMIM:615512"} <= set(equivalent)
    related = card.get("identifiers.related_ids") or {"value": []}
    assert not set(related["value"]) & set(equivalent)
    parents = {r["object_ref"] for r in card.relationships("subclass_of")}
    assert "mondo:MONDO:0002908" in parents
    assert all(r["source_assertion_ids"] for r in card.relationships("subclass_of"))
    assert card.get("annotations.definition")["value"]["text"]


def test_a_related_xref_is_never_identity(mondo):
    # MONDO lists EFO:0001360 for type 2 diabetes only as the source of other xrefs,
    # not as an equivalent: it does not resolve.
    card, resolution = _resolve("efo:EFO:0001360", mondo)
    assert card is None
    assert resolution.status == "not_found"
    assert resolution.decision["rules"] == ["no_stated_equivalence"]


def test_an_obsolete_term_names_its_replacement_but_is_not_followed(mondo):
    card, resolution = _resolve("MONDO:0000002", mondo)
    assert card is None and resolution.status == "obsolete"
    assert [c["entity_ref"] for c in resolution.candidates] == [
        "sabueso:disease:mondo:MONDO:0009299"
    ]
    assert resolution.candidates[0]["basis"] == {
        "stated_by": "MONDO",
        "replaced_by": "MONDO:0009299",
    }


def test_ids_of_other_entities_in_shared_namespaces_are_not_found(mondo):
    # OMIM also numbers genes (190450 is TPI1): no MONDO equivalence, never a disease.
    card, resolution = _resolve("omim:190450", mondo)
    assert card is None and resolution.status == "not_found"


def test_proteins_and_molecules_keep_their_routes():
    from sabueso.tools.resolve import _route

    assert _route("P60174", None)[0] == "protein"
    assert _route("pdb:1HTI", None)[0] == "protein"
    assert _route("TPIS_HUMAN", None)[0] == "protein"
    assert _route("chembl:CHEMBL25", None)[0] == "small_molecule"
    assert _route("doid:9352", None)[0] == "disease"


def test_a_failing_source_is_an_error_not_an_absence():
    card, resolution = _resolve(
        "ORPHA:868", FixtureMONDOClient("temp_data", failing={"Orphanet:868"})
    )
    assert card is None and resolution.status == "error"


def test_the_card_survives_storage_and_migration(mondo, tmp_path):
    card, _ = _resolve("ORPHA:868", mondo)
    data = json.loads(json.dumps(card.to_dict()))
    assert Card.from_dict(data).id == TPI_DEFICIENCY
    store = sabueso.KnowledgeStore(tmp_path / "k.db")
    ref = store.save(card)
    assert store.load(ref).get("identifiers.mondo")["value"] == "MONDO:0014221"
    report = sabueso.migrate_card(data)
    assert report.quality["migration"][-1]["steps"] == []


def test_normalization_of_the_forms_sources_write():
    assert normalize("efo:EFO:0008559") == "EFO:0008559"
    assert normalize("EFO_0008559") == "EFO:0008559"
    assert normalize("mondo:MONDO:0001444") == "MONDO:0001444"
    assert normalize("ORPHA:868") == "Orphanet:868"
    assert normalize("mesh:D003924") == "MESH:D003924"
    assert normalize("uniprot:P60174") is None
    assert normalize("P60174") is None


def test_only_equivalent_xrefs_enter_the_index():
    text = (
        "format-version: 1.2\ndata-version: releases/2026-01-01\n\n[Term]\n"
        "id: MONDO:1\nname: a disease\n"
        'xref: DOID:1 {source="MONDO:equivalentTo"}\n'
        'xref: GARD:1 {source="MONDO:GARD"}\n'
    )
    version, terms, equivalents = parse_release(text)
    assert version == "2026-01-01"
    assert equivalents == {"DOID:1": "MONDO:1"}
    assert [x["equivalent"] for x in terms["MONDO:1"]["xrefs"]] == [True, False]


def test_the_public_function_and_the_entity_type(mondo):
    result = get_term("MONDO:0001444", client=mondo)
    assert result["source"] == "MONDO" and result["version"] == "2026-09-01"
    assert result["record"]["name"] == "Chagas disease"
    card, _ = sabueso.resolve(
        "MONDO:0001444", entity_type="disease", mondo_client=mondo
    )
    assert card.get("names.canonical_name")["value"] == "Chagas disease"
    with pytest.raises(ArgumentError):
        sabueso.resolve("MONDO:0001444", entity_type="illness")


# --- A protein's diseases, grouped through MONDO (#90, step 2) -------------------------


@pytest.fixture(scope="module")
def hstim(mondo):
    import warnings

    from sabueso.resolver import EntityResolver, FixtureUniProtClient
    from sabueso.tools.db.clinvar import FixtureClinVarClient
    from sabueso.tools.db.diseases import FixtureDISEASESClient
    from sabueso.tools.db.open_targets import FixtureOpenTargetsClient
    from sabueso.tools.db.orphadata import FixtureOrphadataClient

    def build(**identity):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # the saved ClinVar and OT rows are cuts
            card, _ = sabueso.resolve(
                "P60174",
                resolver=EntityResolver(FixtureUniProtClient("temp_data")),
                diseases={"channels": ["knowledge", "experiments", "textmining"]},
                diseases_client=FixtureDISEASESClient("temp_data"),
                open_targets={},
                open_targets_client=FixtureOpenTargetsClient("temp_data"),
                orphadata=True,
                orphadata_client=FixtureOrphadataClient("temp_data"),
                clinvar={},
                clinvar_client=FixtureClinVarClient("temp_data"),
                **identity,
            )
        return card

    from sabueso.tools.db.medgen import FixtureMedGenClient

    return (
        build(
            medgen=True,
            medgen_client=FixtureMedGenClient("temp_data"),
            disease_identity=True,
            mondo_client=mondo,
        ),
        build(),
    )


def test_one_disease_across_every_source_that_states_it(hstim):
    card, _ = hstim
    view = card.diseases()
    assert view["rule"]["rule"] == "disease_grouping@3"
    (tpi,) = [d for d in view["diseases"] if d["mondo"] == "MONDO:0014221"]
    assert tpi["mondo_name"] == "triosephosphate isomerase deficiency"
    assert tpi["sources"] == [
        "ClinVar",
        "DISEASES",
        "Open Targets",
        "Orphanet",
        "UniProt",
    ]
    assert {"doid:DOID:0050884", "orphanet:ORPHA:868", "omim:615512"} <= set(
        tpi["refs"]
    )
    bases = {hop["basis"] for s in tpi["statements"] for hop in s["grouped_by"]}
    # MedGen's concept id reaches the same term through MedGen's record and MONDO.
    assert bases == {"same_as", "named_directly", "medgen_same_as"}


def test_identity_is_a_stated_same_as_never_a_name(hstim):
    card, _ = hstim
    for rel in card.relationships("same_as"):
        if rel["object_ref"].startswith("mondo:"):
            assert rel["qualifiers"]["basis"] == "mondo_equivalence@1"
            assert rel["qualifiers"]["source"] == "MONDO"
            (sa,) = [
                card.source_assertion_store.get(i) for i in rel["source_assertion_ids"]
            ]
            assert sa["source"]["name"] == "MONDO"
            assert sa["source"]["version"] == "2026-09-01"


def test_what_mondo_does_not_state_stays_apart_with_its_reason(hstim):
    card, _ = hstim
    ungrouped = card.diseases()["ungrouped"]
    assert {u["reason"] for u in ungrouped} == {
        "no_stated_equivalence",
        "condition_not_provided",
        "no_id_stated",
        "incomplete_identity",
    }
    # ClinVar's "not provided" and "not specified" are not diseases.
    placeholders = [u for u in ungrouped if u["reason"] == "condition_not_provided"]
    assert {u["name"] for u in placeholders} == {"not provided", "not specified"}
    # Some Open Targets EFO terms have no MONDO equivalence: none is matched by name.
    assert any(
        u["reason"] == "no_stated_equivalence" and u["source"] == "Open Targets"
        for u in ungrouped
    )
    (text_only,) = {u["name"] for u in ungrouped if u["reason"] == "no_id_stated"}
    assert text_only == "TPI1-related disorder"
    (record,) = [e for e in card.quality["enrichments"] if e["source"] == "MONDO"]
    assert record["status"] == "added" and record["version"] == "2026-09-01"


def test_without_the_enrichment_only_the_same_id_groups(hstim):
    _, card = hstim
    view = card.diseases()
    # Statements that name the same MONDO id are one disease; everything else waits
    # for MONDO's answer.
    assert {
        hop["basis"]
        for d in view["diseases"]
        for s in d["statements"]
        for hop in s["grouped_by"]
    } == {"named_directly"}
    assert {u["reason"] for u in view["ungrouped"]} == {
        "identity_not_queried",
        "condition_not_provided",
        "no_id_stated",
    }
    assert any(u["refs"] == ["doid:DOID:0050884"] for u in view["ungrouped"])


def test_disease_ids_are_diseases_in_the_glossary(hstim):
    card, _ = hstim
    entities = card.entities()
    entry = entities["mondo:MONDO:0014221"]
    assert entry["entity_type"] == "disease"
    assert "DOID:0050884" in entry["records"]
    assert (
        entities[card.meta["card_id"].split("sabueso:protein:")[1]]["entity_type"]
        == "protein"
    )


def test_a_protein_with_no_disease_has_nothing_to_ask(mondo):
    from sabueso.resolver import EntityResolver, FixtureUniProtClient

    card, _ = sabueso.resolve(
        "P52270",
        resolver=EntityResolver(FixtureUniProtClient("temp_data")),
        disease_identity=True,
        mondo_client=mondo,
    )
    (record,) = [e for e in card.quality["enrichments"] if e["source"] == "MONDO"]
    assert record["status"] == "not_queried"
    assert record["detail"] == "the card names no disease"


class _Card:
    """The little a view reads, to state cases no fixture holds."""

    def __init__(self, conditions, same_as, subclass_of=()):
        from sabueso.core.relationship_store import make_relationship

        self.quality = {"enrichments": [{"source": "MONDO", "ungrouped": []}]}
        self._conditions = conditions
        self._rels = [
            make_relationship(
                subject,
                "same_as",
                obj,
                qualifiers={"source": source, "mondo_name": "a name"},
                source_assertion_ids=["SA_x"],
            )
            for subject, obj, source in same_as
        ] + [
            make_relationship(
                f"mondo:{path[0]}",
                "subclass_of",
                f"mondo:{path[-1]}",
                qualifiers={"source": "MONDO", "path": list(path)},
                source_assertion_ids=["SA_y"],
            )
            for path in subclass_of
        ]

    def get(self, path):
        if path == "annotations.clinical_variants":
            return {"value": [{"accession": "VCV1", "conditions": self._conditions}]}
        return None

    def relationships(self, predicate=None):
        return [r for r in self._rels if predicate in (None, r["predicate"])]


def test_a_condition_named_only_by_medgen_reaches_mondo_through_two_statements():
    from sabueso.core.diseases import diseases_view

    card = _Card(
        [{"name": "TPI deficiency", "xrefs": ["MedGen:C1860808"]}],
        [
            ("MEDGEN:C1860808", "MEDGEN:349893", "MedGen"),
            ("MEDGEN:349893", "mondo:MONDO:0014221", "MONDO"),
        ],
    )
    (disease,) = diseases_view(card)["diseases"]
    assert disease["mondo"] == "MONDO:0014221"
    assert disease["statements"][0]["grouped_by"] == [
        {"id": "MEDGEN:C1860808", "basis": "medgen_same_as"}
    ]


def test_ids_that_reach_two_terms_are_a_conflict_never_a_choice():
    from sabueso.core.diseases import diseases_view

    card = _Card(
        [{"name": "x", "xrefs": ["MONDO:MONDO:0000001", "OMIM:1"]}],
        [("OMIM:1", "mondo:MONDO:0000002", "MONDO")],
    )
    view = diseases_view(card)
    assert view["diseases"] == []
    (conflict,) = view["ungrouped"]
    assert conflict["reason"] == "conflicting_identity"
    assert set(conflict["terms"]) == {"MONDO:0000001", "MONDO:0000002"}


def test_a_condition_named_at_two_granularities_joins_the_broader_disease():
    from sabueso.core.diseases import diseases_view

    # ClinVar names one condition by a subtype's MONDO and OMIM ids and by a broader
    # Orphanet id. MONDO places the subtype under the broader term. What holds for the
    # subtype holds for the disease it belongs to, not the reverse.
    card = _Card(
        [{"name": "x", "xrefs": ["MONDO:MONDO:0000003", "OMIM:3", "Orphanet:9"]}],
        [
            ("OMIM:3", "mondo:MONDO:0000003", "MONDO"),
            ("Orphanet:9", "mondo:MONDO:0000009", "MONDO"),
        ],
        subclass_of=[("MONDO:0000003", "MONDO:0000005", "MONDO:0000009")],
    )
    view = diseases_view(card)
    assert view["ungrouped"] == []
    ((disease, statement),) = [
        (d, s) for d in view["diseases"] for s in d["statements"]
    ]
    assert disease["mondo"] == "MONDO:0000009"
    assert statement["narrower"] == {
        "MONDO:0000003": {
            "ids": [
                {"id": "MONDO:0000003", "basis": "named_directly"},
                {"id": "OMIM:3", "basis": "same_as"},
            ],
            "path": ["MONDO:0000003", "MONDO:0000005", "MONDO:0000009"],
        }
    }
    assert view["rule"]["parameters"]["granularity"] == "mondo_hierarchy@1"


def test_terms_that_are_not_one_above_the_other_stay_a_conflict():
    from sabueso.core.diseases import diseases_view

    # Two subtypes of one disease: MONDO places both under it, neither under the other.
    card = _Card(
        [{"name": "x", "xrefs": ["MONDO:MONDO:0000003", "MONDO:MONDO:0000004"]}],
        [],
        subclass_of=[
            ("MONDO:0000003", "MONDO:0000009"),
            ("MONDO:0000004", "MONDO:0000009"),
        ],
    )
    (conflict,) = diseases_view(card)["ungrouped"]
    assert conflict["reason"] == "conflicting_identity"


def test_the_enrichment_records_mondo_s_chain_between_the_terms_a_card_reaches(
    tmp_path,
):
    from sabueso.enrichers.disease_identity import _hierarchy
    from sabueso.mappings.mondo import map_hierarchy

    obo = tmp_path / "mondo" / "mondo.obo"
    obo.parent.mkdir()
    obo.write_text(
        "data-version: releases/2026-09-01\n\n"
        "[Term]\nid: MONDO:0000009\nname: broad\n\n"
        "[Term]\nid: MONDO:0000005\nname: middle\nis_a: MONDO:0000009 ! broad\n\n"
        "[Term]\nid: MONDO:0000003\nname: subtype\nis_a: MONDO:0000005 ! middle\n\n"
        "[Term]\nid: MONDO:0000004\nname: other\nis_a: MONDO:0000009 ! broad\n",
        encoding="utf-8",
    )
    from sabueso.core.errors import RecordNotFoundError

    client = FixtureMONDOClient(tmp_path)
    chains = _hierarchy(
        client, ["MONDO:0000003", "MONDO:0000004", "MONDO:0000009"], RecordNotFoundError
    )
    mapped = map_hierarchy(chains)
    pairs = {(r["subject_ref"], r["object_ref"]): r for r in mapped["relationships"]}
    # Only the pairs where one term is above the other; siblings are not related.
    assert set(pairs) == {
        ("mondo:MONDO:0000003", "mondo:MONDO:0000009"),
        ("mondo:MONDO:0000004", "mondo:MONDO:0000009"),
    }
    far = pairs[("mondo:MONDO:0000003", "mondo:MONDO:0000009")]
    # Two stated is_a steps: each a MONDO SourceAssertion, their closure derived.
    assert far["qualifiers"]["path"] == [
        "MONDO:0000003",
        "MONDO:0000005",
        "MONDO:0000009",
    ]
    assert len(far["source_assertion_ids"]) == 2
    assert far["derivation"]["rule"] == "mondo_hierarchy@1"
    near = pairs[("mondo:MONDO:0000004", "mondo:MONDO:0000009")]
    assert "derivation" not in near  # one step: MONDO's own statement
    assert {sa["source"]["version"] for sa in mapped["source_assertions"]} == {
        "2026-09-01"
    }


# --- From a disease to its targets and its drugs (#90; #82, point 2) ------------------


def _targets(mondo, **options):
    import warnings

    from sabueso.resolver import EntityResolver, FixtureUniProtClient
    from sabueso.tools.db.open_targets import FixtureOpenTargetsClient
    from sabueso.tools.db.orphadata import FixtureOrphadataClient

    options = {
        "resolver": EntityResolver(FixtureUniProtClient("temp_data")),
        "open_targets_client": FixtureOpenTargetsClient("temp_data"),
        "orphadata_client": FixtureOrphadataClient("temp_data"),
        "mondo_client": mondo,
        **options,
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # the saved Open Targets rows are a cut
        return sabueso.disease_targets("ORPHA:868", **options)


def test_a_disease_s_targets_with_every_statement_that_brought_them(mondo):
    deck = _targets(mondo, limit=3)
    assert deck.meta["kind"] == "disease_targets"
    assert deck.meta["disease"] == TPI_DEFICIENCY
    ids = [c.id for c in deck.cards]
    assert ids[0] == "sabueso:protein:uniprot:P60174"
    basis = deck.basis(ids[0])
    assert basis["rule"] == "disease_targets@2"
    assert {s["source"] for s in basis["statements"]} == {"Open Targets", "Orphanet"}
    ot = next(s for s in basis["statements"] if s["source"] == "Open Targets")
    assert (ot["rank"], ot["symbol"], ot["disease"]) == (1, "TPI1", "MONDO:0014221")
    orpha = next(s for s in basis["statements"] if s["source"] == "Orphanet")
    assert orpha["association_type"].startswith("Disease-causing")


def test_what_the_deck_leaves_out_is_recorded(mondo):
    deck = _targets(mondo, limit=3)
    reasons = {e["reason"] for e in deck.meta["excluded"]}
    # Targets without a saved UniProt entry cannot be built here; past the limit,
    # candidates are listed, never dropped silently.
    assert {"limit", "card_not_built"} <= reasons
    cut = [s for s in deck.meta["sources"] if s["source"] == "Sabueso"]
    assert cut and cut[0]["truncated"] and cut[0]["count"] == 3


def test_a_failing_source_leaves_the_others(mondo):
    from sabueso.tools.db.open_targets import FixtureOpenTargetsClient

    deck = _targets(
        mondo,
        limit=3,
        open_targets_client=FixtureOpenTargetsClient(
            "temp_data", failing={"MONDO:0014221"}
        ),
    )
    statuses = {s["source"]: s["status"] for s in deck.meta["sources"]}
    assert statuses == {"Open Targets": "error", "Orphanet": "added"}
    assert [c.id for c in deck.cards] == ["sabueso:protein:uniprot:P60174"]


def test_a_disease_that_does_not_resolve_is_refused(mondo):
    from sabueso.core.errors import ResolverError

    with pytest.raises(ResolverError, match="no_stated_equivalence"):
        sabueso.disease_targets("doid:9999999", mondo_client=mondo)


def test_the_drugs_whose_indications_name_the_disease(mondo):
    from sabueso.tools.db.chembl import FixtureChEMBLClient
    from sabueso.tools.db.pdb_ccd import FixtureCCDClient
    from sabueso.tools.db.unichem import FixtureUniChemClient

    deck = sabueso.disease_drugs(
        "mesh:D014355",  # Chagas disease, through MONDO's stated equivalence
        chembl_client=FixtureChEMBLClient("temp_data"),
        ccd_client=FixtureCCDClient("temp_data"),
        unichem_client=FixtureUniChemClient("temp_data"),
        mondo_client=mondo,
    )
    assert deck.meta["disease"] == "sabueso:disease:mondo:MONDO:0001444"
    (drug,) = deck.cards  # benznidazole
    basis = deck.basis(drug.id)
    assert basis["rule"] == "disease_drugs@2"
    assert {i["max_phase_for_ind"] for i in basis["indications"]} == {"4.0"}
    assert {i["molecule_chembl_id"] for i in basis["indications"]} == {"CHEMBL110"}
