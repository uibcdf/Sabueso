"""Knowledge packets: a declared query, a deterministic, pinned answer (#71).

HsTIM (P60174) as subject and TcTIM (P52270) as comparator, on frozen responses.
"""

import sqlite3
import warnings
from contextlib import closing

import argdigest
import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.core.errors import ArgumentError, ResolverError, StorageError
from sabueso.core.packets import (
    ASPECT_MAPPING,
    ASPECTS,
    BIOACTIVITY_SOURCES,
    aspect_options,
    card_content_id,
)
from sabueso.enrichers import ENRICHERS
from sabueso.resolver import EntityResolver, FixtureRCSBClient, FixtureUniProtClient
from sabueso.tools.db.alphafold import FixtureAlphaFoldClient
from sabueso.tools.db.chembl import FixtureChEMBLClient
from sabueso.tools.db.clinvar import FixtureClinVarClient
from sabueso.tools.db.diseases import FixtureDISEASESClient
from sabueso.tools.db.europepmc import FixtureEuropePMCClient
from sabueso.tools.db.gnomad import FixtureGnomADClient
from sabueso.tools.db.gpcrdb import FixtureGPCRdbClient
from sabueso.tools.db.gtex import FixtureGTExClient
from sabueso.tools.db.interpro import FixtureInterProClient
from sabueso.tools.db.klifs import FixtureKLIFSClient
from sabueso.tools.db.medgen import FixtureMedGenClient
from sabueso.tools.db.mondo import FixtureMONDOClient
from sabueso.tools.db.ncbi_taxonomy import FixtureNCBITaxonomyClient
from sabueso.tools.db.oma import FixtureOMAClient
from sabueso.tools.db.open_targets import FixtureOpenTargetsClient
from sabueso.tools.db.orphadata import FixtureOrphadataClient
from sabueso.tools.db.pdbe_kb import FixturePDBeKBClient
from sabueso.tools.db.phi_base import FixturePHIBaseClient
from sabueso.tools.db.reactome import FixtureReactomeClient
from sabueso.tools.db.sabdab import FixtureSAbDabClient
from sabueso.tools.db.skempi import FixtureSKEMPIClient
from sabueso.tools.db.uniref import FixtureUniRefClient


@pytest.fixture(scope="module")
def clients():
    return dict(
        resolver=EntityResolver(
            FixtureUniProtClient("temp_data"),
            rcsb_client=FixtureRCSBClient("temp_data"),
        ),
        chembl_client=FixtureChEMBLClient("temp_data"),
        alphafold_client=FixtureAlphaFoldClient("temp_data"),
        pdbe_kb_client=FixturePDBeKBClient("temp_data"),
        interpro_client=FixtureInterProClient("temp_data"),
        taxonomy_client=FixtureNCBITaxonomyClient("temp_data"),
        phi_base_client=FixturePHIBaseClient("temp_data"),
        diseases_client=FixtureDISEASESClient("temp_data"),
        open_targets_client=FixtureOpenTargetsClient("temp_data"),
        orphadata_client=FixtureOrphadataClient("temp_data"),
        reactome_client=FixtureReactomeClient("temp_data"),
        clinvar_client=FixtureClinVarClient("temp_data"),
        gnomad_client=FixtureGnomADClient("temp_data"),
        skempi_client=FixtureSKEMPIClient("temp_data"),
        mondo_client=FixtureMONDOClient("temp_data"),
        medgen_client=FixtureMedGenClient("temp_data"),
        klifs_client=FixtureKLIFSClient("temp_data"),
        gpcrdb_client=FixtureGPCRdbClient("temp_data"),
        sabdab_client=FixtureSAbDabClient("temp_data"),
        oma_client=FixtureOMAClient("temp_data"),
        uniref_client=FixtureUniRefClient("temp_data"),
        gtex_client=FixtureGTExClient("temp_data"),
        europepmc_client=FixtureEuropePMCClient("temp_data"),
    )


@pytest.fixture(scope="module")
def query():
    return sabueso.KnowledgeQuery("P60174", comparator="uniprot:P52270")


def _resolve(accession, **options):
    with warnings.catch_warnings():
        # The saved Open Targets rows are a cut of a larger answer (reported).
        warnings.simplefilter("ignore")
        return sabueso.resolve(accession, **options)


def _packet(query, clients, **kwargs):
    with warnings.catch_warnings():
        # Structures without a saved RCSB response are recorded as not found.
        warnings.simplefilter("ignore")
        return sabueso.knowledge_packet(query, **kwargs, **clients)


@pytest.fixture(scope="module")
def packet(query, clients):
    return _packet(query, clients)


def test_a_query_is_declared_and_normalized(query):
    assert query.to_dict() == {
        "format": "knowledge_query@2",
        "subject": "uniprot:P60174",
        "comparator": "uniprot:P52270",
        "aspects": sorted(a for a in ASPECTS if a != "orthology"),
        "constraints": {"bioactivity_sources": ["ChEMBL"]},
        "detail": "full",
    }
    assert sabueso.KnowledgeQuery.from_dict(query.to_dict()) == query
    # What the aspects ask of the sources is fixed per mapping version. The options are
    # derived from the declared enrichers, so a new enricher in an aspect's areas fails
    # here: that is a new mapping version (packet_aspects@7), never a silent change.
    assert ASPECT_MAPPING == "packet_aspects@7"
    assert query.options() == {
        "clinvar": {},
        "diseases": {},
        "gnomad": {},
        "exon_usage": True,
        "gtex": True,
        "open_targets": {},
        "orphadata": True,
        "phi_base": True,
        "reactome": True,
        "taxonomy": True,
        "structures": "all",
        "predicted_structures": True,
        "interfaces": True,
        "family_sites": True,
        "ligand_sites": True,
        "skempi": True,
        "klifs": {},
        "gpcrdb": {},
        "sabdab": True,
        "uniref": True,
        "medgen": True,
        "disease_identity": True,
        "chembl": {},
        "europepmc": {},
    }
    narrow = sabueso.KnowledgeQuery(
        "P60174",
        aspects=["bioactivities"],
        constraints={"bioactivity_sources": ["BindingDB", "ChEMBL"]},
    )
    assert narrow.options() == {"chembl": {}, "bindingdb": {}}


@pytest.mark.parametrize(
    "kwargs",
    [
        {"subject": "TIM"},
        {"subject": "P60174", "aspects": ["everything"]},
        {"subject": "P60174", "constraints": {"organism": 9606}},
        {"subject": "P60174", "constraints": {"bioactivity_sources": ["IUPHAR"]}},
    ],
)
def test_what_a_query_cannot_state_is_refused(kwargs):
    with pytest.raises(ArgumentError):
        sabueso.KnowledgeQuery(**kwargs)


def test_the_packet_holds_the_declared_aspects_for_both_proteins(packet):
    # Every aspect but orthology, which a query asks for by name (packet_aspects@3).
    assert set(packet.facts) == set(ASPECTS) - {"orthology"}
    assert packet.entities["subject"]["card_id"] == "sabueso:protein:uniprot:P60174"
    assert packet.entities["comparator"]["card_id"] == "sabueso:protein:uniprot:P52270"
    structures = packet.facts["structures"]
    assert set(structures) == {"subject", "comparator", "together"}
    assert structures["together"]["inventory"]["rule"]["rule"].startswith(
        "structure_inventory@"
    )
    assert "identity_audit" in packet.facts["identity"]["together"]
    # Each view keeps its named rule.
    oligomer = packet.facts["oligomer"]["subject"]
    assert {r["rule"] for r in oligomer["rules"]}
    # Quantities stay quantities, with their unit.
    item = structures["subject"]["experimental"]["items"][0]
    assert set(item["resolution"]) == {"value", "unit"}
    assert item["resolution"]["unit"] == "angstrom"


def test_unknowns_follow_the_query(packet, query, clients):
    rows = {
        (r["area"], r["source"]): r["state"] for r in packet.unknowns["subject"]["rows"]
    }
    # Only ChEMBL was asked for bioactivities: the others were not queried.
    assert rows[("relationships.has_bioactivity", "BindingDB")] == "not_queried"
    assert ("relationships.has_bioactivity", "ChEMBL") not in rows
    assert rows[("features_positional.mutagenesis", "UniProt")] == "not_stated"
    assert packet.unknowns["subject"]["rule"]["rule"] == "knowledge_state@5"
    # A packet that asks only about identity reports only identity's unknowns.
    only = _packet(sabueso.KnowledgeQuery("P60174", aspects=["identity"]), clients)
    assert set(only.facts) == {"identity"}
    assert all(
        r["area"].startswith(ASPECTS["identity"]["areas"])
        for r in only.unknowns["subject"]["rows"]
    )


def test_composition_is_deterministic(packet, query, clients):
    again = _packet(query, clients)
    assert again.snapshot_id() == packet.snapshot_id()
    # From the same card states, read back from their JSON form.
    subject = Card.from_dict(
        _resolve("P60174", **query.options(), **clients)[0].to_dict()
    )
    assert card_content_id(subject) == packet.entities["subject"]["content_id"]


def test_retrieval_times_change_the_pin_but_not_the_knowledge(query, clients):
    options = {**query.options(), **clients}
    subject = _resolve("P60174", **options)[0]
    comparator = _resolve("P52270", **options)[0]
    first = sabueso.compose_packet(query, subject, comparator)
    reread = subject.to_dict()
    for assertion in reread["source_assertion_store"]:
        assertion["retrieved_at"] = "2027-01-01T00:00:00+00:00"
    later = sabueso.compose_packet(query, Card.from_dict(reread), comparator)
    assert later.snapshot_id() != first.snapshot_id()
    assert later.same_knowledge(first)
    changed = subject.to_dict()
    changed["sections"]["names"]["canonical_name"]["value"] = "Another name"
    other = sabueso.compose_packet(query, Card.from_dict(changed), comparator)
    assert not other.same_knowledge(first)


def test_a_stored_packet_is_pinned_verified_and_citable(tmp_path, query, clients):
    store = sabueso.KnowledgeStore(tmp_path / "k.db")
    packet = _packet(query, clients, store=store, packet_name="tim_pair", note="first")
    assert packet.ref.startswith("sabueso:packet:tim_pair@sha256:")
    loaded = store.load_packet(packet.ref)
    assert loaded.to_dict() == packet.to_dict()
    assert store.load_packet("tim_pair").ref == packet.ref
    # A SourceAssertion a fact names is cited in the pinned card state it was read in.
    sa_id = packet.facts["identity"]["subject"]["fields"]["names.canonical_name"][
        "source_assertion_ids"
    ][0]
    assert store.source_assertion(packet.cite("subject", sa_id))["id"] == sa_id
    # Assembling the same knowledge again adds no revision; the history says whether
    # the knowledge changed.
    _packet(query, clients, store=store, packet_name="tim_pair")
    history = store.packet_history("tim_pair")
    assert [h["knowledge_changed"] for h in history] == [None]
    assert store.packet_names() == ["tim_pair"]


def test_a_packet_is_stored_only_with_the_cards_it_cites(tmp_path, packet):
    store = sabueso.KnowledgeStore(tmp_path / "k.db")
    with pytest.raises(StorageError):
        store.save_packet(packet, "orphan")
    assert store.packet_names() == []


def test_a_changed_packet_is_refused(tmp_path, query, clients):
    path = tmp_path / "k.db"
    store = sabueso.KnowledgeStore(path)
    packet = _packet(query, clients, store=store, packet_name="tim_pair")
    import zlib

    with closing(sqlite3.connect(path)) as conn, conn:
        for sid, document in conn.execute(
            "SELECT snapshot_id, document FROM packet_snapshots"
        ).fetchall():
            text = (
                zlib.decompress(document)
                .decode()
                .replace("knowledge_state@5", "knowledge_state@9")
            )
            conn.execute(
                "UPDATE packet_snapshots SET document = ? WHERE snapshot_id = ?",
                (zlib.compress(text.encode()), sid),
            )
    with pytest.raises(StorageError, match="no longer matches"):
        store.load_packet(packet.ref)


def test_an_unresolved_or_mismatched_card_is_refused(query, clients):
    options = {**query.options(), **clients}
    subject = _resolve("P60174", **options)[0]
    with pytest.raises(ValueError, match="comparator"):
        sabueso.compose_packet(query, subject)
    with pytest.raises(ValueError, match="asks about"):
        sabueso.compose_packet(query, subject, subject)
    with pytest.raises(ResolverError, match="did not resolve"):
        _packet(sabueso.KnowledgeQuery("A0A000XXX0"), clients)


def test_the_clients_never_change_what_is_asked(query, clients):
    # Knowledge options come from the query only; a keyword is a source client or
    # the resolver.
    with pytest.raises(argdigest.UnknownArgumentError):
        sabueso.knowledge_packet(query, bindingdb={}, **clients)


def test_a_packet_never_leaves_unasked_what_its_aspects_could_ask(packet, query):
    # Every "not queried" unknown has a reason: the source does not cover the
    # organism, only curation states the area, or the query did not name the source.
    unnamed = set(BIOACTIVITY_SOURCES) - set(query.constraints["bioactivity_sources"])
    for role in ("subject", "comparator"):
        for row in packet.unknowns[role]["rows"]:
            if row["state"] != "not_queried":
                continue
            assert (
                row["basis"].get("detail")
                or row["basis"].get("route") == "curation"
                or (
                    row["area"] == "relationships.has_bioactivity"
                    and row["source"] in unnamed
                )
            ), row


#: Enrichers no aspect covers yet, and why.
OUTSIDE_PACKETS = {
    "string": "functional association networks are not a packet aspect yet",
}


@pytest.mark.parametrize("enricher", ENRICHERS, ids=lambda e: e.option)
def test_every_enricher_belongs_to_an_aspect_and_is_asked_by_it(enricher):
    aspects = [
        a
        for a in ASPECTS
        if any(area.startswith(ASPECTS[a]["areas"]) for area in enricher.areas)
    ]
    if enricher.option in OUTSIDE_PACKETS:
        assert not aspects
        return
    assert aspects, f"{enricher.option} answers no packet aspect"
    for aspect in aspects:
        assert aspect_options(aspect)[enricher.option] == enricher.default_request


# --- knowledge_packet@2: references, not copies (#88) ----------------------------------


def test_grouped_disease_statements_name_the_statement_they_group(packet):
    assert packet.format == "knowledge_packet@3"
    facts = packet.facts["disease_association"]["subject"]
    associations = {r["relationship_id"] for r in facts["associations"]}
    variants = {
        v["accession"]: v
        for v in facts["clinical_variants"]["annotations.clinical_variants"]["value"]
    }
    grouped = facts["grouped"]
    statements = [s for d in grouped["diseases"] for s in d["statements"]]
    statements += grouped["ungrouped"]
    kinds = {s["kind"] for s in statements}
    assert {"association", "clinvar_condition"} <= kinds
    for s in statements:
        # Named, not copied: no statement repeats its ids or its name here.
        assert not {"refs", "curies", "name"} & set(s)
        if s["kind"] == "association":
            assert s["relationship_id"] in associations
        elif s["kind"] == "clinvar_condition":
            assert variants[s["variant"]]["conditions"][s["condition"]]
    assert all(s["grouped_by"] for d in grouped["diseases"] for s in d["statements"])
    assert all(s["reason"] for s in grouped["ungrouped"])


def test_the_joint_inventory_names_each_role_s_structures(packet):
    facts = packet.facts["structures"]
    held = {
        item["relationship_id"]: item
        for role in ("subject", "comparator")
        for item in facts[role]["experimental"]["items"]
    }
    items = facts["together"]["inventory"]["items"]
    assert items
    for item in items:
        assert item["relationship_id"] in held
        assert set(item) <= {"relationship_id", "card_id", "substitutions_in_reference"}


def test_a_packet_of_the_earlier_format_is_read_and_never_compared(packet):
    earlier = sabueso.KnowledgePacket(
        {**packet.to_dict(), "format": "knowledge_packet@1"}
    )
    assert earlier.format == "knowledge_packet@1"
    assert earlier.same_knowledge(packet) is None
    with pytest.raises(StorageError):
        sabueso.KnowledgePacket({**packet.to_dict(), "format": "knowledge_packet@9"})


def test_revisions_of_different_formats_are_not_compared(tmp_path, query, clients):
    import time
    from datetime import datetime, timezone

    store = sabueso.KnowledgeStore(tmp_path / "k.db")
    current = _packet(query, clients, store=store, packet_name="tim_pair")
    between = datetime.now(timezone.utc)
    time.sleep(1.1)  # the store keeps times to the second
    earlier = sabueso.KnowledgePacket(
        {**current.to_dict(), "format": "knowledge_packet@1"}
    )
    store.save_packet(earlier, "tim_pair")
    history = store.packet_history("tim_pair")
    assert [h["format"] for h in history] == [
        "knowledge_packet@3",
        "knowledge_packet@1",
    ]
    assert [h["knowledge_changed"] for h in history] == [None, None]
    answer = store.changed_since("tim_pair", between)
    assert (answer["changed"], answer["reason"]) == (None, "format_changed")


def test_orthology_is_asked_by_name_and_states_only_what_oma_states(clients):
    query = sabueso.KnowledgeQuery(
        "P60174", comparator="uniprot:P52270", aspects=["orthology"]
    )
    assert query.options() == {"oma": {}}
    packet = _packet(query, clients)
    orthologs = packet.facts["orthology"]["subject"]["orthologs"]
    assert "uniprot:Q4DV43" in {o["object_ref"] for o in orthologs}
    # OMA maps P52270 to another strain's protein: nothing is joined for it, and OMA
    # states no orthology between the two cards' own accessions.
    assert packet.facts["orthology"]["comparator"]["orthologs"] == []
    assert packet.facts["orthology"]["together"] == {"stated_orthologs": []}


def test_packets_of_different_aspect_mappings_are_not_compared(packet):
    older = packet.to_dict()
    older["aspect_mapping"] = "packet_aspects@3"
    assert packet.same_knowledge(sabueso.KnowledgePacket(older)) is None


def test_the_biological_context_names_each_tissue_s_term(packet):
    # packet_aspects@5 (#102): GTEx's terms beside the pext they name.
    facts = packet.facts["biological_context"]["subject"]
    stated = facts["annotations.tissue_terms"]["value"]
    terms = {t["gtex_id"]: t["ontology_id"] for t in stated}
    assert len(terms) == 49
    assert terms["Muscle_Skeletal"] == "UBERON:0011907"


# --- detail="index": what the cards hold, by reference (#88) ----------------------------


@pytest.fixture(scope="module")
def index_store(tmp_path_factory, clients):
    store = sabueso.KnowledgeStore(tmp_path_factory.mktemp("index") / "k.db")
    query = sabueso.KnowledgeQuery("P60174", comparator="P52270", detail="index")
    packet = _packet(query, clients, store=store, packet_name="tim_index")
    return store, packet


def test_an_index_packet_states_its_detail_and_rule(index_store):
    _, index = index_store
    assert (index.format, index.detail) == ("knowledge_packet@3", "index")
    facts = index.facts["bioactivities"]["subject"]
    assert facts["rule"] == "packet_index@1"
    assert facts["full_views"] == ["bioactivities"]
    # No comparison side by side: that is a view, computed from the pinned cards.
    assert "together" not in index.facts["structures"]


def test_an_index_counts_every_item_and_names_it(index_store, packet):
    _, index = index_store
    full = packet.facts["bioactivities"]["subject"]
    area = index.facts["bioactivities"]["subject"]["areas"][
        "relationships.has_bioactivity"
    ]
    held = {
        m["relationship_id"] for item in full["items"] for m in item["measurements"]
    }
    assert area["count"] == len(area["relationship_ids"]) >= len(held)
    assert held <= set(area["relationship_ids"])
    assert area["by_source"] == {"ChEMBL": area["count"]}
    variants = index.facts["sequence_features"]["subject"]["areas"][
        "annotations.population_variants"
    ]
    assert variants["by_source"] == {"gnomAD": variants["count"]}
    assert len(variants["source_assertion_ids"]) == variants["count"]


def test_an_index_item_is_read_at_the_pinned_card_state(index_store):
    store, index = index_store
    area = index.facts["bioactivities"]["subject"]["areas"][
        "relationships.has_bioactivity"
    ]
    rel = index.item("subject", area["relationship_ids"][0], store)
    assert rel["predicate"] == "has_bioactivity"
    sa_id = rel["source_assertion_ids"][0]
    assert index.item("subject", sa_id, store)["id"] == sa_id


def test_an_index_is_far_smaller_and_never_compared_with_a_full_packet(
    index_store, packet
):
    import json

    _, index = index_store
    assert len(json.dumps(index.to_dict())) < len(json.dumps(packet.to_dict())) / 3
    assert index.same_knowledge(packet) is None
    # What is unknown and what is in conflict are reported whole at either level.
    assert index.unknowns == packet.unknowns


def test_a_query_of_the_earlier_format_reads_as_full(query):
    earlier = {k: v for k, v in query.to_dict().items() if k != "detail"}
    earlier["format"] = "knowledge_query@1"
    assert sabueso.KnowledgeQuery.from_dict(earlier).detail == "full"
    with pytest.raises(ArgumentError):
        sabueso.KnowledgeQuery("P60174", detail="summary")


def _rules(data, found):
    """Every rule name (``name@N``) a packet's facts carry."""
    import re

    named = re.compile(r"^[a-z_]+@[0-9]+$")
    if isinstance(data, dict):
        for key, value in data.items():
            if key in ("rule", "rules") or key.endswith("_rule"):
                if isinstance(value, str) and named.match(value):
                    found.add(value)
                elif isinstance(value, dict) and isinstance(value.get("rule"), str):
                    found.add(value["rule"])
            _rules(value, found)
    elif isinstance(data, list):
        for value in data:
            _rules(value, found)
    return found


def test_an_index_names_the_rules_its_full_views_apply(index_store, packet):
    # uibcdf/moli#22: an index says which rules a reader gets by computing the views.
    _, index = index_store
    for aspect, facts in packet.facts.items():
        declared = set(index.facts[aspect]["subject"]["full_rules"])
        assert _rules(facts, set()) <= declared, aspect


def test_the_level_of_detail_never_changes_what_is_asked():
    # uibcdf/moli#22: the detail chosen does not change the question, so nothing an
    # index reports as not_queried would have been asked by a full packet.
    full = sabueso.KnowledgeQuery("P60174", comparator="P52270")
    index = sabueso.KnowledgeQuery("P60174", comparator="P52270", detail="index")
    assert index.options() == full.options()


def test_a_pin_the_store_does_not_hold_is_never_read_as_the_latest(
    index_store, tmp_path
):
    _, index = index_store
    area = index.facts["bioactivities"]["subject"]["areas"][
        "relationships.has_bioactivity"
    ]
    elsewhere = sabueso.KnowledgeStore(tmp_path / "other.db")
    with pytest.raises(StorageError):
        index.item("subject", area["relationship_ids"][0], elsewhere)
