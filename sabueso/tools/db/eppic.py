"""Explicit precomputed EPPIC annotations; no remote job submission or coordinate fetch."""

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
from sabueso.mappings.eppic import (
    _validated,
    _validated_residues,
    pdb_id,
    validate_component,
    validate_residues,
)
from sabueso.mappings.eppic import interface_id as _interface_id
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://eppic-rest.rcsb.org/rest/api/v3/job/"
COMPONENTS = {"entry": "pdb", "interfaces": "interfaces", "assemblies": "assemblies"}


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    payload = result["record"]
    count = len(payload) if isinstance(payload, list) else 1
    out = {
        "outcome": "received" if count else "empty",
        "count": count,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "prediction_record_revision_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_component",
            "hash": digest(canonical_json(payload)),
        },
        "component": query["component"],
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


def _residue_summary(result, query, fixture, requests):
    summary = _summarize(
        result, {**query, "component": "interface_residues"}, fixture, requests
    )
    summary["interface_id"] = query["interface_id"]
    return summary


class OnlineEPPICClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("EPPIC", "annotation_component", summarize=_summarize)
    def component(self, identifier, component):
        identifier = pdb_id(identifier)
        if component not in COMPONENTS:
            raise ConnectorError("Unsupported EPPIC component.")
        retrieval = stamp("EPPIC")
        try:
            with urlopen(
                URL + COMPONENTS[component] + "/" + identifier,
                timeout=self.timeout,
                expect_json=True,
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"EPPIC {component} access failed: {error}") from error
        validate_component(payload, identifier, component)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}

    @acquisition("EPPIC", "interface_residues", summarize=_residue_summary)
    def interface_residues(self, identifier, interface_id):
        identifier, selected = pdb_id(identifier), _interface_id(interface_id)
        retrieval = stamp("EPPIC")
        try:
            with urlopen(
                URL + f"interfaceResidues/{identifier}/{selected}",
                timeout=self.timeout,
                expect_json=True,
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"EPPIC interface residue access failed: {error}"
            ) from error
        validate_residues(payload)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}


class FixtureEPPICClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "eppic"
        self.retrieved_at = retrieved_at

    @acquisition("EPPIC", "annotation_component", fixture=True, summarize=_summarize)
    def component(self, identifier, component):
        identifier = pdb_id(identifier)
        if component not in COMPONENTS:
            raise ConnectorError("Unsupported EPPIC component.")
        path = self.directory / f"{component}__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"EPPIC fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "EPPIC",
                "kind": component,
                "query": {"pdb_id": identifier},
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_component(result["record"], identifier, component)
        return result

    @acquisition(
        "EPPIC", "interface_residues", fixture=True, summarize=_residue_summary
    )
    def interface_residues(self, identifier, interface_id):
        identifier, selected = pdb_id(identifier), _interface_id(interface_id)
        path = self.directory / f"interface_residues__{identifier}__{selected}.json"
        if not path.is_file():
            raise missing_fixture(f"EPPIC residue fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "EPPIC",
                "kind": "interface_residues",
                "query": {"pdb_id": identifier, "interface_id": selected},
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_residues(result["record"])
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_annotations(identifier, client=None, skip_digestion=False):
    """Bundle three unchanged native responses for one public PDB entry.

    Components retain separate retrieval times and acquisition. A later failed
    component raises with earlier access receipts; an incomplete bundle is never
    reported as empty or mapped. Interface residues and coordinate files are unqueried.
    """
    identifier = pdb_id(identifier)
    client = online(client, OnlineEPPICClient)
    record, metadata = {}, {}
    for component in COMPONENTS:
        result = client.component(identifier, component)
        if not isinstance(result, dict) or result.get("version") is not None:
            raise ConnectorError(
                "EPPIC client component revision/response is unsupported."
            )
        payload = validate_component(result.get("record"), identifier, component)
        record[component] = deepcopy(payload)
        metadata[component] = {
            "retrieved_at": result.get("retrieved_at"),
            "version": None,
            "response_hash": digest(canonical_json(payload)),
        }
        if "snapshot_receipt" in result:
            metadata[component]["snapshot_receipt"] = deepcopy(
                result["snapshot_receipt"]
            )
    envelope = source_record(
        "EPPIC",
        "annotations",
        {"pdb_id": identifier},
        metadata["assemblies"]["retrieved_at"],
        None,
        record,
        truncated=False,
    )
    envelope["component_metadata"] = metadata
    _validated(envelope)
    return envelope


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_interface_residues(identifier, interface_id, client=None, skip_digestion=False):
    """Read native context and residue detail for one explicitly selected interface.

    Two independently observed GETs retain separate times/hashes. Residue rows include
    zero buried area; they do not all declare contact membership. Other interfaces,
    assemblies, sequences and coordinates stay unqueried. A later failure retains
    successful context acquisition; no missing table becomes an empty array.
    """
    identifier, selected = pdb_id(identifier), _interface_id(interface_id)
    client = online(client, OnlineEPPICClient)
    record, metadata = {}, {}
    for component in ("interfaces", "residues"):
        result = (
            client.component(identifier, "interfaces")
            if component == "interfaces"
            else client.interface_residues(identifier, selected)
        )
        if not isinstance(result, dict) or result.get("version") is not None:
            raise ConnectorError(
                "EPPIC residue client revision/response is unsupported."
            )
        payload = result.get("record")
        if component == "interfaces":
            validate_component(payload, identifier, component)
            if not any(row["interfaceId"] == selected for row in payload):
                raise ConnectorError(
                    "EPPIC requested interface is not in the received native context."
                )
        else:
            validate_residues(payload)
        record[component] = deepcopy(payload)
        metadata[component] = {
            "retrieved_at": result.get("retrieved_at"),
            "version": None,
            "response_hash": digest(canonical_json(payload)),
        }
        if "snapshot_receipt" in result:
            metadata[component]["snapshot_receipt"] = deepcopy(
                result["snapshot_receipt"]
            )
    envelope = source_record(
        "EPPIC",
        "interface_residues",
        {"pdb_id": identifier, "interface_id": selected},
        metadata["residues"]["retrieved_at"],
        None,
        record,
        truncated=False,
    )
    envelope["component_metadata"] = metadata
    _validated_residues(envelope)
    return envelope
