"""AlphaFold DB predicted structures of a UniProt protein (uibcdf/sabueso#57).

A predicted model is not an experimental observation. It has no resolution; it has a
per-residue confidence (pLDDT) summarized by the database, a model version and the
tool that produced it. Sabueso records it as a ``has_predicted_structure``
relationship (``mappings/alphafold.py``), apart from experimental ``has_structure``, so
that views about experimental structures never count models. Sabueso never downloads
coordinates: loading structures belongs to MolSysMT.

``prediction(accession)`` returns ``{accession, retrieved_at, record}``, where
``record`` is AlphaFold DB's list of models for the accession (one per fragment for
long proteins). ``OnlineAlphaFoldClient`` queries the AlphaFold DB API;
``FixtureAlphaFoldClient`` reads ``<directory>/alphafold/<accession>.json``. Both raise
``RecordNotFoundError`` when AlphaFold DB holds no model for the accession, and
``ConnectorError`` on failures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.alphafold_acquisition import note_response, observe
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.source_acquisition import capture_acquisitions
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

ALPHAFOLD_API = "https://alphafold.ebi.ac.uk/api/prediction"


class OnlineAlphaFoldClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    @observe()
    def prediction(self, accession: str) -> Dict[str, Any]:
        retrieval = stamp("AlphaFold DB")
        try:
            with urlopen(  # nosec - trusted endpoint
                f"{ALPHAFOLD_API}/{accession}", timeout=self.timeout, expect_json=True
            ) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                note_response(data)
        except HTTPError as exc:
            exc.close()
            if exc.code == 404:
                raise RecordNotFoundError(
                    f"AlphaFold DB has no model for {accession}"
                ) from exc
            raise ConnectorError(
                f"AlphaFold DB request for {accession} failed: HTTP {exc.code}"
            ) from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ConnectorError(
                f"AlphaFold DB request for {accession} failed: {exc}"
            ) from exc
        if not data:
            raise RecordNotFoundError(f"AlphaFold DB has no model for {accession}")
        return {"accession": accession, "retrieved_at": retrieval.value, "record": data}


class FixtureAlphaFoldClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe(fixture=True)
    def prediction(self, accession: str) -> Dict[str, Any]:
        if accession in self.failing:
            raise ConnectorError(
                f"AlphaFold DB request for {accession} failed (simulated)"
            )
        path = self.directory / "alphafold" / f"{accession}.json"
        if not path.is_file():
            raise RecordNotFoundError(f"AlphaFold DB has no model for {accession}")
        record = json.loads(path.read_text(encoding="utf-8"))
        note_response(record)
        return {
            "accession": accession,
            "retrieved_at": self.retrieved_at,
            "record": record,
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_prediction(identifier: str, client: Any = None, skip_digestion: bool = False):
    """The predicted structural models of a UniProt protein (AlphaFold DB)."""
    response = online(client, OnlineAlphaFoldClient).prediction(identifier)
    models = response.get("record") or []
    versions = sorted(
        {m.get("latestVersion") for m in models if m.get("latestVersion")}
    )
    return source_record(
        "AlphaFold DB",
        "prediction",
        {"accession": identifier},
        response.get("retrieved_at"),
        "; ".join(f"v{v}" for v in versions) or None,
        models,
    )
