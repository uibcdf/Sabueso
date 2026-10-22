"""Explicit BRENDA EC-class descriptions through its public SPARQL prototype."""

from __future__ import annotations

import hashlib
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
from sabueso.mappings.brenda import URL, response_query, validate_enzyme_class
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    rows = validate_enzyme_class(result["record"], query["identifier"])
    out = {
        "outcome": "received" if rows else "not_found",
        "count": len(rows),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "native_selected_fields_do_not_state_prototype_dataset_or_EC_record_revision",
        },
        "response_identity": {
            "basis": "native_SPARQL_EC_class_response",
            "hash": digest(canonical_json(result["record"])),
        },
        "coverage": "all_received_solutions_for_one_exact_EC_four_fields; kinetics_and_proteins_unqueried",
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineBrendaClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("BRENDA", "enzyme_class", summarize=_summarize)
    def enzyme_class(self, identifier):
        response_query(identifier)
        url = (
            URL
            + "?"
            + urlencode(
                {"query": response_query(identifier)["sparql"], "format": "json"}
            )
        )
        retrieval = stamp("BRENDA")
        try:
            with urlopen(url, timeout=self.timeout, expect_json=True) as response:
                raw = response.read()
                payload = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, UnicodeError, ValueError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"BRENDA EC-class access failed: {error}") from error
        validate_enzyme_class(payload, identifier)
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotBrendaClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition("BRENDA", "enzyme_class", fixture=True, summarize=_summarize)
    def enzyme_class(self, identifier):
        query = response_query(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"BRENDA snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "BRENDA"
            or result["kind"] != "enzyme_class"
            or result["query"] != query
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied BRENDA source/kind/query/revision differ from request."
            )
        validate_enzyme_class(result["record"], identifier)
        return result


class FixtureBrendaClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "brenda"
        self.retrieved_at = retrieved_at

    def enzyme_class(self, identifier):
        return SnapshotBrendaClient(
            self.directory / f"enzyme_class__{identifier}.json",
            source_metadata={
                "source": "BRENDA",
                "kind": "enzyme_class",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        ).enzyme_class(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_enzyme_class(identifier, client=None, skip_digestion=False):
    """Receive one exact EC class's label, systematic name and description.

    Native RDF terms and missing OPTIONAL bindings survive. Empty solutions
    are received no-match, not absent activity. Prototype revision is unknown;
    no kinetics, protein assignment, linked acquisition or card enrichment.
    """
    query = response_query(identifier)
    result = online(client, OnlineBrendaClient).enzyme_class(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
        or any(
            k in result and result[k] != value
            for k, value in {
                "source": "BRENDA",
                "kind": "enzyme_class",
                "query": query,
            }.items()
        )
    ):
        raise ConnectorError(
            "BRENDA client response/query/revision/cut is unsupported."
        )
    validate_enzyme_class(result.get("record"), identifier)
    envelope = source_record(
        "BRENDA",
        "enzyme_class",
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
