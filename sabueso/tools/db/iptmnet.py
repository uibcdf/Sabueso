"""Read iPTMnet public HTML substrate reports by exact base accession."""

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
from sabueso.mappings.iptmnet import (
    URL_ROOT,
    parse_substrate_report,
    response_query,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import load_source_snapshot


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    parsed = parse_substrate_report(result["record"], query["identifier"])
    selected = parsed["rows"]
    out = {
        "outcome": "received" if selected else "not_found",
        "count": len(selected),
        "received_export_count": len(parsed["rows"]),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "native_dataset_record_sequence_and_scoring_rule_revisions_not_stated",
        },
        "response_identity": {
            "basis": "original_native_HTML_substrate_report",
            "hash": "sha256:"
            + hashlib.sha256(result["record"].encode("utf-8")).hexdigest(),
        },
        "coverage": "all_received_substrate_panel_rows; other_sections_and_expanded_view_unqueried",
        "received_groups": parsed["groups"],
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
        raise missing_fixture(f"iPTMnet snapshot is unavailable: {path}") from error
    envelope["snapshot_receipt"]["native_format"] = (
        "iPTMnet_native_HTML_substrate_panel"
    )
    return envelope


class OnlineIPTMnetClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("iPTMnet", "substrate_report", summarize=_summarize)
    def substrate_report(self, identifier):
        response_query(identifier)
        retrieval = stamp("iPTMnet")
        try:
            with urlopen(URL_ROOT + identifier + "/", timeout=self.timeout) as response:
                raw = response.read()
                text = raw.decode("utf-8")
        except (HTTPError, URLError, OSError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"iPTMnet export access failed: {error}") from error
        parse_substrate_report(text, identifier)
        return {
            "record": text,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotIPTMnetClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path = path
        self.source_metadata = digest_source_metadata(source_metadata)
        self.expected_sha256 = digest_expected_sha256(expected_sha256)

    @acquisition("iPTMnet", "substrate_report", fixture=True, summarize=_summarize)
    def substrate_report(self, identifier):
        query = response_query(identifier)
        result = _load(self.path, self.source_metadata, self.expected_sha256)
        if (
            result["source"] != "iPTMnet"
            or result["kind"] != "substrate_report"
            or result["query"] != query
        ):
            raise ConnectorError(
                "Supplied iPTMnet source/kind/query/revision differ from the request."
            )
        parse_substrate_report(result["record"], identifier)
        if result["version"] is not None:
            raise ConnectorError("iPTMnet snapshot revision must remain unknown.")
        return result


class FixtureIPTMnetClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "iptmnet"
        self.retrieved_at = retrieved_at

    def substrate_report(self, identifier):
        return SnapshotIPTMnetClient(
            self.directory / f"entry__{identifier}.html",
            source_metadata={
                "source": "iPTMnet",
                "kind": "substrate_report",
                "query": response_query(identifier),
                "retrieved_at": self.retrieved_at,
                "version": None,
            },
        ).substrate_report(identifier)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_substrate_report(identifier, client=None, skip_digestion=False):
    """Receive every native substrate row from one original public HTML report.

    Preserve group tabs, missing sites, opaque score labels, and hidden source/
    publication links. No canonical numbering, sequence revision, inferred
    curation class, evidence creation or linked acquisition. The REST API's
    earlier failure remains separate. Data terms are CC BY-NC-SA 4.0.
    """
    query = response_query(identifier)
    result = online(client, OnlineIPTMnetClient).substrate_report(identifier)
    if (
        not isinstance(result, dict)
        or ("source" in result and result["source"] != "iPTMnet")
        or ("kind" in result and result["kind"] != "substrate_report")
        or ("query" in result and result["query"] != query)
        or ("truncated" in result and result["truncated"] is not False)
    ):
        raise ConnectorError(
            "iPTMnet client response/query/revision/cut is unsupported."
        )
    text = result.get("record")
    parse_substrate_report(text, identifier)
    if result.get("version") is not None:
        raise ConnectorError("iPTMnet client revision must remain unknown.")
    envelope = source_record(
        "iPTMnet",
        "substrate_report",
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
