"""Read the native Human Protein Atlas JSON subset for one explicit human gene."""

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
from sabueso.mappings.hpa import CATEGORIES, gene_id, validate_profile
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

SOURCE = "Human Protein Atlas"
URL = "https://www.proteinatlas.org/"


def _query(identifier):
    return {
        "gene_id": identifier,
        "format": "single_gene_json_subset",
    }


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    record = validate_profile(result["record"], query["identifier"])
    out = {
        "outcome": "received",
        "count": 1,
        "categorical_field_count": sum(k in record for k in CATEGORIES),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "native_json_subset_does_not_state_dataset_or_record_revision",
        },
        "response_identity": {
            "basis": "decoded_native_single_gene_json_subset",
            "hash": digest(canonical_json(record)),
        },
        "coverage": "single_gene_json_subset; not_full_expression_or_assay_data",
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineHpaClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("Human Protein Atlas", "gene_profile", summarize=_summarize)
    def gene_profile(self, identifier):
        identifier = gene_id(identifier)
        retrieval = stamp("Human Protein Atlas")
        try:
            with urlopen(
                URL + identifier + ".json",
                timeout=self.timeout,
                expect_json=True,
            ) as response:
                rows = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"Human Protein Atlas access failed: {error}"
            ) from error
        validate_profile(rows, identifier)
        return {"record": rows, "retrieved_at": retrieval.value, "version": None}


class SnapshotHpaClient:
    """Use native supplied JSON/gzip with exact source/query binding and optional SHA."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition(
        "Human Protein Atlas", "gene_profile", fixture=True, summarize=_summarize
    )
    def gene_profile(self, identifier):
        identifier = gene_id(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied Human Protein Atlas snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "Human Protein Atlas"
            or result["kind"] != "gene_profile"
            or result["query"] != _query(identifier)
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied Human Protein Atlas source/kind/query/revision differ from the request."
            )
        validate_profile(result["record"], identifier)
        return result


class FixtureHpaClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "hpa"
        self.retrieved_at = retrieved_at

    @acquisition(
        "Human Protein Atlas", "gene_profile", fixture=True, summarize=_summarize
    )
    def gene_profile(self, identifier):
        identifier = gene_id(identifier)
        path = self.directory / f"profile__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"Human Protein Atlas fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "Human Protein Atlas",
                "kind": "gene_profile",
                "query": _query(identifier),
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_profile(result["record"], identifier)
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_gene_profile(identifier, client=None, skip_digestion=False):
    """Receive HPA's native single-gene JSON subset without discarding fields.

    This route is a search-data summary, not a full tissue/assay export. Dataset,
    gene and sequence revisions are unstated. Categorical mapping keeps RNA and
    protein contexts separate; quantitative projection and card enrichment are
    outside this reader. HPA states CC BY 4.0, with third-party rights retained.
    """
    identifier = gene_id(identifier)
    result = online(client, OnlineHpaClient).gene_profile(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
    ):
        raise ConnectorError(
            "Human Protein Atlas client response/revision/cut is unsupported."
        )
    rows = validate_profile(result.get("record"), identifier)
    envelope = source_record(
        "Human Protein Atlas",
        "gene_profile",
        _query(identifier),
        result.get("retrieved_at"),
        None,
        deepcopy(rows),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
