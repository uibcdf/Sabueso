"""Explicit Pharos target metadata through its documented public GraphQL API."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

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
from sabueso.mappings.pharos import QUERY, URL, response_query, validate_target
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    target = validate_target(result["record"], query["identifier"])
    out = {
        "outcome": "received" if target is not None else "not_found",
        "count": int(target is not None),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "native_selected_fields_do_not_state_dataset_record_sequence_or_TDL_rule_revision",
        },
        "response_identity": {
            "basis": "native_GraphQL_target_response",
            "hash": digest(canonical_json(result["record"])),
        },
        "coverage": "one_exact_target_five_requested_fields; aggregate_associations_unqueried",
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlinePharosClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("Pharos/TCRD", "target", summarize=_summarize)
    def target(self, identifier):
        response_query(identifier)
        url = (
            URL
            + "?"
            + urlencode(
                {"query": QUERY, "variables": json.dumps({"accession": identifier})}
            )
        )
        retrieval = stamp("Pharos/TCRD")
        try:
            with urlopen(url, timeout=self.timeout, expect_json=True) as response:
                raw = response.read()
                payload = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, UnicodeError, ValueError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"Pharos target access failed: {error}") from error
        validate_target(payload, identifier)
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotPharosClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition("Pharos/TCRD", "target", fixture=True, summarize=_summarize)
    def target(self, identifier):
        query = response_query(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Pharos snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "Pharos/TCRD"
            or result["kind"] != "target"
            or result["query"] != query
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied Pharos source/kind/query/revision differ from request."
            )
        validate_target(result["record"], identifier)
        return result


class FixturePharosClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "pharos"
        self.retrieved_at = retrieved_at

    def target(self, identifier):
        return SnapshotPharosClient(
            self.directory / f"target__{identifier}.json",
            source_metadata={
                "source": "Pharos/TCRD",
                "kind": "target",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        ).target(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_target(identifier, client=None, skip_digestion=False):
    """Receive native name/symbol/accession/TDL/family for one exact base accession.

    A null target is a received no-match response, not biological absence.
    GraphQL errors and mismatched identity fail. Dataset and classification-rule
    revisions stay unknown; no ranking, linked acquisition or card enrichment.
    """
    query = response_query(identifier)
    result = online(client, OnlinePharosClient).target(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
        or any(
            k in result and result[k] != value
            for k, value in {
                "source": "Pharos/TCRD",
                "kind": "target",
                "query": query,
            }.items()
        )
    ):
        raise ConnectorError(
            "Pharos client response/query/revision/cut is unsupported."
        )
    validate_target(result.get("record"), identifier)
    envelope = source_record(
        "Pharos/TCRD",
        "target",
        query,
        result.get("retrieved_at"),
        None,
        deepcopy(result["record"]),
        truncated=False,
    )
    for key in ("snapshot_receipt", "download_sha256"):
        if key in result:
            envelope[key] = deepcopy(result[key])
    return envelope
