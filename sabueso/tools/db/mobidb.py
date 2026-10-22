"""Explicit MobiDB v1 single-protein JSON export, with original annotation sets."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path
from urllib.error import HTTPError, URLError

from smonitor import signal

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.snapshot import canonical_json, digest
from sabueso.core.source_acquisition import (
    _terminal,
    acquisition,
    capture_acquisitions,
    missing_fixture,
)
from sabueso.mappings.mobidb import accession, validate_export
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://mobidb.org/api/v1/protein/"


def _headers(headers, count):
    if not isinstance(headers, dict) or any(
        not isinstance(k, str) or not isinstance(v, str) for k, v in headers.items()
    ):
        raise ConnectorError("MobiDB export headers are malformed.")
    normalized = {k.lower(): v for k, v in headers.items()}
    if len(normalized) != len(headers) or normalized.get("x-next-cursor"):
        raise ConnectorError("MobiDB export is ambiguous or has an unconsumed page.")
    if (
        normalized.get("x-returned-count") != str(count)
        or normalized.get("x-page-limit") != "1"
    ):
        raise ConnectorError("MobiDB native export counts/single-protein scope differ.")
    return deepcopy(headers)


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    record = result["record"]
    receipt = result.get("snapshot_receipt")
    out = {
        "outcome": "received" if record else "empty",
        "count": len(record),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": result.get("version"),
            "basis": "native_export_release",
        },
        "response_identity": {
            "basis": "decoded_native_v1_export",
            "hash": digest(canonical_json(record)),
        },
        "annotation_sets": len(record[0]["annotation_sets"]) if record else 0,
        "representation_issues": len(record[0]["issues"]) if record else 0,
        "truncated": False,
    }
    if receipt:
        out.update(access="supplied_file", snapshot_receipt=deepcopy(receipt))
    return out


class OnlineMobiDBClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("MobiDB", "annotations", summarize=_summarize)
    def annotations(self, identifier):
        identifier = accession(identifier)
        retrieval = stamp("MobiDB")
        try:
            with urlopen(
                URL + identifier + "/export?format=json",
                timeout=self.timeout,
                expect_json=True,
            ) as response:
                payload = _json(response.read().decode("utf-8"))
                headers = dict(response.headers.items())
        except HTTPError as error:
            try:
                if error.code == 404:
                    try:
                        native = _json(error.read().decode("utf-8"))
                    except (ValueError, UnicodeError, OSError):
                        native = None
                    if (
                        isinstance(native, dict)
                        and isinstance(native.get("error"), dict)
                        and native.get("error", {}).get("code") == "PROTEIN_NOT_FOUND"
                        and native["error"].get("parameter") == "acc"
                    ):
                        raise RecordNotFoundError(
                            f"MobiDB has no export for {identifier}."
                        ) from error
                raise ConnectorError(f"MobiDB export failed: {error}") from error
            finally:
                error.close()
        except (URLError, OSError, ValueError, UnicodeError) as error:
            raise ConnectorError(f"MobiDB export failed: {error}") from error
        validate_export(payload, identifier)
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": payload[0]["release"]["mobidb_version"] if payload else None,
            "response_headers": _headers(headers, len(payload)),
        }


class FixtureMobiDBClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "mobidb"
        self.retrieved_at = retrieved_at

    @acquisition("MobiDB", "annotations", fixture=True, summarize=_summarize)
    def annotations(self, identifier):
        identifier = accession(identifier)
        path = self.directory / f"annotations__{identifier}.json"
        header_path = self.directory / f"annotations__{identifier}.headers.json"
        if not path.is_file() or not header_path.is_file():
            raise missing_fixture(
                f"MobiDB export/header fixture is unavailable: {path}"
            )
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "MobiDB",
                "kind": "annotations",
                "query": {"accession": identifier},
                "retrieved_at": self.retrieved_at,
            },
        )
        payload = validate_export(result["record"], identifier)
        try:
            header_raw = header_path.read_bytes()
            headers = _json(header_raw.decode("utf-8"))
        except (OSError, ValueError, UnicodeError) as error:
            raise ConnectorError(
                f"MobiDB fixture headers are unreadable: {error}"
            ) from error
        result["response_headers"] = _headers(headers, len(payload))
        result["version"] = payload[0]["release"]["mobidb_version"] if payload else None
        result["snapshot_receipt"]["response_headers"] = {
            "path": str(header_path.resolve()),
            "document_sha256": hashlib.sha256(header_raw).hexdigest(),
            "basis": "supplied_header_file; not_observed_remote_headers",
        }
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_annotations(identifier, client=None, skip_digestion=False):
    """Read one full canonical source export; retain native series and conversion issues.

    Map disorder/PTM regions separately. Native source basis, aggregation and unknown
    measurement semantics are never replaced with clinical or experimental claims.
    """
    identifier = accession(identifier)
    result = online(client, OnlineMobiDBClient).annotations(identifier)
    if not isinstance(result, dict):
        raise ConnectorError("MobiDB client response is malformed.")
    payload = validate_export(result.get("record"), identifier)
    expected_version = payload[0]["release"]["mobidb_version"] if payload else None
    if result.get("version") != expected_version:
        raise ConnectorError("MobiDB client version differs from the native release.")
    headers = _headers(result.get("response_headers"), len(payload))
    envelope = source_record(
        "MobiDB",
        "annotations",
        {"accession": identifier},
        result.get("retrieved_at"),
        expected_version,
        deepcopy(payload),
        truncated=False,
    )
    envelope["response_headers"] = headers
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
