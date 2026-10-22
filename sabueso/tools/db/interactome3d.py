"""Read archived Interactome3D representative protein metadata for one accession."""

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
from sabueso.mappings.interactome3d import (
    ARTIFACT,
    RELEASE,
    URL,
    parse_proteins,
    response_query,
    selected_rows,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    rows = parse_proteins(result["record"])
    selected = selected_rows(rows, query["identifier"])
    out = {
        "outcome": "received" if selected else "not_found",
        "count": len(selected),
        "received_export_count": len(rows),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "selected_archive_route_is_not_native_export_PDB_or_sequence_revision",
        },
        "response_identity": {
            "basis": "original_native_representative_protein_table",
            "hash": "sha256:"
            + hashlib.sha256(result["record"].encode("utf-8")).hexdigest(),
        },
        "coverage": "full_received_representative_protein_export; complete_set_and_interactions_unqueried; no_native_total",
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
    """Retain original native TSV or gzip bytes with explicit caller binding."""
    path = Path(path).expanduser().resolve()
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise missing_fixture(
            f"Interactome3D snapshot is unavailable: {path}"
        ) from error
    checksum = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and checksum != expected_sha256:
        raise ConnectorError(
            f"SHA-256 mismatch for supplied Interactome3D snapshot: {path}"
        )
    compressed = path.suffix.lower() == ".gz"
    try:
        text = (gzip.decompress(raw) if compressed else raw).decode("utf-8")
    except (OSError, EOFError, UnicodeError, zlib.error) as error:
        raise ConnectorError(
            f"Unreadable supplied Interactome3D snapshot: {error}"
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
        "file_format": "tsv",
        "native_format": "Interactome3D_proteins_dat_fourteen_columns",
        "compression": "gzip" if compressed else None,
        "records_key": None,
        "source_metadata_basis": "caller_declaration",
        "declared_terms": deepcopy(metadata.get("terms")),
        "source_access_observed": False,
    }
    return envelope


class OnlineInteractome3DClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("Interactome3D", "protein_structures", summarize=_summarize)
    def protein_structures(self, identifier, release=RELEASE):
        response_query(identifier, release)
        retrieval = stamp("Interactome3D")
        try:
            with urlopen(URL, timeout=self.timeout) as response:
                raw = response.read()
                text = raw.decode("utf-8")
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"Interactome3D export access failed: {error}"
            ) from error
        parse_proteins(text)
        return {
            "record": text,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotInteractome3DClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition(
        "Interactome3D", "protein_structures", fixture=True, summarize=_summarize
    )
    def protein_structures(self, identifier, release=RELEASE):
        query = response_query(identifier, release)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != "Interactome3D"
            or result["kind"] != "protein_structures"
            or result["query"] != query
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied Interactome3D source/kind/query/revision differ from the request."
            )
        parse_proteins(result["record"])
        return result


class FixtureInteractome3DClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "interactome3d"
        self.retrieved_at = retrieved_at

    def protein_structures(self, identifier, release=RELEASE):
        return SnapshotInteractome3DClient(
            self.directory / ARTIFACT,
            source_metadata={
                "source": "Interactome3D",
                "kind": "protein_structures",
                "query": response_query(identifier, release),
                "retrieved_at": self.retrieved_at,
            },
        ).protein_structures(identifier, release=release)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_protein_structures(
    identifier, release=RELEASE, client=None, skip_digestion=False
):
    """Receive the archived human representative protein table for one accession.

    Validate all fourteen columns before exact native accession selection. Retain
    repeated structure/model occurrences, blank chain labels and opaque scores.
    Identity/coverage use independently documented percent quantities. Source
    bounds are not exact full-chain correspondence; route release is distinct
    from unknown native/PDB/sequence revisions. No interaction-pair, coordinate,
    modelling/alignment, protein identity merge or automatic card intake.
    """
    query = response_query(identifier, release)
    result = online(client, OnlineInteractome3DClient).protein_structures(
        identifier, release=release
    )
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or ("source" in result and result["source"] != "Interactome3D")
        or ("kind" in result and result["kind"] != "protein_structures")
        or ("query" in result and result["query"] != query)
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError(
            "Interactome3D client response/query/revision/cut is unsupported."
        )
    text = result.get("record")
    parse_proteins(text)
    envelope = source_record(
        "Interactome3D",
        "protein_structures",
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
