"""Explicit UniParc checksum search with bounded, validated native pagination."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, StorageError
from sabueso.core.snapshot import canonical_json, digest
from sabueso.core.source_acquisition import (
    _terminal,
    acquisition,
    capture_acquisitions,
    missing_fixture,
)
from sabueso.mappings.uniparc import checksum_key, validate_results
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot

URL = "https://rest.uniprot.org/uniparc/search"
DEFAULT_LIMIT = 100
PAGE_SIZE = 500


def _next(link, checksum):
    found = []
    for part in (link or "").split(","):
        if 'rel="next"' not in part:
            continue
        target = part.split(";", 1)[0].strip().strip("<>")
        parsed = urlsplit(target)
        query = parse_qs(parsed.query)
        if (
            parsed.scheme != "https"
            or parsed.netloc != "rest.uniprot.org"
            or parsed.path != "/uniparc/search"
            or parsed.fragment
            or query.get("query") != [f"checksum:{checksum}"]
            or query.get("format") != ["json"]
        ):
            raise ConnectorError("UniParc continuation changes the source or query.")
        found.append(target)
    if len(found) > 1:
        raise ConnectorError("UniParc continuation is ambiguous.")
    return found[0] if found else None


def _validate(result, checksum):
    if not isinstance(result, dict) or result.get("checksum") != checksum:
        raise ConnectorError("UniParc response query binding differs.")
    rows = validate_results(result.get("results"), checksum)
    total = result.get("total")
    if isinstance(total, bool) or not isinstance(total, int) or total < len(rows):
        raise ConnectorError("UniParc total is missing or inconsistent.")
    version = result.get("version")
    if version is not None and (not isinstance(version, str) or not version.strip()):
        raise ConnectorError("UniParc release declaration is malformed.")
    if not isinstance(result.get("truncated"), bool) or result["truncated"] != (
        total > len(rows)
    ):
        raise ConnectorError("UniParc incomplete scope is missing or inconsistent.")
    pages = result.get("pages", [])
    if not isinstance(pages, list):
        raise ConnectorError("UniParc native page receipts must be a list.")
    native_rows = []
    for page in pages:
        if (
            not isinstance(page, dict)
            or isinstance(page.get("total"), bool)
            or page.get("total") != total
            or page.get("release") != result.get("version")
            or not isinstance(page.get("url"), str)
            or not isinstance(page.get("record"), dict)
        ):
            raise ConnectorError("UniParc native page receipt is inconsistent.")
        _next(f'<{page["url"]}>; rel="next"', checksum)
        native_rows.extend(validate_results(page["record"].get("results"), checksum))
    if pages:
        validate_results(native_rows, checksum)
        if (
            rows != native_rows[: len(rows)]
            or not len(rows) <= len(native_rows) <= total
        ):
            raise ConnectorError("UniParc rows differ from their native page receipts.")
    return result


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        out = {"outcome": _terminal(result, fixture, requests)}
        partial = getattr(result, "received_subset", None)
        if partial and partial["results"]:
            out.update(
                outcome="partial",
                count=len(partial["results"]),
                received_subset=deepcopy(partial),
            )
        return out
    out = {
        "outcome": "received" if result["results"] else "empty",
        "count": len(result["results"]),
        "total": result["total"],
        "truncated": result["truncated"],
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": result.get("version"),
            "basis": "declared_fixture_release"
            if fixture
            else "native_response_release_header; not_sequence_revision",
        },
        "response_identity": {
            "basis": "validated_native_search_rows",
            "hash": digest(canonical_json(result["results"])),
        },
        "pages": deepcopy(result.get("pages", [])),
        "reference_scope": "returned_search_UniProtKB_references; other_cross_references_not_queried",
    }
    if "snapshot_receipt" in result:
        out.update(access="supplied_file", snapshot_receipt=result["snapshot_receipt"])
    return out


class OnlineUniParcClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("UniParc", "checksum_search", summarize=_summarize)
    def records(self, checksum, limit=DEFAULT_LIMIT):
        checksum = checksum_key(checksum)
        retrieval = stamp("UniParc")
        target = (
            URL
            + "?"
            + urlencode(
                {
                    "query": f"checksum:{checksum}",
                    "format": "json",
                    "size": min(PAGE_SIZE, limit),
                }
            )
        )
        rows, pages, visited = [], [], set()
        total, release = None, None
        try:
            while target and len(rows) < limit:
                if target in visited:
                    raise ConnectorError("UniParc continuation repeats a page.")
                visited.add(target)
                with urlopen(
                    target, timeout=self.timeout, expect_json=True
                ) as response:
                    payload = _json(response.read().decode("utf-8"))
                    raw_total = response.headers.get("X-Total-Results")
                    page_release = response.headers.get("X-UniProt-Release")
                    link = response.headers.get("Link")
                if not isinstance(raw_total, str) or not raw_total.isdigit():
                    raise ConnectorError(
                        "UniParc search has no valid native total header."
                    )
                if not isinstance(payload, dict):
                    raise ConnectorError("UniParc search response is not an object.")
                page_rows = validate_results(payload.get("results"), checksum)
                page_total = int(raw_total)
                if total is not None and (
                    total != page_total or release != page_release
                ):
                    raise ConnectorError("UniParc page counts/releases disagree.")
                total, release = page_total, page_release
                if not page_rows and (rows or total):
                    raise ConnectorError(
                        "UniParc returned an empty page before completing the search."
                    )
                validate_results(rows + page_rows, checksum)
                if len(rows) + len(page_rows) > total:
                    raise ConnectorError(
                        "UniParc received more rows than its native total."
                    )
                rows.extend(page_rows)
                pages.append(
                    {
                        "url": target,
                        "total": total,
                        "release": release,
                        "record": payload,
                    }
                )
                target = _next(link, checksum)
                if target and len(rows) >= total:
                    raise ConnectorError(
                        "UniParc continuation contradicts its native total."
                    )
                if not target and len(rows) < total and len(rows) < limit:
                    raise ConnectorError(
                        "UniParc continuation is missing from an incomplete search."
                    )
        except (
            HTTPError,
            URLError,
            OSError,
            ValueError,
            UnicodeError,
            StorageError,
            ConnectorError,
        ) as error:
            if isinstance(error, HTTPError):
                error.close()
            failure = ConnectorError(f"UniParc search failed: {error}")
            failure.received_subset = {
                "checksum": checksum,
                "results": rows[:limit],
                "total": total,
                "version": release,
                "retrieved_at": retrieval.value,
                "truncated": total is None or total > len(rows[:limit]),
                "pages": pages,
            }
            raise failure from error
        return _validate(
            {
                "checksum": checksum,
                "results": rows[:limit],
                "total": total,
                "version": release,
                "retrieved_at": retrieval.value,
                "truncated": total > len(rows[:limit]),
                "pages": pages,
            },
            checksum,
        )


class FixtureUniParcClient:
    def __init__(self, directory="temp_data"):
        self.directory = Path(directory)

    @acquisition("UniParc", "checksum_search", fixture=True, summarize=_summarize)
    def records(self, checksum, limit=DEFAULT_LIMIT):
        checksum = checksum_key(checksum)
        path = self.directory / "uniparc" / f"search__{checksum}.json"
        if not path.is_file():
            raise missing_fixture(f"UniParc search fixture is unavailable: {path}")
        snapshot = load_source_snapshot(
            path,
            source_metadata={
                "source": "UniParc",
                "kind": "checksum_search",
                "query": {"checksum": checksum},
            },
        )
        result = deepcopy(_validate(snapshot["record"], checksum))
        result["results"] = result["results"][:limit]
        result["truncated"] = result["total"] > len(result["results"])
        result["snapshot_receipt"] = snapshot["snapshot_receipt"]
        return result


@arg_digest()
@capture_acquisitions
def get_records(checksum, limit=DEFAULT_LIMIT, client=None, skip_digestion=False):
    """Search native sequence records by MD5, retaining caps and original scope."""
    result = _validate(
        online(client, OnlineUniParcClient).records(checksum, limit), checksum
    )
    if len(result["results"]) > limit:
        raise ConnectorError("UniParc client exceeded the requested row limit.")
    envelope = source_record(
        "UniParc",
        "checksum_search",
        {"checksum": checksum, "limit": limit},
        result.get("retrieved_at"),
        result.get("version"),
        {
            "total": result["total"],
            "results": result["results"],
            "pages": result.get("pages", []),
        },
        truncated=result["truncated"],
    )
    if "snapshot_receipt" in result:
        envelope["snapshot_receipt"] = result["snapshot_receipt"]
    return envelope
