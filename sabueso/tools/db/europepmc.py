"""Europe PMC: the publications whose text mentions a protein's accession (#92).

Europe PMC mines the text of abstracts and open-access full texts for database
accession numbers (UniProt, PDB, …). An article whose text states ``P60174`` is found by
``ACCESSION_ID:P60174 AND ACCESSION_TYPE:uniprot``: the accession is written in the
paper, and Europe PMC found it by text mining (``hasTMAccessionNumbers``). This is not
UniProt's curated references (``UNIPROT_PUBS``), which reach the card as
``described_in``.

Only stated accessions are used. Europe PMC's gene and protein annotations ground a
*name* to an entry, without the organism: "triosephosphate isomerase" in a paper on the
human deficiency is tagged with a yeast entry (Q9C401). That is identity by name, and
Sabueso does not use it.

``mentions(accession, limit)`` returns ``{"retrieved_at", "version", "record":
{"query", "hitCount", "articles": [...]}}``: the first ``limit`` articles of the search,
newest first, with their ids and bibliographic data. It raises ``RecordNotFoundError``
when no article mentions the accession.

``OnlineEuropePMCClient`` pages the REST search (no key; ``version`` is the service's
version, e.g. 6.9). ``FixtureEuropePMCClient`` reads
``<directory>/europepmc/<ACCESSION>.json``.
An unsaved search is unavailable (``ConnectorError``), never an empty source answer.

``annotations(article_ids)`` reads accession-number annotations of explicitly named
articles through the Annotations API. Its raw records retain annotation ids, providers,
sections, tags and quote fragments (``prefix``, ``exact``, ``postfix``), when stated.
They are not complete sentences or scientific claims. Returned article ids may use
MED even when the request used PMC. An empty answer does not establish absence in the
article. Explicit card intake uses ``europepmc={"article_ids": ...}``; source access
does not infer identity from names.

Terms: EMBL-EBI places no restrictions of its own on the data and expects attribution;
each article keeps its licence. Accession search keeps bibliography. Explicit annotation
intake keeps text fragments; their storage follows the article's licence, which the
annotations response does not state.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.article_acquisition import (
    note_response as note_article_response,
)
from sabueso.core.article_acquisition import (
    observe as observe_article,
)
from sabueso.core.article_metadata import (
    fixture_name,
)
from sabueso.core.article_metadata import (
    normalize as normalize_article,
)
from sabueso.core.article_metadata import (
    query as article_query,
)
from sabueso.core.article_metadata import (
    response as article_response,
)
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.source_acquisition import (
    acquisition,
    capture_acquisitions,
    missing_fixture,
)
from sabueso.tools.db._http import request, stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "Europe PMC"
SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
ANNOTATIONS = "https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByArticleIds"
#: Sabueso's bounded batch size, not a claim about the server's maximum.
ANNOTATION_BATCH = 8
#: Every mention up to a safety ceiling, unless ``europepmc={"limit": n}`` asks for
#: fewer; a cut is reported (#88).
DEFAULT_LIMIT = 5000
PAGE = 1000
KEPT = (
    "id",
    "source",
    "pmid",
    "pmcid",
    "doi",
    "title",
    "journalTitle",
    "pubYear",
    "isOpenAccess",
    "firstPublicationDate",
)


def query(accession: str) -> str:
    return f"ACCESSION_ID:{accession} AND ACCESSION_TYPE:uniprot"


def _annotation_record(value: Any) -> list[dict]:
    if not isinstance(value, list) or any(
        not isinstance(article, dict)
        or not isinstance(article.get("annotations"), list)
        or any(not isinstance(item, dict) for item in article["annotations"])
        for article in value
    ):
        raise ConnectorError("Europe PMC annotations returned an unreadable record")
    return value


class OnlineEuropePMCClient:
    def __init__(self, timeout: float = 60.0) -> None:
        self.timeout = timeout

    @observe_article()
    def article(self, identifier: str) -> Dict[str, Any]:
        """Core metadata for an explicit native publication identifier; no full-text access."""
        normalize_article(identifier)
        retrieval = stamp(SOURCE)
        params = {
            "query": article_query(identifier),
            "resultType": "core",
            "format": "json",
            "pageSize": 10,
        }
        try:
            with urlopen(
                request(f"{SEARCH}?{urlencode(params)}"),
                timeout=self.timeout,
                expect_json=True,
            ) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                note_article_response(payload)
            record = article_response(payload, identifier)
        except HTTPError as exc:
            exc.close()
            if exc.code == 404:
                raise RecordNotFoundError(
                    f"Europe PMC has no article metadata for {identifier}"
                ) from exc
            raise ConnectorError(
                f"Europe PMC article request failed: HTTP {exc.code}"
            ) from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ConnectorError(f"Europe PMC article request failed: {exc}") from exc
        if record["total_count"] == 0:
            raise RecordNotFoundError(
                f"Europe PMC has no article metadata for {identifier}"
            )
        return {
            "record": record,
            "version": payload.get("version"),
            "retrieved_at": retrieval.value,
        }

    @acquisition(SOURCE, "annotations")
    def annotations(self, article_ids: list[str]) -> Dict[str, Any]:
        """Raw accession annotations, in bounded batches; no source release is stated."""
        retrieval = stamp(SOURCE)
        records = []
        for start in range(0, len(article_ids), ANNOTATION_BATCH):
            batch = article_ids[start : start + ANNOTATION_BATCH]
            params = {
                "articleIds": ",".join(batch),
                "format": "JSON",
                "type": "Accession Numbers",
            }
            try:
                with urlopen(  # nosec - trusted endpoint
                    request(f"{ANNOTATIONS}?{urlencode(params)}"),
                    timeout=self.timeout,
                    expect_json=True,
                ) as resp:
                    records.extend(
                        _annotation_record(json.loads(resp.read().decode("utf-8")))
                    )
            except HTTPError as exc:
                exc.close()
                raise ConnectorError(
                    f"Europe PMC annotations for {batch} failed: HTTP {exc.code}"
                ) from exc
            except (URLError, TimeoutError, OSError, ValueError) as exc:
                raise ConnectorError(
                    f"Europe PMC annotations for {batch} failed: {exc}"
                ) from exc
        return {"retrieved_at": retrieval.value, "version": None, "record": records}

    @acquisition(SOURCE, "mentions")
    def mentions(self, accession: str, limit: int = DEFAULT_LIMIT) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        articles, cursor, hits, version = [], "*", 0, None
        while len(articles) < limit:
            params = {
                "query": query(accession),
                "format": "json",
                "resultType": "lite",
                "pageSize": min(PAGE, limit - len(articles)),
                "cursorMark": cursor,
            }
            try:
                with urlopen(  # nosec - trusted endpoint
                    request(f"{SEARCH}?{urlencode(params)}"),
                    timeout=self.timeout,
                    expect_json=True,
                ) as resp:
                    page = json.loads(resp.read().decode("utf-8"))
            except HTTPError as exc:
                exc.close()
                raise ConnectorError(
                    f"Europe PMC search for {accession} failed: HTTP {exc.code}"
                ) from exc
            except (URLError, TimeoutError, OSError, ValueError) as exc:
                raise ConnectorError(
                    f"Europe PMC search for {accession} failed: {exc}"
                ) from exc
            version, hits = page.get("version"), int(page.get("hitCount") or 0)
            results = (page.get("resultList") or {}).get("result") or []
            articles += [
                {k: r[k] for k in KEPT if r.get(k) is not None} for r in results
            ]
            following = page.get("nextCursorMark")
            if not results or not following or following == cursor:
                break
            cursor = following
        if not hits:
            raise RecordNotFoundError(
                f"No Europe PMC article mentions UniProt {accession}", version=version
            )
        return {
            "retrieved_at": retrieval.value,
            "version": version,
            "record": {
                "query": query(accession),
                "hitCount": hits,
                "articles": articles[:limit],
            },
        }


class FixtureEuropePMCClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe_article(fixture=True)
    def article(self, identifier: str) -> Dict[str, Any]:
        normalize_article(identifier)
        if identifier in self.failing:
            raise ConnectorError(
                f"Europe PMC article request for {identifier} failed (simulated)"
            )
        path = self.directory / "europepmc" / "articles" / fixture_name(identifier)
        if not path.is_file():
            raise RecordNotFoundError(
                f"No saved Europe PMC article metadata for {identifier}"
            )
        payload = json.loads(path.read_text(encoding="utf-8"))
        note_article_response(payload)
        record = article_response(payload, identifier)
        return {
            "record": record,
            "version": payload.get("version"),
            "retrieved_at": self.retrieved_at,
        }

    @acquisition(SOURCE, "annotations", fixture=True)
    def annotations(self, article_ids: list[str]) -> Dict[str, Any]:
        records, retrieved = [], []
        for article_id in article_ids:
            if article_id in self.failing:
                raise ConnectorError(
                    f"Europe PMC annotations for {article_id} failed (simulated)"
                )
            path = (
                self.directory
                / "europepmc"
                / "annotations"
                / f"{article_id.replace(':', '_')}.json"
            )
            if not path.is_file():
                raise RecordNotFoundError(
                    f"No saved Europe PMC annotation response for {article_id}"
                )
            saved = json.loads(path.read_text(encoding="utf-8"))
            records.extend(_annotation_record(saved["record"]))
            retrieved.append(saved.get("retrieved_at", self.retrieved_at))
        return {
            "retrieved_at": retrieved[0]
            if len(set(retrieved)) == 1
            else self.retrieved_at,
            "version": None,
            "record": records,
        }

    @acquisition(SOURCE, "mentions", fixture=True)
    def mentions(self, accession: str, limit: int = DEFAULT_LIMIT) -> Dict[str, Any]:
        if accession in self.failing:
            raise ConnectorError(
                f"Europe PMC search for {accession} failed (simulated)"
            )
        path = self.directory / "europepmc" / f"{accession}.json"
        if not path.is_file():
            raise missing_fixture(
                f"No saved Europe PMC search response for UniProt {accession}"
            )
        saved = json.loads(path.read_text(encoding="utf-8"))
        record = dict(saved["record"])
        record["articles"] = record["articles"][:limit]
        return {"retrieved_at": self.retrieved_at, **saved, "record": record}


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_annotations(
    article_ids: Any,
    client: Any = None,
    skip_digestion: bool = False,
):
    """Raw accession-number annotations for ``MED:<pmid>`` or ``PMC:PMC<id>``.

    One id or a list is accepted. Sections and text fragments remain source-native,
    with the provider and annotation link. Missing annotations do not establish that
    an accession is absent from an article. No annotation becomes a curated reading,
    an extracted scientific claim or a card's identity finding through this function.
    Article licences govern storage of the returned fragments.
    """
    response = online(client, OnlineEuropePMCClient).annotations(article_ids)
    return source_record(
        SOURCE,
        "annotations",
        {"article_ids": article_ids, "type": "Accession Numbers"},
        response.get("retrieved_at"),
        response.get("version"),
        response["record"],
    )


@arg_digest()
@capture_acquisitions
def get_mentions(
    identifier: str,
    limit: int = DEFAULT_LIMIT,
    client: Any = None,
    skip_digestion: bool = False,
):
    """The Europe PMC articles whose text mentions a UniProt accession."""
    response = online(client, OnlineEuropePMCClient).mentions(identifier, limit)
    record = response["record"]
    return source_record(
        SOURCE,
        "mentions",
        {"uniprot": identifier, "limit": limit},
        response.get("retrieved_at"),
        response.get("version"),
        record,
        truncated=record["hitCount"] > len(record["articles"]),
    )


# Explicit metadata lookup keeps the existing mention/annotation APIs independent.
@arg_digest()
@capture_acquisitions
def get_article(identifier: str, client: Any = None, skip_digestion: bool = False):
    """Metadata for pubmed:<id>, pmc:PMC<id> or doi:<doi>, without full-text lookup.

    The core endpoint can return an abstract; the public projection excludes it.
    Licence literals are source declarations, not grants for supplied fragments.
    Multiple matching records remain explicit and cannot be silently bound to a fragment.
    """
    normalize_article(identifier)
    response = online(client, OnlineEuropePMCClient).article(identifier)
    return source_record(
        SOURCE,
        "article",
        {"identifier": identifier},
        response.get("retrieved_at"),
        response.get("version"),
        response.get("record"),
        truncated=(response.get("record") or {}).get("truncated"),
    )
