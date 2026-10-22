"""Read original public FDA OOPD detailed pages by exact numeric page locator."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path
from urllib.error import HTTPError, URLError

from smonitor import signal

from sabueso._private.argdigest import arg_digest
from sabueso._private.argdigest.argument.expected_sha256 import digest_expected_sha256
from sabueso._private.argdigest.argument.source_metadata import digest_source_metadata
from sabueso.core.errors import ConnectorError
from sabueso.core.source_acquisition import (
    _terminal,
    acquisition,
    capture_acquisitions,
    missing_fixture,
)
from sabueso.mappings.fda_orphan import (
    SOURCE,
    URL_ROOT,
    parse_page,
    response_query,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import load_source_snapshot


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    parsed = parse_page(result["record"])
    selected = parsed["records"]
    out = {
        "outcome": "received" if selected else "not_found",
        "count": len(selected),
        "received_export_count": len(parsed["records"]),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "native_dataset_and_record_revisions_not_stated",
        },
        "response_identity": {
            "basis": "original_native_HTML_page",
            "hash": "sha256:"
            + hashlib.sha256(result["record"].encode("utf-8")).hexdigest(),
        },
        "coverage": "all_received_page_tables; search_and_database_totals_unqueried",
        "received_approval_tables": parsed["received_approval_tables"],
        "empty_approval_tables": parsed["empty_approval_tables"],
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


def _load(path, metadata, expected_sha256):
    """Read literal HTML through the shared loader before native validation."""
    try:
        envelope = load_source_snapshot(
            path,
            source_metadata=metadata,
            file_format="html",
            expected_sha256=expected_sha256,
        )
    except OSError as error:
        raise missing_fixture(f"FDA OOPD snapshot is unavailable: {path}") from error
    envelope["snapshot_receipt"]["native_format"] = "FDA_OOPD_native_HTML_page"
    return envelope


class OnlineFDAOrphanClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition(SOURCE, "page", summarize=_summarize)
    def page(self, identifier):
        response_query(identifier)
        retrieval = stamp("FDA Orphan Drug Designations and Approvals")
        try:
            with urlopen(URL_ROOT + identifier, timeout=self.timeout) as response:
                raw = response.read()
                text = raw.decode("utf-8")
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"FDA OOPD export access failed: {error}") from error
        parse_page(text)
        return {
            "record": text,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotFDAOrphanClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition(SOURCE, "page", fixture=True, summarize=_summarize)
    def page(self, identifier):
        query = response_query(identifier)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != SOURCE
            or result["kind"] != "page"
            or result["query"] != query
        ):
            raise ConnectorError(
                "Supplied FDA OOPD source/kind/query/revision differ from the request."
            )
        parse_page(result["record"])
        if result["version"] is not None:
            raise ConnectorError("FDA OOPD snapshot revision must remain unknown.")
        return result


class FixtureFDAOrphanClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "fda_orphan"
        self.retrieved_at = retrieved_at

    def page(self, identifier):
        return SnapshotFDAOrphanClient(
            self.directory / f"page__{identifier}.html",
            source_metadata={
                "source": SOURCE,
                "kind": "page",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
                "version": None,
            },
        ).page(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_page(identifier, client=None, skip_digestion=False):
    """Receive one original public FDA OOPD detailed page by numeric page locator.

    Designation and approval tables retain independent native fields, occurrences,
    dates, blank values and support. The HTML does not echo its page locator;
    observed URL or caller-supplied binding identifies a page, not a stable
    designation, product or protein entity. No search, clinical conclusion,
    linked acquisition or automatic card intake. FDA website policy applies with
    noted and third-party exceptions; no openFDA CC0 grant is substituted.
    Original supplied-artifact reading is qualified; live shared transport has
    returned HTTP 404 and remains an explicit connector failure.
    """
    query = response_query(identifier)
    result = online(client, OnlineFDAOrphanClient).page(identifier)
    if (
        not isinstance(result, dict)
        or ("source" in result and result["source"] != SOURCE)
        or ("kind" in result and result["kind"] != "page")
        or ("query" in result and result["query"] != query)
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError(
            "FDA OOPD client response/query/revision/cut is unsupported."
        )
    text = result.get("record")
    parse_page(text)
    if result.get("version") is not None:
        raise ConnectorError("FDA OOPD client revision must remain unknown.")
    envelope = source_record(
        SOURCE,
        "page",
        query,
        result.get("retrieved_at"),
        None,
        text,
        truncated=False,
    )
    for k in ("snapshot_receipt", "download_sha256"):
        if k in result:
            envelope[k] = deepcopy(result[k])
    return envelope
