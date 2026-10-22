"""GTEx: the tissues of a GTEx release, with the ontology term GTEx states for each (#102).

GTEx (the Genotype-Tissue Expression project) names each tissue it sampled by a
"tissue site detail" id (``Muscle_Skeletal``), and states the ontology term of each:
an UBERON term for a tissue (``UBERON:0011907``), an EFO term for a cell line
(``EFO:0002009``, cultured fibroblasts). The ids are GTEx's; gnomAD's pext names the same
tissues by them, in lower case.

- ``tissues(dataset)``: the tissue site details of a GTEx release (``gtex_v10``), one
  request.

Each answer is ``{"retrieved_at", "version", "record"}``: ``record`` the tissues as GTEx
states them (id, name, tissue site, ontology id and IRI), ``version`` the requested
dataset label, not a source-confirmed revision. Detached acquisition records retain
that distinction and the single-response scope. A missing fixture is unavailable,
not source-stated absence.
``OnlineGTExClient`` queries the GTEx Portal API (v2, open-access data, free to use with
acknowledgement of the GTEx Portal); ``FixtureGTExClient`` reads
``<directory>/gtex/tissue_site_detail_<dataset>.json``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.gtex_acquisition import note_response, observe
from sabueso.core.source_acquisition import capture_acquisitions, missing_fixture
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "GTEx"
API = "https://gtexportal.org/api/v2"
#: The fields of a tissue site detail Sabueso keeps.
KEPT = (
    "tissueSiteDetailId",
    "tissueSiteDetail",
    "tissueSite",
    "ontologyId",
    "ontologyIri",
)


def kept(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [{k: row.get(k) for k in KEPT} for row in rows]


class OnlineGTExClient:
    def __init__(self, timeout: float = 60.0) -> None:
        self.timeout = timeout

    @observe()
    def tissues(self, dataset: str) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        query = urlencode({"datasetId": dataset, "itemsPerPage": 250})
        url = f"{API}/dataset/tissueSiteDetail?{query}"
        try:
            with urlopen(url, timeout=self.timeout, expect_json=True) as resp:
                found = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            exc.close()
            if exc.code in (404, 422):
                raise RecordNotFoundError(f"GTEx has no dataset {dataset}") from exc
            raise ConnectorError(f"GTEx request failed: {exc}") from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ConnectorError(f"GTEx request failed: {exc}") from exc
        rows = note_response(dataset, found)
        if not rows:
            raise RecordNotFoundError(f"GTEx states no tissues for {dataset}")
        return {
            "retrieved_at": retrieval.value,
            "version": dataset,
            "record": kept(rows),
        }


class FixtureGTExClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory) / "gtex"
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe(fixture=True)
    def tissues(self, dataset: str) -> Dict[str, Any]:
        if dataset in self.failing:
            raise ConnectorError(f"GTEx request for {dataset} failed (simulated)")
        path = self.directory / f"tissue_site_detail_{dataset}.json"
        if not path.is_file():
            raise missing_fixture(f"GTEx fixture is unavailable for {dataset}")
        try:
            found = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConnectorError(f"GTEx fixture could not be read: {exc}") from exc
        rows = note_response(dataset, found, fixture=True)
        return {
            "retrieved_at": self.retrieved_at,
            "version": dataset,
            "record": kept(rows),
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_tissues(dataset: str, client: Any = None, skip_digestion: bool = False):
    """The tissues of a GTEx release, with the ontology term GTEx states for each."""
    response = online(client, OnlineGTExClient).tissues(dataset)
    return source_record(
        SOURCE,
        "tissues",
        {"dataset": dataset},
        response.get("retrieved_at"),
        response.get("version"),
        {"tissues": response["record"]},
    )
