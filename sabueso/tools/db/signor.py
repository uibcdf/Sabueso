"""Read native SIGNOR headerless causal interaction tables with exact query binding."""

from __future__ import annotations

import gzip
import hashlib
import zlib
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request

from smonitor import signal

from sabueso._private.argdigest import arg_digest
from sabueso._private.argdigest.argument.expected_sha256 import digest_expected_sha256
from sabueso._private.argdigest.argument.source_metadata import digest_source_metadata
from sabueso.core.errors import ConnectorError
from sabueso.core.source_acquisition import (
    _terminal,
    acquisition,
    capture_acquisitions,
    missing_fixture,
)
from sabueso.mappings.signor import (
    NO_RESULTS,
    accession,
    organism,
    parse_relations,
    response_query,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

URL = "https://signor.uniroma2.it/getData.php?"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    rows = parse_relations(result["record"], query["identifier"])
    out = {
        "outcome": "received" if rows else "empty",
        "count": len(rows),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "export_relation_sequence_and_score_revisions_not_stated",
        },
        "response_identity": {
            "basis": "original_native_headerless_tsv",
            "hash": "sha256:"
            + hashlib.sha256(result["record"].encode("utf-8")).hexdigest(),
        },
        "native_taxonomy_literals": sorted({r["fields"]["TAX_ID"] for r in rows}),
        "native_publication_pointers": sorted({r["fields"]["PMID"] for r in rows}),
        "native_result_declaration": NO_RESULTS
        if result["record"] == NO_RESULTS
        else "received_tsv",
        "coverage": "all_received_rows; requested_organism_not_observed_taxonomy; no_native_total",
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


def _load(path, metadata, expected_sha256=None):
    """Read this native headerless format; generic TSV snapshots require headers."""
    path = Path(path).expanduser().resolve()
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise missing_fixture(f"SIGNOR snapshot is unavailable: {path}") from error
    checksum = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and checksum != expected_sha256:
        raise ConnectorError(f"SHA-256 mismatch for supplied SIGNOR snapshot: {path}")
    compressed = path.suffix.lower() == ".gz"
    try:
        text = (gzip.decompress(raw) if compressed else raw).decode("utf-8")
    except (OSError, EOFError, UnicodeError, zlib.error) as error:
        raise ConnectorError(f"Unreadable supplied SIGNOR snapshot: {error}") from error
    envelope = source_record(
        metadata["source"],
        metadata["kind"],
        metadata.get("query", {}),
        metadata.get("retrieved_at"),
        metadata.get("version"),
        text,
    )
    envelope["snapshot_receipt"] = {
        "format": "sabueso.supplied_snapshot@1",
        "access": "supplied_file",
        "path": str(path),
        "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "document_sha256": checksum,
        "digest_verification": "matched_caller_digest"
        if expected_sha256
        else "not_requested",
        "file_format": "tsv",
        "native_format": "SIGNOR_headerless_28_columns_with_optional_empty_trailer",
        "compression": "gzip" if compressed else None,
        "records_key": None,
        "source_metadata_basis": "caller_declaration",
        "declared_terms": deepcopy(metadata.get("terms")),
        "source_access_observed": False,
    }
    return envelope


class OnlineSignorClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("SIGNOR", "causal_relations", summarize=_summarize)
    def relations(self, identifier, taxon_id):
        identifier, taxon_id = accession(identifier), organism(taxon_id)
        retrieval = stamp("SIGNOR")
        try:
            with urlopen(
                Request(
                    URL + urlencode({"id": identifier, "organism": taxon_id}),
                    headers={"Accept": "text/tab-separated-values"},
                ),
                timeout=self.timeout,
            ) as response:
                text = response.read().decode("utf-8")
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"SIGNOR access failed: {error}") from error
        parse_relations(text, identifier)
        return {"record": text, "retrieved_at": retrieval.value, "version": None}


class SnapshotSignorClient:
    """Use an original native TSV/gzip file with declared source and exact query."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition("SIGNOR", "causal_relations", fixture=True, summarize=_summarize)
    def relations(self, identifier, taxon_id):
        query = response_query(identifier, taxon_id)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != "SIGNOR"
            or result["kind"] != "causal_relations"
            or result["query"] != query
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied SIGNOR source/kind/query/revision differ from the request."
            )
        parse_relations(result["record"], query["accession"])
        return result


class FixtureSignorClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "signor"
        self.retrieved_at = retrieved_at

    @acquisition("SIGNOR", "causal_relations", fixture=True, summarize=_summarize)
    def relations(self, identifier, taxon_id):
        query = response_query(identifier, taxon_id)
        result = _load(
            self.directory
            / f"relations__{query['accession']}__{query['requested_organism']}.tsv",
            {
                "source": "SIGNOR",
                "kind": "causal_relations",
                "query": query,
                "retrieved_at": self.retrieved_at,
            },
        )
        parse_relations(result["record"], query["accession"])
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_relations(identifier, taxon_id=9606, client=None, skip_digestion=False):
    """Receive every native SIGNOR row for an explicit UniProt/organism request.

    Requested organism is separate from each returned TAX_ID: responses can include
    other species, unspecified context and in-vitro -1. Original regulator/target,
    effect/mechanism, DIRECT flags, residue/sequence, score and publication context
    survive. No query expansion, binding inference, experimental class, current
    sequence placement, linked retrieval, calculation or card enrichment occurs.
    """
    identifier, taxon_id = accession(identifier), organism(taxon_id)
    result = online(client, OnlineSignorClient).relations(identifier, taxon_id)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
    ):
        raise ConnectorError("SIGNOR client response/revision/cut is unsupported.")
    parse_relations(result.get("record"), identifier)
    envelope = source_record(
        "SIGNOR",
        "causal_relations",
        response_query(identifier, taxon_id),
        result.get("retrieved_at"),
        None,
        result["record"],
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
