"""PDB Chemical Component Dictionary (CCD) records of structure ligands (uibcdf/sabueso#25).

A structure lists its ligands by chemical-component code (e.g. ``BTS``, ``SO4``). The
wwPDB Chemical Component Dictionary gives each code its chemistry: name, formula, type,
SMILES and a standard InChI/InChIKey. That InChIKey is what lets a structure ligand be
recognised as the same molecule that other sources describe
(``sabueso.tools.card.small_molecule``).

``components(comp_ids)`` returns ``{retrieved_at, components, missing}``: the records found,
keyed by code, and the requested codes that the CCD does not hold. RCSB omits unknown
codes from a batch without an error, so ``missing`` is computed, never assumed empty.
``OnlineCCDClient`` queries the RCSB GraphQL service; ``FixtureCCDClient`` reads
``<directory>/pdb_ccd/<CODE>.json``. Both raise ``ConnectorError`` on failures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError
from urllib.request import Request

from sabueso._private.argdigest import arg_digest
from sabueso.core.chemical_identity_acquisition import note_response, observe
from sabueso.core.errors import ConnectorError
from sabueso.core.source_acquisition import capture_acquisitions
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

RCSB_GRAPHQL = "https://data.rcsb.org/graphql"
COMPONENTS_QUERY = """query($ids: [String!]!) { chem_comps(comp_ids: $ids) {
  chem_comp { id name formula type formula_weight pdbx_release_status }
  rcsb_chem_comp_descriptor { InChI InChIKey SMILES SMILES_stereo }
} }"""


def _codes(comp_ids: Iterable[str]) -> List[str]:
    return sorted({c.upper() for c in comp_ids if c})


class OnlineCCDClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    @observe("PDB CCD", "components")
    def components(self, comp_ids: Iterable[str]) -> Dict[str, Any]:
        codes = _codes(comp_ids)
        retrieval = stamp("PDB CCD")
        if not codes:
            return {"retrieved_at": retrieval.value, "components": {}, "missing": []}
        body = json.dumps(
            {"query": COMPONENTS_QUERY, "variables": {"ids": codes}}
        ).encode("utf-8")
        request = Request(
            RCSB_GRAPHQL, data=body, headers={"Content-Type": "application/json"}
        )
        try:
            with urlopen(request, timeout=self.timeout, expect_json=True) as resp:  # nosec - trusted endpoint
                data = json.loads(resp.read().decode("utf-8"))
                note_response(data)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(f"CCD request for {codes} failed: {exc}") from exc
        if data.get("errors"):
            raise ConnectorError(f"CCD request for {codes} failed: {data['errors']}")
        found = {
            record["chem_comp"]["id"]: record
            for record in (data.get("data") or {}).get("chem_comps") or []
            if record and record.get("chem_comp")
        }
        return {
            "retrieved_at": retrieval.value,
            "components": found,
            "missing": [c for c in codes if c not in found],
        }


class FixtureCCDClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe("PDB CCD", "components", fixture=True)
    def components(self, comp_ids: Iterable[str]) -> Dict[str, Any]:
        codes = _codes(comp_ids)
        if self.failing & set(codes):
            raise ConnectorError(f"CCD request for {codes} failed (simulated)")
        found: Dict[str, Any] = {}
        for code in codes:
            path = self.directory / "pdb_ccd" / f"{code}.json"
            if path.is_file():
                found[code] = json.loads(path.read_text(encoding="utf-8"))
                note_response(found[code], code=code)
        return {
            "retrieved_at": self.retrieved_at,
            "components": found,
            "missing": [c for c in codes if c not in found],
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_components(identifiers: Any, client: Any = None, skip_digestion: bool = False):
    """PDB Chemical Component Dictionary records by component code."""
    response = online(client, OnlineCCDClient).components(identifiers)
    return source_record(
        "PDB CCD",
        "components",
        {"codes": list(identifiers)},
        response.get("retrieved_at"),
        None,
        {"components": response.get("components"), "missing": response.get("missing")},
    )
