"""Read native 3did domain-motif instances for one exact PDB literal."""

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
from sabueso.mappings.threedid import (
    URL,
    parse_motif_interactions,
    response_query,
    selected_instances,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    rows = parse_motif_interactions(result["record"])
    selected = selected_instances(rows, query["identifier"])
    out = {
        "outcome": "received" if selected else "not_found",
        "count": len(selected),
        "received_pair_count": len(rows),
        "received_instance_count": sum(len(b["instances"]) for b in rows),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "export_PDB_Pfam_sequence_and_pattern_revisions_unqualified",
        },
        "response_identity": {
            "basis": "original_native_3did_DMI_flat_export",
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
    """Retain original ID/PT/3D blocks rather than inferring tabular headers."""
    path = Path(path).expanduser().resolve()
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise missing_fixture(f"ThreeDID snapshot is unavailable: {path}") from error
    checksum = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and checksum != expected_sha256:
        raise ConnectorError(f"SHA-256 mismatch for supplied ThreeDID snapshot: {path}")
    compressed = path.suffix.lower() == ".gz"
    try:
        text = (gzip.decompress(raw) if compressed else raw).decode("utf-8")
    except (OSError, EOFError, UnicodeError, zlib.error) as error:
        raise ConnectorError(
            f"Unreadable supplied ThreeDID snapshot: {error}"
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
        "file_format": "text",
        "native_format": "3did_DMI_ID_PT_3D_terminated_blocks",
        "compression": "gzip" if compressed else None,
        "records_key": None,
        "source_metadata_basis": "caller_declaration",
        "declared_terms": deepcopy(metadata.get("terms")),
        "source_access_observed": False,
    }
    return envelope


class OnlineThreeDIDClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("3did", "domain_motif_interactions", summarize=_summarize)
    def motif_interactions(self, identifier):
        response_query(identifier)
        retrieval = stamp("3did")
        try:
            with urlopen(URL, timeout=self.timeout) as response:
                raw = response.read()
                text = gzip.decompress(raw).decode("utf-8")
        except (
            HTTPError,
            URLError,
            OSError,
            EOFError,
            UnicodeError,
            zlib.error,
        ) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"ThreeDID export access failed: {error}") from error
        parse_motif_interactions(text)
        return {
            "record": text,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotThreeDIDClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition(
        "3did", "domain_motif_interactions", fixture=True, summarize=_summarize
    )
    def motif_interactions(self, identifier):
        query = response_query(identifier)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != "3did"
            or result["kind"] != "domain_motif_interactions"
            or result["query"] != query
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied ThreeDID source/kind/query/revision differ from the request."
            )
        parse_motif_interactions(result["record"])
        return result


class FixtureThreeDIDClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "3did"
        self.retrieved_at = retrieved_at

    def motif_interactions(self, identifier):
        return SnapshotThreeDIDClient(
            self.directory / "3did_dmi_flat.gz",
            source_metadata={
                "source": "3did",
                "kind": "domain_motif_interactions",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        ).motif_interactions(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_motif_interactions(identifier, client=None, skip_digestion=False):
    """Receive all native DMI blocks and select one lowercase PDB literal.

    Every received block validates before selection. Preserve domain/motif labels,
    opaque patterns/dates, chain/range/sequence, contextual contact count and topology
    literals with original support. No regex execution, chain decoding, coordinate
    arithmetic, protein identity, function, linked acquisition or card intake.
    """
    query = response_query(identifier)
    result = online(client, OnlineThreeDIDClient).motif_interactions(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or ("source" in result and result["source"] != "3did")
        or ("kind" in result and result["kind"] != "domain_motif_interactions")
        or ("query" in result and result["query"] != query)
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError(
            "ThreeDID client response/query/revision/cut is unsupported."
        )
    text = result.get("record")
    parse_motif_interactions(text)
    envelope = source_record(
        "3did",
        "domain_motif_interactions",
        query,
        result.get("retrieved_at"),
        None,
        text,
        truncated=False,
    )
    for k in ("snapshot_receipt", "download_sha256"):
        if k in result:
            envelope[k] = deepcopy(result[k])
    return envelope
