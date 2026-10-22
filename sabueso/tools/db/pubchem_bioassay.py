"""PubChem BioAssay: the assays PubChem links to a protein (uibcdf/sabueso#68).

Many PubChem assays are deposited by other databases, ChEMBL and BindingDB above all,
and state it: ``SourceName`` and ``SourceID`` name the depositor and its own assay id.
Sabueso records such data as copies with a declared origin (``copy_of``). They are
pointers: grouped with the original when the card holds it, and leading to it when it
does not. They are never counted as independent confirmations.

``assays(accession, limit)`` returns ``{accession, retrieved_at, record}``, where
``record`` holds:

- ``aids``: the assay ids with results for the protein;
- ``summaries``: per assay kept, the name, depositor and its assay id;
- ``concise``: per assay kept, the table of results. Each row holds the SID, the CID,
  the outcome, the target accession, the value in µM, the activity name and the PubMed
  id. The relation of a value (``>``) is not in this table;
- ``inchikeys``: the InChIKey PubChem states for each CID, so molecules are anchored
  without computing anything;
- ``rows``, ``total_rows``, ``row_order``: the rows kept of the protein's rows, and the
  rule that ordered them (#98).

Every result of a target comes from **one** request,
``assay/target/accession/<acc>/concise``: PubChem's rows for that protein, from every
assay. Rows of another protein (a multi-target assay) are left out. Up to ``limit``
rows are kept (5000 by default, #88), in the order of ``pubchem_row_order@1``:
confirmatory rows with a value, then other rows with a value, then rows without one,
each by AID and SID. Assay summaries and InChIKeys are asked in batches, and requests
keep to PubChem's policy of at most five per second.

``OnlinePubChemBioAssayClient`` queries PUG REST; ``FixturePubChemBioAssayClient`` reads
``<directory>/pubchem_bioassay/<accession>.json`` and applies the same ceiling.
"""

from __future__ import annotations

import csv
import io
import json
import time
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.pubchem_acquisition import note_response, observe
from sabueso.core.source_acquisition import capture_acquisitions
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

PUG = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
#: PubChem asks for no more than five requests per second.
PAUSE = 0.25
#: Every result up to a safety ceiling, unless ``pubchem_bioassay={"limit": n}`` asks
#: for fewer; a cut is reported (#88).
DEFAULT_LIMIT = 5000
ROW_ORDER = "pubchem_row_order@1"


def _order(accession: str, cell: Dict[str, str]) -> tuple:
    """``pubchem_row_order@1``: confirmatory rows with a value, then other rows with a
    value, then rows without one; each by AID and SID."""
    has_value = bool(str(cell.get("Activity Value [uM]") or "").strip())
    confirmatory = cell.get("Assay Type") == "Confirmatory"
    rank = 0 if has_value and confirmatory else 1 if has_value else 2
    return (rank, int(cell.get("AID") or 0), int(cell.get("SID") or 0))


def keep_rows(record: Dict[str, Any], accession: str, limit: int) -> Dict[str, Any]:
    """The record with the protein's rows cut to ``limit`` by ``pubchem_row_order@1``,
    and its summaries and InChIKeys cut to the assays and compounds kept."""
    rows = []
    for aid, table in (record.get("concise") or {}).items():
        columns = (table.get("Columns") or {}).get("Column") or []
        for row in table.get("Row") or []:
            cell = dict(zip(columns, row.get("Cell") or []))
            cell.setdefault("AID", str(aid))
            if cell.get("Target Accession") not in (accession, "", None):
                continue  # a row of a multi-target assay about another protein
            rows.append((columns, row, cell))
    rows.sort(key=lambda r: _order(accession, r[2]))
    kept = rows[:limit]
    concise: Dict[str, Dict[str, Any]] = {}
    for columns, row, cell in sorted(kept, key=lambda r: _order("", r[2])[1:]):
        table = concise.setdefault(
            str(cell["AID"]), {"Columns": {"Column": columns}, "Row": []}
        )
        table["Row"].append(row)
    cids = {str(cell.get("CID")) for _, _, cell in kept if cell.get("CID")}
    return {
        **record,
        "aids": sorted({int(cell["AID"]) for _, _, cell in rows}),
        "summaries": [
            s for s in record.get("summaries") or [] if str(s.get("AID")) in concise
        ],
        "concise": concise,
        "inchikeys": {
            k: v for k, v in (record.get("inchikeys") or {}).items() if k in cids
        },
        "rows": len(kept),
        "total_rows": len(rows),
        "row_order": ROW_ORDER,
    }


class OnlinePubChemBioAssayClient:
    def __init__(self, timeout: float = 90.0) -> None:
        self.timeout = timeout

    def _get(self, path: str, as_text: bool = False) -> Any:
        try:
            with urlopen(f"{PUG}/{path}", timeout=self.timeout) as resp:  # nosec
                body = resp.read().decode("utf-8")
                data = body if as_text else json.loads(body)
        except HTTPError as exc:
            exc.close()
            if exc.code == 404:
                raise RecordNotFoundError(f"PubChem has no {path}") from exc
            raise ConnectorError(
                f"PubChem request {path} failed: HTTP {exc.code}"
            ) from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ConnectorError(f"PubChem request {path} failed: {exc}") from exc
        time.sleep(PAUSE)
        note_response(path, data)
        return data

    @observe("assays")
    def assays(self, accession: str, limit: int = DEFAULT_LIMIT) -> Dict[str, Any]:
        retrieval = stamp("PubChem BioAssay")
        # One request for every result of the target, in every assay (#98).
        text = self._get(f"assay/target/accession/{accession}/concise/CSV", True)
        reader = csv.reader(io.StringIO(text))
        columns = next(reader, [])
        concise: Dict[str, Dict[str, Any]] = {}
        for cells in reader:
            aid = cells[0] if cells else ""
            if not aid:
                continue
            table = concise.setdefault(aid, {"Columns": {"Column": columns}, "Row": []})
            table["Row"].append({"Cell": cells})
        if not concise:
            raise RecordNotFoundError(f"PubChem links no assay to {accession}")
        record = keep_rows({"concise": concise}, accession, limit)
        if not record["concise"]:
            raise RecordNotFoundError(f"PubChem states no result for {accession}")
        aids = sorted(record["concise"], key=int)
        summaries = []
        for i in range(0, len(aids), 50):
            chunk = ",".join(aids[i : i + 50])
            summaries += self._get(f"assay/aid/{chunk}/summary/JSON")["AssaySummaries"][
                "AssaySummary"
            ]
        cids = sorted(
            {
                row["Cell"][columns.index("CID")]
                for t in record["concise"].values()
                for row in t["Row"]
                if row["Cell"][columns.index("CID")]
            },
            key=int,
        )
        inchikeys: Dict[str, str] = {}
        for i in range(0, len(cids), 100):
            chunk = ",".join(cids[i : i + 100])
            table = self._get(f"compound/cid/{chunk}/property/InChIKey/JSON")
            for prop in table["PropertyTable"]["Properties"]:
                inchikeys[str(prop["CID"])] = prop.get("InChIKey")
        return {
            "accession": accession,
            "retrieved_at": retrieval.value,
            "record": {**record, "summaries": summaries, "inchikeys": inchikeys},
        }


class FixturePubChemBioAssayClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe("assays", fixture=True)
    def assays(self, accession: str, limit: int = DEFAULT_LIMIT) -> Dict[str, Any]:
        if accession in self.failing:
            raise ConnectorError(f"PubChem request for {accession} failed (simulated)")
        path = self.directory / "pubchem_bioassay" / f"{accession}.json"
        if not path.is_file():
            raise RecordNotFoundError(f"PubChem links no assay to {accession}")
        record = json.loads(path.read_text(encoding="utf-8"))
        record["concise"] = {str(k): v for k, v in record["concise"].items()}
        return {
            "accession": accession,
            "retrieved_at": self.retrieved_at,
            "record": keep_rows(record, accession, limit),
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_assays(
    identifier: str,
    limit: int = DEFAULT_LIMIT,
    client: Any = None,
    skip_digestion: bool = False,
):
    """PubChem's results for a UniProt protein, with their assays and depositors, up to
    ``limit`` rows (``pubchem_row_order@1``)."""
    response = online(client, OnlinePubChemBioAssayClient).assays(identifier, limit)
    record = response.get("record") or {}
    return source_record(
        "PubChem BioAssay",
        "assays",
        {"accession": identifier, "limit": limit},
        response.get("retrieved_at"),
        None,
        record,
        truncated=record.get("total_rows", 0) > record.get("rows", 0),
    )
