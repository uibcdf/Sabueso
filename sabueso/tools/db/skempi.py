"""SKEMPI 2.0: binding changes of mutations at protein–protein interfaces (#83).

SKEMPI curates, from publications, how mutations at the interface of a protein complex
of known structure change its binding: the affinities of the mutant and the wild type,
and, where measured, kinetics (kon, koff) and thermodynamics (ΔH, ΔS). Each row names a
PDB entry, the chains of its two sides (``1BRS_A_D``), and the mutations in that entry's
author numbering (``KA27A``: Lys 27 of chain A to Ala).

It is published as one CSV file (CC BY 4.0). ``OnlineSKEMPIClient`` downloads it once per
process and indexes it by PDB entry (``tools.db._release``); the file states no finer
version than the database's (2.0), so its SHA-256 is recorded with each answer, and a
corrected file is told apart. ``FixtureSKEMPIClient`` reads
``<directory>/skempi/skempi_v2.csv``, a subset of the same file.

``mutations(pdb_ids)`` returns ``{"retrieved_at", "version", "checksum", "record":
{pdb_id: [row, ...]}, "missing": [...]}``: SKEMPI's rows as stated (column names
kept), and the entries SKEMPI has no row for.
"""

from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError
from sabueso.tools.db import _release
from sabueso.tools.db._http import request, stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "SKEMPI"
VERSION = "2.0"
URL = "https://life.bsc.es/pid/skempi2/database/download/skempi_v2.csv"


def parse_release(payload: bytes) -> tuple:
    """``(checksum, {pdb_id: [row, ...]})`` of the SKEMPI CSV file."""
    checksum = hashlib.sha256(payload).hexdigest()
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8")), delimiter=";")
    index: Dict[str, List[Dict[str, str]]] = {}
    for row in reader:
        entry = (row.get("#Pdb") or "").split("_")[0].upper()
        if entry:
            index.setdefault(entry, []).append(dict(row))
    return checksum, index


def _select(
    index: Dict[str, List[Dict[str, str]]], pdb_ids: Iterable[str]
) -> Dict[str, Any]:
    ids = sorted({str(p).upper() for p in pdb_ids if p})
    return {
        "record": {p: index[p] for p in ids if p in index},
        "missing": [p for p in ids if p not in index],
    }


class OnlineSKEMPIClient:
    def __init__(self, timeout: float = 120.0) -> None:
        self.timeout = timeout

    def _download(self) -> tuple:
        try:
            with urlopen(request(URL), timeout=self.timeout) as resp:  # nosec - trusted
                payload = resp.read()
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(f"SKEMPI download failed: {exc}") from exc
        try:
            return parse_release(payload)
        except (UnicodeDecodeError, csv.Error) as exc:
            raise ConnectorError(f"SKEMPI file could not be read: {exc}") from exc

    def mutations(self, pdb_ids: Iterable[str]) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        checksum, index = _release.remembered(SOURCE, VERSION, self._download)
        return {
            "retrieved_at": retrieval.value,
            "version": VERSION,
            "checksum": checksum,
            **_select(index, pdb_ids),
        }


class FixtureSKEMPIClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.path = Path(directory) / "skempi" / "skempi_v2.csv"
        self.retrieved_at = retrieved_at
        self.failing = {str(p).upper() for p in failing or ()}

    def mutations(self, pdb_ids: Iterable[str]) -> Dict[str, Any]:
        ids = {str(p).upper() for p in pdb_ids}
        if self.failing & ids:
            raise ConnectorError(f"SKEMPI request for {sorted(ids)} failed (simulated)")
        checksum, index = parse_release(self.path.read_bytes())
        return {
            "retrieved_at": self.retrieved_at,
            "version": VERSION,
            "checksum": checksum,
            **_select(index, ids),
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
def get_mutations(identifiers: Any, client: Any = None, skip_digestion: bool = False):
    """SKEMPI's rows for PDB entries: interface mutations of each complex, with the
    binding affinities, kinetics and thermodynamics of mutant and wild type as stated."""
    response = online(client, OnlineSKEMPIClient).mutations(identifiers)
    return source_record(
        SOURCE,
        "mutations",
        {"pdb_ids": sorted({str(p).upper() for p in identifiers})},
        response.get("retrieved_at"),
        response.get("version"),
        {"rows": response["record"], "missing": response["missing"]},
    )
