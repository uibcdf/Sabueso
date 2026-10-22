"""Read one dated native HPO gene-phenotype export, retaining original content."""

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
from sabueso.mappings.hpo import RELEASE, export_url, parse_annotations, response_query
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    rows, count = parse_annotations(result["record"], query["identifier"])
    out = {
        "outcome": "received" if rows else "not_found",
        "count": len(rows),
        "received_export_count": count,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": query["release"],
            "basis": "exact_dated_provider_release_route",
        },
        "response_identity": {
            "basis": "original_native_six_column_export",
            "hash": "sha256:" + hashlib.sha256(result["record"].encode()).hexdigest(),
        },
        "coverage": "all_received_rows; no_native_total_or_current_database_completeness_claim",
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
    path = Path(path).expanduser().resolve()
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise missing_fixture(f"HPO snapshot is unavailable: {path}") from error
    checksum = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and checksum != expected_sha256:
        raise ConnectorError(f"SHA-256 mismatch for supplied HPO snapshot: {path}")
    compressed = path.suffix.lower() == ".gz"
    try:
        text = (gzip.decompress(raw) if compressed else raw).decode("utf-8")
    except (OSError, EOFError, UnicodeError, zlib.error) as error:
        raise ConnectorError(f"Unreadable supplied HPO snapshot: {error}") from error
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
        "native_format": "HPO_genes_to_phenotype_six_columns",
        "compression": "gzip" if compressed else None,
        "records_key": None,
        "source_metadata_basis": "caller_declaration",
        "declared_terms": deepcopy(metadata.get("terms")),
        "source_access_observed": False,
    }
    return envelope


class OnlineHPOClient:
    def __init__(self, timeout=45.0):
        self.timeout = timeout

    @acquisition("HPO", "gene_phenotypes", summarize=_summarize)
    def gene_annotations(self, identifier, release=RELEASE):
        response_query(identifier, release)
        retrieval = stamp("HPO")
        try:
            with urlopen(export_url(release), timeout=self.timeout) as response:
                raw = response.read()
                text = raw.decode("utf-8")
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"HPO export access failed: {error}") from error
        parse_annotations(text, identifier)
        return {
            "record": text,
            "retrieved_at": retrieval.value,
            "version": release,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotHPOClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition("HPO", "gene_phenotypes", fixture=True, summarize=_summarize)
    def gene_annotations(self, identifier, release=RELEASE):
        query = response_query(identifier, release)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != "HPO"
            or result["kind"] != "gene_phenotypes"
            or result["query"] != query
            or result["version"] != release
        ):
            raise ConnectorError(
                "Supplied HPO source/kind/query/release differ from the request."
            )
        parse_annotations(result["record"], identifier)
        return result


class FixtureHPOClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "hpo"
        self.retrieved_at = retrieved_at

    def gene_annotations(self, identifier, release=RELEASE):
        return SnapshotHPOClient(
            self.directory / release / "genes_to_phenotype.txt",
            source_metadata={
                "source": "HPO",
                "kind": "gene_phenotypes",
                "query": response_query(identifier, release),
                "retrieved_at": self.retrieved_at,
                "version": release,
            },
        ).gene_annotations(identifier, release)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_gene_annotations(
    identifier, release=RELEASE, client=None, skip_digestion=False
):
    """Retain the complete native dated export; select an exact NCBI Gene ID.

    Every received row validates before selection. Symbols and frequency strings
    stay literal; disease-associated annotations do not assert gene penetrance,
    inherited ontology ancestors, individual patients or protein/isoform identity.
    The released file remains unchanged. No linked input, diagnostic calculation
    or automatic card intake occurs. Not-listed is distinct from failed access.
    """
    query = response_query(identifier, release)
    result = online(client, OnlineHPOClient).gene_annotations(identifier, release)
    if (
        not isinstance(result, dict)
        or result.get("version") != release
        or ("source" in result and result["source"] != "HPO")
        or ("kind" in result and result["kind"] != "gene_phenotypes")
        or ("query" in result and result["query"] != query)
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError("HPO client response/query/release/cut is unsupported.")
    text = result.get("record")
    parse_annotations(text, identifier)
    envelope = source_record(
        "HPO",
        "gene_phenotypes",
        query,
        result.get("retrieved_at"),
        release,
        text,
        truncated=False,
    )
    for key in ("snapshot_receipt", "download_sha256"):
        if key in result:
            envelope[key] = deepcopy(result[key])
    return envelope
