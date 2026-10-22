"""OMA: orthologs of a protein across about 2,600 genomes (#83, wave 2).

OMA (Orthologous MAtrix, Dessimoz lab; data CC BY 4.0) infers pairwise orthologs between
the proteins of complete genomes, and states each relation's type (``1:1``, ``1:n``,
``m:1``, ``m:n``), with the ortholog's OMA id, species and taxon, and its canonical id: a
UniProt accession, a Swiss-Prot entry name (``TPIS_HUMAN``) or another database's id
(GenBank).

Access is OMA's REST API (``/api``, no key):

- ``xrefs(accession)``: the cross-references OMA states for the protein it maps an
  accession to, each with ``seq_match`` (``exact`` when OMA's sequence is the
  accession's, ``modified`` otherwise);
- ``orthologs(accession, rel_type=None)``: its pairwise orthologs, in one request.

``accessions(names)`` asks UniProt which accession each Swiss-Prot entry name is (100
names per request): UniProt states that, not OMA. Only active entries count: a retired
entry can keep the name of the one that replaced it.

Each answer is ``{"retrieved_at", "record"}``. ``OnlineOMAClient`` queries the APIs;
``FixtureOMAClient`` reads ``<directory>/oma/``: ``xref_<acc>.json``,
``orthologs_<acc>.json`` and ``entry_names.json`` (``{name: accession}``).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.oma_acquisition import note_name_resolution, note_response, observe
from sabueso.core.source_acquisition import capture_acquisitions, missing_fixture
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "OMA"
API = "https://omabrowser.org/api"
UNIPROT_SEARCH = "https://rest.uniprot.org/uniprotkb/search"
NAMES_PER_REQUEST = 100
#: OMA's service answers HTTP 502 to about one request in three, however spaced (measured
#: 2026-10-01); beyond the general retries, a request is tried this many times.
UNSTABLE_ATTEMPTS = 4
UNSTABLE_PAUSE = 2.0  # seconds, times the attempt


def active_accessions(answer: Dict[str, Any], names: Iterable[str]) -> Dict[str, str]:
    """``{entry name: accession}`` from a UniProt search answer: only active entries
    count. A retired entry can keep the name (TPIS_HUMAN: P00938, demerged into P60174
    and P60175), and a name with more than one active entry is left unresolved."""
    wanted = set(names)
    active: Dict[str, List[str]] = {}
    for row in answer.get("results") or []:
        name = row.get("uniProtkbId")
        if name in wanted and row.get("entryType") != "Inactive":
            accession = row.get("primaryAccession")
            if not isinstance(accession, str) or not accession:
                raise ConnectorError(
                    "UniProt entry-name row does not state an accession"
                )
            active.setdefault(name, []).append(accession)
    return {name: hits[0] for name, hits in active.items() if len(set(hits)) == 1}


class OnlineOMAClient:
    def __init__(self, timeout: float = 120.0) -> None:
        self.timeout = timeout

    def _get(
        self, url: str, what: str, source: str = SOURCE, kind: str = "rows", names=None
    ) -> Dict[str, Any]:
        # Entry names are resolved by UniProt, which states them; its answers are
        # UniProt's retrievals.
        retrieval = stamp("UniProt") if source == "UniProt" else stamp(SOURCE)
        for attempt in range(UNSTABLE_ATTEMPTS):
            try:
                with urlopen(url, timeout=self.timeout, expect_json=True) as resp:
                    found = json.loads(resp.read().decode("utf-8"))
                    headers = getattr(resp, "headers", {})
                    note_response(
                        found,
                        kind=kind,
                        url=url,
                        release=headers.get("X-UniProt-Release")
                        if source == "UniProt"
                        else None,
                        link=headers.get("Link"),
                        names=names,
                    )
                break
            except HTTPError as exc:
                exc.close()
                if exc.code == 404:
                    raise RecordNotFoundError(f"{source} has no {what}") from exc
                if exc.code in (502, 503) and attempt + 1 < UNSTABLE_ATTEMPTS:
                    time.sleep(UNSTABLE_PAUSE * (attempt + 1))
                    continue
                raise ConnectorError(f"{source} request failed: {exc}") from exc
            except (URLError, TimeoutError, OSError, ValueError) as exc:
                raise ConnectorError(f"{source} request failed: {exc}") from exc
        return {"retrieved_at": retrieval.value, "record": found}

    @observe("oma_xrefs")
    def xrefs(self, accession: str) -> Dict[str, Any]:
        return self._rows(
            self._get(f"{API}/protein/{accession}/xref/", f"protein {accession}")
        )

    @staticmethod
    def _rows(answer: Dict[str, Any]) -> Dict[str, Any]:
        rows = answer["record"]
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise ConnectorError("OMA response does not state a record list")
        return answer

    @observe("oma_protein")
    def protein(self, entry_id: str) -> Dict[str, Any]:
        """An OMA protein entry: its canonical id, species and sequence length."""
        answer = self._get(
            f"{API}/protein/{entry_id}/", f"protein {entry_id}", kind="protein"
        )
        record = answer["record"]
        if not isinstance(record, dict) or not any(
            record.get(key) for key in ("omaid", "canonicalid", "entry_nr")
        ):
            raise ConnectorError("OMA response does not identify a protein record")
        return answer

    @observe("oma_orthologs")
    def orthologs(self, accession: str, rel_type: str | None = None) -> Dict[str, Any]:
        query = f"?{urlencode({'rel_type': rel_type})}" if rel_type else ""
        return self._rows(
            self._get(
                f"{API}/protein/{accession}/orthologs/{query}", f"protein {accession}"
            )
        )

    @observe("oma_entry_names")
    def accessions(self, names: Iterable[str]) -> Dict[str, str]:
        wanted = sorted({n for n in names if n})
        found: Dict[str, str] = {}
        for i in range(0, len(wanted), NAMES_PER_REQUEST):
            chunk = wanted[i : i + NAMES_PER_REQUEST]
            query = urlencode(
                {
                    "query": " OR ".join(f"id:{n}" for n in chunk),
                    "fields": "accession,id",
                    "format": "json",
                    "size": 500,
                }
            )
            answer = self._get(
                f"{UNIPROT_SEARCH}?{query}",
                "entry names",
                source="UniProt",
                kind="names",
                names=chunk,
            )
            record = answer["record"]
            if (
                not isinstance(record, dict)
                or not isinstance(record.get("results"), list)
                or not all(isinstance(row, dict) for row in record["results"])
            ):
                raise ConnectorError(
                    "UniProt entry-name response does not state a results list"
                )
            resolved = active_accessions(answer["record"], chunk)
            note_name_resolution(resolved)
            found.update(resolved)
        return found


class FixtureOMAClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory) / "oma"
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    def _read(
        self, name: str, what: str, kind: str = "rows", names=None
    ) -> Dict[str, Any]:
        if name in self.failing:
            raise ConnectorError(f"OMA request for {name} failed (simulated)")
        path = self.directory / f"{name}.json"
        if not path.is_file():
            raise missing_fixture(f"OMA fixture is unavailable: {name}")
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConnectorError(f"OMA fixture cannot be read: {name}") from exc
        note_response(record, kind=kind, fixture=True, names=names)
        return {
            "retrieved_at": self.retrieved_at,
            "record": record,
        }

    @observe("oma_xrefs", fixture=True)
    def xrefs(self, accession: str) -> Dict[str, Any]:
        return self._read(f"xref_{accession}", f"protein {accession}")

    @observe("oma_protein", fixture=True)
    def protein(self, entry_id: str) -> Dict[str, Any]:
        return self._read(f"protein_{entry_id}", f"protein {entry_id}", kind="protein")

    @observe("oma_orthologs", fixture=True)
    def orthologs(self, accession: str, rel_type: str | None = None) -> Dict[str, Any]:
        found = self._read(f"orthologs_{accession}", f"protein {accession}")
        if rel_type:
            found["record"] = [
                o for o in found["record"] if o.get("rel_type") == rel_type
            ]
        return found

    @observe("oma_entry_names", fixture=True)
    def accessions(self, names: Iterable[str]) -> Dict[str, str]:
        saved = self._read("entry_names", "entry names", kind="names", names=names)[
            "record"
        ]
        resolved = {n: saved[n] for n in names if n in saved}
        note_name_resolution(resolved)
        return resolved


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_orthologs(identifier: str, client: Any = None, skip_digestion: bool = False):
    """OMA's pairwise orthologs of the protein OMA maps a UniProt accession to, with the
    cross-references OMA states for that protein (``seq_match`` says whether OMA's
    sequence is the accession's)."""
    source = online(client, OnlineOMAClient)
    xrefs = source.xrefs(identifier)
    found = source.orthologs(identifier)
    return source_record(
        SOURCE,
        "orthologs",
        {"uniprot": identifier},
        found.get("retrieved_at"),
        None,
        {"xrefs": xrefs["record"], "orthologs": found["record"]},
    )
