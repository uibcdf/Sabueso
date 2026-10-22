"""Read native CIViC accepted-item TSV for explicit monthly molecular profiles."""

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
from sabueso.mappings.civic import (
    monthly_release,
    parse_export,
    profile_id,
    response_query,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "CIViC"
BASE_URL = "https://civicdb.org/downloads"


def export_url(release):
    release = monthly_release(release)
    return f"{BASE_URL}/{release}/{release}-AcceptedClinicalEvidenceSummaries.tsv"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    native = parse_export(result["record"])
    matches = [
        r
        for r in native["rows"]
        if query["identifier"] == r["fields"]["molecular_profile_id"]
    ]
    out = {
        "outcome": "received" if matches else "not_found",
        "count": len(matches),
        "received_export_rows": len(native["rows"]),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": result.get("version"),
            "basis": "explicit_monthly_export_label; entity_and_sequence_revisions_not_stated",
        },
        "response_identity": {
            "basis": "original_native_tsv_export",
            "hash": "sha256:"
            + hashlib.sha256(result["record"].encode("utf-8")).hexdigest(),
        },
        "native_result_declaration": "matched_native_molecular_profile_ID"
        if matches
        else "not_listed_in_received_export",
        "coverage": "all_received_export_rows_validated; no_independent_database_total",
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


def _load(path, metadata, expected_sha256=None):
    """Read original native TSV/gzip and retain its original byte identity."""
    path = Path(path).expanduser().resolve()
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise missing_fixture(f"CIViC snapshot is unavailable: {path}") from error
    checksum = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and checksum != expected_sha256:
        raise ConnectorError(f"SHA-256 mismatch for supplied CIViC snapshot: {path}")
    compressed = path.suffix.lower() == ".gz"
    try:
        text = (gzip.decompress(raw) if compressed else raw).decode("utf-8")
    except (OSError, EOFError, UnicodeError, zlib.error) as error:
        raise ConnectorError(f"Unreadable supplied CIViC snapshot: {error}") from error
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
        "native_format": "CIViC_accepted_items_25_columns",
        "compression": "gzip" if compressed else None,
        "records_key": None,
        "source_metadata_basis": "caller_declaration",
        "declared_terms": deepcopy(metadata.get("terms")),
        "source_access_observed": False,
    }
    return envelope


class OnlineCIViCClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("CIViC", "molecular_profile_items", summarize=_summarize)
    def molecular_profile_items(self, identifier, release):
        identifier = profile_id(identifier)
        release = monthly_release(release)
        retrieval = stamp("CIViC")
        try:
            with urlopen(
                Request(
                    export_url(release),
                    headers={"Accept": "text/tab-separated-values"},
                ),
                timeout=self.timeout,
            ) as response:
                raw = response.read()
                text = raw.decode("utf-8")
        except (
            HTTPError,
            URLError,
            OSError,
            UnicodeError,
            EOFError,
            zlib.error,
        ) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"CIViC access failed: {error}") from error
        parse_export(text)
        return {
            "record": text,
            "retrieved_at": retrieval.value,
            "version": release,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotCIViCClient:
    """Use original TSV/gzip bound to source, monthly release and molecular profile."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition("CIViC", "molecular_profile_items", fixture=True, summarize=_summarize)
    def molecular_profile_items(self, identifier, release):
        query = response_query(identifier, release)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != "CIViC"
            or result["kind"] != "molecular_profile_items"
            or result["query"] != query
            or result["version"] != release
        ):
            raise ConnectorError(
                "Supplied CIViC source/kind/query/revision differ from the request."
            )
        parse_export(result["record"])
        return result


class FixtureCIViCClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "civic"
        self.retrieved_at = retrieved_at

    @acquisition("CIViC", "molecular_profile_items", fixture=True, summarize=_summarize)
    def molecular_profile_items(self, identifier, release):
        query = response_query(identifier, release)
        result = _load(
            self.directory / f"{release}-AcceptedClinicalEvidenceSummaries.tsv",
            {
                "source": "CIViC",
                "kind": "molecular_profile_items",
                "query": query,
                "retrieved_at": self.retrieved_at,
                "version": release,
            },
        )
        parse_export(result["record"])
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_molecular_profile_items(
    identifier, *, release, client=None, skip_digestion=False
):
    """Receive a complete monthly accepted-items export for exact profile selection.

    The release is explicit (for example 01-Oct-2026). Every row is validated
    before selection. Molecular profiles, therapy combinations, directions,
    significance, ratings, accepted status and flags stay literal. This does not
    fetch CIViC Assertions, submitted items or linked publications, infer clinical
    relevance, merge identities or enrich protein cards.
    """
    identifier = profile_id(identifier)
    release = monthly_release(release)
    result = online(client, OnlineCIViCClient).molecular_profile_items(
        identifier, release
    )
    if (
        not isinstance(result, dict)
        or result.get("version") != release
        or result.get("truncated", False) is not False
    ):
        raise ConnectorError("CIViC client response/revision/cut is unsupported.")
    parse_export(result.get("record"))
    envelope = source_record(
        "CIViC",
        "molecular_profile_items",
        response_query(identifier, release),
        result.get("retrieved_at"),
        release,
        result["record"],
        truncated=False,
    )
    for key in ("download_sha256", "snapshot_receipt"):
        if key in result:
            envelope[key] = deepcopy(result[key])
    return envelope
