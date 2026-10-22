"""Read native TTD target listing blocks by exact source target ID."""

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
from sabueso.mappings.ttd import (
    URL,
    parse_targets,
    response_query,
    selected_rows,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    parsed = parse_targets(result["record"])
    selected = selected_rows(parsed, query["identifier"])
    out = {
        "outcome": "received" if selected else "not_found",
        "count": len(selected),
        "received_export_count": len(parsed["rows"]),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": parsed["version"],
            "basis": "native_export_header_release; individual_target_and_UniProt_revisions_unknown",
        },
        "response_identity": {
            "basis": "original_native_tag_value_target_listing",
            "hash": "sha256:"
            + hashlib.sha256(result["record"].encode("utf-8")).hexdigest(),
        },
        "coverage": "full_received_export; not_listed_is_not_biological_absence; no_native_total",
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
    """Retain native tag-value blocks and original bytes; generic TSV snapshots require headers."""
    path = Path(path).expanduser().resolve()
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise missing_fixture(f"TTD snapshot is unavailable: {path}") from error
    checksum = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and checksum != expected_sha256:
        raise ConnectorError(f"SHA-256 mismatch for supplied TTD snapshot: {path}")
    compressed = path.suffix.lower() == ".gz"
    try:
        text = (gzip.decompress(raw) if compressed else raw).decode("utf-8")
    except (OSError, EOFError, UnicodeError, zlib.error) as error:
        raise ConnectorError(f"Unreadable supplied TTD snapshot: {error}") from error
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
        "file_format": "text",
        "native_format": "TTD_four_tag_value_target_blocks",
        "compression": "gzip" if compressed else None,
        "records_key": None,
        "source_metadata_basis": "caller_declaration",
        "declared_terms": deepcopy(metadata.get("terms")),
        "source_access_observed": False,
    }
    return envelope


class OnlineTTDClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("TTD", "target_listing", summarize=_summarize)
    def target_listing(self, identifier):
        response_query(identifier)
        retrieval = stamp("TTD")
        try:
            with urlopen(URL, timeout=self.timeout) as response:
                raw = response.read()
                text = raw.decode("utf-8")
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"TTD export access failed: {error}") from error
        parsed = parse_targets(text)
        return {
            "record": text,
            "retrieved_at": retrieval.value,
            "version": parsed["version"],
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotTTDClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition("TTD", "target_listing", fixture=True, summarize=_summarize)
    def target_listing(self, identifier):
        query = response_query(identifier)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != "TTD"
            or result["kind"] != "target_listing"
            or result["query"] != query
        ):
            raise ConnectorError(
                "Supplied TTD source/kind/query/revision differ from the request."
            )
        parsed = parse_targets(result["record"])
        if result["version"] != parsed["version"]:
            raise ConnectorError("TTD snapshot release differs from its native header.")
        return result


class FixtureTTDClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "ttd"
        self.retrieved_at = retrieved_at

    def target_listing(self, identifier):
        return SnapshotTTDClient(
            self.directory / "P2-01-TTD_uniprot_all.txt",
            source_metadata={
                "source": "TTD",
                "kind": "target_listing",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
                "version": "10.1.01",
            },
        ).target_listing(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_target_listing(identifier, client=None, skip_digestion=False):
    """Receive the full native target listing for one exact TTD target ID.

    Validate all four-field blocks first; retain native labels, cross-reference
    entry names, NOUNIPROTAC, blanks and repeated/conflicting occurrences.
    Native header release is explicit; target/UniProt revisions stay unknown.
    No accession inference, gene/protein merge, drug/disease/activity join,
    derived druggability, clinical conclusion or automatic card enrichment.
    Data use/sharing remain unknown under NOT-STATED terms.
    """
    query = response_query(identifier)
    result = online(client, OnlineTTDClient).target_listing(identifier)
    if (
        not isinstance(result, dict)
        or ("source" in result and result["source"] != "TTD")
        or ("kind" in result and result["kind"] != "target_listing")
        or ("query" in result and result["query"] != query)
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError("TTD client response/query/revision/cut is unsupported.")
    text = result.get("record")
    parsed = parse_targets(text)
    if result.get("version") != parsed["version"]:
        raise ConnectorError("TTD client release differs from its native header.")
    envelope = source_record(
        "TTD",
        "target_listing",
        query,
        result.get("retrieved_at"),
        parsed["version"],
        text,
        truncated=False,
    )
    for k in ("snapshot_receipt", "download_sha256"):
        if k in result:
            envelope[k] = deepcopy(result[k])
    return envelope
