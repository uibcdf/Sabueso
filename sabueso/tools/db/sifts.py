"""Explicit SIFTS UniProt segment mappings for a single PDB entry."""

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
from sabueso.mappings.sifts import pdb_id, validate_mappings
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.db._snapshot import BoundSourceSnapshot
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    record = result["record"]
    references = next(iter(record.values()))["UniProt"]
    count = sum(len(r["mappings"]) for r in references.values())
    out = {
        "outcome": "received" if count else "empty",
        "count": count,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "not_stated_in_native_mapping_response",
        },
        "response_identity": {
            "basis": "decoded_native_mapping_response",
            "hash": digest(canonical_json(record)),
        },
        "uniprot_references": list(references),
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineSIFTSClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("SIFTS", "mappings", summarize=_summarize)
    def mappings(self, identifier):
        identifier = pdb_id(identifier)
        retrieval = stamp("SIFTS")
        try:
            with urlopen(
                URL + identifier, timeout=self.timeout, expect_json=True
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"SIFTS mapping access failed: {error}") from error
        validate_mappings(payload, identifier)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}


class SnapshotSIFTSClient(BoundSourceSnapshot):
    """Read caller-bound native structure correspondences from original JSON/gzip."""

    @acquisition("SIFTS", "mappings", fixture=True, summarize=_summarize)
    def mappings(self, identifier):
        identifier = pdb_id(identifier)
        result = self.read(
            "SIFTS", "mappings", {"pdb_id": identifier}, file_format="json"
        )
        validate_mappings(result["record"], identifier)
        return result


class FixtureSIFTSClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "sifts"
        self.retrieved_at = retrieved_at

    @acquisition("SIFTS", "mappings", fixture=True, summarize=_summarize)
    def mappings(self, identifier):
        identifier = pdb_id(identifier)
        path = self.directory / f"mappings__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"SIFTS fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "SIFTS",
                "kind": "mappings",
                "query": {"pdb_id": identifier},
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_mappings(result["record"], identifier)
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_mappings(identifier, client=None, skip_digestion=False):
    """Read native segments and numbering for one PDB entry, retaining every UniProt reference."""
    identifier = pdb_id(identifier)
    result = online(client, OnlineSIFTSClient).mappings(identifier)
    if not isinstance(result, dict) or result.get("version") is not None:
        raise ConnectorError(
            "SIFTS client response/version is malformed or unstated by the source."
        )
    payload = validate_mappings(result.get("record"), identifier)
    envelope = source_record(
        "SIFTS",
        "mappings",
        {"pdb_id": identifier},
        result.get("retrieved_at"),
        None,
        deepcopy(payload),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
