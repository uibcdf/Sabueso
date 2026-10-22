"""UniProt: record access (``OnlineUniProtClient``, ``FixtureUniProtClient``), and a
protein card from one UniProt record.

These helpers map a single UniProt entry into a card. They do **not** resolve the
entity: a secondary, demerged or isoform accession is taken as given, no identity links
are added, and no enrichment runs. The card's fields come from that one record, so the
aggregator's subject guard holds (uibcdf/sabueso#21). To resolve a query into a protein
entity, with its identity links, structures and enrichments, use
``resolve_protein_card``.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.snapshot import canonical_json, digest
from sabueso.core.source_acquisition import (
    _terminal,
    acquisition,
    capture_acquisitions,
    missing_fixture,
)
from sabueso.mappings.uniprot_isoforms import (
    isoform_id,
    parse_fasta,
    select_isoform,
    validate_components,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot


def load_json(path: str | Path) -> Dict[str, Any]:
    """Load UniProt JSON from a local file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _now_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def create_protein_card_from_json(
    uniprot_json: Dict[str, Any], retrieved_at: str | None = None
) -> Any:
    """Create a Protein Card from one UniProt record (offline, no entity resolution)."""
    from sabueso.core.aggregator import build_card_from_mapping
    from sabueso.mappings.uniprot import map_protein

    mapping = map_protein(uniprot_json, retrieved_at=retrieved_at or _now_date())
    accession = uniprot_json.get("primaryAccession")
    return build_card_from_mapping(
        mapping,
        meta={"entity_type": "protein"},
        entity_subjects={f"uniprot:{accession}"} if accession else None,
    )


def create_protein_card_from_file(
    path: str | Path, retrieved_at: str | None = None
) -> Any:
    """Create a Protein Card from a UniProt JSON file."""
    return create_protein_card_from_json(load_json(path), retrieved_at=retrieved_at)


def create_protein_card(
    uniprot_id: str, retrieved_at: str | None = None, data_dir: str | Path = "temp_data"
) -> Any:
    """
    Create a Protein Card by UniProt ID using a local JSON fixture.

    This is an offline helper. It expects a file named <ID>.json in data_dir.
    """
    path = Path(data_dir) / f"{uniprot_id}.json"
    return create_protein_card_from_file(path, retrieved_at=retrieved_at)


def fetch_uniprot_json(uniprot_id: str) -> Dict[str, Any]:
    """Deprecated: use ``get_entry(accession)["record"]`` (#49)."""
    from sabueso._private.smonitor.outcomes import report_deprecated

    report_deprecated(
        "sabueso.tools.db.uniprot.fetch_uniprot_json",
        'sabueso.tools.db.uniprot.get_entry(accession)["record"]',
    )
    entry, _ = OnlineUniProtClient().fetch_entry(uniprot_id)
    return entry


def create_protein_card_online(uniprot_id: str, retrieved_at: str | None = None) -> Any:
    """Deprecated: use ``sabueso.resolve(accession)``, which resolves the entity (#49)."""
    from sabueso._private.smonitor.outcomes import report_deprecated

    report_deprecated(
        "sabueso.create_protein_card_online", "sabueso.resolve(accession)"
    )
    entry, retrieved = OnlineUniProtClient().fetch_entry(uniprot_id)
    return create_protein_card_from_json(entry, retrieved_at=retrieved_at or retrieved)


# --- Record access (moved from sabueso.resolver.uniprot_client, uibcdf/sabueso#49) ---


UNIPROT_REST = "https://rest.uniprot.org/uniprotkb"
# Lineage and gene loci let the resolver tell paralogs from redundant entries (#55).
SEARCH_FIELDS = (
    "accession,reviewed,organism_name,organism_id,length,sequence,lineage,"
    "xref_veupathdb,xref_geneid"
)
SEARCH_SIZE = 500


def search_query(name: str, organism: int | str, include_subtaxa: bool = False) -> str:
    """UniProt query for a protein name within an organism (optionally its subtree)."""
    if isinstance(organism, int) or str(organism).isdigit():
        field = "taxonomy_id" if include_subtaxa else "organism_id"
        scope = f"{field}:{organism}"
    else:
        scope = f'organism_name:"{organism}"'
    return f'(protein_name:"{name}") AND ({scope})'


def search_key(name: str, organism: int | str, include_subtaxa: bool = False) -> str:
    """File stem used for saved search responses."""
    suffix = "_subtaxa" if include_subtaxa else ""
    return f"{name.replace(' ', '_')}__{str(organism).replace(' ', '_')}{suffix}"


class OnlineUniProtClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    @acquisition("UniProt", "entry")
    def fetch_entry(self, accession: str) -> Tuple[Dict[str, Any], str]:
        request = Request(
            f"{UNIPROT_REST}/{accession}.json", headers={"Accept": "application/json"}
        )
        retrieval = stamp("UniProt")
        try:
            with urlopen(request, timeout=self.timeout, expect_json=True) as resp:  # nosec - trusted endpoint
                return json.loads(resp.read().decode("utf-8")), retrieval.value
        except HTTPError as exc:
            exc.close()
            if exc.code == 404:
                raise RecordNotFoundError(f"UniProt has no record {accession}") from exc
            raise ConnectorError(
                f"UniProt request for {accession} failed: HTTP {exc.code}"
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ConnectorError(
                f"UniProt request for {accession} failed: {exc}"
            ) from exc

    @acquisition("UniProt", "search")
    def search(
        self, name: str, organism: int | str, include_subtaxa: bool = False
    ) -> Dict[str, Any]:
        """Search entries by protein name and organism.

        ``total`` may exceed ``len(results)`` when the search is truncated.
        """
        query = search_query(name, organism, include_subtaxa)
        params = urlencode(
            {
                "query": query,
                "fields": SEARCH_FIELDS,
                "format": "json",
                "size": SEARCH_SIZE,
            }
        )
        retrieval = stamp("UniProt")
        try:
            with urlopen(  # nosec - trusted endpoint
                f"{UNIPROT_REST}/search?{params}",
                timeout=self.timeout,
                expect_json=True,
            ) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", [])
                total = int(resp.headers.get("X-Total-Results", len(results)))
                release = resp.headers.get("X-UniProt-Release")
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(f"UniProt search {query!r} failed: {exc}") from exc
        return {
            "query": query,
            "total": total,
            "release": release,
            "retrieved_at": retrieval.value,
            "results": results,
        }


class FixtureUniProtClient:
    """Serve saved UniProt REST responses.

    Entries come from ``<directory>/<accession>.json`` and searches from
    ``<directory>/uniprot_search/<search_key>.json``. Identifiers or search keys listed in
    ``failing`` simulate a source failure.
    """

    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @acquisition("UniProt", "entry", fixture=True)
    def fetch_entry(self, accession: str) -> Tuple[Dict[str, Any], str]:
        if accession in self.failing:
            raise ConnectorError(f"UniProt request for {accession} failed (simulated)")
        path = self.directory / f"{accession}.json"
        if not path.is_file():
            raise RecordNotFoundError(f"UniProt has no record {accession}")
        return json.loads(path.read_text(encoding="utf-8")), self.retrieved_at

    @acquisition("UniProt", "search", fixture=True)
    def search(
        self, name: str, organism: int | str, include_subtaxa: bool = False
    ) -> Dict[str, Any]:
        key = search_key(name, organism, include_subtaxa)
        if key in self.failing:
            raise ConnectorError(f"UniProt search {key} failed (simulated)")
        path = self.directory / "uniprot_search" / f"{key}.json"
        if not path.is_file():
            raise missing_fixture(f"No saved UniProt search response for {key}")
        saved = json.loads(path.read_text(encoding="utf-8"))
        return {**saved, "retrieved_at": self.retrieved_at}


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


def _isoform_parent_summary(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    _, status = select_isoform(result["record"], query["identifier"])
    out = {
        "outcome": "received",
        "count": 1,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": (result["record"].get("entryAudit") or {}).get("entryVersion"),
            "basis": "parent_entry_version",
        },
        "response_identity": {
            "basis": "native_parent_entry",
            "hash": digest(canonical_json(result["record"])),
        },
        "isoform_declaration_status": status,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


def _isoform_fasta_summary(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    value, _ = parse_fasta(result["record"], query["identifier"])
    out = {
        "outcome": "received",
        "count": 1,
        "sequence_length": len(value),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "isoform_sequence_revision_not_stated",
        },
        "database_release": result.get("database_release"),
        "response_identity": {
            "basis": "native_isoform_FASTA",
            "hash": "sha256:" + hashlib.sha256(result["record"].encode()).hexdigest(),
        },
        "completeness_scope": "one_explicit_isoform; other_isoforms_unqueried",
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineUniProtIsoformClient:
    """Read a native parent declaration and one explicitly requested isoform FASTA."""

    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("UniProt", "isoform_parent", summarize=_isoform_parent_summary)
    def parent(self, identifier):
        identifier = isoform_id(identifier)
        retrieval = stamp("UniProt")
        try:
            with urlopen(
                f"{UNIPROT_REST}/{identifier.rsplit('-', 1)[0]}.json",
                timeout=self.timeout,
                expect_json=True,
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"UniProt isoform parent access failed: {error}"
            ) from error
        select_isoform(payload, identifier)
        return {"record": payload, "retrieved_at": retrieval.value}

    @acquisition("UniProt", "isoform_fasta", summarize=_isoform_fasta_summary)
    def sequence(self, identifier):
        identifier = isoform_id(identifier)
        retrieval = stamp("UniProt")
        try:
            with urlopen(
                f"{UNIPROT_REST}/{identifier}.fasta", timeout=self.timeout
            ) as response:
                document = response.read().decode("utf-8")
                release = response.headers.get("X-UniProt-Release")
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"UniProt isoform FASTA access failed: {error}"
            ) from error
        parse_fasta(document, identifier)
        return {
            "record": document,
            "retrieved_at": retrieval.value,
            "version": None,
            "database_release": release,
        }


class FixtureUniProtIsoformClient:
    """Unmodified parent JSON and explicit FASTA files in ``uniprot_isoforms``."""

    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "uniprot_isoforms"
        self.retrieved_at = retrieved_at

    @acquisition(
        "UniProt", "isoform_parent", fixture=True, summarize=_isoform_parent_summary
    )
    def parent(self, identifier):
        identifier = isoform_id(identifier)
        accession = identifier.rsplit("-", 1)[0]
        path = self.directory / f"{accession}.json"
        if not path.is_file():
            raise missing_fixture(
                f"UniProt isoform parent fixture is unavailable: {path}"
            )
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "UniProt",
                "kind": "isoform_parent",
                "query": {"accession": accession},
                "retrieved_at": self.retrieved_at,
            },
        )
        select_isoform(result["record"], identifier)
        return result

    @acquisition(
        "UniProt", "isoform_fasta", fixture=True, summarize=_isoform_fasta_summary
    )
    def sequence(self, identifier):
        identifier = isoform_id(identifier)
        path = self.directory / f"{identifier}.fasta"
        if not path.is_file():
            raise missing_fixture(
                f"UniProt isoform FASTA fixture is unavailable: {path}"
            )
        try:
            raw = path.read_bytes()
            document = raw.decode("utf-8")
        except (OSError, UnicodeError) as error:
            raise ConnectorError(
                f"UniProt isoform FASTA fixture is unreadable: {error}"
            ) from error
        parse_fasta(document, identifier)
        return {
            "record": document,
            "retrieved_at": self.retrieved_at,
            "version": None,
            "database_release": None,
            "snapshot_receipt": {
                "format": "sabueso.uniprot_supplied_isoform_fasta@1",
                "access": "supplied_file",
                "path": str(path.resolve()),
                "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "document_sha256": hashlib.sha256(raw).hexdigest(),
                "file_format": "fasta",
                "source_metadata_basis": "fixture_client_declaration",
                "source_access_observed": False,
            },
        }


@arg_digest()
@capture_acquisitions
def get_isoform_sequence(identifier, client=None, skip_digestion=False):
    """Read one source-declared isoform sequence without reconstructing variants.

    The parent JSON and selected FASTA retain separate times and hashes. Unknown,
    not-described and external sequences remain unqueried; names never define IDs.
    The result does not enrich a card or query all isoforms automatically.
    """
    identifier = isoform_id(identifier)
    client = online(client, OnlineUniProtIsoformClient)
    result = client.parent(identifier)
    if not isinstance(result, dict) or result.get("truncated", False) is not False:
        raise ConnectorError("UniProt isoform parent client response is malformed.")
    _, status = select_isoform(result.get("record"), identifier)
    native_version = (result["record"].get("entryAudit") or {}).get("entryVersion")
    if result.get("version") is not None and str(result["version"]) != str(
        native_version
    ):
        raise ConnectorError(
            "UniProt parent client revision differs from the native audit."
        )
    parent = source_record(
        "UniProt",
        "isoform_parent",
        {"accession": identifier.rsplit("-", 1)[0]},
        result.get("retrieved_at"),
        native_version,
        deepcopy(result["record"]),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        parent["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    sequence = None
    if status == "declared":
        received = client.sequence(identifier)
        if (
            not isinstance(received, dict)
            or received.get("version") is not None
            or received.get("truncated", False) is not False
        ):
            raise ConnectorError(
                "UniProt isoform FASTA client revision/response is unsupported."
            )
        parse_fasta(received.get("record"), identifier)
        sequence = source_record(
            "UniProt",
            "isoform_fasta",
            {"isoform_id": identifier},
            received.get("retrieved_at"),
            None,
            received["record"],
            truncated=False,
        )
        sequence["database_release"] = received.get("database_release")
        if "snapshot_receipt" in received:
            sequence["snapshot_receipt"] = deepcopy(received["snapshot_receipt"])
    _, status, _ = validate_components(parent, sequence, identifier)
    return source_record(
        "UniProt",
        "isoform_sequence",
        {"isoform_id": identifier},
        (sequence or parent).get("retrieved_at"),
        None,
        {
            "parent_entry": parent,
            "isoform_sequence": sequence,
            "selection_status": status,
        },
        truncated=False,
    )


@arg_digest()
@capture_acquisitions
def get_entry(identifier: str, client: Any = None, skip_digestion: bool = False):
    """The UniProtKB entry of an accession, in a provenance envelope.

    ``version`` is the entry version. Raises RecordNotFoundError or ConnectorError.
    """
    entry, retrieved_at = online(client, OnlineUniProtClient).fetch_entry(identifier)
    if not isinstance(entry, dict) or (
        entry.get("entryAudit") is not None
        and not isinstance(entry["entryAudit"], dict)
    ):
        raise ConnectorError("UniProt entry or entry audit response is malformed.")
    version = (entry.get("entryAudit") or {}).get("entryVersion")
    return source_record(
        "UniProt", "entry", {"accession": identifier}, retrieved_at, version, entry
    )


@arg_digest()
@capture_acquisitions
def search(
    name: str,
    organism: int | str,
    include_subtaxa: bool = False,
    client: Any = None,
    skip_digestion: bool = False,
):
    """UniProtKB entries whose protein name matches, within an organism (NCBI taxonomy
    id or name; ``include_subtaxa`` adds strains and other taxa below it)."""
    result = online(client, OnlineUniProtClient).search(name, organism, include_subtaxa)
    return source_record(
        "UniProt",
        "search",
        {"name": name, "organism": organism, "include_subtaxa": include_subtaxa},
        result.get("retrieved_at"),
        result.get("release"),
        {"total": result.get("total"), "results": result.get("results")},
    )
