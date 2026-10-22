"""Argument contracts at the public API, through ArgDigest (uibcdf/sabueso#31).

Integrated as in the sibling components (MolSysMT, MolSysViewer): ``sabueso/_argdigest.py``,
one digester per argument name, and ``skip_digestion`` on every decorated function.
"""

import importlib
import inspect
import warnings

import argdigest
import pytest

from sabueso import (
    ambiguity_deck,
    extract_literature_mentions,
    ligand_deck,
    resolve,
    resolve_molecule_card,
    resolve_protein_card,
)
from sabueso.core.card import Card
from sabueso.core.card_access import CardAccess
from sabueso.core.card_exploration import CardExplorer, CardView
from sabueso.core.card_exploration_storage import read_exploration
from sabueso.core.deck import Deck
from sabueso.core.errors import ArgumentError, SabuesoError
from sabueso.core.tables import to_dataframe
from sabueso.resolver import EntityResolver, FixtureRCSBClient, FixtureUniProtClient
from sabueso.tools.card.storage import load_card_sqlite, save_card_sqlite
from sabueso.tools.db import (
    chembl as _chembl,
)
from sabueso.tools.db import (
    interpro as _interpro,
)
from sabueso.tools.db import (
    pdb_ccd as _pdb_ccd,
)
from sabueso.tools.db import (
    pdbe_kb as _pdbe_kb,
)
from sabueso.tools.db import (
    pubchem as _pubchem,
)
from sabueso.tools.db import (
    rcsb as _rcsb,
)
from sabueso.tools.db import (
    stringdb as _stringdb,
)
from sabueso.tools.db import (
    unichem as _unichem,
)
from sabueso.tools.db import (
    uniprot as _uniprot,
)
from sabueso.tools.db.chembl import FixtureChEMBLClient
from sabueso.tools.deck.storage import (
    META_TABLE,
    load_deck_sqlite,
    read_deck_sqlite,
    save_deck_sqlite,
)
from sabueso.tools.sequence import find_protein_candidates
from sabueso.tools.source_snapshot import load_source_snapshot

SOURCE_FUNCTIONS = [
    _uniprot.get_entry,
    _uniprot.search,
    _rcsb.get_entry,
    _chembl.get_bioactivities,
    _chembl.get_molecules,
    _pubchem.get_compound,
    _interpro.get_site_residues,
    _pdbe_kb.get_ligand_sites,
    _pdbe_kb.get_interface_residues,
    _pdb_ccd.get_components,
    _unichem.get_compound,
    _stringdb.get_partners,
]


def _discovered():
    """Every ``get_*`` of ``sabueso.tools.db`` and every digested public method of the
    core objects, so that a new public function cannot miss its digesters unnoticed
    (the hand-written lists above had fallen behind by 2026-09-26)."""
    import pkgutil

    import sabueso.tools.db as db
    from sabueso import CurationStore, ExtractionStore, KnowledgeStore
    from sabueso.core.card_access import AccessSelection, CardAccess
    from sabueso.core.packets import KnowledgePacket

    found = []
    for info in pkgutil.iter_modules(db.__path__):
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"sabueso.tools.db.{info.name}")
        found += [
            f
            for name, f in vars(module).items()
            if (name.startswith("get_") or name == "search")
            and callable(f)
            and getattr(f, "__module__", None) == module.__name__
        ]
    for cls in (
        Card,
        Deck,
        KnowledgeStore,
        CurationStore,
        ExtractionStore,
        KnowledgePacket,
        CardAccess,
        AccessSelection,
        CardExplorer,
        CardView,
    ):
        for name, f in vars(cls).items():
            f = getattr(f, "__func__", f)
            if not name.startswith("_") and callable(f) and inspect.unwrap(f) is not f:
                found.append(f)
    return found


PUBLIC_TOOLS = [
    read_exploration,
    find_protein_candidates,
    CardAccess.__init__,
    CardExplorer.__init__,
    load_source_snapshot,
    extract_literature_mentions,
    *_discovered(),
    *SOURCE_FUNCTIONS,
    resolve,
    resolve_protein_card,
    resolve_molecule_card,
    ligand_deck,
    ambiguity_deck,
    Card.bioactivities,
    Card.add_literature_assertion,
    Card.add_literature_relationship,
    Card.add_literature_bioactivity,
    Card.table,
    to_dataframe,
    Card.structures,
    Card.ligands,
    Card.compare_ligands,
    Card.extract,
    Deck.summarize,
    EntityResolver.__init__,
    save_card_sqlite,
    load_card_sqlite,
    save_deck_sqlite,
    read_deck_sqlite,
    load_deck_sqlite,
]


@pytest.fixture(scope="module")
def resolver():
    return EntityResolver(
        FixtureUniProtClient("temp_data"), rcsb_client=FixtureRCSBClient("temp_data")
    )


@pytest.fixture(scope="module")
def protein(resolver):
    card, _ = resolve_protein_card("P52270", resolver)
    return card


def test_every_public_tool_is_digested():
    # The digester check above is only meaningful for functions ArgDigest wraps.
    assert [t.__qualname__ for t in PUBLIC_TOOLS if inspect.unwrap(t) is t] == []


def _structures_requested(card):
    return [
        e["structure"]
        for e in card.quality["enrichments"]
        if e.get("source") == "RCSB PDB"
    ]


def test_every_parameter_of_every_public_tool_has_a_digester():
    # STRICTNESS="warn" would only warn at call time; this makes the gap a failure.
    missing = []
    for tool in PUBLIC_TOOLS:
        for name, parameter in inspect.signature(
            inspect.unwrap(tool)
        ).parameters.items():
            # **options is admitted through a declared domain (function contract).
            if name == "self" or parameter.kind is parameter.VAR_KEYWORD:
                continue
            try:
                module = importlib.import_module(
                    f"sabueso._private.argdigest.argument.{name}"
                )
            except ModuleNotFoundError:
                missing.append(f"{tool.__qualname__}({name})")
                continue
            if not callable(getattr(module, f"digest_{name}", None)):
                missing.append(f"{tool.__qualname__}({name})")
    assert missing == []


def test_a_single_pdb_id_is_one_structure_not_four_characters(resolver):
    # Before ArgDigest, structures="1SUX" iterated the string: four requests, four
    # "not found" outcomes, and a card silently without its structure.
    card, _ = resolve_protein_card("P52270", resolver, structures="1sux")
    assert _structures_requested(card) == ["1SUX"]


@pytest.mark.parametrize(
    "call",
    [
        lambda r: resolve_protein_card(
            "P52270", r, structures=["1SUX", "not-a-pdb-id"]
        ),
        lambda r: resolve_protein_card("P52270", r, chembl={"limt": 10}),
        lambda r: resolve_protein_card("P52270", r, chembl={"limit": 0}),
        lambda r: resolve_protein_card("P52270", r, string={"required_score": 2000}),
        lambda r: resolve_protein_card("P52270", r, ligand_sites="yes"),
        lambda r: resolve_protein_card("   ", r),
        lambda r: resolve_protein_card("P52270", resolver="https://rest.uniprot.org"),
        lambda r: resolve_protein_card("P52270", r, chembl={}, chembl_client="ChEMBL"),
        lambda r: resolve_molecule_card(""),
        lambda r: ligand_deck({"meta": {}}),
        lambda r: ambiguity_deck(None),
    ],
)
def test_a_wrong_value_is_refused_before_anything_runs(resolver, call):
    with pytest.raises(ArgumentError) as info:
        call(resolver)
    error = info.value
    assert error.code == "SABUESO-E-ARG-001"
    assert isinstance(error, SabuesoError) and isinstance(error, ValueError)


def test_an_unsupported_identifier_is_still_an_answer_not_an_argument_error():
    # Whether an identifier names a supported record is the resolver's answer.
    card, resolution = resolve_molecule_card("not-an-identifier", unichem=False)
    assert card is None and resolution.status == "unsupported"


def test_an_unknown_keyword_is_refused_like_python_would(resolver):
    with pytest.raises(argdigest.UnknownArgumentError):
        resolve_protein_card(
            "P52270", resolver, structure=["1SUX"]
        )  # typo for structures


def test_options_reach_the_source_client_normalized(resolver):
    from sabueso._private.smonitor.warnings import EnrichmentTruncatedWarning

    with pytest.warns(EnrichmentTruncatedWarning):  # 5 of 493: truncation is reported
        card, _ = resolve_protein_card(
            "P52270",
            resolver,
            chembl={"limit": 5},
            chembl_client=FixtureChEMBLClient("temp_data"),
        )
    (enrichment,) = [e for e in card.quality["enrichments"] if e["source"] == "ChEMBL"]
    assert enrichment["limit"] == 5


def test_no_digestion_warnings_on_ordinary_calls(resolver):
    with warnings.catch_warnings():
        warnings.simplefilter("error", argdigest.DigestNotDigestedWarning)
        resolve_protein_card("P52270", resolver, structures=["1SUX"])


def test_skip_digestion_false_is_digested_and_a_false_non_boolean_is_refused(resolver):
    # A truthy value switches digestion off before the flag itself is digested (ArgDigest
    # checks SKIP_PARAM first), so only a falsy non-boolean can reach its digester.
    with pytest.raises(ArgumentError):
        resolve_protein_card("P52270", resolver, skip_digestion=0)


@pytest.mark.parametrize(
    "call",
    [
        lambda card, db: EntityResolver(policy="prefer_reviewed"),
        lambda card, db: EntityResolver(uniprot_client="https://rest.uniprot.org"),
        lambda card, db: card.structures(include_fragments="yes"),
        lambda card, db: card.ligands(card.to_deck().cards),
        lambda card, db: card.compare_ligands(Deck(), card.to_deck(), Deck()),
        lambda card, db: card.extract(["identifiers.uniprot", 7]),
        lambda card, db: card.extract("identifiers..uniprot"),
        lambda card, db: Deck([card]).summarize(None),
        lambda card, db: save_card_sqlite(card, db, table="cards; DROP TABLE x"),
        lambda card, db: save_card_sqlite(card, db, id_field=""),
        lambda card, db: load_card_sqlite(db, table="two words"),
        lambda card, db: load_card_sqlite(db, card_id=""),
        lambda card, db: save_deck_sqlite(card.to_deck(), db, table=META_TABLE),
        lambda card, db: save_deck_sqlite([card], db),
        lambda card, db: read_deck_sqlite(db, table="1cards"),
        lambda card, db: load_deck_sqlite(None),
        lambda card, db: Card.from_sqlite(db, table="cards--"),
        lambda card, db: Deck.from_sqlite(db, table=META_TABLE),
    ],
)
def test_a_wrong_value_is_refused_at_every_digested_boundary(protein, tmp_path, call):
    with pytest.raises(ArgumentError) as info:
        call(protein, tmp_path / "cards.sqlite")
    assert info.value.code == "SABUESO-E-ARG-001"


def test_a_table_name_never_reaches_sql_unchecked(protein, tmp_path):
    # save_card_sqlite interpolated any table name into SQL before #31.
    db = tmp_path / "cards.sqlite"
    save_card_sqlite(protein, db)
    with pytest.raises(ArgumentError):
        save_card_sqlite(protein, db, table="x (a); DROP TABLE cards; --")
    assert load_card_sqlite(db).id == protein.id


def test_a_single_field_path_is_one_field_not_its_characters(protein):
    path = "identifiers.uniprot"
    assert list(protein.extract(path)) == [path]
    assert list(protein.compare(protein, path)) == [path]
    assert [list(row) for row in Deck([protein]).summarize(path)] == [[path]]
    compared = Deck([protein]).compare(Deck([protein]), path)
    assert [list(row) for row in compared["self"]] == [[path]]


def test_digested_storage_round_trips(protein, tmp_path):
    db = tmp_path / "cards.sqlite"
    save_deck_sqlite(
        protein.to_deck(), db, table="proteins", id_field="identifiers.uniprot"
    )
    meta, cards = read_deck_sqlite(db, table="proteins")
    assert [c.id for c in cards] == [protein.id]
    assert load_deck_sqlite(db, table="proteins").ids() == [protein.id]


def test_expand_follows_only_relationship_predicates(protein):
    # It once returned an empty Deck for any kind, which read as "nothing related".
    with pytest.raises(ArgumentError):
        protein.expand("structures")


def test_a_misspelt_topic_or_rank_is_refused_not_answered_empty(protein):
    # Both used to answer silently: no claims, and every card in the None group.
    with pytest.raises(ArgumentError):
        protein.claims("interfase")
    with pytest.raises(ArgumentError):
        Deck([protein]).group_by_rank("genera")
    assert protein.claims()["items"] == []
    assert list(Deck([protein]).group_by_rank("Genus")) == [None]  # no taxonomy asked
