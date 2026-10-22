"""NCBI Gene: the UniProt entries a gene's products are (uibcdf/sabueso#69).

``gene(gene_id)`` returns ``(record, retrieved_at)``, the record parsed by
``sabueso.mappings.ncbi_gene.parse_gene``. ``OnlineNCBIGeneClient`` queries Entrez
E-utilities (``efetch``, XML); ``FixtureNCBIGeneClient`` reads
``<directory>/ncbi_gene/<gene_id>.xml``. Both raise ``RecordNotFoundError`` when NCBI
holds no such gene and ``ConnectorError`` when the source cannot answer.

An NCBI key is optional (``api_key=``, or ``$SABUESO_NCBI_KEY``; ``tools.db._keys``): it
raises NCBI's rate limit, and changes nothing in what NCBI answers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.mappings.ncbi_gene import parse_gene
from sabueso.tools.db import _keys
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def _record(gene_id: str, xml: str) -> Dict[str, Any]:
    record = parse_gene(xml)
    if record is None:
        raise RecordNotFoundError(f"NCBI Gene has no gene {gene_id}")
    return record


class OnlineNCBIGeneClient:
    def __init__(self, timeout: float = 30.0, api_key: str | None = None) -> None:
        self.timeout = timeout
        self._api_key = api_key

    def gene(self, gene_id: str) -> Tuple[Dict[str, Any], str]:
        query = {"db": "gene", "id": str(gene_id), "retmode": "xml"}
        api_key = _keys.key("ncbi", self._api_key)
        if api_key:
            query["api_key"] = api_key
        url = f"{EFETCH}?{urlencode(query)}"
        retrieval = stamp("NCBI Gene")
        try:
            with urlopen(url, timeout=self.timeout) as resp:  # nosec - trusted endpoint
                xml = resp.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            detail = _keys.scrub(str(exc), api_key)
            raise ConnectorError(
                f"NCBI Gene request for {gene_id} failed: {detail}"
            ) from (None if api_key else exc)  # a key never reaches a traceback
        return _record(str(gene_id), xml), retrieval.value


class FixtureNCBIGeneClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = {str(g) for g in failing or ()}

    def gene(self, gene_id: str) -> Tuple[Dict[str, Any], str]:
        if str(gene_id) in self.failing:
            raise ConnectorError(f"NCBI Gene request for {gene_id} failed (simulated)")
        path = self.directory / "ncbi_gene" / f"{gene_id}.xml"
        if not path.is_file():
            raise RecordNotFoundError(f"NCBI Gene has no gene {gene_id}")
        return _record(
            str(gene_id), path.read_text(encoding="utf-8")
        ), self.retrieved_at


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
def get_gene(identifier: str, client: Any = None, skip_digestion: bool = False):
    """NCBI Gene's record of a gene: symbol, locus tag, taxon, and the UniProt entries
    of its products."""
    record, retrieved_at = online(client, OnlineNCBIGeneClient).gene(identifier)
    return source_record(
        "NCBI Gene", "gene", {"gene_id": str(identifier)}, retrieved_at, None, record
    )
