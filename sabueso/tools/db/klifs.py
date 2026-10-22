"""KLIFS: kinase pockets and the conformations of kinase structures (#83, wave 2).

KLIFS (Kooistra et al., Vrije Universiteit Amsterdam) annotates every kinase structure
in the PDB: the kinase it is (with the UniProt accession KLIFS states for it), its
group, family and subfamily, the 85 residues of the ATP pocket in a common numbering,
and, per structure and chain, the conformation (DFG in or out, αC helix in or out), the
ligands, and a quality score.

Access is KLIFS's REST API (``api_v2``, no key):

- ``kinases()``: every kinase KLIFS holds (human and mouse), with its UniProt accession,
  in one request (``kinase_names``), kept for the process;
- ``kinase(kinase_id)``: its classification and pocket sequence (``kinase_information``);
- ``structures(kinase_id)``: its structures, one per PDB entry, chain and alternate
  location (``structures_list``); a kinase with none is answered with an empty list;
- ``pocket(structure_id)``: the author residue number of each pocket position in one
  structure (``interactions_match_residues``).

Each answer is ``{"retrieved_at", "record"}``. ``OnlineKLIFSClient`` queries the API;
``FixtureKLIFSClient`` reads ``<directory>/klifs/``: ``kinase_names.json``,
``kinase_<id>.json``, ``structures_<id>.json`` and ``pocket_<structure id>.json``.

KLIFS states no formal licence; its FAQ says all data is freely available and open, for
academia and industry, and asks to be cited.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "KLIFS"
API = "https://klifs.net/api_v2"


class OnlineKLIFSClient:
    _kinases: Dict[str, Any] | None = None

    def __init__(self, timeout: float = 120.0) -> None:
        self.timeout = timeout

    def _get(self, path: str) -> Any:
        try:
            with urlopen(
                f"{API}/{path}", timeout=self.timeout, expect_json=True
            ) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            try:
                # KLIFS answers 400 with [400, "KLIFS error: …"] for an id it does not hold.
                try:
                    body = json.loads(exc.read().decode("utf-8"))
                except (ValueError, OSError):
                    body = None
                if exc.code == 400 and isinstance(body, list) and len(body) == 2:
                    raise RecordNotFoundError(f"KLIFS: {body[1]}") from exc
                raise ConnectorError(f"KLIFS request failed: {exc}") from exc
            finally:
                exc.close()
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ConnectorError(f"KLIFS request failed: {exc}") from exc

    def kinases(self) -> Dict[str, Any]:
        if OnlineKLIFSClient._kinases is None:
            retrieval = stamp(SOURCE)
            OnlineKLIFSClient._kinases = {
                "retrieved_at": retrieval.value,
                "record": self._get("kinase_names"),
            }
        return OnlineKLIFSClient._kinases

    def kinase(self, kinase_id: int) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        found = self._get(f"kinase_information?kinase_ID={int(kinase_id)}")
        if not found:
            raise RecordNotFoundError(f"KLIFS has no kinase {kinase_id}")
        return {"retrieved_at": retrieval.value, "record": found[0]}

    def structures(self, kinase_id: int) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        try:
            found = self._get(f"structures_list?kinase_ID={int(kinase_id)}")
        except RecordNotFoundError:
            # A kinase KLIFS lists but holds no structure of.
            found = []
        return {"retrieved_at": retrieval.value, "record": found}

    def pocket(self, structure_id: int) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        found = self._get(
            f"interactions_match_residues?structure_ID={int(structure_id)}"
        )
        return {"retrieved_at": retrieval.value, "record": found}


class FixtureKLIFSClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory) / "klifs"
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    def _read(self, name: str) -> Any:
        if name in self.failing:
            raise ConnectorError(f"KLIFS request for {name} failed (simulated)")
        path = self.directory / f"{name}.json"
        if not path.is_file():
            raise RecordNotFoundError(f"KLIFS has no {name}")
        return {
            "retrieved_at": self.retrieved_at,
            "record": json.loads(path.read_text(encoding="utf-8")),
        }

    def kinases(self) -> Dict[str, Any]:
        return self._read("kinase_names")

    def kinase(self, kinase_id: int) -> Dict[str, Any]:
        found = self._read(f"kinase_{int(kinase_id)}")
        return {**found, "record": found["record"][0]}

    def structures(self, kinase_id: int) -> Dict[str, Any]:
        try:
            return self._read(f"structures_{int(kinase_id)}")
        except RecordNotFoundError:
            return {"retrieved_at": self.retrieved_at, "record": []}

    def pocket(self, structure_id: int) -> Dict[str, Any]:
        return self._read(f"pocket_{int(structure_id)}")


def kinases_of(listing: List[Dict[str, Any]], accession: str) -> List[Dict[str, Any]]:
    """The kinases KLIFS states are this UniProt entry (a protein with two kinase
    domains, such as a JAK, has two)."""
    return sorted(
        (k for k in listing if k.get("accession") == accession),
        key=lambda k: k.get("kinase_ID") or 0,
    )


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
def get_kinases(identifier: str, client: Any = None, skip_digestion: bool = False):
    """The KLIFS kinases whose UniProt accession KLIFS states is ``identifier``, each
    with its classification and pocket sequence."""
    source = online(client, OnlineKLIFSClient)
    listing = source.kinases()
    found = [
        source.kinase(k["kinase_ID"])["record"]
        for k in kinases_of(listing["record"], identifier)
    ]
    if not found:
        raise RecordNotFoundError(f"KLIFS states no kinase for {identifier}")
    return source_record(
        SOURCE,
        "kinases",
        {"uniprot": identifier},
        listing.get("retrieved_at"),
        None,
        {"kinases": found},
    )


@arg_digest()
def get_structures(identifier: str, client: Any = None, skip_digestion: bool = False):
    """KLIFS's structures of a kinase (a KLIFS kinase id, e.g. ``"406"``), with their
    conformations."""
    response = online(client, OnlineKLIFSClient).structures(int(identifier))
    return source_record(
        SOURCE,
        "structures",
        {"kinase_id": int(identifier)},
        response.get("retrieved_at"),
        None,
        {"structures": response["record"]},
    )
