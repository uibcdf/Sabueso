"""Read AmyPro's native JSON export for one explicitly selected AmyPro entry ID."""

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
from sabueso.mappings.amypro import entry_id, select_entry
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://amypro.net/data/amypro.json"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    selected = select_entry(result["record"], query["identifier"])
    out = {
        "outcome": "received" if selected is not None else "not_found",
        "count": int(selected is not None),
        "received_export_count": len(result["record"]),
        "selected_region_count": len(selected["regions"])
        if selected is not None
        else None,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "export_record_and_sequence_revisions_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_export",
            "hash": digest(canonical_json(result["record"])),
        },
        "completeness_scope": "full_received_export; no_native_total_or_current_database_coverage_claim",
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineAmyProClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("AmyPro", "entry", summarize=_summarize)
    def entry(self, identifier):
        identifier = entry_id(identifier)
        retrieval = stamp("AmyPro")
        try:
            with urlopen(URL, timeout=self.timeout, expect_json=True) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"AmyPro export access failed: {error}") from error
        select_entry(payload, identifier)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}


class FixtureAmyProClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "amypro"
        self.retrieved_at = retrieved_at

    @acquisition("AmyPro", "entry", fixture=True, summarize=_summarize)
    def entry(self, identifier):
        identifier = entry_id(identifier)
        path = self.directory / "entries.json"
        if not path.is_file():
            raise missing_fixture(f"AmyPro export fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "AmyPro",
                "kind": "entry",
                "query": {"entry_id": identifier},
                "retrieved_at": self.retrieved_at,
            },
        )
        select_entry(result["record"], identifier)
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_entry(identifier, client=None, skip_digestion=False):
    """Receive the whole public JSON export and select one exact AmyPro ID.

    ``record`` retains the full received native array, validated before selection.
    Missing selection means not listed in this export, not biological absence.
    No parent-UniProt query, sequence search, individual malformed JSON download,
    publication lookup, coordinate access or automatic card enrichment occurs.
    """
    identifier = entry_id(identifier)
    result = online(client, OnlineAmyProClient).entry(identifier)
    if not isinstance(result, dict) or result.get("version") is not None:
        raise ConnectorError("AmyPro client response/revision is unsupported.")
    payload = result.get("record")
    select_entry(payload, identifier)
    envelope = source_record(
        "AmyPro",
        "entry",
        {"entry_id": identifier},
        result.get("retrieved_at"),
        None,
        deepcopy(payload),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
