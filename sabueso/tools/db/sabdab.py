"""SAbDab: antibody structures and the antigens they are bound to (#83, wave 2).

SAbDab (Oxford Protein Informatics Group, CC BY 4.0) annotates every antibody structure
in the PDB: per antibody instance, its heavy and light chains (with chain type: H, κ, λ,
VNAR; a nanobody has no light chain) and the antigens SAbDab assigns to it, each with
the PDB entity and chain it is and its type (protein, peptide, hapten, sugar, ion,
nucleic acid). Chains are given as the PDB names them (``PDB auth_asym_id``).

It publishes its annotations for the PDB as one JSON file (``rcsb-pdb-annotations``,
about 15 MB). ``OnlineSAbDabClient`` downloads it once per process and indexes it by
PDB entry (``tools.db._release``). The file states no release, so its SHA-256 is
recorded with each answer, beside the API version. ``FixtureSAbDabClient`` reads
``<directory>/sabdab/rcsb_pdb_annotations.json``, a subset of the same file.

``complexes(pdb_ids)`` returns ``{"retrieved_at", "version", "checksum", "record":
{pdb_id: [instance, ...]}, "missing": [...]}``: SAbDab's antibody instances as stated
(keys kept), and the entries SAbDab has none for.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError
from sabueso.tools.db import _release
from sabueso.tools.db._http import request, stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "SAbDab"
API = "https://opig.stats.ox.ac.uk/webapps/sabdab-sabpred/sabdab/api"
ANNOTATIONS = f"{API}/rcsb-pdb-annotations"
SPEC = f"{API}/openapi.json"


def classic_id(pdb_id: str) -> str:
    """``1YY9`` from SAbDab's extended id ``pdb_00001yy9`` (or a classic id)."""
    text = str(pdb_id).strip()
    if text.lower().startswith("pdb_") and text[4:8] == "0000":
        return text[8:].upper()
    return text.upper()


def parse_release(payload: bytes) -> tuple:
    """``(checksum, {pdb_id: [instance, ...]})`` of SAbDab's annotations file."""
    checksum = hashlib.sha256(payload).hexdigest()
    index: Dict[str, List[Dict[str, Any]]] = {}
    for instance in json.loads(payload.decode("utf-8")):
        entry = classic_id(instance.get("PDB ID") or "")
        if entry:
            index.setdefault(entry, []).append(instance)
    return checksum, index


def _select(
    index: Dict[str, List[Dict[str, Any]]], pdb_ids: Iterable[str]
) -> Dict[str, Any]:
    ids = sorted({str(p).upper() for p in pdb_ids if p})
    return {
        "record": {p: index[p] for p in ids if p in index},
        "missing": [p for p in ids if p not in index],
    }


class OnlineSAbDabClient:
    def __init__(self, timeout: float = 300.0) -> None:
        self.timeout = timeout

    def _download(self) -> tuple:
        try:
            with urlopen(request(SPEC), timeout=self.timeout, expect_json=True) as resp:  # nosec
                version = json.loads(resp.read().decode("utf-8"))["info"]["version"]
            with urlopen(request(ANNOTATIONS), timeout=self.timeout) as resp:  # nosec
                payload = resp.read()
        except (HTTPError, URLError, TimeoutError, OSError, KeyError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(f"SAbDab download failed: {exc}") from exc
        try:
            checksum, index = parse_release(payload)
        except (UnicodeDecodeError, ValueError) as exc:
            raise ConnectorError(f"SAbDab file could not be read: {exc}") from exc
        return version, checksum, index

    def complexes(self, pdb_ids: Iterable[str]) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        version, checksum, index = _release.remembered(
            SOURCE, "current", self._download
        )
        return {
            "retrieved_at": retrieval.value,
            "version": version,
            "checksum": checksum,
            **_select(index, pdb_ids),
        }


class FixtureSAbDabClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.path = Path(directory) / "sabdab" / "rcsb_pdb_annotations.json"
        self.retrieved_at = retrieved_at
        self.failing = {str(p).upper() for p in failing or ()}

    def complexes(self, pdb_ids: Iterable[str]) -> Dict[str, Any]:
        ids = {str(p).upper() for p in pdb_ids}
        if self.failing & ids:
            raise ConnectorError(f"SAbDab request for {sorted(ids)} failed (simulated)")
        checksum, index = parse_release(self.path.read_bytes())
        return {
            "retrieved_at": self.retrieved_at,
            "version": "2.1.4",
            "checksum": checksum,
            **_select(index, ids),
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
def get_complexes(identifiers: Any, client: Any = None, skip_digestion: bool = False):
    """SAbDab's antibody instances in PDB entries: heavy and light chains, and the
    antigens SAbDab assigns to each, as stated."""
    response = online(client, OnlineSAbDabClient).complexes(identifiers)
    return source_record(
        SOURCE,
        "complexes",
        {"pdb_ids": sorted({str(p).upper() for p in identifiers})},
        response.get("retrieved_at"),
        response.get("version"),
        {"complexes": response["record"], "missing": response["missing"]},
    )
