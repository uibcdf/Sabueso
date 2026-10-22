"""Explicit native GlyGen protein access with complete modification tables."""

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
from sabueso.mappings.glygen import TABLES, accession, validate_protein
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.db._snapshot import BoundSourceSnapshot
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://api.glygen.org/protein/detail/"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    out = {
        "outcome": "received",
        "count": 1,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "protein_record_revision_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_protein",
            "hash": digest(canonical_json(result["record"])),
        },
        "annotation_counts": {t: len(result["record"][t]) for t in TABLES},
        "completeness_scope": "native glycosylation/phosphorylation totals; other sections unqualified",
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineGlyGenClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("GlyGen", "protein", summarize=_summarize)
    def protein(self, identifier):
        identifier = accession(identifier)
        retrieval = stamp("GlyGen")
        try:
            with urlopen(
                URL + identifier + "/", timeout=self.timeout, expect_json=True
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"GlyGen protein access failed: {error}") from error
        validate_protein(payload, identifier)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}


class SnapshotGlyGenClient(BoundSourceSnapshot):
    """Read one caller-bound native protein JSON/gzip with complete modification tables."""

    @acquisition("GlyGen", "protein", fixture=True, summarize=_summarize)
    def protein(self, identifier):
        identifier = accession(identifier)
        result = self.read(
            "GlyGen", "protein", {"accession": identifier}, file_format="json"
        )
        validate_protein(result["record"], identifier)
        return result


class FixtureGlyGenClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "glygen"
        self.retrieved_at = retrieved_at

    @acquisition("GlyGen", "protein", fixture=True, summarize=_summarize)
    def protein(self, identifier):
        identifier = accession(identifier)
        path = self.directory / f"protein__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"GlyGen protein fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "GlyGen",
                "kind": "protein",
                "query": {"accession": identifier},
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_protein(result["record"], identifier)
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_protein(identifier, client=None, skip_digestion=False):
    """Read a native protein record, without requesting paginated modification tables.

    Both table totals must equal their received rows. Raw unrelated sections remain
    native data; their completeness and direct access to referenced providers are
    not inferred. Map modifications separately; no automatic card enrichment.
    """
    identifier = accession(identifier)
    result = online(client, OnlineGlyGenClient).protein(identifier)
    if not isinstance(result, dict) or result.get("version") is not None:
        raise ConnectorError("GlyGen client response/revision is unsupported.")
    payload = validate_protein(result.get("record"), identifier)
    envelope = source_record(
        "GlyGen",
        "protein",
        {"accession": identifier},
        result.get("retrieved_at"),
        None,
        deepcopy(payload),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
