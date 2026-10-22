"""STRING functional associations for resolved proteins.

STRING network edges are *functional associations* scored from several evidence channels
(genomic neighborhood, gene fusion, phylogenetic co-occurrence, co-expression, experiments,
curated databases, text mining). They are not physical interactions, so Sabueso records
them as ``functionally_associated_with`` relationships (``mappings/stringdb.py``), used by
``resolve_protein_card(..., string={...})``.

``partners(identifier, species, required_score, limit)`` returns
``{query, version, retrieved_at, results, truncated}``: the partners at or above
``required_score``, most confident first, at most ``limit``. STRING states no total, so
the client asks for one partner more than ``limit``; ``truncated`` says STRING holds
more. ``OnlineStringClient`` queries the STRING API;
``FixtureStringClient`` reads ``<directory>/string/<identifier>__<species>.json``. Both raise
``RecordNotFoundError`` when STRING has no such protein and ``ConnectorError`` on failures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

STRING_API = "https://string-db.org/api/json"
CALLER_IDENTITY = "sabueso"
DEFAULT_REQUIRED_SCORE = 700  # STRING "high confidence"
#: Every partner at or above the score, up to a safety ceiling; a cut is reported.
DEFAULT_LIMIT = 5000


def _get(endpoint: str, params: Dict[str, Any], timeout: float) -> Any:
    url = f"{STRING_API}/{endpoint}?" + urlencode(
        {**params, "caller_identity": CALLER_IDENTITY}
    )
    try:
        with urlopen(url, timeout=timeout, expect_json=True) as resp:  # nosec - trusted endpoint
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        exc.close()
        if exc.code == 404:
            raise RecordNotFoundError(f"STRING has no protein for {params}") from exc
        raise ConnectorError(f"STRING {endpoint} failed: HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        raise ConnectorError(f"STRING {endpoint} failed: {exc}") from exc


class OnlineStringClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout
        self._version: str | None = None

    def version(self) -> str | None:
        if self._version is None:
            info = _get("version", {}, self.timeout)
            self._version = (info[0] if info else {}).get("string_version")
        return self._version

    def partners(
        self,
        identifier: str,
        species: int,
        required_score: int = DEFAULT_REQUIRED_SCORE,
        limit: int = DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        query = {
            "identifiers": identifier,
            "species": species,
            "required_score": required_score,
            "limit": limit,
        }
        retrieval = stamp("STRING")
        # One partner more than the limit tells whether STRING holds more: STRING
        # states no total, and a cut must never pass for the whole answer.
        results = _get(
            "interaction_partners", {**query, "limit": limit + 1}, self.timeout
        )
        if results and isinstance(results[0], dict) and results[0].get("Error"):
            raise RecordNotFoundError(
                f"STRING has no protein {identifier} in {species}"
            )
        return {
            "query": query,
            "version": self.version(),
            "retrieved_at": retrieval.value,
            "results": results[:limit],
            "truncated": len(results) > limit,
        }


class FixtureStringClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    def partners(
        self,
        identifier: str,
        species: int,
        required_score: int = DEFAULT_REQUIRED_SCORE,
        limit: int = DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        key = f"{identifier}__{species}"
        if key in self.failing:
            raise ConnectorError(f"STRING request for {key} failed (simulated)")
        path = self.directory / "string" / f"{key}.json"
        if not path.is_file():
            raise RecordNotFoundError(
                f"STRING has no protein {identifier} in {species}"
            )
        saved = json.loads(path.read_text(encoding="utf-8"))
        return {**saved, "retrieved_at": self.retrieved_at}


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
def get_partners(
    identifier: str,
    species: int,
    required_score: int = DEFAULT_REQUIRED_SCORE,
    limit: int = DEFAULT_LIMIT,
    client: Any = None,
    skip_digestion: bool = False,
):
    """STRING functional partners of a protein within a species (NCBI taxonomy id)."""
    response = online(client, OnlineStringClient).partners(
        identifier, species, required_score=required_score, limit=limit
    )
    return source_record(
        "STRING",
        "partners",
        response.get("query"),
        response.get("retrieved_at"),
        response.get("version"),
        response.get("results"),
        truncated=bool(response.get("truncated")),
    )
