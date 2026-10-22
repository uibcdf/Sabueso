from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sabueso")
except PackageNotFoundError:
    # Package is not installed
    try:
        from ._version import __version__
    except ImportError:
        __version__ = "0.0.0+unknown"

from smonitor.integrations import ensure_configured as _ensure_smonitor_configured

from sabueso._private.smonitor import PACKAGE_ROOT as _SMONITOR_PACKAGE_ROOT
from sabueso.core.attribution import attribution
from sabueso.core.card_exploration_storage import read_exploration
from sabueso.core.curation_store import CurationStore
from sabueso.core.errors import (
    ConnectorError,
    ResolverError,
    SabuesoError,
    SchemaError,
    StorageError,
)
from sabueso.core.extraction_store import ExtractionStore
from sabueso.core.knowledge_store import KnowledgeStore
from sabueso.core.migration import migrate_card, refresh_card
from sabueso.core.packets import KnowledgePacket, KnowledgeQuery, compose_packet
from sabueso.core.tables import to_dataframe
from sabueso.tools.card.disease import (
    disease_drugs,
    disease_targets,
    resolve_disease_card,
)
from sabueso.tools.card.protein import ambiguity_deck, resolve_protein_card
from sabueso.tools.card.small_molecule import ligand_deck, resolve_molecule_card
from sabueso.tools.card.storage import save_card_json, save_card_sqlite
from sabueso.tools.db._archive import RetrievalArchive
from sabueso.tools.db.chembl import (
    create_molecule_card_from_file,
    create_molecule_card_from_json,
    create_molecule_card_online,
)
from sabueso.tools.db.pubchem import (
    create_compound_card_from_file,
    create_compound_card_from_json,
    create_compound_card_online,
)
from sabueso.tools.db.uniprot import (
    create_protein_card,
    create_protein_card_from_file,
    create_protein_card_from_json,
    create_protein_card_online,
)
from sabueso.tools.deck.storage import save_deck_jsonl, save_deck_sqlite
from sabueso.tools.literature import extract_literature_mentions
from sabueso.tools.navigate import expand
from sabueso.tools.packet import knowledge_packet
from sabueso.tools.resolve import resolve

# SMonitor is configured when Sabueso is imported (uibcdf/sabueso#31).
_ensure_smonitor_configured(_SMONITOR_PACKAGE_ROOT)

__all__ = [
    "read_exploration",
    "extract_literature_mentions",
    "attribution",
    "create_protein_card_from_file",
    "create_protein_card_from_json",
    "create_protein_card",
    "create_protein_card_online",
    "create_compound_card_from_file",
    "create_compound_card_from_json",
    "create_compound_card_online",
    "create_molecule_card_from_file",
    "create_molecule_card_from_json",
    "create_molecule_card_online",
    "resolve",
    "KnowledgeQuery",
    "KnowledgePacket",
    "compose_packet",
    "knowledge_packet",
    "CurationStore",
    "ExtractionStore",
    "KnowledgeStore",
    "RetrievalArchive",
    "migrate_card",
    "refresh_card",
    "to_dataframe",
    "resolve_protein_card",
    "resolve_molecule_card",
    "ligand_deck",
    "ambiguity_deck",
    "resolve_disease_card",
    "disease_targets",
    "disease_drugs",
    "expand",
    "save_card_json",
    "save_card_sqlite",
    "save_deck_jsonl",
    "save_deck_sqlite",
    "SabuesoError",
    "ResolverError",
    "SchemaError",
    "StorageError",
    "ConnectorError",
]
