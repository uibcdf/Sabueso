"""Read one existing MetalPDB site through the public native JSON API."""

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
from sabueso.mappings.metalpdb import URL, response_query, site_id, validate_sites
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    record = validate_sites(result["record"], query["identifier"])
    out = {
        "outcome": "received" if record else "not_found",
        "count": len(record),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "site_structure_and_sequence_revisions_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_site_array",
            "hash": digest(canonical_json(record)),
        },
        "coverage": "one_explicit_site; other_sites_and_database_total_unqueried",
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


class OnlineMetalPDBClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("MetalPDB", "site", summarize=_summarize)
    def site(self, identifier):
        identifier = site_id(identifier)
        retrieval = stamp("MetalPDB")
        try:
            with urlopen(
                URL + identifier, timeout=self.timeout, expect_json=True
            ) as response:
                raw = response.read()
                payload = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"MetalPDB site access failed: {error}") from error
        validate_sites(payload, identifier)
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotMetalPDBClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path, self.source_metadata = path, deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition("MetalPDB", "site", fixture=True, summarize=_summarize)
    def site(self, identifier):
        query = response_query(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied MetalPDB snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "MetalPDB"
            or result["kind"] != "site"
            or result["query"] != query
            or result.get("version") is not None
        ):
            raise ConnectorError(
                "Supplied MetalPDB source/kind/query/revision differ from the request."
            )
        validate_sites(result["record"], identifier)
        return result


class FixtureMetalPDBClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "metalpdb"
        self.retrieved_at = retrieved_at

    def site(self, identifier):
        identifier = site_id(identifier)
        return SnapshotMetalPDBClient(
            self.directory / f"site__{identifier}.json",
            source_metadata={
                "source": "MetalPDB",
                "kind": "site",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        ).site(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_site(identifier, client=None, skip_digestion=False):
    """Read the full native array for one explicitly selected MetalPDB site ID.

    Native site/PDB identity, representative false, geometry, counts, metal and
    original ligand/donor numbering survive. The mapper uses the qualified public
    Coordination Sphere distance unit. No protein merge, canonical placement,
    geometry computation, coordinate/sequence acquisition or card intake occurs.
    Failed/missing access differs from an empty received site query.
    """
    identifier = site_id(identifier)
    query = response_query(identifier)
    result = online(client, OnlineMetalPDBClient).site(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or ("source" in result and result["source"] != "MetalPDB")
        or ("kind" in result and result["kind"] != "site")
        or ("query" in result and (result["query"] != query))
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError(
            "MetalPDB client response/query/revision/cut is unsupported."
        )
    record = validate_sites(result.get("record"), identifier)
    envelope = source_record(
        "MetalPDB",
        "site",
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
