"""Read one explicit public PRIDE Archive project; source identity stays project-scoped."""

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
from sabueso.mappings.pride import project_id, validate_project
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://www.ebi.ac.uk/pride/ws/archive/v2/projects/"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    record = validate_project(result["record"], query["identifier"])
    out = {
        "outcome": "received",
        "count": 1,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "project_and_sequence_revisions_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_project_metadata",
            "hash": digest(canonical_json(record)),
        },
        "native_license": record.get("license"),
        "coverage": "one_project_metadata_response; not_peptide_protein_file_or_archive_coverage",
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


class OnlinePrideClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("PRIDE", "project", summarize=_summarize)
    def project(self, identifier):
        identifier = project_id(identifier)
        retrieval = stamp("PRIDE")
        try:
            with urlopen(
                URL + identifier, timeout=self.timeout, expect_json=True
            ) as response:
                raw = response.read()
                payload = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"PRIDE Archive access failed: {error}") from error
        validate_project(payload, identifier)
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotPrideClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path, self.source_metadata = path, deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition("PRIDE", "project", fixture=True, summarize=_summarize)
    def project(self, identifier):
        identifier = project_id(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied PRIDE snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "PRIDE"
            or result["kind"] != "project"
            or result["query"] != {"project_accession": identifier}
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied PRIDE source/kind/query/revision differ from the request."
            )
        validate_project(result["record"], identifier)
        return result


class FixturePrideClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "pride"
        self.retrieved_at = retrieved_at

    def project(self, identifier):
        identifier = project_id(identifier)
        return SnapshotPrideClient(
            self.directory / f"project__{identifier}.json",
            source_metadata={
                "source": "PRIDE",
                "kind": "project",
                "query": {"project_accession": identifier},
                "retrieved_at": self.retrieved_at,
            },
        ).project(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_project(identifier, client=None, skip_digestion=False):
    """Receive native dataset metadata for one exact public PXD project accession.

    Native per-project licence, protocols, CV terms, dates and publication pointers
    survive. No name search, linked file/peptide/protein download, sequence placement,
    result interpretation, project analysis or automatic card enrichment is added.
    Failed/not-available HTTP access is not converted into an empty project.
    """
    identifier = project_id(identifier)
    query = {"project_accession": identifier}
    result = online(client, OnlinePrideClient).project(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
        or ("source" in result and result["source"] != "PRIDE")
        or ("kind" in result and result["kind"] != "project")
        or ("query" in result and result["query"] != query)
    ):
        raise ConnectorError("PRIDE client response/revision/query/cut is unsupported.")
    record = validate_project(result.get("record"), identifier)
    envelope = source_record(
        "PRIDE",
        "project",
        query,
        result.get("retrieved_at"),
        None,
        deepcopy(record),
        truncated=False,
    )
    for k in ("snapshot_receipt", "download_sha256"):
        if k in result:
            envelope[k] = deepcopy(result[k])
    return envelope
