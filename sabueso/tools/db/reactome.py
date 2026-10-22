"""Reactome: the pathways and reactions a protein takes part in (#83).

Reactome maps each UniProt accession to the curated events (pathways and reactions) it
takes part in, in its species. For species other than human, many events are inferred
by Reactome from orthology (``isInferred``); the flag is kept.

``pathways(accession)`` returns ``{"retrieved_at", "version", "record": {"pathways",
"reactions", "ancestors": {stId: [[event, ...], ...]}}}``, where ``pathways`` are the
lowest-level pathways naming the protein and ``ancestors`` the paths up to their top-level
pathway. It raises ``RecordNotFoundError`` when Reactome maps the accession to nothing.

``OnlineReactomeClient`` queries the Content Service (no key; data CC0 1.0).
``FixtureReactomeClient`` reads ``<directory>/reactome/<ACCESSION>.json``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.tools.db._http import request, stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "Reactome"
CONTENT = "https://reactome.org/ContentService/data"
KEPT = ("stId", "displayName", "speciesName", "isInferred", "schemaClass")


#: The one endpoint that answers plain text; every other answers JSON, and an
#: unreadable answer is asked again (#97).
TEXT_PATHS = ("database/version",)


def _get(path: str, timeout: float, missing_ok: bool = False) -> Any:
    try:
        with urlopen(
            request(f"{CONTENT}/{path}"),
            timeout=timeout,
            expect_json=path not in TEXT_PATHS,
        ) as resp:  # nosec
            body = resp.read().decode("utf-8")
    except HTTPError as exc:
        exc.close()
        if exc.code == 404 and missing_ok:
            return None
        raise ConnectorError(f"Reactome {path} failed: HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ConnectorError(f"Reactome {path} failed: {exc}") from exc
    try:
        return json.loads(body)
    except ValueError:
        return body.strip()  # the version endpoint answers plain text


def _events(items: List[Dict[str, Any]] | None) -> List[Dict[str, Any]]:
    return [{k: e.get(k) for k in KEPT} for e in items or []]


class OnlineReactomeClient:
    def __init__(self, timeout: float = 60.0) -> None:
        self.timeout = timeout

    def pathways(self, accession: str) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        pathways = _get(
            f"mapping/UniProt/{accession}/pathways", self.timeout, missing_ok=True
        )
        reactions = _get(
            f"mapping/UniProt/{accession}/reactions", self.timeout, missing_ok=True
        )
        if not pathways and not reactions:
            try:
                version = str(_get("database/version", self.timeout))
            except ConnectorError:
                version = None  # the answer stands; only its release is unknown
            raise RecordNotFoundError(
                f"Reactome maps UniProt {accession} to nothing", version=version
            )
        ancestors = {}
        for pathway in pathways or []:
            paths = _get(f"event/{pathway['stId']}/ancestors", self.timeout) or []
            ancestors[pathway["stId"]] = [_events(path) for path in paths]
        return {
            "retrieved_at": retrieval.value,
            "version": str(_get("database/version", self.timeout)),
            "record": {
                "pathways": _events(pathways),
                "reactions": _events(reactions),
                "ancestors": ancestors,
            },
        }


class FixtureReactomeClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    def pathways(self, accession: str) -> Dict[str, Any]:
        if accession in self.failing:
            raise ConnectorError(f"Reactome request for {accession} failed (simulated)")
        path = self.directory / "reactome" / f"{accession}.json"
        if not path.is_file():
            raise RecordNotFoundError(f"Reactome maps UniProt {accession} to nothing")
        saved = json.loads(path.read_text(encoding="utf-8"))
        return {"retrieved_at": self.retrieved_at, **saved}


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
def get_pathways(identifier: str, client: Any = None, skip_digestion: bool = False):
    """The Reactome pathways and reactions a UniProt accession takes part in."""
    response = online(client, OnlineReactomeClient).pathways(identifier)
    return source_record(
        SOURCE,
        "pathways",
        {"uniprot": identifier},
        response.get("retrieved_at"),
        response.get("version"),
        response["record"],
    )
