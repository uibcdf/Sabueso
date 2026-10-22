"""Explicit fixed-route CATH domain summaries, including bound supplied snapshots."""

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
from sabueso.mappings.cath import domain_id, release_id, validate_summary
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://www.cathdb.info/version/"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    data = validate_summary(result["record"], query["identifier"])
    out = {
        "outcome": "received",
        "count": 1,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "record_and_sequence_revisions_not_stated",
        },
        "requested_release": query["release"],
        "release_basis": "requested_route; response_does_not_state_release",
        "response_identity": {
            "basis": "decoded_native_summary",
            "hash": digest(canonical_json(result["record"])),
        },
        "residue_count": len(data["residues"]),
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineCathClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("CATH", "domain_summary", summarize=_summarize)
    def domain_summary(self, identifier, release):
        identifier, release = domain_id(identifier), release_id(release)
        retrieval = stamp("CATH")
        try:
            with urlopen(
                URL
                + release
                + "/api/rest/domain_summary/"
                + identifier
                + "?content-type=application/json",
                timeout=self.timeout,
                expect_json=True,
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"CATH domain access failed: {error}") from error
        validate_summary(payload, identifier)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}


class SnapshotCathClient:
    """Read one supplied native JSON/gzip file with exact declared source/query binding."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition("CATH", "domain_summary", fixture=True, summarize=_summarize)
    def domain_summary(self, identifier, release):
        identifier, release = domain_id(identifier), release_id(release)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied CATH snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "CATH"
            or result["kind"] != "domain_summary"
            or result["query"] != {"domain_id": identifier, "release": release}
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied CATH source/kind/query/revision differ from this request."
            )
        validate_summary(result["record"], identifier)
        return result


class FixtureCathClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "cath"
        self.retrieved_at = retrieved_at

    @acquisition("CATH", "domain_summary", fixture=True, summarize=_summarize)
    def domain_summary(self, identifier, release):
        identifier, release = domain_id(identifier), release_id(release)
        path = self.directory / release / f"domain_summary__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"CATH domain fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "CATH",
                "kind": "domain_summary",
                "query": {"domain_id": identifier, "release": release},
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_summary(result["record"], identifier)
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_domain_summary(identifier, release, client=None, skip_digestion=False):
    """Read one explicit domain on a fixed release route, retaining native context.

    The route selector is a request declaration, not an observed record/sequence
    revision. No search, coordinate download, sequence scan, linked annotation
    fetch, protein card enrichment or canonical numbering projection occurs.
    """
    identifier, release = domain_id(identifier), release_id(release)
    result = online(client, OnlineCathClient).domain_summary(identifier, release)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
    ):
        raise ConnectorError("CATH client response/revision/cut is unsupported.")
    payload = result.get("record")
    validate_summary(payload, identifier)
    envelope = source_record(
        "CATH",
        "domain_summary",
        {"domain_id": identifier, "release": release},
        result.get("retrieved_at"),
        None,
        deepcopy(payload),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
