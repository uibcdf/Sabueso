"""Read existing ChannelsDB annotations for one explicit PDB entry."""

from __future__ import annotations

import hashlib
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
from sabueso.mappings.channelsdb import (
    CHANNELS_URL,
    GROUPS,
    URL,
    annotation_count,
    channel_counts,
    pdb_id,
    validate_annotations,
    validate_channels,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    payload = validate_annotations(result["record"])
    count = annotation_count(payload)
    out = {
        "outcome": "received" if count else "empty",
        "count": count,
        "received_counts": {
            "EntryAnnotations": len(payload["EntryAnnotations"]),
            **{g: len(payload["ResidueAnnotations"][g]) for g in GROUPS},
        },
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "record_input_sequence_and_annotation_revisions_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_PDB_annotations_DTO",
            "hash": digest(canonical_json(payload)),
        },
        "coverage": "full_received_DTO; no_native_total_or_database_coverage_claim",
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


def _summarize_channels(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    payload = validate_channels(result["record"])
    counts = channel_counts(payload)
    count = sum(counts.values())
    out = {
        "outcome": "received" if count else "empty",
        "count": count,
        "received_counts": counts,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "channel_input_membership_and_scientific_revisions_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_PDB_channel_DTO",
            "hash": digest(canonical_json(payload)),
        },
        "coverage": "all_received_membership_and_channel_annotation_tables; geometry_unqualified; no_native_total",
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


class OnlineChannelsDBClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("ChannelsDB", "pdb_annotations", summarize=_summarize)
    def annotations(self, identifier):
        identifier = pdb_id(identifier)
        retrieval = stamp("ChannelsDB")
        try:
            with urlopen(
                URL + identifier, timeout=self.timeout, expect_json=True
            ) as response:
                raw = response.read()
                payload = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"ChannelsDB annotation access failed: {error}"
            ) from error
        validate_annotations(payload)
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }

    @acquisition("ChannelsDB", "pdb_channels", summarize=_summarize_channels)
    def channels(self, identifier):
        identifier = pdb_id(identifier)
        retrieval = stamp("ChannelsDB")
        try:
            with urlopen(
                CHANNELS_URL + identifier, timeout=self.timeout, expect_json=True
            ) as response:
                raw = response.read()
                payload = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"ChannelsDB channel access failed: {error}"
            ) from error
        validate_channels(payload)
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotChannelsDBClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path, self.source_metadata = path, deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition("ChannelsDB", "pdb_annotations", fixture=True, summarize=_summarize)
    def annotations(self, identifier):
        identifier = pdb_id(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied ChannelsDB snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "ChannelsDB"
            or result["kind"] != "pdb_annotations"
            or result["query"] != {"pdb_id": identifier}
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied ChannelsDB source/kind/query/revision differ from the request."
            )
        validate_annotations(result["record"])
        return result

    @acquisition(
        "ChannelsDB", "pdb_channels", fixture=True, summarize=_summarize_channels
    )
    def channels(self, identifier):
        identifier = pdb_id(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied ChannelsDB channels snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "ChannelsDB"
            or result["kind"] != "pdb_channels"
            or result["query"] != {"pdb_id": identifier}
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied ChannelsDB channel source/kind/query/revision differ from the request."
            )
        validate_channels(result["record"])
        return result


class FixtureChannelsDBClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "channelsdb"
        self.retrieved_at = retrieved_at

    def annotations(self, identifier):
        identifier = pdb_id(identifier)
        return SnapshotChannelsDBClient(
            self.directory / f"annotations__{identifier}.json",
            source_metadata={
                "source": "ChannelsDB",
                "kind": "pdb_annotations",
                "query": {"pdb_id": identifier},
                "retrieved_at": self.retrieved_at,
            },
        ).annotations(identifier)

    def channels(self, identifier):
        identifier = pdb_id(identifier)
        return SnapshotChannelsDBClient(
            self.directory / f"channels__{identifier}.json",
            source_metadata={
                "source": "ChannelsDB",
                "kind": "pdb_channels",
                "query": {"pdb_id": identifier},
                "retrieved_at": self.retrieved_at,
            },
        ).channels(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_annotations(identifier, client=None, skip_digestion=False):
    """Receive independent entry and residue annotations for one explicit PDB ID.

    Original text, reactions, references, groups and residue/chain literals remain
    intact. No numbering axis, tunnel relation, UniProt identity, model/assembly,
    function inference, coordinate acquisition, calculation or card intake is added.
    A failed/missing route is an acquisition failure, not annotation absence.
    """
    identifier = pdb_id(identifier)
    query = {"pdb_id": identifier}
    result = online(client, OnlineChannelsDBClient).annotations(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or ("source" in result and result["source"] != "ChannelsDB")
        or ("kind" in result and result["kind"] != "pdb_annotations")
        or ("query" in result and result["query"] != query)
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError(
            "ChannelsDB client response/query/revision/cut is unsupported."
        )
    record = validate_annotations(result.get("record"))
    envelope = source_record(
        "ChannelsDB",
        "pdb_annotations",
        query,
        result.get("retrieved_at"),
        None,
        deepcopy(record),
        truncated=False,
    )
    for k in ("snapshot_receipt", "download_sha256"):
        if k in result:
            envelope[k] = deepcopy(result[k])
    return envelope


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_channels(identifier, client=None, skip_digestion=False):
    """Read existing channel data for one explicit PDB entry, without a calculation.

    Native membership/annotation tables are qualified; raw profile geometry and
    physical properties remain uninterpreted. Source URL/caller declaration binds
    the query, not an echoed structure identity. No assembly or annotation join,
    protein identity, current residue projection, coordinates or jobs are added.
    """
    identifier = pdb_id(identifier)
    query = {"pdb_id": identifier}
    result = online(client, OnlineChannelsDBClient).channels(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or ("source" in result and result["source"] != "ChannelsDB")
        or ("kind" in result and result["kind"] != "pdb_channels")
        or ("query" in result and result["query"] != query)
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError(
            "ChannelsDB channel client response/query/revision/cut is unsupported."
        )
    record = validate_channels(result.get("record"))
    envelope = source_record(
        "ChannelsDB",
        "pdb_channels",
        query,
        result.get("retrieved_at"),
        None,
        deepcopy(record),
        truncated=False,
    )
    for key in ("snapshot_receipt", "download_sha256"):
        if key in result:
            envelope[key] = deepcopy(result[key])
    return envelope
