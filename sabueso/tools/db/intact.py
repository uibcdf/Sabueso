"""Bounded direct IntAct PSICQUIC access, keeping original MITAB 2.7 and scope."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode

from smonitor import signal

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError
from sabueso.core.source_acquisition import (
    _terminal,
    acquisition,
    capture_acquisitions,
    missing_fixture,
)
from sabueso.mappings.intact import (
    HEADERS,
    LIMIT,
    accession,
    page_limit,
    parse_page,
    response_query,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json

URL = "https://www.ebi.ac.uk/Tools/webservices/psicquic/intact/webservices/current/search/query/"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    _, scope = parse_page(
        result["record"],
        result["response_headers"],
        result["response_query"],
        query["identifier"],
        query["limit"],
    )
    out = {
        "outcome": "received" if scope["returned_rows"] else "empty",
        "count": scope["returned_rows"],
        "scope": scope,
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "record_revision_not_stated; service_versions_separate",
        },
        "response_identity": {
            "basis": "original_native_mitab",
            "hash": hashlib.sha256(result["record"].encode()).hexdigest(),
        },
        "truncated": scope["truncated"],
    }
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineIntActClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("IntAct", "interactions", summarize=_summarize)
    def interactions(self, identifier, limit=LIMIT):
        identifier, limit = accession(identifier), page_limit(limit)
        query = response_query(identifier, limit)
        retrieval = stamp("IntAct")
        url = (
            URL
            + quote(query["miql"], safe="")
            + "?"
            + urlencode({"format": "tab27", "firstResult": 0, "maxResults": limit})
        )
        try:
            with urlopen(url, timeout=self.timeout) as response:
                document = response.read().decode("utf-8")
                headers = {
                    name: response.headers.get(name)
                    for name in HEADERS
                    if response.headers.get(name) is not None
                }
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"IntAct access failed: {error}") from error
        parse_page(document, headers, query, identifier, limit)
        return {
            "record": document,
            "response_headers": headers,
            "response_query": query,
            "retrieved_at": retrieval.value,
            "version": None,
        }


class FixtureIntActClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "intact"
        self.retrieved_at = retrieved_at

    @acquisition("IntAct", "interactions", fixture=True, summarize=_summarize)
    def interactions(self, identifier, limit=LIMIT):
        identifier, limit = accession(identifier), page_limit(limit)
        path = self.directory / f"interactions__{identifier}.mitab"
        context_path = path.with_suffix(".headers.json")
        if not path.is_file() or not context_path.is_file():
            raise missing_fixture(f"IntAct body/header fixture is unavailable: {path}")
        try:
            raw, context_raw = path.read_bytes(), context_path.read_bytes()
            document, context = raw.decode("utf-8"), _json(context_raw.decode("utf-8"))
        except (OSError, ValueError, UnicodeError) as error:
            raise ConnectorError(f"IntAct fixture is unreadable: {error}") from error
        if not isinstance(context, dict) or set(context) != {
            "response_query",
            "response_headers",
        }:
            raise ConnectorError(
                "IntAct supplied body/header query declaration is malformed."
            )
        parse_page(
            document,
            context["response_headers"],
            context["response_query"],
            identifier,
            limit,
        )
        return {
            "record": document,
            **deepcopy(context),
            "version": None,
            "retrieved_at": self.retrieved_at,
            "snapshot_receipt": {
                "format": "sabueso.intact_supplied_mitab@1",
                "access": "supplied_file",
                "path": str(path.resolve()),
                "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "document_sha256": hashlib.sha256(raw).hexdigest(),
                "file_format": "mitab27",
                "header_path": str(context_path.resolve()),
                "header_sha256": hashlib.sha256(context_raw).hexdigest(),
                "source_metadata_basis": "fixture_client_query_and_header_declaration",
                "source_access_observed": False,
            },
        }


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_interactions(identifier, limit=LIMIT, client=None, skip_digestion=False):
    """Read one bounded page for an exact UniProt reference (including isoforms).

    All native response rows are checked before the output cap. The count describes
    this MIQL query, not unique partners or biological absence. Continuation pages,
    referenced publications and source sequences are unqueried; no card is enriched.
    """
    identifier, limit = accession(identifier), page_limit(limit)
    result = online(client, OnlineIntActClient).interactions(identifier, limit)
    if not isinstance(result, dict) or result.get("version") is not None:
        raise ConnectorError("IntAct client response/revision is unsupported.")
    _, scope = parse_page(
        result.get("record"),
        result.get("response_headers"),
        result.get("response_query"),
        identifier,
        limit,
    )
    envelope = source_record(
        "IntAct",
        "interactions",
        {"accession": identifier, "limit": limit},
        result.get("retrieved_at"),
        None,
        result["record"],
        truncated=scope["truncated"],
    )
    envelope.update(
        response_headers=deepcopy(result["response_headers"]),
        response_query=deepcopy(result["response_query"]),
        scope=scope,
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = deepcopy(result["snapshot_receipt"])
    return envelope
