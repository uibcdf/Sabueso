"""Read one explicitly selected Complex Portal native JSON declaration."""

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
from sabueso.mappings.complex_portal import complex_id, validate_complex
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://www.ebi.ac.uk/intact/complex-ws/complex/"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    payload = validate_complex(result["record"], query["identifier"])
    out = {
        "outcome": "received",
        "count": 1,
        "participant_count": len(payload["participants"]),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "complex_record_revision_not_returned; release_dates_separate",
        },
        "response_identity": {
            "basis": "decoded_native_complex",
            "hash": digest(canonical_json(payload)),
        },
        "native_release_dates": deepcopy(payload["releaseDates"]),
        "native_predicted_complex": payload["predictedComplex"],
        "native_evidence_type": deepcopy(payload["evidenceType"]),
        "native_references": [
            {
                k: r.get(k)
                for k in ("database", "identifier", "qualifier", "dbMI", "qualifierMI")
            }
            for r in payload["crossReferences"]
        ],
        "truncated": False,
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineComplexPortalClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("Complex Portal", "complex", summarize=_summarize)
    def complex(self, identifier):
        identifier = complex_id(identifier)
        retrieval = stamp("Complex Portal")
        try:
            with urlopen(
                URL + identifier, timeout=self.timeout, expect_json=True
            ) as response:
                payload = _json(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"Complex Portal access failed: {error}") from error
        validate_complex(payload, identifier)
        return {"record": payload, "retrieved_at": retrieval.value, "version": None}


class SnapshotComplexPortalClient:
    """Use one native supplied JSON/gzip file with exact source/query binding."""

    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition("Complex Portal", "complex", fixture=True, summarize=_summarize)
    def complex(self, identifier):
        identifier = complex_id(identifier)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied Complex Portal snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "Complex Portal"
            or result["kind"] != "complex"
            or result["query"] != {"complex_id": identifier}
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied Complex Portal source/kind/query/revision differ from the request."
            )
        validate_complex(result["record"], identifier)
        return result


class FixtureComplexPortalClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "complex_portal"
        self.retrieved_at = retrieved_at

    @acquisition("Complex Portal", "complex", fixture=True, summarize=_summarize)
    def complex(self, identifier):
        identifier = complex_id(identifier)
        path = self.directory / f"complex__{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"Complex Portal fixture is unavailable: {path}")
        result = load_source_snapshot(
            path,
            source_metadata={
                "source": "Complex Portal",
                "kind": "complex",
                "query": {"complex_id": identifier},
                "retrieved_at": self.retrieved_at,
            },
        )
        validate_complex(result["record"], identifier)
        return result


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_complex(identifier, client=None, skip_digestion=False):
    """Receive one exact primary CPX declaration without searching or expanding it.

    Native participant occurrences, stoichiometry, feature/reference alternatives,
    ECO context and dates survive. Record/participant sequence revisions remain
    unknown. No name/protein search, secondary ID following, linked support or
    sequence retrieval, binary interaction expansion or card enrichment occurs.
    """
    identifier = complex_id(identifier)
    result = online(client, OnlineComplexPortalClient).complex(identifier)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or result.get("truncated", False) is not False
    ):
        raise ConnectorError(
            "Complex Portal client response/revision/cut is unsupported."
        )
    payload = result.get("record")
    validate_complex(payload, identifier)
    envelope = source_record(
        "Complex Portal",
        "complex",
        {"complex_id": identifier},
        result.get("retrieved_at"),
        None,
        deepcopy(payload),
        truncated=False,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
