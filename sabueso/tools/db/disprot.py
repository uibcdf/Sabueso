"""Explicit DisProt search by native UniProt accession, with supplied-file intake."""

from __future__ import annotations

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
from sabueso.mappings.disprot import accession, validate_records
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://disprot.org/api/search"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    payload = result["record"]
    receipt = result.get("snapshot_receipt")
    out = {
        "outcome": "received" if payload["data"] else "empty",
        "count": len(payload["data"]),
        "retrieved_at": result["retrieved_at"],
        "source_version": {
            "value": result.get("version"),
            "basis": "caller_declaration" if receipt else "not_stated_in_search",
        },
        "response_identity": {
            "basis": "decoded_native_search",
            "hash": digest(canonical_json(payload)),
        },
        "region_scope": [
            {
                "disprot_id": r["disprot_id"],
                "returned": len(r["regions"]),
                "stated": r["regions_counter"],
            }
            for r in payload["data"]
        ],
        "native_references": [
            {key: r[key] for key in ("reference_source", "reference_id") if key in r}
            for entry in payload["data"]
            for r in entry["regions"]
        ],
    }
    if receipt:
        out.update(access="supplied_file", snapshot_receipt=receipt)
    return out


class OnlineDisProtClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("DisProt", "records", summarize=_summarize)
    def records(self, identifier):
        identifier = accession(identifier)
        retrieval = stamp("DisProt")
        try:
            with urlopen(
                URL + "?" + urlencode({"acc": identifier}),
                timeout=self.timeout,
                expect_json=True,
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            # A missing API route cannot prove that a protein has no annotation.
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"DisProt search failed: {error}") from error
        validate_records(payload, identifier)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}


class SnapshotDisProtClient:
    """Use one supplied native search file; validate its exact source/query binding."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = source_metadata
        self.expected_sha256 = expected_sha256

    @acquisition("DisProt", "records", fixture=True, summarize=_summarize)
    def records(self, identifier):
        identifier = accession(identifier)
        result = load_source_snapshot(
            self.path,
            source_metadata=self.source_metadata,
            expected_sha256=self.expected_sha256,
        )
        if (
            result["source"] != "DisProt"
            or result["kind"] != "records"
            or result["query"] != {"accession": identifier}
        ):
            raise ConnectorError(
                "Supplied DisProt source/kind/query do not match this request."
            )
        validate_records(result["record"], identifier)
        return result


class FixtureDisProtClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at

    @acquisition("DisProt", "records", fixture=True, summarize=_summarize)
    def records(self, identifier):
        identifier = accession(identifier)
        path = self.directory / "disprot" / f"records__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"DisProt fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "DisProt",
                "kind": "records",
                "query": {"accession": identifier},
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_records(result["record"], identifier)
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_records(identifier, client=None, skip_digestion=False):
    """Return raw default DisProt annotations, retaining explicit region-subset scope."""
    identifier = accession(identifier)
    result = online(client, OnlineDisProtClient).records(identifier)
    envelope = source_record(
        "DisProt",
        "records",
        {"accession": identifier},
        result.get("retrieved_at"),
        result.get("version"),
        result["record"],
        truncated=any(
            r["regions_counter"] > len(r["regions"]) for r in result["record"]["data"]
        ),
    )
    if result.get("snapshot_receipt") is not None:
        envelope["snapshot_receipt"] = result["snapshot_receipt"]
    return envelope
