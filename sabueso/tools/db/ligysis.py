"""Read one explicitly selected public LIGYSIS result segment as unchanged HTML."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request

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
from sabueso.mappings.ligysis import (
    accession,
    parse_result,
    segment_id,
    structure_id,
    validate_structure_mapping,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.db._snapshot import BoundSourceSnapshot
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://www.compbio.dundee.ac.uk/ligysis/results/"
MAPPING_URL = "https://www.compbio.dundee.ac.uk/ligysis/get-uniprot-mapping"


def _summarize_mapping(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    payload = validate_structure_mapping(result["record"], query["pdb_id"])
    counts = {"chain2acc": len(payload["chain2acc"]), "chains": len(payload["chains"])}
    counts.update(
        {key: len(payload[key][query["pdb_id"]]) for key in ("pdb2up", "up2pdb")}
    )
    out = {
        "outcome": "received" if sum(counts.values()) else "empty",
        "count": sum(counts.values()),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {"value": None, "basis": "mapping_revision_not_stated"},
        "response_identity": {
            "basis": "decoded_native_mapping",
            "hash": digest(canonical_json(payload)),
        },
        "native_table_counts": counts,
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    native = parse_result(result["record"], query["identifier"], query["segment"])
    out = {
        "outcome": "received" if native["chartData"]["ID"] else "empty",
        "count": len(native["chartData"]["ID"]),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {"value": None, "basis": "result_revision_not_stated"},
        "response_identity": {
            "basis": "original_native_html",
            "hash": hashlib.sha256(result["record"].encode("utf-8")).hexdigest(),
        },
        "segment": query["segment"],
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineLigysisClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("LIGYSIS", "structure_mapping", summarize=_summarize_mapping)
    def structure_mapping(self, identifier, segment, pdb_id):
        identifier, segment, pdb_id = (
            accession(identifier),
            segment_id(segment),
            structure_id(pdb_id),
        )
        request = Request(
            MAPPING_URL,
            data=json.dumps(
                {"pdbId": pdb_id, "proteinId": identifier, "segmentId": str(segment)}
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        retrieval = stamp("LIGYSIS")
        try:
            with urlopen(request, timeout=self.timeout, expect_json=True) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"LIGYSIS structure mapping access failed: {error}"
            ) from error
        validate_structure_mapping(payload, pdb_id)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}

    @acquisition("LIGYSIS", "result_page", summarize=_summarize)
    def result_page(self, identifier, segment):
        identifier, segment = accession(identifier), segment_id(segment)
        retrieval = stamp("LIGYSIS")
        try:
            with urlopen(
                URL + identifier + "/" + str(segment), timeout=self.timeout
            ) as response:
                document = response.read().decode("utf-8")
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"LIGYSIS result page access failed: {error}"
            ) from error
        parse_result(document, identifier, segment)
        return {"record": document, "retrieved_at": retrieval.value, "version": None}


class SnapshotLigysisClient(BoundSourceSnapshot):
    """Read one explicitly bound original result HTML or structure-mapping JSON/gzip.

    Each method requires its own exact source/kind/query declaration before file
    access. Neither a supplied file nor its declared terms establish remote access,
    current source revision, chain identity outside native declarations or permission.
    """

    @acquisition("LIGYSIS", "result_page", fixture=True, summarize=_summarize)
    def result_page(self, identifier, segment):
        identifier, segment = accession(identifier), segment_id(segment)
        result = self.read(
            "LIGYSIS",
            "result_page",
            {"accession": identifier, "segment": segment},
            file_format="html",
        )
        parse_result(result["record"], identifier, segment)
        return result

    @acquisition(
        "LIGYSIS", "structure_mapping", fixture=True, summarize=_summarize_mapping
    )
    def structure_mapping(self, identifier, segment, pdb_id):
        identifier, segment, pdb_id = (
            accession(identifier),
            segment_id(segment),
            structure_id(pdb_id),
        )
        result = self.read(
            "LIGYSIS",
            "structure_mapping",
            {"accession": identifier, "segment": segment, "pdb_id": pdb_id},
            file_format="json",
        )
        validate_structure_mapping(result["record"], pdb_id)
        return result


class FixtureLigysisClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "ligysis"
        self.retrieved_at = retrieved_at

    @acquisition(
        "LIGYSIS", "structure_mapping", fixture=True, summarize=_summarize_mapping
    )
    def structure_mapping(self, identifier, segment, pdb_id):
        identifier, segment, pdb_id = (
            accession(identifier),
            segment_id(segment),
            structure_id(pdb_id),
        )
        path = self.directory / f"mapping__{identifier}__{segment}__{pdb_id}.json"
        if not path.is_file():
            raise missing_fixture(f"LIGYSIS mapping fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "LIGYSIS",
                "kind": "structure_mapping",
                "query": {
                    "accession": identifier,
                    "segment": segment,
                    "pdb_id": pdb_id,
                },
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_structure_mapping(result["record"], pdb_id)
        return result

    @acquisition("LIGYSIS", "result_page", fixture=True, summarize=_summarize)
    def result_page(self, identifier, segment):
        identifier, segment = accession(identifier), segment_id(segment)
        path = self.directory / f"result__{identifier}__{segment}.html"
        if not path.is_file():
            raise missing_fixture(f"LIGYSIS result fixture is unavailable: {path}")
        try:
            raw = path.read_bytes()
            document = raw.decode("utf-8")
        except (OSError, UnicodeError) as error:
            raise ConnectorError(
                f"LIGYSIS result fixture is unreadable: {error}"
            ) from error
        parse_result(document, identifier, segment)
        return {
            "record": document,
            "retrieved_at": self.retrieved_at,
            "version": None,
            "snapshot_receipt": {
                "format": "sabueso.ligysis_supplied_html@1",
                "access": "supplied_file",
                "path": str(path.resolve()),
                "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "document_sha256": hashlib.sha256(raw).hexdigest(),
                "file_format": "html",
                "source_metadata_basis": "fixture_client_declaration",
                "source_access_observed": False,
            },
        }


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_result_page(identifier, segment, client=None, skip_digestion=False):
    """Read unchanged HTML for one explicit segment, without executing page scripts.

    A validated site table and membership retain declared counts/bounds. Other
    segments, ligand details and coordinates remain unqueried; no job is submitted.
    """
    identifier, segment = accession(identifier), segment_id(segment)
    result = online(client, OnlineLigysisClient).result_page(identifier, segment)
    if not isinstance(result, dict) or result.get("version") is not None:
        raise ConnectorError("LIGYSIS client response/revision is unsupported.")
    document = result.get("record")
    parse_result(document, identifier, segment)
    envelope = source_record(
        "LIGYSIS",
        "result_page",
        {"accession": identifier, "segment": segment},
        result.get("retrieved_at"),
        None,
        document,
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_structure_mapping(
    identifier, segment, pdb_id, client=None, skip_digestion=False
):
    """Read four native mapping tables for one explicit PDB structure.

    This is a read-only JSON POST. Protein/segment query context is not echoed;
    both residue directions must explicitly name the requested structure. Native
    chain declarations remain separate, without current-sequence projection or jobs.
    """
    identifier, segment, pdb_id = (
        accession(identifier),
        segment_id(segment),
        structure_id(pdb_id),
    )
    result = online(client, OnlineLigysisClient).structure_mapping(
        identifier, segment, pdb_id
    )
    if not isinstance(result, dict) or result.get("version") is not None:
        raise ConnectorError("LIGYSIS mapping client response/revision is unsupported.")
    payload = validate_structure_mapping(result.get("record"), pdb_id)
    envelope = source_record(
        "LIGYSIS",
        "structure_mapping",
        {"accession": identifier, "segment": segment, "pdb_id": pdb_id},
        result.get("retrieved_at"),
        None,
        deepcopy(payload),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
