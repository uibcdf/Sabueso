"""Orphadata (Orphanet): genes associated with rare diseases (#82, #83).

Orphanet curates, per rare disorder, the genes associated with it: the type of
association (e.g. "Disease-causing germline mutation(s) in"), its status ("Assessed"),
and the publications that validate it. Each gene states its UniProt (Swiss-Prot)
accession, so a card joins through an identifier the source states.

The data is published as one XML file (``en_product6.xml``, CC BY 4.0), dated in its
header. ``OnlineOrphadataClient`` downloads it (about 22 MB) and indexes it once per
process, in memory; nothing is written. The version recorded is the file's date. ``FixtureOrphadataClient`` reads
``<directory>/orphadata/en_product6.xml``.

``associations(accession)`` returns ``{"retrieved_at", "version", "record": [row,
...]}``, one row per disorder–gene association naming the accession. It raises
``RecordNotFoundError`` when no association names it.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET  # nosec - a trusted source's own file
from pathlib import Path
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.orphadata_acquisition import (
    ObservedIndex,
    document,
    note_index,
    observe,
)
from sabueso.core.source_acquisition import capture_acquisitions, missing_fixture
from sabueso.tools.db import _release
from sabueso.tools.db._http import request, stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "Orphanet"
URL = "https://www.orphadata.com/data/xml/en_product6.xml"


def _text(node: Any, path: str) -> str | None:
    found = node.find(path) if node is not None else None
    return found.text.strip() if found is not None and found.text else None


def parse_release(xml: bytes) -> tuple:
    """``(version, {accession: [row, ...]})`` of an ``en_product6.xml`` file."""
    root = ET.fromstring(xml)  # nosec - a trusted source's own file
    version = (root.get("date") or "")[:10] or None
    index: Dict[str, List[Dict[str, Any]]] = {}
    for disorder in root.iter("Disorder"):
        code = _text(disorder, "OrphaCode")
        base = {
            "orpha_code": code,
            "disorder_name": _text(disorder, "Name"),
            "disorder_type": _text(disorder, "DisorderType/Name"),
            "disorder_group": _text(disorder, "DisorderGroup/Name"),
        }
        for association in disorder.iter("DisorderGeneAssociation"):
            gene = association.find("Gene")
            refs = {
                _text(r, "Source"): _text(r, "Reference")
                for r in (gene.iter("ExternalReference") if gene is not None else [])
            }
            accession = refs.get("SwissProt")
            if not accession:
                continue
            validation = _text(association, "SourceOfValidation")
            row = {
                **base,
                "gene_symbol": _text(gene, "Symbol"),
                "gene_name": _text(gene, "Name"),
                "ensembl_gene": refs.get("Ensembl"),
                "hgnc": refs.get("HGNC"),
                "omim": refs.get("OMIM"),
                "association_type": _text(
                    association, "DisorderGeneAssociationType/Name"
                ),
                "association_status": _text(
                    association, "DisorderGeneAssociationStatus/Name"
                ),
                "validation": [v.replace("[PMID]", "") for v in validation.split("_")]
                if validation
                else [],
            }
            index.setdefault(accession, []).append(
                {k: v for k, v in row.items() if v not in (None, "", [])}
            )
    return version, index


def genes_of(
    index: Dict[str, List[Dict[str, Any]]], orpha_code: str
) -> List[Dict[str, Any]]:
    """The gene associations of one disorder (``ORPHA:868`` or ``868``), each with the
    UniProt accession Orphanet states for the gene (#90)."""
    code = str(orpha_code).split(":")[-1]
    return [
        {**row, "uniprot": accession}
        for accession, rows in sorted(index.items())
        for row in rows
        if str(row.get("orpha_code")) == code
    ]


def _parse_document(payload):
    try:
        root = ET.fromstring(payload)  # nosec - source document sanity check
        if root.tag != "JDBOR" or root.find("DisorderList") is None:
            raise ConnectorError("Orphadata document has no native disorder list.")
        return parse_release(payload)
    except (ET.ParseError, ValueError) as error:
        raise ConnectorError(f"Orphadata file is not valid XML: {error}") from error


class OnlineOrphadataClient:
    def __init__(self, timeout: float = 300.0):
        self.timeout = timeout

    def _index(self) -> tuple:
        """``(version, index)`` of the file, downloaded and parsed once per process.
        The file's date is known only once it is read, so it is kept under one key."""
        reused = _release.recall(SOURCE, "en_product6") is not None
        index = _release.remembered(SOURCE, "en_product6", self._download)
        note_index(index, getattr(index, "origin", None), reused=reused)
        return index

    def _download(self) -> tuple:
        from sabueso.tools.db._http import observing_requests

        retrieval = stamp(SOURCE)
        try:
            with (
                observing_requests() as receipts,
                urlopen(request(URL), timeout=self.timeout) as resp,
            ):  # nosec - trusted
                payload = resp.read()
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(f"Orphadata download failed: {exc}") from exc
        origin = document(
            payload, getattr(resp, "retrieved_at", None) or retrieval.value, receipts
        )
        return ObservedIndex(_parse_document(payload), origin)

    @observe("associations")
    def associations(self, accession: str) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        native = self._index()
        version, index = native
        if accession not in index:
            raise RecordNotFoundError(
                f"Orphadata ({version}) names no gene with UniProt {accession}",
                version=version,
            )
        return {
            "retrieved_at": (getattr(native, "origin", None) or {}).get("retrieved_at")
            or retrieval.value,
            "version": version,
            "record": index[accession],
        }

    @observe("genes")
    def genes(self, orpha_code: str) -> Dict[str, Any]:
        """The genes Orphanet associates with a disorder: ``{"retrieved_at",
        "version", "record": [row with "uniprot", ...]}``."""
        retrieval = stamp(SOURCE)
        native = self._index()
        version, index = native
        rows = genes_of(index, orpha_code)
        if not rows:
            raise RecordNotFoundError(
                f"Orphadata ({version}) names no gene for ORPHA:{orpha_code}",
                version=version,
            )
        return {
            "retrieved_at": (getattr(native, "origin", None) or {}).get("retrieved_at")
            or retrieval.value,
            "version": version,
            "record": rows,
        }


class FixtureOrphadataClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.path = Path(directory) / "orphadata" / "en_product6.xml"
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    def _index(self):
        try:
            payload = self.path.read_bytes()
        except FileNotFoundError as error:
            raise missing_fixture(
                f"Orphadata fixture is unavailable: {self.path.name}"
            ) from error
        except OSError as error:
            raise ConnectorError(
                f"Orphadata fixture could not be read: {error}"
            ) from error
        origin = document(payload, self.retrieved_at, fixture=True)
        index = _parse_document(payload)
        note_index(index, origin)
        return index

    @observe("associations", fixture=True)
    def associations(self, accession: str) -> Dict[str, Any]:
        if accession in self.failing:
            raise ConnectorError(
                f"Orphadata request for {accession} failed (simulated)"
            )
        version, index = self._index()
        if accession not in index:
            raise RecordNotFoundError(
                f"Orphadata names no gene with UniProt {accession}", version=version
            )
        return {
            "retrieved_at": self.retrieved_at,
            "version": version,
            "record": index[accession],
        }

    @observe("genes", fixture=True)
    def genes(self, orpha_code: str) -> Dict[str, Any]:
        if orpha_code in self.failing:
            raise ConnectorError(
                f"Orphadata request for {orpha_code} failed (simulated)"
            )
        version, index = self._index()
        rows = genes_of(index, orpha_code)
        if not rows:
            raise RecordNotFoundError(
                f"Orphadata names no gene for ORPHA:{orpha_code}", version=version
            )
        return {"retrieved_at": self.retrieved_at, "version": version, "record": rows}


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_associations(identifier: str, client: Any = None, skip_digestion: bool = False):
    """Orphanet's rare-disorder associations of a gene, by its UniProt accession."""
    response = online(client, OnlineOrphadataClient).associations(identifier)
    return source_record(
        SOURCE,
        "associations",
        {"uniprot": identifier},
        response.get("retrieved_at"),
        response.get("version"),
        response["record"],
    )
