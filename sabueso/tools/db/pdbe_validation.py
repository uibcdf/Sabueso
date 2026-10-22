"""Explicit entry-wide PDBe validation metrics for a single PDB entry."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from urllib.error import HTTPError, URLError

from smonitor import signal

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError
from sabueso.core.snapshot import canonical_json, digest
from sabueso.core.source_acquisition import (
    _terminal,
    acquisition,
    capture_acquisitions,
    missing_fixture,
)
from sabueso.mappings.pdbe_validation import pdb_id, validate_percentiles
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://www.ebi.ac.uk/pdbe/api/validation/global-percentiles/entry/"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    record = result["record"]
    count = len(next(iter(record.values())))
    out = {
        "outcome": "received" if count else "empty",
        "count": count,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "not_stated_in_native_validation_response",
        },
        "response_identity": {
            "basis": "decoded_native_validation_response",
            "hash": digest(canonical_json(record)),
        },
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlinePDBeValidationClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("PDBe Validation", "global_percentiles", summarize=_summarize)
    def global_percentiles(self, identifier):
        identifier = pdb_id(identifier)
        retrieval = stamp("PDBe Validation")
        try:
            with urlopen(
                URL + identifier, timeout=self.timeout, expect_json=True
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"PDBe validation access failed: {error}") from error
        validate_percentiles(payload, identifier)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}


class FixturePDBeValidationClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "pdbe_validation"
        self.retrieved_at = retrieved_at

    @acquisition(
        "PDBe Validation", "global_percentiles", fixture=True, summarize=_summarize
    )
    def global_percentiles(self, identifier):
        identifier = pdb_id(identifier)
        path = self.directory / f"global_percentiles__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"PDBe validation fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "PDBe Validation",
                "kind": "global_percentiles",
                "query": {"pdb_id": identifier},
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_percentiles(result["record"], identifier)
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_global_percentiles(identifier, client=None, skip_digestion=False):
    """Read raw values and archive/comparable percentiles for one PDB entry."""
    identifier = pdb_id(identifier)
    result = online(client, OnlinePDBeValidationClient).global_percentiles(identifier)
    if not isinstance(result, dict) or result.get("version") is not None:
        raise ConnectorError(
            "PDBe validation client response/version is malformed or unstated by the source."
        )
    payload = validate_percentiles(result.get("record"), identifier)
    envelope = source_record(
        "PDBe Validation",
        "global_percentiles",
        {"pdb_id": identifier},
        result.get("retrieved_at"),
        None,
        deepcopy(payload),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
