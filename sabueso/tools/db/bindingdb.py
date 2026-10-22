"""BindingDB measured affinities of a protein (uibcdf/sabueso#66).

BindingDB curates binding affinities (Ki, Kd, IC50, EC50) from the literature and
patents, and imports part of ChEMBL. Its REST service, keyed by UniProt accession,
returns per record the monomer id, SMILES, affinity type, value in nanomolar (the
relation, if any, written in the value: ``">1.00e+5"``), PubMed id and DOI. It does not
state where a record came from (BindingDB curation or a ChEMBL import); the bulk
download does. So records from this service are compared with other sources by their
statement (``sabueso.core.measurements``), never by declared provenance.

Licence: data curated by BindingDB is CC BY 3.0, and data imported from ChEMBL keeps
ChEMBL's CC BY-SA 3.0. Records from this service carry no origin, so Sabueso treats
them as CC BY-SA 3.0.

``ligands(accession, cutoff, limit)`` returns ``{accession, retrieved_at, record,
total_count}`` with the list of affinities: up to ``limit`` records (5000 by default,
#88, #98), ordered by ``bindingdb_record_order@1`` (monomer id, affinity type, value) so
that the same answer keeps the same records. ``total_count`` is what BindingDB returned.
Each kept monomer needs a UniChem lookup for its identity, so the ceiling also bounds
those. ``OnlineBindingDBClient`` queries the REST service; ``FixtureBindingDBClient``
reads ``<directory>/bindingdb/<accession>.json``.

The documented empty-string response (an exactly empty HTTP 200 body or JSON
``""``) and an empty native affinities list mean no matching records (#114).
Malformed or unexpected nonempty responses remain connector failures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.bindingdb_acquisition import note_response, observe
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.source_acquisition import capture_acquisitions
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

BINDINGDB_REST = "https://bindingdb.org/rest/getLigandsByUniprots"
#: No affinity cutoff by default (nanomolar): every record is kept, weak ones included.
DEFAULT_CUTOFF = 100_000_000
#: Every record up to a safety ceiling, unless ``bindingdb={"limit": n}`` asks for
#: fewer; a cut is reported (#88).
DEFAULT_LIMIT = 5000
RECORD_ORDER = "bindingdb_record_order@1"


def _decode(content: bytes) -> Any:
    return "" if content == b"" else json.loads(content.decode("utf-8"))


def _affinities(data: Any) -> list:
    if data == "":
        return []
    envelope = (
        data.get("getLindsByUniprotsResponse") if isinstance(data, dict) else None
    )
    records = envelope.get("affinities") if isinstance(envelope, dict) else None
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ConnectorError("BindingDB returned an unexpected affinity response.")
    return records


def _kept(
    accession: str, retrieved_at: str, records: list, limit: int
) -> Dict[str, Any]:
    """``bindingdb_record_order@1``: by monomer id, affinity type and value; the first
    ``limit``."""
    ordered = sorted(
        records,
        key=lambda r: (
            int(r.get("monomerid") or 0),
            str(r.get("affinity_type") or ""),
            str(r.get("affinity") or ""),
        ),
    )
    return {
        "accession": accession,
        "retrieved_at": retrieved_at,
        "record": ordered[:limit],
        "total_count": len(records),
        "record_order": RECORD_ORDER,
    }


class OnlineBindingDBClient:
    def __init__(self, timeout: float = 60.0) -> None:
        self.timeout = timeout

    @observe()
    def ligands(
        self,
        accession: str,
        cutoff: float = DEFAULT_CUTOFF,
        limit: int = DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        query = urlencode(
            {"uniprot": accession, "cutoff": cutoff, "response": "application/json"}
        )
        retrieval = stamp("BindingDB")
        try:
            with urlopen(
                f"{BINDINGDB_REST}?{query}",
                timeout=self.timeout,
                expect_json=True,
                allow_empty_body=True,
            ) as resp:  # nosec
                content = resp.read()
                data = _decode(content)
                if data == "" and getattr(resp, "status", 200) != 200:
                    raise ValueError("an empty BindingDB response requires HTTP 200")
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(
                f"BindingDB request for {accession} failed: {exc}"
            ) from exc
        note_response(data)
        records = _affinities(data)
        if not records:
            raise RecordNotFoundError(f"BindingDB has no affinities for {accession}")
        return _kept(accession, retrieval.value, records, limit)


class FixtureBindingDBClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe(fixture=True)
    def ligands(
        self,
        accession: str,
        cutoff: float = DEFAULT_CUTOFF,
        limit: int = DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        if accession in self.failing:
            raise ConnectorError(
                f"BindingDB request for {accession} failed (simulated)"
            )
        path = self.directory / "bindingdb" / f"{accession}.json"
        records = []
        if path.is_file():
            data = _decode(path.read_bytes())
            note_response(data)
            records = _affinities(data)
        if not records:
            raise RecordNotFoundError(f"BindingDB has no affinities for {accession}")
        return _kept(accession, self.retrieved_at, records, limit)


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_affinities(
    identifier: str,
    limit: int = DEFAULT_LIMIT,
    client: Any = None,
    skip_digestion: bool = False,
):
    """The affinities BindingDB holds for a UniProt protein, up to ``limit`` records
    (``bindingdb_record_order@1``)."""
    response = online(client, OnlineBindingDBClient).ligands(identifier, limit=limit)
    return source_record(
        "BindingDB",
        "affinities",
        {"accession": identifier, "limit": limit},
        response.get("retrieved_at"),
        None,
        response.get("record"),
        truncated=response.get("total_count", 0) > len(response.get("record") or []),
    )
