"""Read one native human OmniPath interaction query with original aggregate support."""

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
from sabueso.mappings.omnipath import accession, response_query, validate_interactions
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://omnipathdb.org/interactions?"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    rows = validate_interactions(result["record"], query["identifier"])
    out = {
        "outcome": "received" if rows else "empty",
        "count": len(rows),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "dataset_interaction_and_support_revisions_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_interaction_array",
            "hash": digest(canonical_json(rows)),
        },
        "native_result_declaration": "received_array"
        if rows
        else "received_empty_array",
        "coverage": "all_received_rows; no_client_limit; no_native_total_or_database_completeness_claim",
        "query_scope": response_query(query["identifier"]),
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


class OnlineOmniPathClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("OmniPath", "interactions", summarize=_summarize)
    def interactions(self, identifier):
        query = response_query(identifier)
        retrieval = stamp("OmniPath")
        try:
            with urlopen(
                URL + urlencode(query), timeout=self.timeout, expect_json=True
            ) as response:
                raw = response.read()
                payload = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"OmniPath access failed: {error}") from error
        validate_interactions(payload, query["partners"])
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotOmniPathClient:
    """Read original JSON/gzip with declared exact query and optional byte hash."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition("OmniPath", "interactions", fixture=True, summarize=_summarize)
    def interactions(self, identifier):
        query = response_query(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied OmniPath snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "OmniPath"
            or result["kind"] != "interactions"
            or canonical_json(result["query"]) != canonical_json(query)
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied OmniPath source/kind/query/revision differ from the request."
            )
        validate_interactions(result["record"], query["partners"])
        return result


class FixtureOmniPathClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "omnipath"
        self.retrieved_at = retrieved_at

    def interactions(self, identifier):
        identifier = accession(identifier)
        return SnapshotOmniPathClient(
            self.directory / f"interactions__{identifier}.json",
            source_metadata={
                "source": "OmniPath",
                "kind": "interactions",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        ).interactions(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_interactions(identifier, client=None, skip_digestion=False):
    """Receive all returned human OmniPath rows for one exact UniProt partner.

    The explicit academic licence filter selects access scope, not reuse rights.
    Returned resource/reference annotations remain aggregate native support;
    licence and dataset filters do not reconstruct strict source-only annotations.
    Both effects and consensus survive. Revisions and independent totals are unknown.
    No mouse/rat orthology translation, identity merge, reference lookup, binary
    binding inference, analysis job or automatic card enrichment is performed.
    """
    identifier = accession(identifier)
    result = online(client, OnlineOmniPathClient).interactions(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
        or ("source" in result and result["source"] != "OmniPath")
        or ("kind" in result and result["kind"] != "interactions")
        or (
            "query" in result
            and canonical_json(result["query"])
            != canonical_json(response_query(identifier))
        )
    ):
        raise ConnectorError("OmniPath client response/revision/cut is unsupported.")
    record = validate_interactions(result.get("record"), identifier)
    envelope = source_record(
        "OmniPath",
        "interactions",
        response_query(identifier),
        result.get("retrieved_at"),
        None,
        deepcopy(record),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    if "download_sha256" in result:
        envelope["download_sha256"] = result["download_sha256"]
    return envelope
