"""GPCRdb: a GPCR's classification, generic residue numbers and structure states (#83).

GPCRdb (Kooistra, Gloriam et al.) curates the G protein-coupled receptors: each receptor
entry states its UniProt accession and sequence, its class and family, and, per residue,
the segment it lies in (TM1-7, loops, helix 8) and its generic number in each scheme
(Ballesteros-Weinstein ``3.32``, GPCRdb ``3.32x32``, and those of classes B, C and F);
per structure, the receptor's activation state (active, inactive, intermediate), the
ligands with their function (agonist, antagonist, inverse agonist…) and the signalling
protein bound.

Access is GPCRdb's REST services (no key; data CC BY 4.0):

- ``receptor(accession)``: the receptor entry of a UniProt accession
  (``protein/accession/<acc>``); ``RecordNotFoundError`` when GPCRdb has none;
- ``residues(entry_name)``: its residues with segments and generic numbers
  (``residues/extended/<entry>``);
- ``structures(entry_name)``: its structures (``structure/protein/<entry>``).

Each answer is ``{"retrieved_at", "record"}``. ``OnlineGPCRdbClient`` queries the
services; ``FixtureGPCRdbClient`` reads ``<directory>/gpcrdb/``: ``receptor_<acc>.json``,
``residues_<entry>.json`` and ``structures_<entry>.json``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "GPCRdb"
API = "https://gpcrdb.org/services"


class OnlineGPCRdbClient:
    def __init__(self, timeout: float = 120.0) -> None:
        self.timeout = timeout

    def _get(self, path: str, what: str) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        try:
            with urlopen(
                f"{API}/{path}", timeout=self.timeout, expect_json=True
            ) as resp:
                found = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            exc.close()
            if exc.code == 404:
                raise RecordNotFoundError(f"GPCRdb has no {what}") from exc
            raise ConnectorError(f"GPCRdb request failed: {exc}") from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ConnectorError(f"GPCRdb request failed: {exc}") from exc
        return {"retrieved_at": retrieval.value, "record": found}

    def receptor(self, accession: str) -> Dict[str, Any]:
        return self._get(f"protein/accession/{accession}/", f"receptor for {accession}")

    def residues(self, entry_name: str) -> Dict[str, Any]:
        return self._get(
            f"residues/extended/{entry_name}/", f"residues of {entry_name}"
        )

    def structures(self, entry_name: str) -> Dict[str, Any]:
        return self._get(
            f"structure/protein/{entry_name}/", f"structures of {entry_name}"
        )


class FixtureGPCRdbClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory) / "gpcrdb"
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    def _read(self, name: str, what: str) -> Dict[str, Any]:
        if name in self.failing:
            raise ConnectorError(f"GPCRdb request for {name} failed (simulated)")
        path = self.directory / f"{name}.json"
        if not path.is_file():
            raise RecordNotFoundError(f"GPCRdb has no {what}")
        return {
            "retrieved_at": self.retrieved_at,
            "record": json.loads(path.read_text(encoding="utf-8")),
        }

    def receptor(self, accession: str) -> Dict[str, Any]:
        return self._read(f"receptor_{accession}", f"receptor for {accession}")

    def residues(self, entry_name: str) -> Dict[str, Any]:
        return self._read(f"residues_{entry_name}", f"residues of {entry_name}")

    def structures(self, entry_name: str) -> Dict[str, Any]:
        try:
            return self._read(f"structures_{entry_name}", f"structures of {entry_name}")
        except RecordNotFoundError:
            return {"retrieved_at": self.retrieved_at, "record": []}


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
def get_receptor(identifier: str, client: Any = None, skip_digestion: bool = False):
    """The GPCRdb receptor entry of a UniProt accession, with its residues (segments
    and generic numbers) and its structures (states, ligands, signalling proteins)."""
    source = online(client, OnlineGPCRdbClient)
    receptor = source.receptor(identifier)
    entry_name = receptor["record"]["entry_name"]
    return source_record(
        SOURCE,
        "receptor",
        {"uniprot": identifier},
        receptor.get("retrieved_at"),
        None,
        {
            "receptor": receptor["record"],
            "residues": source.residues(entry_name)["record"],
            "structures": source.structures(entry_name)["record"],
        },
    )
