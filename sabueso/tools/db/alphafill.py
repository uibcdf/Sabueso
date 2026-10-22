"""Explicit precomputed AlphaFill metadata, through the shared source transport."""

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
from sabueso.mappings.alphafill import accession, validate_metadata
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.db._snapshot import BoundSourceSnapshot
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://alphafill.eu/v1/aff/"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    payload = result["record"]
    out = {
        "outcome": "received",
        "count": 1,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "metadata_record_revision_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_metadata",
            "hash": digest(canonical_json(payload)),
        },
        "model_id": payload["id"],
        "hit_count": len(payload["hits"] or []),
        "transplant_count": sum(len(h["transplants"]) for h in payload["hits"] or []),
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineAlphaFillClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("AlphaFill", "metadata", summarize=_summarize)
    def metadata(self, identifier):
        identifier = accession(identifier)
        retrieval = stamp("AlphaFill")
        try:
            with urlopen(
                URL + identifier + "/json", timeout=self.timeout, expect_json=True
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"AlphaFill metadata access failed: {error}"
            ) from error
        validate_metadata(payload, identifier)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}


class SnapshotAlphaFillClient(BoundSourceSnapshot):
    """Read caller-bound original native JSON or JSON/gzip, retaining declared support."""

    @acquisition("AlphaFill", "metadata", fixture=True, summarize=_summarize)
    def metadata(self, identifier):
        identifier = accession(identifier)
        result = self.read(
            "AlphaFill", "metadata", {"accession": identifier}, file_format="json"
        )
        validate_metadata(result["record"], identifier)
        return result


class FixtureAlphaFillClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "alphafill"
        self.retrieved_at = retrieved_at

    @acquisition("AlphaFill", "metadata", fixture=True, summarize=_summarize)
    def metadata(self, identifier):
        identifier = accession(identifier)
        path = self.directory / f"metadata__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"AlphaFill metadata fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "AlphaFill",
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
    """Read a precomputed metadata record; download no coordinates and submit no job.

    The returned fragment/model ID is explicit. Run software/date are separate
    context, not the unknown metadata revision or current UniProt equivalence.
    """
    identifier = accession(identifier)
    result = online(client, OnlineAlphaFillClient).metadata(identifier)
    if not isinstance(result, dict) or result.get("version") is not None:
        raise ConnectorError("AlphaFill client response/revision is unsupported.")
    payload = validate_metadata(result.get("record"), identifier)
    envelope = source_record(
        "AlphaFill",
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
