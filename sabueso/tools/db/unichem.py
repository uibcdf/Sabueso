"""UniChem cross-references of a chemical structure (uibcdf/sabueso#25).

UniChem (EMBL-EBI) groups the records that many chemistry resources hold for one
standard InChI. Given a standard InChIKey, it lists the compound records of ChEMBL,
PubChem, DrugBank, the PDB chemical components, BindingDB and others. Sabueso uses it to
connect a small molecule with its records in sources that it has not queried directly
(``sabueso.tools.card.small_molecule``).

``compound(inchikey)`` returns ``{retrieved_at, compound}``, where ``compound`` holds
``uci`` (the UniChem compound id), ``standardInchiKey`` and ``sources`` (``id``,
``shortName``, ``compoundId``). ``OnlineUniChemClient`` queries the UniChem REST API;
``FixtureUniChemClient`` reads ``<directory>/unichem/<INCHIKEY>.json``. Both raise
``RecordNotFoundError`` when UniChem holds no such structure and ``ConnectorError`` on
failures.

``compound_by_source(source_id, compound_id)`` looks a structure up by a source's own
record id instead, e.g. a BindingDB monomer (``BINDINGDB_SOURCE``, #66); the fixture
reads ``<directory>/unichem/source<id>__<compound id>.json``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request

from sabueso._private.argdigest import arg_digest
from sabueso.core.chemical_identity_acquisition import note_response, observe
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.source_acquisition import capture_acquisitions
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

UNICHEM_API = "https://www.ebi.ac.uk/unichem/api/v1/compounds"
SOURCE_FIELDS = ("id", "shortName", "compoundId")
#: UniChem's source ids used by Sabueso.
BINDINGDB_SOURCE = 31
#: UniChem answers one compound per request and states no rate limit: Sabueso asks with
#: a few threads, and never more than five requests per second (#98).
WORKERS = 4
PER_SECOND = 5.0


def _compound(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "uci": record.get("uci"),
        "standardInchiKey": record.get("standardInchiKey"),
        "inchi": (record.get("inchi") or {}).get("inchi"),
        "sources": sorted(
            ({k: s.get(k) for k in SOURCE_FIELDS} for s in record.get("sources") or []),
            key=lambda s: (s["id"] or 0, str(s["compoundId"])),
        ),
    }


class OnlineUniChemClient:
    #: How many lookups a caller may run at once, and how fast (``_http.gather``).
    workers = WORKERS
    per_second = PER_SECOND

    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    @observe("UniChem", "compound")
    def compound(self, inchikey: str) -> Dict[str, Any]:
        body = json.dumps({"type": "inchikey", "compound": inchikey}).encode("utf-8")
        request = Request(
            UNICHEM_API, data=body, headers={"Content-Type": "application/json"}
        )
        retrieval = stamp("UniChem")
        try:
            with urlopen(request, timeout=self.timeout, expect_json=True) as resp:  # nosec - trusted endpoint
                data = json.loads(resp.read().decode("utf-8"))
                note_response(data)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(
                f"UniChem request for {inchikey} failed: {exc}"
            ) from exc
        compounds = data.get("compounds") or []
        if not compounds:
            raise RecordNotFoundError(f"UniChem has no compound {inchikey}")
        return {"retrieved_at": retrieval.value, "compound": _compound(compounds[0])}

    @observe("UniChem", "compound_by_source")
    def compound_by_source(self, source_id: int, compound_id: str) -> Dict[str, Any]:
        body = json.dumps(
            {
                "type": "sourceID",
                "compound": str(compound_id),
                "sourceID": int(source_id),
            }
        ).encode("utf-8")
        request = Request(
            UNICHEM_API, data=body, headers={"Content-Type": "application/json"}
        )
        retrieval = stamp("UniChem")
        label = f"source {source_id} compound {compound_id}"
        try:
            with urlopen(request, timeout=self.timeout, expect_json=True) as resp:  # nosec - trusted endpoint
                data = json.loads(resp.read().decode("utf-8"))
                note_response(data)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(f"UniChem request for {label} failed: {exc}") from exc
        compounds = data.get("compounds") or []
        if not compounds:
            raise RecordNotFoundError(f"UniChem has no {label}")
        return {"retrieved_at": retrieval.value, "compound": _compound(compounds[0])}


class FixtureUniChemClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe("UniChem", "compound", fixture=True)
    def compound(self, inchikey: str) -> Dict[str, Any]:
        if inchikey in self.failing:
            raise ConnectorError(f"UniChem request for {inchikey} failed (simulated)")
        path = self.directory / "unichem" / f"{inchikey}.json"
        if not path.is_file():
            raise RecordNotFoundError(f"UniChem has no compound {inchikey}")
        saved = json.loads(path.read_text(encoding="utf-8"))
        note_response(saved)
        return {"retrieved_at": self.retrieved_at, "compound": saved}

    @observe("UniChem", "compound_by_source", fixture=True)
    def compound_by_source(self, source_id: int, compound_id: str) -> Dict[str, Any]:
        label = f"source {source_id} compound {compound_id}"
        if str(compound_id) in self.failing:
            raise ConnectorError(f"UniChem request for {label} failed (simulated)")
        path = self.directory / "unichem" / f"source{source_id}__{compound_id}.json"
        saved = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
        if saved is not None:
            note_response(saved)
        if not saved or saved.get("not_found"):
            raise RecordNotFoundError(f"UniChem has no {label}")
        return {"retrieved_at": self.retrieved_at, "compound": saved}


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_compound(identifier: str, client: Any = None, skip_digestion: bool = False):
    """The records other resources hold for a standard InChIKey (UniChem)."""
    response = online(client, OnlineUniChemClient).compound(identifier)
    return source_record(
        "UniChem",
        "compound",
        {"inchikey": identifier},
        response.get("retrieved_at"),
        None,
        response.get("compound"),
    )
