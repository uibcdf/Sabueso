"""Read native WikiPathways bulk JSON with exact namespaced cross-reference selection."""

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
from sabueso.mappings.wikipathways import (
    response_query,
    validate_export,
    xref_id,
    xref_matches,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

SOURCE = "WikiPathways"
URL = "https://www.wikipathways.org/json/findPathwaysByXref.json"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    record = validate_export(result["record"])
    count = sum(
        bool(xref_matches(row, query["identifier"])) for row in record["pathwayInfo"]
    )
    out = {
        "outcome": "received" if count else "not_found",
        "count": count,
        "received_export_rows": len(record["pathwayInfo"]),
        "native_result_declaration": "matched_native_xref_tokens"
        if count
        else "not_listed_in_received_export",
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "native_pathway_date_labels_do_not_state_dataset_or_sequence_revision",
        },
        "response_identity": {
            "basis": "decoded_native_findPathwaysByXref_export",
            "hash": digest(canonical_json(record)),
        },
        "coverage": "all_received_rows_validated; no_independent_database_total_or_species_filter",
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


class OnlineWikiPathwaysClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("WikiPathways", "pathway_cross_references", summarize=_summarize)
    def pathway_cross_references(self, identifier):
        identifier = xref_id(identifier)
        retrieval = stamp(SOURCE)
        try:
            with urlopen(URL, timeout=self.timeout, expect_json=True) as response:
                raw = response.read()
                payload = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"WikiPathways access failed: {error}") from error
        validate_export(payload)
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotWikiPathwaysClient:
    """Use original JSON/gzip with exact source/query binding and optional byte SHA."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition(
        "WikiPathways", "pathway_cross_references", fixture=True, summarize=_summarize
    )
    def pathway_cross_references(self, identifier):
        identifier = xref_id(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied WikiPathways snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != SOURCE
            or result["kind"] != "pathway_cross_references"
            or result["query"] != response_query(identifier)
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied WikiPathways source/kind/query/revision differ from the request."
            )
        validate_export(result["record"])
        return result


class FixtureWikiPathwaysClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "wikipathways"
        self.retrieved_at = retrieved_at

    @acquisition(
        "WikiPathways", "pathway_cross_references", fixture=True, summarize=_summarize
    )
    def pathway_cross_references(self, identifier):
        identifier = xref_id(identifier)
        path = self.directory / "findPathwaysByXref.json"
        if not path.is_file():
            raise missing_fixture(f"WikiPathways fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": SOURCE,
                "kind": "pathway_cross_references",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_export(result["record"])
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_pathways_by_xref(identifier, client=None, skip_digestion=False):
    """Receive the native bulk export for exact local namespaced-token selection.

    Supported namespaces are uniprot, ensembl, ncbigene, wikidata, chebi and
    inchikey. All native rows are validated before selection across the seven
    original xref fields. Species, aliases, original field locations and pathway
    date labels survive without identity merging, role/mechanism inference,
    implicit species filters, GPML downloads, searches or automatic card intake.
    WikiPathways content is CC0; preserve source and contributor attribution.
    """
    identifier = xref_id(identifier)
    result = online(client, OnlineWikiPathwaysClient).pathway_cross_references(
        identifier
    )
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
    ):
        raise ConnectorError(
            "WikiPathways client response/revision/cut is unsupported."
        )
    record = validate_export(result.get("record"))
    envelope = source_record(
        SOURCE,
        "pathway_cross_references",
        response_query(identifier),
        result.get("retrieved_at"),
        None,
        deepcopy(record),
        truncated=False,
    )
    for key in ("snapshot_receipt", "download_sha256"):
        if key in result:
            envelope[key] = deepcopy(result[key])
    return envelope
