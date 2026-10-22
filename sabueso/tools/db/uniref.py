"""UniRef: the sequence clusters UniProt places an entry in (#103).

UniProt clusters every sequence at three identity levels: UniRef100 (identical
sequences and their fragments), UniRef90 and UniRef50 (at least 90% and 50% identity
to the cluster's seed, over 80% of the longer sequence). Each cluster lists its members:
UniProtKB entries (by entry name and accessions) and UniParc sequences without an entry,
each with its organism, length and its own UniRef100 cluster.

A cluster is UniProt's statement of sequence similarity. It is never identity: two
members are related sequences, possibly of different strains or species, and Sabueso
does not merge them.

- ``clusters(accession)``: the UniRef100, UniRef90 and UniRef50 clusters of an entry
  (one request);
- ``members(cluster_id)``: a cluster's members (500 per request, at most 100 pages).
  Repeated request URLs or an exhausted page budget raise ``ConnectorError``;
  the detached trace retains completed pages. The member ceiling remains a
  successful, explicitly truncated result.

Each answer is ``{"retrieved_at", "version", "record"}``, ``version`` the UniProt release
the service states. ``OnlineUniRefClient`` queries UniProt's REST API (CC BY 4.0, as
UniProtKB); ``FixtureUniRefClient`` reads ``<directory>/uniref/``: ``clusters_<acc>.json``
and ``members_<cluster>.json``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.source_acquisition import capture_acquisitions, missing_fixture
from sabueso.core.uniref_acquisition import note_response, observe
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "UniProt"
API = "https://rest.uniprot.org/uniref"
PAGE = 500
#: Members of a cluster kept, at most; a cut is reported.
MAX_MEMBERS = 5000
#: Logical member pages requested, including empty pages; retries are separate.
MAX_MEMBER_PAGES = 100


class OnlineUniRefClient:
    def __init__(self, timeout: float = 120.0) -> None:
        self.timeout = timeout

    def _get(self, url: str) -> tuple:
        try:
            with urlopen(url, timeout=self.timeout, expect_json=True) as resp:
                found = json.loads(resp.read().decode("utf-8"))
                note_response(
                    found,
                    url=url,
                    release=resp.headers.get("X-UniProt-Release"),
                    next_url=_next(resp.headers.get("Link")),
                    total=resp.headers.get("X-Total-Results"),
                )
                return (
                    found,
                    resp.headers.get("X-UniProt-Release"),
                    resp.headers.get("Link"),
                )
        except HTTPError as exc:
            exc.close()
            if exc.code == 404:
                raise RecordNotFoundError(f"UniRef has no {url}") from exc
            raise ConnectorError(f"UniRef request failed: {exc}") from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ConnectorError(f"UniRef request failed: {exc}") from exc

    @observe("uniref_clusters")
    def clusters(self, accession: str) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        query = urlencode(
            {
                "query": f"uniprot_id:{accession}",
                "fields": "id,name,count,identity",
                "format": "json",
                "size": 10,
            }
        )
        found, release, _ = self._get(f"{API}/search?{query}")
        return {
            "retrieved_at": retrieval.value,
            "version": release,
            "record": [
                {
                    "id": c.get("id"),
                    "level": c.get("entryType"),
                    "member_count": c.get("memberCount"),
                }
                for c in found.get("results") or []
            ],
        }

    @observe("uniref_members")
    def members(self, cluster_id: str) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        url = (
            f"{API}/{cluster_id}/members?{urlencode({'format': 'json', 'size': PAGE})}"
        )
        members: List[Dict[str, Any]] = []
        release = None
        requested_urls = set()
        while url and len(members) < MAX_MEMBERS:
            if url in requested_urls:
                raise _pagination_error("repeated_url", url, len(requested_urls))
            if len(requested_urls) >= MAX_MEMBER_PAGES:
                raise _pagination_error("page_limit", url, len(requested_urls))
            requested_urls.add(url)
            found, release, link = self._get(url)
            members.extend(found.get("results") or [])
            url = _next(link)
        return {
            "retrieved_at": retrieval.value,
            "version": release,
            "record": members[:MAX_MEMBERS],
            "truncated": bool(url) or len(members) > MAX_MEMBERS,
        }


def _pagination_error(reason: str, url: str, requested_pages: int) -> ConnectorError:
    return ConnectorError(
        f"UniRef member pagination stopped ({reason}); no partial result returned",
        extra={
            "uniref_pagination": {
                "rule": "uniref_member_pagination@1",
                "stop_reason": reason,
                "remaining_url": url,
                "requested_pages": requested_pages,
                "page_limit": MAX_MEMBER_PAGES,
            }
        },
    )


def _next(link: str | None) -> str | None:
    """The next page of a paginated answer (``Link: <url>; rel="next"``)."""
    for part in (link or "").split(","):
        if 'rel="next"' in part:
            return part.split(";")[0].strip().strip("<>")
    return None


class FixtureUniRefClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory) / "uniref"
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    def _read(self, name: str) -> Dict[str, Any]:
        if name in self.failing:
            raise ConnectorError(f"UniRef request for {name} failed (simulated)")
        path = self.directory / f"{name}.json"
        if not path.is_file():
            raise missing_fixture(f"UniRef fixture is unavailable: {name}")
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConnectorError(f"UniRef fixture cannot be read: {name}") from exc
        note_response(
            saved,
            fixture=True,
            release=saved.get("version") if isinstance(saved, dict) else None,
        )
        return {"retrieved_at": self.retrieved_at, **saved}

    @observe("uniref_clusters", fixture=True)
    def clusters(self, accession: str) -> Dict[str, Any]:
        return self._read(f"clusters_{accession}")

    @observe("uniref_members", fixture=True)
    def members(self, cluster_id: str) -> Dict[str, Any]:
        return {"truncated": False, **self._read(f"members_{cluster_id}")}


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_clusters(identifier: str, client: Any = None, skip_digestion: bool = False):
    """The UniRef100, UniRef90 and UniRef50 clusters UniProt places an entry in."""
    response = online(client, OnlineUniRefClient).clusters(identifier)
    return source_record(
        SOURCE,
        "uniref_clusters",
        {"uniprot": identifier},
        response.get("retrieved_at"),
        response.get("version"),
        {"clusters": response["record"]},
    )
