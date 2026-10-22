"""Read the native MEROPS assignment export and select one exact accession literal."""

from __future__ import annotations

import gzip
import hashlib
import zlib
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError

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
from sabueso.mappings.merops import (
    URL,
    parse_assignments,
    representation_issues,
    response_query,
    selected_rows,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    rows = parse_assignments(result["record"])
    selected = selected_rows(rows, query["identifier"])
    out = {
        "outcome": "received"
        if selected or representation_issues(rows)
        else "not_found",
        "count": len(selected),
        "received_export_count": len(rows),
        "representation_issues": representation_issues(rows),
        "selection_complete": not representation_issues(rows),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "export_assignment_and_sequence_revisions_not_stated",
        },
        "response_identity": {
            "basis": "original_native_headerless_accession_export",
            "hash": "sha256:"
            + hashlib.sha256(result["record"].encode("utf-8")).hexdigest(),
        },
        "coverage": "all_received_rows; unassigned_and_quoted_rows_explicit; no_native_total_or_completeness_claim",
        "truncated": False,
    }
    if "download_sha256" in result:
        out["download_sha256"] = result["download_sha256"]
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


def _load(path, metadata, expected_sha256):
    """Retain this native headerless TSV; generic TSV snapshots require headers."""
    path = Path(path).expanduser().resolve()
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise missing_fixture(f"MEROPS snapshot is unavailable: {path}") from error
    checksum = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and checksum != expected_sha256:
        raise ConnectorError(f"SHA-256 mismatch for supplied MEROPS snapshot: {path}")
    compressed = path.suffix.lower() == ".gz"
    try:
        text = (gzip.decompress(raw) if compressed else raw).decode("utf-8")
    except (OSError, EOFError, UnicodeError, zlib.error) as error:
        raise ConnectorError(f"Unreadable supplied MEROPS snapshot: {error}") from error
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
        "native_format": "MEROPS_headerless_three_columns_and_explicit_unassigned_four_columns",
        "compression": "gzip" if compressed else None,
        "records_key": None,
        "source_metadata_basis": "caller_declaration",
        "declared_terms": deepcopy(metadata.get("terms")),
        "source_access_observed": False,
    }
    return envelope


class OnlineMEROPSClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("MEROPS", "accession_assignments", summarize=_summarize)
    def assignments(self, identifier):
        response_query(identifier)
        retrieval = stamp("MEROPS")
        try:
            with urlopen(URL, timeout=self.timeout) as response:
                raw = response.read()
                text = raw.decode("utf-8")
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"MEROPS export access failed: {error}") from error
        parse_assignments(text)
        return {
            "record": text,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotMEROPSClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition("MEROPS", "accession_assignments", fixture=True, summarize=_summarize)
    def assignments(self, identifier):
        query = response_query(identifier)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != "MEROPS"
            or result["kind"] != "accession_assignments"
            or result["query"] != query
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied MEROPS source/kind/query/revision differ from the request."
            )
        parse_assignments(result["record"])
        return result


class FixtureMEROPSClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "merops"
        self.retrieved_at = retrieved_at

    def assignments(self, identifier):
        return SnapshotMEROPSClient(
            self.directory / "accession_assignments.tsv",
            source_metadata={
                "source": "MEROPS",
                "kind": "accession_assignments",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        ).assignments(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_assignments(identifier, client=None, skip_digestion=False):
    """Receive the full native export and select one literal accession, case intact.

    All rows validate before selection. Three-column native assignments and
    unresolved four-column rows and quoted literals stay explicit and unchanged.
    No split accession repair, namespace/protein merge, role/activity/cleavage,
    sequence, linked acquisition or automatic card intake is inferred. A missing
    match cannot establish complete selection when unresolved rows remain.
    """
    query = response_query(identifier)
    result = online(client, OnlineMEROPSClient).assignments(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or ("source" in result and result["source"] != "MEROPS")
        or ("kind" in result and result["kind"] != "accession_assignments")
        or ("query" in result and result["query"] != query)
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError(
            "MEROPS client response/query/revision/cut is unsupported."
        )
    text = result.get("record")
    rows = parse_assignments(text)
    envelope = source_record(
        "MEROPS",
        "accession_assignments",
        query,
        result.get("retrieved_at"),
        None,
        text,
        truncated=False,
    )
    envelope["representation_issues"] = representation_issues(rows)
    envelope["selection_complete"] = not envelope["representation_issues"]
    for k in ("snapshot_receipt", "download_sha256"):
        if k in result:
            envelope[k] = deepcopy(result[k])
    return envelope
