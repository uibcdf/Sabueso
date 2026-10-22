"""ClinVar: variants of a human gene and their clinical classification (#83).

ClinVar aggregates what submitters state about variants: a germline classification
("Pathogenic", "Uncertain significance"…, or "Conflicting classifications of
pathogenicity" when submitters disagree), its review status, and the conditions. Records
are found by the NCBI Gene id the UniProt entry cross-references, never by gene symbol.

``variants(gene_ids, limit)`` returns ``{"retrieved_at", "version", "record": [summary,
...], "total_count", "truncated"}``: ClinVar's summaries (E-utilities ``esummary``),
keeping the fields Sabueso maps, at most ``limit`` per gene. ``version`` is the ClinVar
database build. ``OnlineClinVarClient`` uses the E-utilities, with the optional NCBI key
(``api_key=``, or ``$SABUESO_NCBI_KEY``; ``tools.db._keys``); ``FixtureClinVarClient`` reads
``<directory>/clinvar/<gene id>.json``.

Terms: freely available; ClinVar asks to be credited as the source. It is not for
direct diagnostic use or medical decisions without review by a genetics professional.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError
from sabueso.core.ncbi_disease_acquisition import note_fixture, observe, validate
from sabueso.core.source_acquisition import capture_acquisitions, missing_fixture
from sabueso.tools.db import _keys
from sabueso.tools.db._http import request, stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "ClinVar"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
#: Every record of the gene, up to a safety ceiling; a cut is reported.
DEFAULT_LIMIT = 5000
BATCH = 200
KEPT = (
    "uid",
    "accession",
    "accession_version",
    "title",
    "obj_type",
    "protein_change",
    "molecular_consequence_list",
    "genes",
)


def _get(
    path: str, params: Dict[str, Any], timeout: float, api_key: str | None = None
) -> Dict[str, Any]:
    query = {**params, "retmode": "json", "tool": "sabueso"}
    if api_key:
        query["api_key"] = api_key
    url = f"{EUTILS}/{path}?" + urlencode(query)
    try:
        with urlopen(request(url), timeout=timeout, expect_json=True) as resp:  # nosec - trusted
            payload = json.loads(resp.read().decode("utf-8"))
        validate(SOURCE, path, params, payload)
        return payload
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        if isinstance(exc, HTTPError):
            exc.close()
        detail = _keys.scrub(str(exc), api_key)
        raise ConnectorError(f"ClinVar {path} failed: {detail}") from (
            None if api_key else exc  # a key never reaches a traceback
        )


def _summary(record: Dict[str, Any]) -> Dict[str, Any]:
    kept = {k: record.get(k) for k in KEPT}
    classification = record.get("germline_classification") or {}
    kept["germline_classification"] = {
        "description": classification.get("description"),
        "review_status": classification.get("review_status"),
        "last_evaluated": classification.get("last_evaluated"),
        "trait_set": [
            {
                "trait_name": t.get("trait_name"),
                "trait_xrefs": t.get("trait_xrefs") or [],
            }
            for t in classification.get("trait_set") or []
        ],
    }
    kept["variation_set"] = [
        {
            k: v.get(k)
            for k in ("variation_name", "cdna_change", "canonical_spdi", "variant_type")
        }
        for v in record.get("variation_set") or []
    ]
    return kept


class OnlineClinVarClient:
    def __init__(self, timeout: float = 60.0, api_key: str | None = None) -> None:
        self.timeout = timeout
        self._api_key = api_key

    @observe(SOURCE, "variants")
    def variants(
        self, gene_ids: Iterable[str], limit: int = DEFAULT_LIMIT
    ) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        api_key = _keys.key("ncbi", self._api_key)
        info = _get("einfo.fcgi", {"db": "clinvar"}, self.timeout, api_key)
        version = ((info.get("einforesult") or {}).get("dbinfo") or [{}])[0].get(
            "dbbuild"
        )
        records: List[Dict[str, Any]] = []
        total = 0
        for gene in sorted({str(g) for g in gene_ids if g}):
            found = (
                _get(
                    "esearch.fcgi",
                    {"db": "clinvar", "term": f"{gene}[geneid]", "retmax": limit},
                    self.timeout,
                    api_key,
                ).get("esearchresult")
                or {}
            )
            total += int(found.get("count") or 0)
            ids = found.get("idlist") or []
            for i in range(0, len(ids), BATCH):
                result = (
                    _get(
                        "esummary.fcgi",
                        {"db": "clinvar", "id": ",".join(ids[i : i + BATCH])},
                        self.timeout,
                        api_key,
                    ).get("result")
                    or {}
                )
                records.extend(_summary(result[u]) for u in result.get("uids") or [])
        return {
            "retrieved_at": retrieval.value,
            "version": version,
            "record": records,
            "total_count": total,
            "truncated": total > len(records),
        }


class FixtureClinVarClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory) / "clinvar"
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe(SOURCE, "variants", fixture=True)
    def variants(
        self, gene_ids: Iterable[str], limit: int = DEFAULT_LIMIT
    ) -> Dict[str, Any]:
        genes = sorted({str(g) for g in gene_ids if g})
        if self.failing & set(genes):
            raise ConnectorError(f"ClinVar request for {genes} failed (simulated)")
        records, total, version = [], 0, None
        seen_version = False
        for gene in genes:
            path = self.directory / f"{gene}.json"
            if not path.is_file():
                raise missing_fixture(f"ClinVar fixture for Gene {gene} is unavailable")
            try:
                saved = json.loads(path.read_text(encoding="utf-8"))
                if (
                    not isinstance(saved, dict)
                    or not isinstance(saved.get("record"), list)
                    or type(saved.get("total_count")) is not int
                    or saved["total_count"] < len(saved["record"])
                    or not all(isinstance(row, dict) for row in saved["record"])
                ):
                    raise ValueError("invalid variant envelope")
                current = saved.get("version")
                if current is not None and not isinstance(current, str):
                    raise ValueError("invalid database version")
            except (OSError, ValueError) as error:
                raise ConnectorError(
                    f"ClinVar fixture for Gene {gene} is invalid: {error}"
                ) from error
            note_fixture({"gene_ids": [gene], "limit": limit}, saved, SOURCE)
            if seen_version:
                if current != version:
                    raise ConnectorError(
                        "ClinVar fixtures have inconsistent database versions"
                    )
            version = current
            seen_version = True
            total += saved["total_count"]
            records.extend(saved["record"][:limit])
        return {
            "retrieved_at": self.retrieved_at,
            "version": version,
            "record": records,
            "total_count": total,
            "truncated": total > len(records),
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_variants(
    identifiers: Any,
    limit: int = DEFAULT_LIMIT,
    client: Any = None,
    skip_digestion: bool = False,
):
    """ClinVar's variant summaries for NCBI Gene ids, at most ``limit`` per gene."""
    response = online(client, OnlineClinVarClient).variants(identifiers, limit)
    return source_record(
        SOURCE,
        "variants",
        {"gene_ids": list(identifiers), "limit": limit},
        response.get("retrieved_at"),
        response.get("version"),
        {
            "variants": response["record"],
            "total_count": response["total_count"],
            "truncated": response["truncated"],
        },
    )
