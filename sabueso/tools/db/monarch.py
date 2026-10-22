"""Read one explicitly bounded native Monarch association page for an exact subject."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

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
from sabueso.mappings.monarch import page_is_partial, response_query, validate_page
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://api-v3.monarchinitiative.org/v3/api/association?"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    record = validate_page(
        result["record"], query["identifier"], query["limit"], query["offset"]
    )
    out = {
        "outcome": "received" if record["items"] else "empty",
        "count": len(record["items"]),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "KG_association_entity_and_sequence_revisions_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_expanded_association_page",
            "hash": digest(canonical_json(record)),
        },
        "native_page": {k: record[k] for k in ("limit", "offset", "total")},
        "coverage": "one_exact_subject_page; no_implicit_pagination_or_absence_claim",
        "truncated": page_is_partial(record),
    }
    if "download_sha256" in result:
        out["download_sha256"] = result["download_sha256"]
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineMonarchClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("Monarch", "associations", summarize=_summarize)
    def associations(self, identifier, limit, offset):
        query = response_query(identifier, limit, offset)
        retrieval = stamp("Monarch")
        try:
            with urlopen(
                URL + urlencode(query), timeout=self.timeout, expect_json=True
            ) as response:
                raw = response.read()
                payload = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"Monarch access failed: {error}") from error
        validate_page(payload, identifier, limit, offset)
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotMonarchClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path, self.source_metadata = path, deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition("Monarch", "associations", fixture=True, summarize=_summarize)
    def associations(self, identifier, limit, offset):
        query = response_query(identifier, limit, offset)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied Monarch snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "Monarch"
            or result["kind"] != "associations"
            or result["query"] != query
            or response_query(
                result["query"].get("subject"),
                result["query"].get("limit"),
                result["query"].get("offset"),
            )
            != query
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied Monarch source/kind/query/revision differ from the request."
            )
        validate_page(result["record"], identifier, limit, offset)
        return result


class FixtureMonarchClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "monarch"
        self.retrieved_at = retrieved_at

    def associations(self, identifier, limit, offset):
        query = response_query(identifier, limit, offset)
        return SnapshotMonarchClient(
            self.directory
            / f"associations__{identifier.replace(':', '_')}__limit{limit}__offset{offset}.json",
            source_metadata={
                "source": "Monarch",
                "kind": "associations",
                "query": query,
                "retrieved_at": self.retrieved_at,
            },
        ).associations(identifier, limit, offset)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_associations(identifier, limit=20, offset=0, client=None, skip_digestion=False):
    """Receive one direct-subject page, keeping native types, qualifiers and sources.

    ``direct=true`` binds the exact entity and excludes ancestor matching; it is
    not a physical-binding declaration. Limits are 1 to 500; offsets are nonnegative.
    Native totals/cuts stay explicit. No automatic pagination, disease-only filter,
    protein transfer, identity merge, reference lookup or analysis job is performed.
    Input-specific licences remain separate from Monarch software/API versions.
    """
    query = response_query(identifier, limit, offset)
    result = online(client, OnlineMonarchClient).associations(identifier, limit, offset)
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or ("source" in result and result["source"] != "Monarch")
        or ("kind" in result and result["kind"] != "associations")
        or ("query" in result and result["query"] != query)
    ):
        raise ConnectorError("Monarch client response/revision/query is unsupported.")
    if (
        "query" in result
        and response_query(
            result["query"].get("subject"),
            result["query"].get("limit"),
            result["query"].get("offset"),
        )
        != query
    ):
        raise ConnectorError("Monarch client query types differ from the request.")
    record = validate_page(result.get("record"), identifier, limit, offset)
    cut = page_is_partial(record)
    if "truncated" in result and result["truncated"] is not cut:
        raise ConnectorError("Monarch client cut differs from native page coverage.")
    envelope = source_record(
        "Monarch",
        "associations",
        query,
        result.get("retrieved_at"),
        None,
        deepcopy(record),
        truncated=cut,
    )
    for k in ("snapshot_receipt", "download_sha256"):
        if k in result:
            envelope[k] = deepcopy(result[k])
    return envelope
