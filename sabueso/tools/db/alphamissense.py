"""Explicit precomputed AlphaMissense annotations discovered through AlphaFold DB."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError

from smonitor import signal

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError
from sabueso.core.source_acquisition import (
    _terminal,
    acquisition,
    capture_acquisitions,
    missing_fixture,
)
from sabueso.mappings.alphamissense import (
    accession,
    decode_csv,
    select_descriptor,
    validate_artifact,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.db.alphafold import (
    FixtureAlphaFoldClient,
    OnlineAlphaFoldClient,
    get_prediction,
)

DEFAULT_LIMIT = 10000


class _DiscoveryBoundary:
    """Validate this consumer's input without changing the AlphaFold public API."""

    def __init__(self, client):
        self.client = client

    def prediction(self, identifier):
        response = self.client.prediction(identifier)
        if (
            not isinstance(response, dict)
            or not isinstance(response.get("record"), list)
            or any(not isinstance(model, dict) for model in response["record"])
        ):
            raise ConnectorError(
                "AlphaMissense discovery must contain native model objects."
            )
        for model in response["record"]:
            version = model.get("latestVersion")
            if version is not None and (
                isinstance(version, bool) or not isinstance(version, int) or version < 1
            ):
                raise ConnectorError(
                    "AlphaMissense discovery model version is malformed."
                )
        return response


def _artifact(raw, descriptor, retrieved_at, limit):
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise ConnectorError("AlphaMissense artifact is not UTF-8 CSV.") from error
    rows, coverage = decode_csv(text, descriptor)
    return {
        "url": descriptor["amAnnotationsUrl"],
        "csv": text,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "retrieved_at": retrieved_at,
        "rows": rows[:limit],
        "total": len(rows),
        "coverage": coverage,
    }


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    out = {
        "outcome": "received" if result["total"] else "empty",
        "count": len(result["rows"]),
        "total": result["total"],
        "total_basis": "parsed_validated_artifact_rows; not_native_header",
        "truncated": result["total"] > len(result["rows"]),
        "coverage": deepcopy(result["coverage"]),
        "retrieved_at": result["retrieved_at"],
        "source_version": {
            "value": None,
            "basis": "not_stated_in_score_artifact; not_AlphaFold_model_version",
        },
        "response_identity": {
            "basis": "original_native_csv_bytes",
            "hash": "sha256:" + result["sha256"],
        },
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineAlphaMissenseClient:
    def __init__(self, timeout=30.0, *, alphafold_client=None):
        self.timeout = timeout
        self.alphafold_client = (
            alphafold_client
            if alphafold_client is not None
            else OnlineAlphaFoldClient(timeout)
        )

    def annotations(self, identifier, limit=DEFAULT_LIMIT):
        identifier = accession(identifier)
        discovery = get_prediction(
            identifier, client=_DiscoveryBoundary(self.alphafold_client)
        )
        descriptor = select_descriptor(discovery, identifier)
        artifact = (
            self._download(identifier, descriptor, limit)
            if descriptor is not None
            else None
        )
        return {"discovery": discovery, "artifact": artifact}

    @acquisition("AlphaMissense", "annotations", summarize=_summarize)
    def _download(self, identifier, descriptor, limit):
        retrieval = stamp("AlphaMissense")
        try:
            with urlopen(
                descriptor["amAnnotationsUrl"], timeout=self.timeout, expect_json=False
            ) as response:
                raw = response.read()
        except (HTTPError, URLError, OSError) as error:
            # A source-declared but unavailable artifact is failed access, not absence.
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(
                f"AlphaMissense artifact download failed: {error}"
            ) from error
        return _artifact(raw, descriptor, retrieval.value, limit)


class FixtureAlphaMissenseClient(OnlineAlphaMissenseClient):
    def __init__(
        self, directory="temp_data", retrieved_at=None, *, alphafold_client=None
    ):
        self.directory = Path(directory) / "alphamissense"
        self.retrieved_at = retrieved_at
        self.alphafold_client = (
            alphafold_client
            if alphafold_client is not None
            else FixtureAlphaFoldClient(self.directory, retrieved_at=retrieved_at)
        )

    @acquisition("AlphaMissense", "annotations", fixture=True, summarize=_summarize)
    def _download(self, identifier, descriptor, limit):
        path = self.directory / f"AF-{identifier}-F1-aa-substitutions.csv"
        if not path.is_file():
            raise missing_fixture(
                f"AlphaMissense artifact fixture is unavailable: {path}"
            )
        try:
            result = _artifact(path.read_bytes(), descriptor, self.retrieved_at, limit)
        except OSError as error:
            raise ConnectorError(
                f"AlphaMissense supplied file could not be read: {error}"
            ) from error
        result["snapshot_receipt"] = {
            "access": "supplied_file",
            "path": str(path.resolve()),
            "document_sha256": result["sha256"],
            "file_format": "csv",
            "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source_metadata_basis": "fixture_client_declaration",
            "source_access_observed": False,
        }
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_annotations(identifier, limit=DEFAULT_LIMIT, client=None, skip_digestion=False):
    """Get precomputed canonical human substitutions, with exact source scope.

    Validate the complete source artifact before capping returned rows. Discovery
    and score downloads have separate acquisition records. No artifact declaration
    is ``not_stated`` and causes no score download; missing files/routes are failures.
    AlphaFold model versions never become AlphaMissense score revisions. No card
    enrichment, new prediction, clinical assertion or isoform reconstruction occurs.
    """
    identifier = accession(identifier)
    result = online(client, OnlineAlphaMissenseClient).annotations(identifier, limit)
    if not isinstance(result, dict):
        raise ConnectorError("AlphaMissense client response is malformed.")
    descriptor = select_descriptor(result.get("discovery"), identifier)
    artifact = result.get("artifact")
    if descriptor is None:
        if artifact is not None:
            raise ConnectorError("AlphaMissense artifact has no discovery declaration.")
    else:
        validate_artifact(artifact, descriptor, limit)
    return source_record(
        "AlphaMissense",
        "annotations",
        {"accession": identifier, "limit": limit},
        artifact.get("retrieved_at") if artifact else None,
        None,
        {
            "discovery": deepcopy(result["discovery"]),
            "artifact": deepcopy(artifact),
            "availability": "declared" if artifact is not None else "not_stated",
            "scope": "exact_full_canonical_human_descriptor; isoforms_not_queried",
        },
        truncated=artifact["total"] > len(artifact["rows"]) if artifact else False,
    )
