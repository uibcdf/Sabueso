"""MedGen (NCBI): the record behind a concept id (#90).

ClinVar names conditions by MedGen concept ids (``C1860808``, or ``CN169374`` for a
concept MedGen created). MONDO states its equivalences to MedGen by the record's UID
(``MEDGEN:349893``), not by the concept id. MedGen states, record by record, which UID a
concept id is. ``concepts(ids)`` asks it, so that a condition named only by a MedGen
concept id can reach MONDO through two statements, MedGen's and MONDO's, and never
through an assumption about identifier schemes.

Only the UID and the concept id are kept. MedGen integrates source vocabularies whose
names can carry their own terms, and no name is needed to join.

``OnlineMedGenClient`` uses the E-utilities (``esearch`` by ``[ConceptId]``, then
``esummary``, in batches), with the optional NCBI key (``tools.db._keys``).
``FixtureMedGenClient`` reads ``<directory>/medgen/concepts.json``.

``concepts(ids)`` returns ``{"retrieved_at", "version", "record": {concept id: uid},
"missing": [...]}``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError
from sabueso.core.ncbi_disease_acquisition import note_fixture, observe, validate
from sabueso.core.source_acquisition import capture_acquisitions, missing_fixture
from sabueso.tools.db import _keys
from sabueso.tools.db._http import request, stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "MedGen"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
BATCH = 100


def _ids(concept_ids: Iterable[str]) -> list:
    return sorted({str(c).split(":")[-1].strip() for c in concept_ids if c})


class OnlineMedGenClient:
    def __init__(self, timeout: float = 60.0, api_key: str | None = None) -> None:
        self.timeout = timeout
        self._api_key = api_key

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        api_key = _keys.key("ncbi", self._api_key)
        query = {**params, "retmode": "json", "tool": "sabueso"}
        if api_key:
            query["api_key"] = api_key
        try:
            with urlopen(  # nosec - trusted endpoint
                request(f"{EUTILS}/{path}?{urlencode(query)}"),
                timeout=self.timeout,
                expect_json=True,
            ) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            validate(SOURCE, path, params, payload)
            return payload
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            detail = _keys.scrub(str(exc), api_key)
            raise ConnectorError(f"MedGen {path} failed: {detail}") from (
                None if api_key else exc  # a key never reaches a traceback
            )

    @observe(SOURCE, "concepts")
    def concepts(self, concept_ids: Iterable[str]) -> Dict[str, Any]:
        ids = _ids(concept_ids)
        retrieval = stamp(SOURCE)
        info = self._get("einfo.fcgi", {"db": "medgen"})
        version = ((info.get("einforesult") or {}).get("dbinfo") or [{}])[0].get(
            "lastupdate"
        )
        record: Dict[str, str] = {}
        for i in range(0, len(ids), BATCH):
            chunk = ids[i : i + BATCH]
            term = " OR ".join(f"{c}[ConceptId]" for c in chunk)
            found = self._get(
                "esearch.fcgi", {"db": "medgen", "term": term, "retmax": 10 * BATCH}
            )
            uids = (found.get("esearchresult") or {}).get("idlist") or []
            if int(found["esearchresult"]["count"]) > len(uids):
                raise ConnectorError(
                    "MedGen identity search is incomplete; missing concepts cannot be established"
                )
            if not uids:
                continue
            summary = self._get("esummary.fcgi", {"db": "medgen", "id": ",".join(uids)})
            result = summary.get("result") or {}
            for uid in result.get("uids") or []:
                concept = (result.get(uid) or {}).get("conceptid")
                if concept in chunk:
                    if concept in record and record[concept] != str(uid):
                        raise ConnectorError(
                            f"MedGen states multiple UIDs for concept {concept}; identity is ambiguous"
                        )
                    record[concept] = str(uid)
        return {
            "retrieved_at": retrieval.value,
            "version": version,
            "record": record,
            "missing": [c for c in ids if c not in record],
        }


class FixtureMedGenClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.path = Path(directory) / "medgen" / "concepts.json"
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe(SOURCE, "concepts", fixture=True)
    def concepts(self, concept_ids: Iterable[str]) -> Dict[str, Any]:
        ids = _ids(concept_ids)
        if self.failing & set(ids):
            raise ConnectorError(f"MedGen request for {ids} failed (simulated)")
        if not self.path.is_file():
            raise missing_fixture("MedGen concept fixture is unavailable")
        try:
            saved = json.loads(self.path.read_text(encoding="utf-8"))
            if (
                not isinstance(saved, dict)
                or not isinstance(saved.get("record"), dict)
                or not all(
                    isinstance(c, str) and isinstance(uid, str) and uid.isdigit()
                    for c, uid in saved["record"].items()
                )
                or (
                    saved.get("version") is not None
                    and not isinstance(saved["version"], str)
                )
            ):
                raise ValueError("invalid concept envelope")
        except (OSError, ValueError) as error:
            raise ConnectorError(
                f"MedGen concept fixture is invalid: {error}"
            ) from error
        note_fixture({"concept_ids": ids}, saved, SOURCE)
        record = {c: saved["record"][c] for c in ids if c in saved["record"]}
        return {
            "retrieved_at": self.retrieved_at,
            "version": saved.get("version"),
            "record": record,
            "missing": [c for c in ids if c not in record],
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_concepts(identifiers: Any, client: Any = None, skip_digestion: bool = False):
    """The MedGen record (UID) of each concept id, as MedGen states it."""
    response = online(client, OnlineMedGenClient).concepts(identifiers)
    return source_record(
        SOURCE,
        "concepts",
        {"concept_ids": _ids(identifiers)},
        response.get("retrieved_at"),
        response.get("version"),
        {"uids": response["record"], "missing": response["missing"]},
    )
