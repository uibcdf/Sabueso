"""NCBI Taxonomy: ranks and ancestors of an organism (uibcdf/sabueso#67).

UniProt states an entry's taxon id and a lineage of names without ranks, and for
strain-level taxa its lineage can stop above the species. NCBI Taxonomy gives, per
taxon, its rank and the ids of all its ancestors, which makes relations between
organisms exact (a strain and its species) and lets cohorts be grouped by rank.

``taxa(tax_ids)`` returns ``{"retrieved_at", "record": [taxon, ...], "missing": [...]}``
where each taxon is NCBI's record (``tax_id``, ``organism_name``, ``rank``, ``lineage``:
the ancestor ids from the root). ``OnlineNCBITaxonomyClient`` queries the NCBI Datasets
API in batches; ``FixtureNCBITaxonomyClient`` reads
``<directory>/ncbi_taxonomy/<tax_id>.json``. A taxon NCBI does not hold is listed in
``missing``; a failed request raises ``ConnectorError``.
Fixture-only missing files additionally appear in ``unavailable``; they are not
source-stated missing taxa.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.ncbi_taxonomy_acquisition import note_page, observe
from sabueso.core.source_acquisition import capture_acquisitions, missing_fixture
from sabueso.tools.db import _keys
from sabueso.tools.db._http import request, stamp, urlopen
from sabueso.tools.db._record import online, source_record

DATASETS_TAXON = "https://api.ncbi.nlm.nih.gov/datasets/v2/taxonomy/taxon"
BATCH = 50
KEPT = ("tax_id", "organism_name", "rank", "lineage", "blast_name")


def _ids(tax_ids: Iterable[Any]) -> List[int]:
    return sorted({int(t) for t in tax_ids})


class OnlineNCBITaxonomyClient:
    def __init__(self, timeout: float = 30.0, api_key: str | None = None) -> None:
        self.timeout = timeout
        self._api_key = api_key

    @observe()
    def taxa(self, tax_ids: Iterable[Any]) -> Dict[str, Any]:
        ids = _ids(tax_ids)
        retrieval = stamp("NCBI Taxonomy")
        found: Dict[int, Dict[str, Any]] = {}
        for i in range(0, len(ids), BATCH):
            chunk = ids[i : i + BATCH]
            url = f"{DATASETS_TAXON}/{','.join(map(str, chunk))}"
            api_key = _keys.key("ncbi", self._api_key)
            headers = {"api-key": api_key} if api_key else {}
            try:
                with urlopen(
                    request(url, headers=headers),
                    timeout=self.timeout,
                    expect_json=True,
                ) as resp:  # nosec
                    data = json.loads(resp.read().decode("utf-8"))
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                if isinstance(exc, HTTPError):
                    exc.close()
                detail = _keys.scrub(str(exc), api_key)
                raise ConnectorError(f"NCBI Taxonomy request failed: {detail}") from (
                    None if api_key else exc
                )  # a key never reaches a traceback
            page = note_page(chunk, data)
            for node in data.get("taxonomy_nodes") or []:
                taxon = node.get("taxonomy") or {}
                if taxon.get("tax_id") is not None:
                    found[int(taxon["tax_id"])] = {
                        k: taxon[k] for k in KEPT if k in taxon
                    }
            page.update(
                outcome="received",
                received_ids=[t for t in chunk if t in found],
            )
        return {
            "retrieved_at": retrieval.value,
            "record": [found[t] for t in ids if t in found],
            "missing": [t for t in ids if t not in found],
        }


class FixtureNCBITaxonomyClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[int] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = {int(t) for t in failing or ()}

    @observe(fixture=True)
    def taxa(self, tax_ids: Iterable[Any]) -> Dict[str, Any]:
        ids = _ids(tax_ids)
        if self.failing & set(ids):
            raise ConnectorError("NCBI Taxonomy request failed (simulated)")
        record, missing = [], []
        for t in ids:
            path = self.directory / "ncbi_taxonomy" / f"{t}.json"
            if path.is_file():
                taxon = json.loads(path.read_text(encoding="utf-8"))
                record.append(taxon)
                note_page([t], taxon, fixture=True).update(
                    outcome="received", received_ids=[t]
                )
            else:
                missing.append(t)
                note_page([t], None, fixture=True).update(outcome="unavailable")
        return {
            "retrieved_at": self.retrieved_at,
            "record": record,
            "missing": missing,
            **({"unavailable": list(missing)} if missing else {}),
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_taxon(identifier: str, client: Any = None, skip_digestion: bool = False):
    """NCBI Taxonomy's record of a taxon: rank, name and ancestor ids."""
    response = online(client, OnlineNCBITaxonomyClient).taxa([identifier])
    if not response["record"]:
        if response.get("unavailable"):
            raise missing_fixture(
                f"NCBI Taxonomy fixture is unavailable for {identifier}"
            )
        raise RecordNotFoundError(f"NCBI Taxonomy has no taxon {identifier}")
    return source_record(
        "NCBI Taxonomy",
        "taxon",
        {"tax_id": int(identifier)},
        response.get("retrieved_at"),
        None,
        response["record"][0],
    )
