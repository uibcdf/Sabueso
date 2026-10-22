"""Read one existing ECOD experimental domain through the public JSON API."""

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
from sabueso.mappings.ecod import URL, response_query, uid_id, validate_domain
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    record = validate_domain(result["record"], query["identifier"])
    out = {
        "outcome": "received",
        "count": 1,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "domain_classification_and_sequence_revisions_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_experimental_domain",
            "hash": digest(canonical_json(record)),
        },
        "coverage": "one_explicit_UID; other_domains_and_predicted_origins_unqueried",
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


class OnlineECODClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("ECOD", "domain", summarize=_summarize)
    def domain(self, identifier):
        identifier = uid_id(identifier)
        retrieval = stamp("ECOD")
        try:
            with urlopen(
                URL + identifier, timeout=self.timeout, expect_json=True
            ) as response:
                raw = response.read()
                payload = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"ECOD domain access failed: {error}") from error
        validate_domain(payload, identifier)
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotECODClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path, self.source_metadata = path, deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition("ECOD", "domain", fixture=True, summarize=_summarize)
    def domain(self, identifier):
        query = response_query(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied ECOD snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "ECOD"
            or result["kind"] != "domain"
            or result["query"] != query
            or result.get("version") is not None
            or type(result["query"].get("uid")) is not int
        ):
            raise ConnectorError(
                "Supplied ECOD source/kind/query/revision differ from the request."
            )
        validate_domain(result["record"], identifier)
        return result


class FixtureECODClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "ecod"
        self.retrieved_at = retrieved_at

    def domain(self, identifier):
        identifier = uid_id(identifier)
        return SnapshotECODClient(
            self.directory / f"domain__{identifier}.json",
            source_metadata={
                "source": "ECOD",
                "kind": "domain",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        ).domain(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_domain(identifier, client=None, skip_digestion=False):
    """Read one explicit numeric UID, qualifying only native experimental domains.

    Source range/chain, id/name classification and false/manual flags survive.
    No residue placement, protein merge, predicted-domain transfer, search, file
    acquisition, computation or automatic card enrichment is performed. HTTP is
    the explicitly qualified public route; there is no silent protocol fallback.
    """
    identifier = uid_id(identifier)
    query = response_query(identifier)
    result = online(client, OnlineECODClient).domain(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or ("source" in result and result["source"] != "ECOD")
        or ("kind" in result and result["kind"] != "domain")
        or (
            "query" in result
            and (
                result["query"] != query or type(result["query"].get("uid")) is not int
            )
        )
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError("ECOD client response/query/revision/cut is unsupported.")
    record = validate_domain(result.get("record"), identifier)
    envelope = source_record(
        "ECOD",
        "domain",
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
