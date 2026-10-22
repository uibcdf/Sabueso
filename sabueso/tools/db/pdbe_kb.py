"""PDBe-KB ligand binding sites (uibcdf/sabueso#28) and interface residues (#40) of a
protein.

PDBe-KB aggregates, over all PDB structures of a UniProt protein, the residues that each
ligand contacts. Positions are stated in UniProt numbering, with the entries, entities
and chains where each contact is observed. Sabueso records them as ``has_ligand_site``
relationships (``mappings/pdbe_kb.py``) through
``resolve_protein_card(..., ligand_sites=True)``.

``interface_residues(accession)`` is the same for the residues PDBe-KB reports at the
protein's interfaces with other polymer chains, per partner protein
(``has_interface_with``, ``resolve_protein_card(..., interfaces=True)``). PDBe-KB derives
them from the structures (PISA); Sabueso records them as PDBe-KB states them.

``ligand_sites(accession)`` returns ``{accession, retrieved_at, record}``, where
``record`` is PDBe-KB's record for that accession (``sequence``, ``length``, ``dataType``
and ``data``). ``OnlinePDBeKBClient`` queries the PDBe graph API;
``FixturePDBeKBClient`` reads ``<directory>/pdbe_kb/ligand_sites__<accession>.json``. Both
raise ``RecordNotFoundError`` when PDBe-KB holds no ligand sites for the protein (the API
answers 404) and ``ConnectorError`` on failures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.pdbe_kb_acquisition import note_response, observe
from sabueso.core.source_acquisition import capture_acquisitions
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

PDBE_GRAPH_API = "https://www.ebi.ac.uk/pdbe/graph-api"


#: PDBe-KB data kinds: the graph API path and what a missing record means.
KINDS = {
    "ligand_sites": "ligand sites",
    "interface_residues": "interface residues",
}


class OnlinePDBeKBClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    def _fetch(self, kind: str, accession: str) -> Dict[str, Any]:
        url = f"{PDBE_GRAPH_API}/uniprot/{kind}/{accession}"
        retrieval = stamp("PDBe-KB")
        missing = f"PDBe-KB has no {KINDS[kind]} for {accession}"
        try:
            with urlopen(url, timeout=self.timeout, expect_json=True) as resp:  # nosec - trusted endpoint
                data = json.loads(resp.read().decode("utf-8"))
                note_response(data)
        except HTTPError as exc:
            exc.close()
            if exc.code == 404:
                raise RecordNotFoundError(missing) from exc
            raise ConnectorError(
                f"PDBe-KB request for {accession} failed: HTTP {exc.code}"
            ) from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ConnectorError(
                f"PDBe-KB request for {accession} failed: {exc}"
            ) from exc
        record = data.get(accession)
        if not record:
            raise RecordNotFoundError(missing)
        return {
            "accession": accession,
            "retrieved_at": retrieval.value,
            "record": record,
        }

    @observe("ligand_sites")
    def ligand_sites(self, accession: str) -> Dict[str, Any]:
        return self._fetch("ligand_sites", accession)

    @observe("interface_residues")
    def interface_residues(self, accession: str) -> Dict[str, Any]:
        return self._fetch("interface_residues", accession)


class FixturePDBeKBClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    def _read(self, kind: str, accession: str) -> Dict[str, Any]:
        if accession in self.failing:
            raise ConnectorError(f"PDBe-KB request for {accession} failed (simulated)")
        path = self.directory / "pdbe_kb" / f"{kind}__{accession}.json"
        if not path.is_file():
            raise RecordNotFoundError(f"PDBe-KB has no {KINDS[kind]} for {accession}")
        record = json.loads(path.read_text(encoding="utf-8"))
        note_response(record)
        return {
            "accession": accession,
            "retrieved_at": self.retrieved_at,
            "record": record,
        }

    @observe("ligand_sites", fixture=True)
    def ligand_sites(self, accession: str) -> Dict[str, Any]:
        return self._read("ligand_sites", accession)

    @observe("interface_residues", fixture=True)
    def interface_residues(self, accession: str) -> Dict[str, Any]:
        return self._read("interface_residues", accession)


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_ligand_sites(identifier: str, client: Any = None, skip_digestion: bool = False):
    """The residues each ligand contacts in a UniProt protein's structures (PDBe-KB)."""
    response = online(client, OnlinePDBeKBClient).ligand_sites(identifier)
    return source_record(
        "PDBe-KB",
        "ligand_sites",
        {"accession": identifier},
        response.get("retrieved_at"),
        None,
        response.get("record"),
    )


@arg_digest()
@capture_acquisitions
def get_interface_residues(
    identifier: str, client: Any = None, skip_digestion: bool = False
):
    """The residues at a UniProt protein's interfaces, per partner chain (PDBe-KB)."""
    response = online(client, OnlinePDBeKBClient).interface_residues(identifier)
    return source_record(
        "PDBe-KB",
        "interface_residues",
        {"accession": identifier},
        response.get("retrieved_at"),
        None,
        response.get("record"),
    )
