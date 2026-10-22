"""Read existing SWISS-MODEL Repository metadata, without coordinates or jobs."""

from __future__ import annotations

from collections import Counter
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
from sabueso.mappings.swissmodel import accession, validate_metadata
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

SOURCE = "SWISS-MODEL Repository"
URL = "https://swissmodel.expasy.org/repository/uniprot/"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    payload = result["record"]
    rows = payload["result"]["structures"]
    out = {
        "outcome": "received" if rows else "empty",
        "count": len(rows),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "metadata_and_source_sequence_revisions_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_metadata",
            "hash": digest(canonical_json(payload)),
        },
        "native_api_version": payload["api_version"],
        "native_query_date": payload["query_date"],
        "provider_counts": dict(Counter(row["provider"] for row in rows)),
        "completeness_scope": "full_received_structure_array; no_native_total_or_current_database_coverage_claim",
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineSwissModelClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition(SOURCE, "metadata", summarize=_summarize)
    def metadata(self, identifier):
        identifier = accession(identifier)
        retrieval = stamp(SOURCE)
        try:
            with urlopen(
                URL + identifier + ".json", timeout=self.timeout, expect_json=True
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"SWISS-MODEL metadata access failed: {error}"
            ) from error
        validate_metadata(payload, identifier)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}


class FixtureSwissModelClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "swissmodel"
        self.retrieved_at = retrieved_at

    @acquisition(SOURCE, "metadata", fixture=True, summarize=_summarize)
    def metadata(self, identifier):
        identifier = accession(identifier)
        path = self.directory / f"metadata__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(
                f"SWISS-MODEL metadata fixture is unavailable: {path}"
            )
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": SOURCE,
                "kind": "metadata",
                "query": {"accession": identifier},
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_metadata(result["record"], identifier)
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_metadata(identifier, client=None, skip_digestion=False):
    """Get the full unfiltered metadata for one base UniProt accession.

    Preserve all native providers, target sequence and chain alignments. No model
    is selected, rebuilt or downloaded, and no current UniProt sequence is queried.
    Native returned URLs may change; their presence is not coordinate acquisition.
    """
    identifier = accession(identifier)
    result = online(client, OnlineSwissModelClient).metadata(identifier)
    if not isinstance(result, dict) or result.get("version") is not None:
        raise ConnectorError("SWISS-MODEL client response/revision is unsupported.")
    payload = validate_metadata(result.get("record"), identifier)
    envelope = source_record(
        SOURCE,
        "metadata",
        {"accession": identifier},
        result.get("retrieved_at"),
        None,
        deepcopy(payload),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
