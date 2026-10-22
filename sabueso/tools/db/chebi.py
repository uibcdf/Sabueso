"""ChEBI: what a molecule is chemically, and what roles it plays (#83, wave 2).

ChEBI (EMBL-EBI, CC BY 4.0) curates chemical entities of biological interest: each entry
states its structure (a standard InChIKey), the classes it belongs to (``is a``), its
roles (``has role``: biological, chemical, or an application), a definition and a
curation level (stars, 3 = curated by ChEBI).

Sabueso reaches a ChEBI entry only through a stated link: UniChem lists the ChEBI ids of
a structure, and the entry joins the card only when the InChIKey ChEBI states for it is
the card's anchor.

``compounds(ids)`` returns ``{"retrieved_at", "compounds": {accession: record},
"missing": [...]}``, asking ChEBI 2.0's API for up to 200 entries per request. A
secondary id is answered by its primary entry. ``OnlineChEBIClient`` queries the API;
``FixtureChEBIClient`` reads ``<directory>/chebi/compounds.json``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError
from sabueso.tools.db._http import request, stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "ChEBI"
COMPOUNDS = "https://www.ebi.ac.uk/chebi/backend/api/public/compounds/"
BATCH = 200
#: What Sabueso reads of an entry.
KEPT = (
    "id",
    "chebi_accession",
    "name",
    "stars",
    "definition",
    "default_structure",
    "chemical_data",
    "ontology_relations",
    "roles_classification",
    "secondary_ids",
    "modified_on",
)


def accession(value: str) -> str:
    """``CHEBI:<n>`` from ``chebi:<n>``, ``CHEBI:<n>`` or ``<n>``."""
    text = str(value).strip()
    return "CHEBI:" + text.split(":", 1)[1] if ":" in text else f"CHEBI:{text}"


def _kept(data: Dict[str, Any]) -> Dict[str, Any]:
    kept = {k: data.get(k) for k in KEPT}
    relations = (data.get("ontology_relations") or {}).get("outgoing_relations") or []
    kept["ontology_relations"] = {"outgoing_relations": relations}
    return kept


class OnlineChEBIClient:
    def __init__(self, timeout: float = 120.0) -> None:
        self.timeout = timeout

    def compounds(self, ids: Iterable[str]) -> Dict[str, Any]:
        wanted = sorted({accession(i) for i in ids if i})
        retrieval = stamp(SOURCE)
        found: Dict[str, Any] = {}
        missing = []
        for i in range(0, len(wanted), BATCH):
            chunk = wanted[i : i + BATCH]
            body = json.dumps({"chebi_ids": chunk}).encode("utf-8")
            try:
                with urlopen(
                    request(
                        COMPOUNDS,
                        data=body,
                        headers={"Content-Type": "application/json"},
                    ),
                    timeout=self.timeout,
                    expect_json=True,
                ) as resp:
                    answer = json.loads(resp.read().decode("utf-8"))
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                if isinstance(exc, HTTPError):
                    exc.close()
                raise ConnectorError(f"ChEBI request failed: {exc}") from exc
            for asked, entry in answer.items():
                if entry.get("exists") and entry.get("data"):
                    found[accession(asked)] = {
                        "primary": entry.get("primary_chebi_id"),
                        "data": _kept(entry["data"]),
                    }
                else:
                    missing.append(accession(asked))
        return {"retrieved_at": retrieval.value, "compounds": found, "missing": missing}


class FixtureChEBIClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    def compounds(self, ids: Iterable[str]) -> Dict[str, Any]:
        wanted = sorted({accession(i) for i in ids if i})
        if set(wanted) & self.failing:
            raise ConnectorError("ChEBI request failed (simulated)")
        path = self.directory / "chebi" / "compounds.json"
        saved = json.loads(path.read_text(encoding="utf-8"))["compounds"]
        found = {
            a: {"primary": saved[a].get("primary_chebi_id"), "data": saved[a]["data"]}
            for a in wanted
            if a in saved and saved[a].get("exists")
        }
        return {
            "retrieved_at": self.retrieved_at,
            "compounds": found,
            "missing": [a for a in wanted if a not in found],
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
def get_compounds(identifiers: Any, client: Any = None, skip_digestion: bool = False):
    """ChEBI entries by id (``CHEBI:<n>``): structure, classes, roles, definition."""
    response = online(client, OnlineChEBIClient).compounds(identifiers)
    return source_record(
        SOURCE,
        "compounds",
        {"chebi": sorted(accession(i) for i in identifiers)},
        response.get("retrieved_at"),
        None,
        {"compounds": response["compounds"], "missing": response["missing"]},
    )
