"""Read native DrugCentral drug-target TSV with exact accession-token selection."""

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
from sabueso.mappings.drugcentral import accession, parse_export, response_query
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "DrugCentral"
URL = "https://unmtid-dbs.net/download/drug.target.interaction.tsv.gz"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    native = parse_export(result["record"])
    matches = [r for r in native["rows"] if query["identifier"] in r["accessions"]]
    out = {
        "outcome": "received" if matches else "not_found",
        "count": len(matches),
        "received_export_rows": len(native["rows"]),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "export_target_drug_and_sequence_revisions_not_stated",
        },
        "response_identity": {
            "basis": "original_native_tsv_export",
            "hash": "sha256:"
            + hashlib.sha256(result["record"].encode("utf-8")).hexdigest(),
        },
        "native_result_declaration": "matched_native_accession_tokens"
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
        raise missing_fixture(f"DrugCentral snapshot is unavailable: {path}") from error
    checksum = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and checksum != expected_sha256:
        raise ConnectorError(
            f"SHA-256 mismatch for supplied DrugCentral snapshot: {path}"
        )
    compressed = path.suffix.lower() == ".gz"
    try:
        text = (gzip.decompress(raw) if compressed else raw).decode("utf-8")
    except (OSError, EOFError, UnicodeError, zlib.error) as error:
        raise ConnectorError(
            f"Unreadable supplied DrugCentral snapshot: {error}"
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
        "native_format": "DrugCentral_drug_target_20_columns",
        "compression": "gzip" if compressed else None,
        "records_key": None,
        "source_metadata_basis": "caller_declaration",
        "declared_terms": deepcopy(metadata.get("terms")),
        "source_access_observed": False,
    }
    return envelope


class OnlineDrugCentralClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("DrugCentral", "target_relations", summarize=_summarize)
    def target_relations(self, identifier):
        identifier = accession(identifier)
        retrieval = stamp("DrugCentral")
        try:
            with urlopen(
                Request(
                    URL,
                    headers={"Accept": "application/gzip"},
                ),
                timeout=self.timeout,
            ) as response:
                raw = response.read()
                text = gzip.decompress(raw).decode("utf-8")
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
            raise ConnectorError(f"DrugCentral access failed: {error}") from error
        parse_export(text)
        return {
            "record": text,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotDrugCentralClient:
    """Use original TSV/gzip with declared source and exact accession query."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition("DrugCentral", "target_relations", fixture=True, summarize=_summarize)
    def target_relations(self, identifier):
        query = response_query(identifier)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != "DrugCentral"
            or result["kind"] != "target_relations"
            or result["query"] != query
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied DrugCentral source/kind/query/revision differ from the request."
            )
        parse_export(result["record"])
        return result


class FixtureDrugCentralClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "drugcentral"
        self.retrieved_at = retrieved_at

    @acquisition("DrugCentral", "target_relations", fixture=True, summarize=_summarize)
    def target_relations(self, identifier):
        query = response_query(identifier)
        result = _load(
            self.directory / "target_relations.tsv.gz",
            {
                "source": "DrugCentral",
                "kind": "target_relations",
                "query": query,
                "retrieved_at": self.retrieved_at,
            },
        )
        parse_export(result["record"])
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_target_relations(identifier, client=None, skip_digestion=False):
    """Receive the full native drug-target export for exact local accession selection.

    Every received row is validated before matching native pipe-separated tokens.
    Compound target groups, native activity/units/relations, MOA and source pointers
    remain unchanged. No target-group expansion, potency conversion, drug identity
    merge, clinical inference or automatic card enrichment. Scientific revisions
    and independent database totals are not stated by this export.
    """
    identifier = accession(identifier)
    result = online(client, OnlineDrugCentralClient).target_relations(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
    ):
        raise ConnectorError("DrugCentral client response/revision/cut is unsupported.")
    parse_export(result.get("record"))
    envelope = source_record(
        "DrugCentral",
        "target_relations",
        response_query(identifier),
        result.get("retrieved_at"),
        None,
        result["record"],
        truncated=False,
    )
    if "download_sha256" in result:
        envelope["download_sha256"] = result["download_sha256"]
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
