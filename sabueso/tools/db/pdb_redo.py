"""Read existing public PDB-REDO databank statistics and revision descriptions."""

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
from sabueso.mappings.pdb_redo import pdb_id, validate_record
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://pdb-redo.eu/db/"
COMPONENTS = {"entry": "data.json", "versions": "versions.json"}


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    out = {
        "outcome": "received",
        "count": 1,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "databank_record_revision_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_record",
            "hash": digest(canonical_json(result["record"])),
        },
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlinePDBRedoClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("PDB-REDO", "databank_component", summarize=_summarize)
    def component(self, identifier, component):
        identifier = pdb_id(identifier)
        if component not in COMPONENTS:
            raise ConnectorError("Unsupported PDB-REDO component.")
        retrieval = stamp("PDB-REDO")
        try:
            with urlopen(
                URL + identifier + "/" + COMPONENTS[component],
                timeout=self.timeout,
                expect_json=True,
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"PDB-REDO {component} access failed: {error}"
            ) from error
        validate_record(payload, identifier, component)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}


class FixturePDBRedoClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "pdb_redo"
        self.retrieved_at = retrieved_at

    @acquisition("PDB-REDO", "databank_component", fixture=True, summarize=_summarize)
    def component(self, identifier, component):
        identifier = pdb_id(identifier)
        if component not in COMPONENTS:
            raise ConnectorError("Unsupported PDB-REDO component.")
        path = self.directory / f"{component}__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"PDB-REDO fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "PDB-REDO",
                "kind": component,
                "query": {"pdb_id": identifier},
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_record(result["record"], identifier, component)
        return result


def _get(identifier, client, component):
    identifier = pdb_id(identifier)
    result = online(client, OnlinePDBRedoClient).component(identifier, component)
    if not isinstance(result, dict) or result.get("version") is not None:
        raise ConnectorError("PDB-REDO client response/revision is unsupported.")
    payload = validate_record(result.get("record"), identifier, component)
    envelope = source_record(
        "PDB-REDO",
        component,
        {"pdb_id": identifier},
        result.get("retrieved_at"),
        None,
        deepcopy(payload),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_entry(identifier, client=None, skip_digestion=False):
    """Read existing databank statistics, retaining every original property and array."""
    return _get(identifier, client, "entry")


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_versions(identifier, client=None, skip_digestion=False):
    """Read input/software revision descriptions separately; submit no calculation."""
    return _get(identifier, client, "versions")
