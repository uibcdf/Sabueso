"""ClinicalTrials.gov: registered clinical studies, by NCT id (uibcdf/sabueso#81).

A study names its interventions only as text ("Benznidazole", a brand name, a code), so
it is never matched to a molecule by name. Sabueso asks only for the NCT ids another
source states for a molecule: ChEMBL's drug indications cite them.

``studies(nct_ids)`` returns ``{"retrieved_at", "version", "record": {nct_id: study},
"missing": [...]}``. ``study`` keeps the fields Sabueso maps (``FIELDS``) as the API v2
states them, and ``version`` is the API's data timestamp. An id ClinicalTrials.gov does
not hold is listed in ``missing``, and a failed request raises ``ConnectorError``.
``OnlineClinicalTrialsClient`` queries the API v2 in batches; the fixture client reads
``<directory>/clinicaltrials/studies.json``.

Terms: works of the US government, not under copyright in the US; NLM asks that the
source be acknowledged ("Source: National Library of Medicine").
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.clinicaltrials_acquisition import (
    nct_id,
    normalize_ids,
    note_fixture,
    note_response,
    observe,
)
from sabueso.core.errors import ConnectorError
from sabueso.core.source_acquisition import capture_acquisitions, missing_fixture
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "ClinicalTrials.gov"
API = "https://clinicaltrials.gov/api/v2"
BATCH = 50
#: The parts of a study Sabueso keeps: identity, status and dates, design (type, phases,
#: enrolment), conditions, interventions, lead sponsor, and whether results are posted.
FIELDS = (
    "protocolSection.identificationModule.nctId",
    "protocolSection.identificationModule.briefTitle",
    "protocolSection.statusModule.overallStatus",
    "protocolSection.statusModule.startDateStruct",
    "protocolSection.statusModule.completionDateStruct",
    "protocolSection.statusModule.lastUpdatePostDateStruct",
    "protocolSection.designModule.studyType",
    "protocolSection.designModule.phases",
    "protocolSection.designModule.enrollmentInfo",
    "protocolSection.conditionsModule.conditions",
    "protocolSection.armsInterventionsModule.interventions",
    "protocolSection.sponsorCollaboratorsModule.leadSponsor",
    "hasResults",
)
# Bibliography is an explicit source route, not added to frozen clinical assertions.
REFERENCE_FIELDS = (
    "protocolSection.identificationModule.nctId",
    "protocolSection.identificationModule.briefTitle",
    "protocolSection.statusModule.lastUpdatePostDateStruct",
    "protocolSection.referencesModule",
)


def _get(path: str, params: Dict[str, Any], timeout: float) -> Any:
    url = f"{API}/{path}" + ("?" + urlencode(params) if params else "")
    try:
        with urlopen(url, timeout=timeout, expect_json=True) as resp:  # nosec - trusted endpoint
            payload = json.loads(resp.read().decode("utf-8"))
            note_response(path, params, payload)
            return payload
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        if isinstance(exc, HTTPError):
            exc.close()
        raise ConnectorError(f"ClinicalTrials.gov {path} failed: {exc}") from exc


def _nct(study: Dict[str, Any]) -> str | None:
    return nct_id(study)


class OnlineClinicalTrialsClient:
    def __init__(self, timeout: float = 60.0) -> None:
        self.timeout = timeout

    @observe("studies")
    def studies(self, nct_ids: Iterable[str]) -> Dict[str, Any]:
        return self._records(nct_ids, FIELDS)

    @observe("study_references")
    def study_references(self, nct_ids: Iterable[str]) -> Dict[str, Any]:
        """Native reference modules for explicitly named NCT records; no linked lookup."""
        return self._records(nct_ids, REFERENCE_FIELDS)

    def _records(self, nct_ids, fields):
        ids = normalize_ids(nct_ids)
        retrieval = stamp(SOURCE)
        version = (
            _get("version", {}, self.timeout).get("dataTimestamp") if ids else None
        )
        found: Dict[str, Any] = {}
        for i in range(0, len(ids), BATCH):
            chunk = ids[i : i + BATCH]
            params = {
                "filter.ids": ",".join(chunk),
                "fields": ",".join(fields),
                "pageSize": len(chunk),
                "format": "json",
            }
            seen_tokens = set()
            while True:
                page = _get("studies", params, self.timeout)
                for study in page["studies"]:
                    identifier = _nct(study)
                    if identifier in found and found[identifier] != study:
                        raise ConnectorError(
                            "ClinicalTrials.gov returned conflicting records for one NCT id"
                        )
                    found[identifier] = study
                token = page.get("nextPageToken")
                if token is None:
                    break
                if token in seen_tokens:
                    raise ConnectorError(
                        "ClinicalTrials.gov repeated a continuation token"
                    )
                seen_tokens.add(token)
                params = {**params, "pageToken": token}
        return {
            "retrieved_at": retrieval.value,
            "version": version,
            "record": {i: found[i] for i in ids if i in found},
            "missing": [i for i in ids if i not in found],
        }


class FixtureClinicalTrialsClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe("studies", fixture=True)
    def studies(self, nct_ids: Iterable[str]) -> Dict[str, Any]:
        return self._records(nct_ids, "studies.json")

    @observe("study_references", fixture=True)
    def study_references(self, nct_ids: Iterable[str]) -> Dict[str, Any]:
        return self._records(nct_ids, "references.json")

    def _records(self, nct_ids, filename):
        ids: List[str] = normalize_ids(nct_ids)
        if self.failing & set(ids):
            raise ConnectorError(
                f"ClinicalTrials.gov request for {ids} failed (simulated)"
            )
        path = self.directory / "clinicaltrials" / filename
        if not ids:
            return {
                "retrieved_at": self.retrieved_at,
                "version": None,
                "record": {},
                "missing": [],
            }
        if not path.is_file():
            raise missing_fixture(
                f"ClinicalTrials.gov fixture {filename} is unavailable"
            )
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConnectorError(
                f"ClinicalTrials.gov fixture {filename} is unreadable"
            ) from exc
        if not isinstance(saved, dict) or not isinstance(saved.get("studies"), dict):
            raise ConnectorError("ClinicalTrials.gov fixture has no studies mapping")
        if any(
            saved.get(key) is not None and not isinstance(saved[key], str)
            for key in ("version", "api_version")
        ):
            raise ConnectorError(
                "ClinicalTrials.gov fixture has invalid version metadata"
            )
        selected = {i: saved["studies"][i] for i in ids if i in saved["studies"]}
        if any(_nct(study) != identifier for identifier, study in selected.items()):
            raise ConnectorError(
                "ClinicalTrials.gov fixture key contradicts its native NCT identity"
            )
        declared_missing = saved.get("missing", [])
        if (
            not isinstance(declared_missing, list)
            or any(not isinstance(i, str) for i in declared_missing)
            or set(selected) & set(declared_missing)
        ):
            raise ConnectorError(
                "ClinicalTrials.gov fixture has invalid absence declarations"
            )
        receipt = note_fixture({"nct_ids": ids}, saved, selected)
        unsaved = set(ids) - set(selected) - set(declared_missing)
        if unsaved:
            if not selected:
                receipt["outcome"] = "unavailable"
            raise missing_fixture(
                f"ClinicalTrials.gov has no saved answer for {sorted(unsaved)}"
            )
        return {
            "retrieved_at": self.retrieved_at,
            "version": saved.get("version"),
            "record": selected,
            "missing": [i for i in ids if i not in selected],
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_studies(identifiers: Any, client: Any = None, skip_digestion: bool = False):
    """ClinicalTrials.gov studies by NCT id; ``missing`` lists ids it does not hold."""
    identifiers = list(identifiers)
    response = online(client, OnlineClinicalTrialsClient).studies(identifiers)
    return source_record(
        SOURCE,
        "studies",
        {"nct_ids": list(identifiers)},
        response.get("retrieved_at"),
        response.get("version"),
        {"studies": response["record"], "missing": response["missing"]},
    )


@arg_digest()
@capture_acquisitions
def get_study_references(
    identifiers: Any, client: Any = None, skip_digestion: bool = False
):
    """Native references of explicit NCT studies, separate from clinical card intake.

    PMID/type/citation/retraction and linked-resource forms remain source statements.
    No linked publication, website or participant-data endpoint is consulted.
    """
    identifiers = list(identifiers)
    response = online(client, OnlineClinicalTrialsClient).study_references(identifiers)
    return source_record(
        SOURCE,
        "study_references",
        {"nct_ids": identifiers},
        response.get("retrieved_at"),
        response.get("version"),
        {"studies": response["record"], "missing": response["missing"]},
    )
