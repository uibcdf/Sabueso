"""Receive unchanged PDBTM XML and explicit source-chain topology."""

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
from sabueso.mappings.pdbtm import (
    BASE,
    decode_xml,
    native_hash,
    parse_topology,
    response_query,
    xml_encoding,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    _, chains = parse_topology(result["record"], query["identifier"])
    out = {
        "outcome": "received",
        "count": len(chains),
        "received_region_count": sum(len(c["regions"]) for c in chains),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "entry_PDB_and_sequence_revisions_unqualified",
        },
        "response_identity": {
            "basis": "unchanged_native_PDBTM_XML_in_declared_encoding",
            "hash": "sha256:" + native_hash(result["record"]),
        },
        "coverage": "full_received_entry; no_source_wide_or_sequence_completeness_claim",
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


def _load(path, metadata, expected_sha256):
    path = Path(path).expanduser().resolve()
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise missing_fixture(f"PDBTM snapshot is unavailable: {path}") from error
    checksum = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and checksum != expected_sha256:
        raise ConnectorError(f"SHA-256 mismatch for supplied PDBTM snapshot: {path}")
    compressed = path.suffix.lower() == ".gz"
    try:
        text = decode_xml(gzip.decompress(raw) if compressed else raw)
    except (OSError, EOFError, zlib.error) as error:
        raise ConnectorError(f"Unreadable supplied PDBTM snapshot: {error}") from error
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
        "native_format": "pdbtm_xml",
        "native_encoding": xml_encoding(text),
        "compression": "gzip" if compressed else None,
        "records_key": None,
        "source_metadata_basis": "caller_declaration",
        "declared_terms": deepcopy(metadata.get("terms")),
        "source_access_observed": False,
    }
    return envelope


class OnlinePDBTMClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("PDBTM", "transmembrane_topology", summarize=_summarize)
    def topology(self, identifier):
        response_query(identifier)
        retrieval = stamp("PDBTM")
        try:
            with urlopen(BASE + identifier + ".xml", timeout=self.timeout) as response:
                text = decode_xml(response.read())
        except (HTTPError, URLError, OSError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"PDBTM entry access failed: {error}") from error
        parse_topology(text, identifier)
        return {"record": text, "retrieved_at": retrieval.value, "version": None}


class SnapshotPDBTMClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition("PDBTM", "transmembrane_topology", fixture=True, summarize=_summarize)
    def topology(self, identifier):
        query = response_query(identifier)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != "PDBTM"
            or result["kind"] != "transmembrane_topology"
            or result["query"] != query
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied PDBTM source/kind/query/revision differ from the request."
            )
        parse_topology(result["record"], identifier)
        return result


class FixturePDBTMClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "pdbtm"
        self.retrieved_at = retrieved_at

    def topology(self, identifier):
        return SnapshotPDBTMClient(
            self.directory / (identifier + ".xml"),
            source_metadata={
                "source": "PDBTM",
                "kind": "transmembrane_topology",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        ).topology(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_topology(identifier, client=None, skip_digestion=False):
    """Read one exact native PDB entry without coordinates or canonical projection.

    Original XML/copyright survives in the envelope and each mapped occurrence.
    All chains/regions validate before mapping. Nonprofit unchanged-content and
    commercial-agreement conditions remain explicit; automated use/sharing is
    unknown. No sequence-offset mapping, chain merge, quantity or transform is
    inferred from original numbering, matrices or site/history version labels.
    """
    query = response_query(identifier)
    result = online(client, OnlinePDBTMClient).topology(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or ("source" in result and result["source"] != "PDBTM")
        or ("kind" in result and result["kind"] != "transmembrane_topology")
        or ("query" in result and result["query"] != query)
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError("PDBTM client response/query/revision/cut is unsupported.")
    text = result.get("record")
    parse_topology(text, identifier)
    checksum = native_hash(text)
    if result.get("native_document_sha256", checksum) != checksum:
        raise ConnectorError("PDBTM client document identity differs.")
    envelope = source_record(
        "PDBTM",
        "transmembrane_topology",
        query,
        result.get("retrieved_at"),
        None,
        text,
        truncated=False,
    )
    envelope["native_document_sha256"] = checksum
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
