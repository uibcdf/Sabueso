"""Read native ClinGen gene-disease validity CSV exports with exact gene binding."""

from __future__ import annotations

import gzip
import hashlib
import zlib
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
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
from sabueso.mappings.clingen import gene_id, parse_export, response_query
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "ClinGen"
URL = "https://search.clinicalgenome.org/kb/gene-validity/download"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    native = parse_export(result["record"])
    matches = [
        r
        for r in native["rows"]
        if r["fields"]["GENE ID (HGNC)"] == query["identifier"]
    ]
    out = {
        "outcome": "received" if matches else "not_found",
        "count": len(matches),
        "received_export_rows": len(native["rows"]),
        "native_file_created": native["file_created"],
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "dataset_gene_and_sequence_revisions_not_stated; file_date_is_not_revision",
        },
        "response_identity": {
            "basis": "original_native_csv_export",
            "hash": "sha256:"
            + hashlib.sha256(result["record"].encode("utf-8")).hexdigest(),
        },
        "native_result_declaration": "matched_native_gene_rows"
        if matches
        else "not_listed_in_received_export",
        "coverage": "all_received_export_rows_validated; no_independent_database_total",
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


def _load(path, metadata, expected_sha256=None):
    """Read native CSV with its preamble; generic CSV snapshots have a first-row header."""
    path = Path(path).expanduser().resolve()
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise missing_fixture(f"ClinGen snapshot is unavailable: {path}") from error
    checksum = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and checksum != expected_sha256:
        raise ConnectorError(f"SHA-256 mismatch for supplied ClinGen snapshot: {path}")
    compressed = path.suffix.lower() == ".gz"
    try:
        text = (gzip.decompress(raw) if compressed else raw).decode("utf-8")
    except (OSError, EOFError, UnicodeError, zlib.error) as error:
        raise ConnectorError(
            f"Unreadable supplied ClinGen snapshot: {error}"
        ) from error
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
        "file_format": "csv",
        "native_format": "ClinGen_gene_validity_preamble_and_10_columns",
        "compression": "gzip" if compressed else None,
        "records_key": None,
        "source_metadata_basis": "caller_declaration",
        "declared_terms": deepcopy(metadata.get("terms")),
        "source_access_observed": False,
    }
    return envelope


class OnlineClinGenClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("ClinGen", "gene_validity", summarize=_summarize)
    def gene_validity(self, identifier):
        identifier = gene_id(identifier)
        retrieval = stamp("ClinGen")
        try:
            with urlopen(
                Request(
                    URL,
                    headers={"Accept": "text/csv"},
                ),
                timeout=self.timeout,
            ) as response:
                text = response.read().decode("utf-8")
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"ClinGen access failed: {error}") from error
        parse_export(text)
        return {"record": text, "retrieved_at": retrieval.value, "version": None}


class SnapshotClinGenClient:
    """Use an original native CSV/gzip export with declared source and exact gene query."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition("ClinGen", "gene_validity", fixture=True, summarize=_summarize)
    def gene_validity(self, identifier):
        query = response_query(identifier)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != "ClinGen"
            or result["kind"] != "gene_validity"
            or result["query"] != query
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied ClinGen source/kind/query/revision differ from the request."
            )
        parse_export(result["record"])
        return result


class FixtureClinGenClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "clingen"
        self.retrieved_at = retrieved_at

    @acquisition("ClinGen", "gene_validity", fixture=True, summarize=_summarize)
    def gene_validity(self, identifier):
        query = response_query(identifier)
        result = _load(
            self.directory / "gene_validity.csv",
            {
                "source": "ClinGen",
                "kind": "gene_validity",
                "query": query,
                "retrieved_at": self.retrieved_at,
            },
        )
        parse_export(result["record"])
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_gene_validity(identifier, client=None, skip_digestion=False):
    """Receive the full native ClinGen gene-validity export for exact local gene selection.

    Every native row is validated before selection. File and classification dates
    remain native labels, not scientific revisions. Not listed in this received
    export is separate from an explicit No Known Disease Relationship classification
    and from failed access. Mapping keeps independent classifications, MOI, SOP and
    panel context on the gene; no protein/variant inference or card enrichment.
    """
    identifier = gene_id(identifier)
    result = online(client, OnlineClinGenClient).gene_validity(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
    ):
        raise ConnectorError("ClinGen client response/revision/cut is unsupported.")
    parse_export(result.get("record"))
    envelope = source_record(
        "ClinGen",
        "gene_validity",
        response_query(identifier),
        result.get("retrieved_at"),
        None,
        result["record"],
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
