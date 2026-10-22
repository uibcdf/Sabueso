"""Read the complete native EMA orphan-designation pages JSON export."""

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
from sabueso.mappings.ema_orphan import designation_id, response_query, validate_export
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

SOURCE = "EMA Orphan Designations"
URL = "https://www.ema.europa.eu/en/documents/report/medicines-output-orphan_designations-json-report_en.json"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    record = validate_export(result["record"])
    matches = [
        row
        for row in record["data"]
        if row["eu_designation_number"] == query["identifier"]
    ]
    out = {
        "outcome": "received" if matches else "not_found",
        "count": len(matches),
        "received_export_rows": len(record["data"]),
        "native_export_metadata": deepcopy(record["meta"]),
        "native_result_declaration": "matched_native_EU_number"
        if matches
        else "not_listed_in_received_export",
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "native_export_does_not_state_dataset_or_designation_revision",
        },
        "response_identity": {
            "basis": "decoded_native_orphan_designations_export",
            "hash": digest(canonical_json(record)),
        },
        "coverage": "all_received_rows_validated; native_total_matches_received_rows; no_independent_registry_total",
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


class OnlineEmaOrphanClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("EMA Orphan Designations", "designations", summarize=_summarize)
    def designations(self, identifier):
        identifier = designation_id(identifier)
        retrieval = stamp("EMA Orphan Designations")
        try:
            with urlopen(
                URL,
                timeout=self.timeout,
                expect_json=True,
            ) as response:
                raw = response.read()
                rows = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"EMA Orphan Designations access failed: {error}"
            ) from error
        validate_export(rows)
        return {
            "record": rows,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotEmaOrphanClient:
    """Use native supplied JSON/gzip with exact source/query binding and optional SHA."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition(
        "EMA Orphan Designations", "designations", fixture=True, summarize=_summarize
    )
    def designations(self, identifier):
        identifier = designation_id(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied EMA Orphan Designations snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "EMA Orphan Designations"
            or result["kind"] != "designations"
            or result["query"] != response_query(identifier)
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied EMA Orphan Designations source/kind/query/revision differ from the request."
            )
        validate_export(result["record"])
        return result


class FixtureEmaOrphanClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "ema_orphan"
        self.retrieved_at = retrieved_at

    @acquisition(
        "EMA Orphan Designations", "designations", fixture=True, summarize=_summarize
    )
    def designations(self, identifier):
        identifier = designation_id(identifier)
        path = self.directory / "designations.json"
        if not path.is_file():
            raise missing_fixture(
                f"EMA Orphan Designations fixture is unavailable: {path}"
            )
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "EMA Orphan Designations",
                "kind": "designations",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_export(result["record"])
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_designations(identifier, client=None, skip_digestion=False):
    """Receive a full native EMA orphan export for exact local EU-number selection.

    All rows and declared totals are validated before selecting source pages.
    The original export, generation timestamp, date/status/product literals and
    independent repeated occurrences remain available. Generation and publication
    times are separate from acquisition time and unknown scientific revisions.
    This does not infer marketing authorisation, modality, efficacy, molecule or
    protein identity, acquire linked pages or automatically enrich cards.
    EMA-owned content may be reproduced with EMA acknowledgement; third-party
    material and publication rights remain separate.
    """
    identifier = designation_id(identifier)
    result = online(client, OnlineEmaOrphanClient).designations(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
    ):
        raise ConnectorError("EMA orphan client response/revision/cut is unsupported.")
    rows = validate_export(result.get("record"))
    envelope = source_record(
        "EMA Orphan Designations",
        "designations",
        response_query(identifier),
        result.get("retrieved_at"),
        None,
        deepcopy(rows),
        truncated=False,
    )
    for key in ("snapshot_receipt", "download_sha256"):
        if key in result:
            envelope[key] = deepcopy(result[key])
    return envelope
