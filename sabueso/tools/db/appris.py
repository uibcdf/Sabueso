"""Read the native default APPRIS exporter for one explicit human Ensembl gene."""

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
from sabueso.mappings.appris import gene_id, validate_annotations
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://apprisws.bioinfo.cnio.es/rest/exporter/id/homo_sapiens/"


def _query(identifier):
    return {
        "gene_id": identifier,
        "species": "homo_sapiens",
        "filters": "provider_default",
    }


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    rows = validate_annotations(result["record"], query["identifier"])
    out = {
        "outcome": "received",
        "count": len(rows),
        "transcript_reference_count": len({r["transcript_id"] for r in rows}),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "native_exporter_does_not_state_dataset_or_record_revision",
        },
        "response_identity": {
            "basis": "decoded_native_exporter_rows",
            "hash": digest(canonical_json(rows)),
        },
        "coverage": "provider_default_received_rows; no_native_total_or_assembly_revision",
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineApprisClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("APPRIS", "gene_annotations", summarize=_summarize)
    def gene_annotations(self, identifier):
        identifier = gene_id(identifier)
        retrieval = stamp("APPRIS")
        try:
            with urlopen(
                URL + identifier + "?format=json",
                timeout=self.timeout,
                expect_json=True,
            ) as response:
                rows = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"APPRIS access failed: {error}") from error
        validate_annotations(rows, identifier)
        return {"record": rows, "retrieved_at": retrieval.value, "version": None}


class SnapshotApprisClient:
    """Use native supplied JSON/gzip with exact source/query binding and optional SHA."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition("APPRIS", "gene_annotations", fixture=True, summarize=_summarize)
    def gene_annotations(self, identifier):
        identifier = gene_id(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied APPRIS snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "APPRIS"
            or result["kind"] != "gene_annotations"
            or result["query"] != _query(identifier)
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied APPRIS source/kind/query/revision differ from the request."
            )
        validate_annotations(result["record"], identifier)
        return result


class FixtureApprisClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "appris"
        self.retrieved_at = retrieved_at

    @acquisition("APPRIS", "gene_annotations", fixture=True, summarize=_summarize)
    def gene_annotations(self, identifier):
        identifier = gene_id(identifier)
        path = self.directory / f"annotations__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"APPRIS fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "APPRIS",
                "kind": "gene_annotations",
                "query": _query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_annotations(result["record"], identifier)
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_gene_annotations(identifier, client=None, skip_digestion=False):
    """Receive all default native rows for one human ENSG gene without collapsing them.

    Assembly/dataset/record/sequence revisions remain unstated. This exact route
    adds no search, filter, principal-isoform choice, linked sequence/publication
    acquisition, genomic-to-protein projection, calculation or card enrichment.
    APPRIS's stated CC BY-NC-SA 4.0 obligations accompany source assertions.
    """
    identifier = gene_id(identifier)
    result = online(client, OnlineApprisClient).gene_annotations(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
    ):
        raise ConnectorError("APPRIS client response/revision/cut is unsupported.")
    rows = validate_annotations(result.get("record"), identifier)
    envelope = source_record(
        "APPRIS",
        "gene_annotations",
        _query(identifier),
        result.get("retrieved_at"),
        None,
        deepcopy(rows),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
