"""AAindex1 native amino-acid reference scales; explicit direct source access.

Recovered from the July client with strict parsing, shared transport, native
metadata and detached acquisition. No automatic protein enrichment is performed.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.error import HTTPError, URLError

from smonitor import signal

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.snapshot import canonical_json, digest
from sabueso.core.source_acquisition import (
    _terminal,
    acquisition,
    capture_acquisitions,
    missing_fixture,
)
from sabueso.mappings.aaindex import parse_index, validate_identifier
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "AAindex"
URL = "https://www.genome.jp/ftp/db/community/aaindex/aaindex1"


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        if isinstance(result, RecordNotFoundError):
            return {"outcome": "not_found", "count": 0}
        return {"outcome": _terminal(result, fixture, requests)}
    return {
        "outcome": "received",
        "count": 1,
        "retrieved_at": result["retrieved_at"],
        "source_version": {"value": None, "basis": "not_stated_in_download"},
        "response_identity": {
            "basis": "decoded_native_index_record",
            "hash": digest(canonical_json(result["record"])),
        },
        "document_identity": {
            "basis": "download_bytes",
            "hash": result["document_sha256"],
        },
        "native_references": result["record"]["references"],
        "bibliography_gaps": [
            "Native reference literals are retained; linked publications were not queried."
        ],
    }


class OnlineAAindexClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition(SOURCE, "index", summarize=_summarize)
    def index(self, identifier):
        validate_identifier(identifier)
        retrieval = stamp(SOURCE)
        try:
            with urlopen(URL, timeout=self.timeout) as response:
                raw = response.read()
            text = raw.decode("utf-8")
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"AAindex1 download failed: {error}") from error
        return {
            "record": parse_index(text, identifier),
            "retrieved_at": retrieval.value,
            "version": None,
            "document_sha256": hashlib.sha256(raw).hexdigest(),
        }


class FixtureAAindexClient:
    def __init__(self, directory):
        self.directory = Path(directory)

    @acquisition(SOURCE, "index", fixture=True, summarize=_summarize)
    def index(self, identifier):
        validate_identifier(identifier)
        path = self.directory / "aaindex" / "aaindex1"
        if not path.is_file():
            raise missing_fixture(f"AAindex fixture document is unavailable: {path}")
        try:
            raw = path.read_bytes()
            record = parse_index(raw.decode("utf-8"), identifier)
        except (OSError, UnicodeError) as error:
            raise ConnectorError(
                f"AAindex fixture document is unreadable: {error}"
            ) from error
        return {
            "record": record,
            "retrieved_at": stamp(SOURCE).value,
            "version": None,
            "document_sha256": hashlib.sha256(raw).hexdigest(),
        }


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_index(identifier, client=None, skip_digestion=False):
    """Return one native AAindex1 scale, preserving missing values and unit gaps."""
    response = online(client, OnlineAAindexClient).index(identifier)
    return source_record(
        SOURCE,
        "index",
        {"identifier": identifier},
        response.get("retrieved_at"),
        response.get("version"),
        response["record"],
    )
