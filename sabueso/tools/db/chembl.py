"""ChEMBL database tools: molecule records and target bioactivities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.chembl_acquisition import note_page, observe
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.source_acquisition import capture_acquisitions
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record


def load_json(path: str | Path) -> Dict[str, Any]:
    """Load ChEMBL JSON from a local file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def create_molecule_card_from_json(
    chembl_json: Dict[str, Any], retrieved_at: str
) -> Any:
    """Create a SmallMolecule Card from one ChEMBL molecule record (offline).

    The card is anchored at the molecule's standard InChIKey
    (``sabueso:small_molecule:inchikey:<key>``), like every small molecule card
    (uibcdf/sabueso#25). A record without one raises ``SchemaError``. To resolve an
    identifier and link the molecule's records in other sources, use
    ``resolve_molecule_card``.
    """
    from sabueso.tools.card.small_molecule import single_molecule_card

    chembl_id = chembl_json.get("molecule_chembl_id") or ""
    return single_molecule_card(
        chembl={"retrieved_at": retrieved_at, "molecules": {chembl_id: chembl_json}}
    )


def create_molecule_card_from_file(path: str | Path, retrieved_at: str) -> Any:
    """Create a SmallMolecule Card from a ChEMBL JSON file."""
    return create_molecule_card_from_json(load_json(path), retrieved_at=retrieved_at)


def fetch_chembl_json(chembl_id: str) -> Dict[str, Any]:
    """Deprecated: use ``get_molecules([chembl_id])`` (#49)."""
    from sabueso._private.smonitor.outcomes import report_deprecated

    report_deprecated(
        "sabueso.tools.db.chembl.fetch_chembl_json",
        "sabueso.tools.db.chembl.get_molecules([chembl_id])",
    )
    response = OnlineChEMBLClient().molecules([chembl_id])
    if chembl_id not in response["molecules"]:
        raise RecordNotFoundError(f"ChEMBL has no molecule {chembl_id}")
    return response["molecules"][chembl_id]


def create_molecule_card_online(chembl_id: str, retrieved_at: str) -> Any:
    """Deprecated: use ``sabueso.resolve("chembl:<id>")``, which links the molecule's
    records across sources (#49)."""
    from sabueso._private.smonitor.outcomes import report_deprecated

    report_deprecated(
        "sabueso.create_molecule_card_online", 'sabueso.resolve("chembl:<id>")'
    )
    response = OnlineChEMBLClient().molecules([chembl_id])
    if chembl_id not in response["molecules"]:
        raise RecordNotFoundError(f"ChEMBL has no molecule {chembl_id}")
    return create_molecule_card_from_json(
        response["molecules"][chembl_id], retrieved_at=retrieved_at
    )


# --- Target bioactivities (uibcdf/sabueso#23) -------------------------------------------
#
# ``bioactivities(target, limit)`` returns ``{query, version, retrieved_at, total_count,
# truncated, activities, assays}``: the ChEMBL activity records of a target (only the
# fields in ACTIVITY_FIELDS, ordered by activity id) and, keyed by assay id, the metadata
# of their assays, including the target-assignment confidence. ``OnlineChEMBLClient``
# queries the ChEMBL web services; ``FixtureChEMBLClient`` reads
# ``<directory>/chembl/<target>.json``. Both raise ``RecordNotFoundError`` when ChEMBL
# has no such target and ``ConnectorError`` on failures.

CHEMBL_API = "https://www.ebi.ac.uk/chembl/api/data"
DEFAULT_ACTIVITY_LIMIT = 5000
PAGE_SIZE = 1000
ASSAY_CHUNK = 50
DOCUMENT_FIELDS = (
    "document_chembl_id",
    "pubmed_id",
    "doi",
    "title",
    "year",
    "journal",
    "src_id",
)

ACTIVITY_FIELDS = (
    "activity_id",
    "target_chembl_id",
    "molecule_chembl_id",
    "parent_molecule_chembl_id",
    "molecule_pref_name",
    "canonical_smiles",
    "assay_chembl_id",
    "assay_description",
    "assay_type",
    "assay_variant_mutation",
    "standard_type",
    "standard_relation",
    "standard_value",
    "standard_upper_value",
    "standard_units",
    "standard_text_value",
    "pchembl_value",
    "activity_comment",
    "data_validity_comment",
    "potential_duplicate",
    "action_type",
    "document_chembl_id",
    "document_year",
    "document_journal",
)
MOLECULE_CHUNK = 50
#: A drug's indications (``drug_indication``), with the references ChEMBL cites for each
#: (ClinicalTrials.gov NCT ids, ATC, FDA, EMA, DailyMed…; #81).
INDICATION_FIELDS = (
    "drugind_id",
    "molecule_chembl_id",
    "parent_molecule_chembl_id",
    "efo_id",
    "efo_term",
    "mesh_id",
    "mesh_heading",
    "max_phase_for_ind",
    "indication_refs",
)
MOLECULE_FIELDS = (
    "molecule_chembl_id",
    "pref_name",
    "molecule_type",
    "max_phase",
    "molecule_hierarchy",
    "molecule_structures",
    "molecule_properties",
)
ASSAY_FIELDS = (
    "assay_chembl_id",
    "confidence_score",
    "confidence_description",
    "relationship_type",
    "relationship_description",
    "assay_organism",
    "assay_tax_id",
    "assay_parameters",
    "variant_sequence",
)


def _chembl_get(path: str, params: Dict[str, Any], timeout: float) -> Any:
    url = f"{CHEMBL_API}/{path}"
    if params:
        url += "?" + urlencode(params)
    try:
        with urlopen(url, timeout=timeout, expect_json=True) as resp:  # nosec - trusted endpoint
            payload = json.loads(resp.read().decode("utf-8"))
            note_page(path, params, payload)
            return payload
    except HTTPError as exc:
        exc.close()
        if exc.code == 404:
            raise RecordNotFoundError(f"ChEMBL has no record for {path}") from exc
        raise ConnectorError(f"ChEMBL {path} failed: HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        raise ConnectorError(f"ChEMBL {path} failed: {exc}") from exc


def _keep(record: Dict[str, Any], fields: tuple) -> Dict[str, Any]:
    return {k: record.get(k) for k in fields}


def _molecule(record: Dict[str, Any]) -> Dict[str, Any]:
    kept = _keep(record, MOLECULE_FIELDS)
    structures = dict(kept.get("molecule_structures") or {})
    structures.pop("molfile", None)  # coordinates for drawing, not knowledge
    kept["molecule_structures"] = structures or None
    return kept


class OnlineChEMBLClient:
    def __init__(self, timeout: float = 60.0) -> None:
        self.timeout = timeout
        self._version: str | None = None

    def version(self) -> str | None:
        if self._version is None:
            status = _chembl_get("status.json", {}, self.timeout)
            self._version = status.get("chembl_db_version")
        return self._version

    @observe("bioactivities")
    def bioactivities(
        self, target: str, limit: int = DEFAULT_ACTIVITY_LIMIT
    ) -> Dict[str, Any]:
        retrieval = stamp("ChEMBL")
        _chembl_get(f"target/{target}.json", {"only": "target_chembl_id"}, self.timeout)
        activities: list = []
        total = 0
        offset = 0
        while len(activities) < limit:
            page = _chembl_get(
                "activity.json",
                {
                    "target_chembl_id": target,
                    "order_by": "activity_id",
                    "only": ",".join(ACTIVITY_FIELDS),
                    "limit": min(PAGE_SIZE, limit - len(activities)),
                    "offset": offset,
                },
                self.timeout,
            )
            batch = page.get("activities", [])
            total = page.get("page_meta", {}).get("total_count", total)
            activities.extend(_keep(a, ACTIVITY_FIELDS) for a in batch)
            offset += len(batch)
            if not batch or not page.get("page_meta", {}).get("next"):
                break
        assays, documents = self._context(activities)
        return {
            "query": {"target_chembl_id": target, "limit": limit},
            "version": self.version(),
            "retrieved_at": retrieval.value,
            "total_count": total,
            "truncated": total > len(activities),
            "activities": activities,
            "assays": assays,
            "documents": documents,
        }

    def _context(self, activities: list) -> tuple:
        """The assays and documents of the activities: their metadata, and PubMed ids and
        DOIs so that a measurement can be matched to a publication (#44)."""
        assay_ids = sorted(
            {a["assay_chembl_id"] for a in activities if a.get("assay_chembl_id")}
        )
        assays: Dict[str, Any] = {}
        for i in range(0, len(assay_ids), ASSAY_CHUNK):
            chunk = assay_ids[i : i + ASSAY_CHUNK]
            page = _chembl_get(
                "assay.json",
                {
                    "assay_chembl_id__in": ",".join(chunk),
                    "only": ",".join(ASSAY_FIELDS),
                    "limit": len(chunk),
                },
                self.timeout,
            )
            for assay in page.get("assays", []):
                assays[assay["assay_chembl_id"]] = _keep(assay, ASSAY_FIELDS)
        # The documents the measurements come from, with their PubMed id and DOI, so a
        # measurement can be matched to a publication (#44).
        document_ids = sorted(
            {a["document_chembl_id"] for a in activities if a.get("document_chembl_id")}
        )
        documents: Dict[str, Any] = {}
        for i in range(0, len(document_ids), ASSAY_CHUNK):
            chunk = document_ids[i : i + ASSAY_CHUNK]
            page = _chembl_get(
                "document.json",
                {
                    "document_chembl_id__in": ",".join(chunk),
                    "only": ",".join(DOCUMENT_FIELDS),
                    "limit": len(chunk),
                },
                self.timeout,
            )
            for document in page.get("documents", []):
                documents[document["document_chembl_id"]] = _keep(
                    document, DOCUMENT_FIELDS
                )
        return assays, documents

    @observe("assay_activities")
    def assay_activities(
        self, assay_ids: Iterable[str], limit: int = DEFAULT_ACTIVITY_LIMIT
    ) -> Dict[str, Any]:
        """The activities of named assays, whatever their target: how a PubChem copy
        leads to a ChEMBL original a target-based query did not return (#68)."""
        retrieval = stamp("ChEMBL")
        ids = sorted({i for i in assay_ids if i})
        activities: list = []
        for i in range(0, len(ids), ASSAY_CHUNK):
            chunk = ids[i : i + ASSAY_CHUNK]
            offset = 0
            while len(activities) < limit:
                page = _chembl_get(
                    "activity.json",
                    {
                        "assay_chembl_id__in": ",".join(chunk),
                        "order_by": "activity_id",
                        "only": ",".join(ACTIVITY_FIELDS),
                        "limit": min(PAGE_SIZE, limit - len(activities)),
                        "offset": offset,
                    },
                    self.timeout,
                )
                batch = page.get("activities", [])
                activities.extend(_keep(a, ACTIVITY_FIELDS) for a in batch)
                offset += len(batch)
                if not batch or not page.get("page_meta", {}).get("next"):
                    break
        assays, documents = self._context(activities)
        return {
            "query": {"assay_chembl_id": ids, "limit": limit},
            "version": self.version(),
            "retrieved_at": retrieval.value,
            "total_count": len(activities),
            "truncated": len(activities) >= limit,
            "activities": activities,
            "assays": assays,
            "documents": documents,
        }

    @observe("molecules")
    def molecules(self, chembl_ids: Iterable[str]) -> Dict[str, Any]:
        """Molecule records by ChEMBL id: ``{version, retrieved_at, molecules, missing}``."""
        ids = sorted({i for i in chembl_ids if i})
        retrieval = stamp("ChEMBL")
        found: Dict[str, Any] = {}
        for i in range(0, len(ids), MOLECULE_CHUNK):
            chunk = ids[i : i + MOLECULE_CHUNK]
            page = _chembl_get(
                "molecule.json",
                {
                    "molecule_chembl_id__in": ",".join(chunk),
                    "only": ",".join(MOLECULE_FIELDS),
                    "limit": len(chunk),
                },
                self.timeout,
            )
            for record in page.get("molecules", []):
                found[record["molecule_chembl_id"]] = _molecule(record)
        return {
            "version": self.version(),
            "retrieved_at": retrieval.value,
            "molecules": found,
            "missing": [i for i in ids if i not in found],
        }

    @observe("indications")
    def indications(self, chembl_ids: Iterable[str]) -> Dict[str, Any]:
        """Indications by molecule ChEMBL id: ``{version, retrieved_at, indications,
        missing}``. ``missing`` lists molecules ChEMBL states no indication for."""
        ids = sorted({i for i in chembl_ids if i})
        retrieval = stamp("ChEMBL")
        found: Dict[str, List[Dict[str, Any]]] = {}
        for i in range(0, len(ids), MOLECULE_CHUNK):
            chunk = ids[i : i + MOLECULE_CHUNK]
            offset = 0
            while True:
                page = _chembl_get(
                    "drug_indication.json",
                    {
                        "molecule_chembl_id__in": ",".join(chunk),
                        "order_by": "drugind_id",
                        "limit": PAGE_SIZE,
                        "offset": offset,
                    },
                    self.timeout,
                )
                records = page.get("drug_indications") or []
                for record in records:
                    found.setdefault(record["molecule_chembl_id"], []).append(
                        _keep(record, INDICATION_FIELDS)
                    )
                offset += len(records)
                if not records or not (page.get("page_meta") or {}).get("next"):
                    break
        return {
            "version": self.version(),
            "retrieved_at": retrieval.value,
            "indications": found,
            "missing": [i for i in ids if i not in found],
        }

    @observe("indications_for")
    def indications_for(self, disease_ids: Iterable[str]) -> Dict[str, Any]:
        """Indications naming a disease, by the ids ChEMBL states for it (#90):
        ``EFO:…``/``MONDO:…`` (``efo_id``) or ``MESH:D…`` (``mesh_id``). Returns
        ``{version, retrieved_at, indications: {molecule: [indication, ...]}}``."""
        ids = sorted({i for i in disease_ids if i})
        retrieval = stamp("ChEMBL")
        found: Dict[str, List[Dict[str, Any]]] = {}
        filters = {
            "efo_id__in": [i for i in ids if not i.upper().startswith("MESH:")],
            "mesh_id__in": [
                i.split(":", 1)[1] for i in ids if i.upper().startswith("MESH:")
            ],
        }
        seen = set()
        for name, values in filters.items():
            if not values:
                continue
            offset = 0
            while True:
                page = _chembl_get(
                    "drug_indication.json",
                    {
                        name: ",".join(values),
                        "order_by": "drugind_id",
                        "limit": PAGE_SIZE,
                        "offset": offset,
                    },
                    self.timeout,
                )
                records = page.get("drug_indications") or []
                for record in records:
                    if record.get("drugind_id") in seen:
                        continue
                    seen.add(record.get("drugind_id"))
                    found.setdefault(record["molecule_chembl_id"], []).append(
                        _keep(record, INDICATION_FIELDS)
                    )
                offset += len(records)
                if not records or not (page.get("page_meta") or {}).get("next"):
                    break
        return {
            "version": self.version(),
            "retrieved_at": retrieval.value,
            "indications": found,
        }


def _names_disease(indication: Dict[str, Any], ids: Iterable[str]) -> bool:
    wanted = {i.upper() for i in ids}
    efo = str(indication.get("efo_id") or "").upper()
    mesh = str(indication.get("mesh_id") or "")
    return efo in wanted or (mesh and f"MESH:{mesh}".upper() in wanted)


class FixtureChEMBLClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe("bioactivities", fixture=True)
    def bioactivities(
        self, target: str, limit: int = DEFAULT_ACTIVITY_LIMIT
    ) -> Dict[str, Any]:
        if target in self.failing:
            raise ConnectorError(f"ChEMBL request for {target} failed (simulated)")
        path = self.directory / "chembl" / f"{target}.json"
        if not path.is_file():
            raise RecordNotFoundError(f"ChEMBL has no target {target}")
        saved = json.loads(path.read_text(encoding="utf-8"))
        activities = saved["activities"][:limit]
        return {
            **saved,
            "query": {"target_chembl_id": target, "limit": limit},
            "retrieved_at": self.retrieved_at,
            "truncated": saved["total_count"] > len(activities),
            "activities": activities,
        }

    @observe("assay_activities", fixture=True)
    def assay_activities(
        self, assay_ids: Iterable[str], limit: int = DEFAULT_ACTIVITY_LIMIT
    ) -> Dict[str, Any]:
        """Activities of named assays, from every saved target response."""
        ids = {i for i in assay_ids if i}
        if self.failing & ids:
            raise ConnectorError(
                f"ChEMBL assay request for {sorted(ids)} failed (simulated)"
            )
        activities, assays, documents, version = [], {}, {}, None
        for path in sorted((self.directory / "chembl").glob("CHEMBL*.json")):
            saved = json.loads(path.read_text(encoding="utf-8"))
            if "activities" not in saved:
                continue
            version = version or saved.get("version")
            for activity in saved["activities"]:
                if activity.get("assay_chembl_id") in ids:
                    activities.append(activity)
                    aid, did = (
                        activity.get("assay_chembl_id"),
                        activity.get("document_chembl_id"),
                    )
                    if aid in (saved.get("assays") or {}):
                        assays[aid] = saved["assays"][aid]
                    if did in (saved.get("documents") or {}):
                        documents[did] = saved["documents"][did]
        activities = sorted(activities, key=lambda a: a["activity_id"])[:limit]
        return {
            "query": {"assay_chembl_id": sorted(ids), "limit": limit},
            "version": version,
            "retrieved_at": self.retrieved_at,
            "total_count": len(activities),
            "truncated": False,
            "activities": activities,
            "assays": assays,
            "documents": documents,
        }

    @observe("molecules", fixture=True)
    def molecules(self, chembl_ids: Iterable[str]) -> Dict[str, Any]:
        ids = sorted({i for i in chembl_ids if i})
        if self.failing & set(ids):
            raise ConnectorError(
                f"ChEMBL molecule request for {ids} failed (simulated)"
            )
        path = self.directory / "chembl" / "molecules.json"
        saved = (
            json.loads(path.read_text(encoding="utf-8"))
            if path.is_file()
            else {"version": None, "molecules": {}}
        )
        found = {i: saved["molecules"][i] for i in ids if i in saved["molecules"]}
        return {
            "version": saved.get("version"),
            "retrieved_at": self.retrieved_at,
            "molecules": found,
            "missing": [i for i in ids if i not in found],
        }

    @observe("indications", fixture=True)
    def indications(self, chembl_ids: Iterable[str]) -> Dict[str, Any]:
        ids = sorted({i for i in chembl_ids if i})
        if self.failing & set(ids):
            raise ConnectorError(
                f"ChEMBL indication request for {ids} failed (simulated)"
            )
        path = self.directory / "chembl" / "indications.json"
        saved = (
            json.loads(path.read_text(encoding="utf-8"))
            if path.is_file()
            else {"version": None, "indications": {}}
        )
        found = {i: saved["indications"][i] for i in ids if i in saved["indications"]}
        return {
            "version": saved.get("version"),
            "retrieved_at": self.retrieved_at,
            "indications": found,
            "missing": [i for i in ids if i not in found],
        }

    @observe("indications_for", fixture=True)
    def indications_for(self, disease_ids: Iterable[str]) -> Dict[str, Any]:
        ids = sorted({i for i in disease_ids if i})
        if self.failing & set(ids):
            raise ConnectorError(
                f"ChEMBL indication request for {ids} failed (simulated)"
            )
        path = self.directory / "chembl" / "indications.json"
        saved = (
            json.loads(path.read_text(encoding="utf-8"))
            if path.is_file()
            else {"version": None, "indications": {}}
        )
        found = {}
        for molecule, indications in sorted(saved["indications"].items()):
            named = [i for i in indications if _names_disease(i, ids)]
            if named:
                found[molecule] = named
        return {
            "version": saved.get("version"),
            "retrieved_at": self.retrieved_at,
            "indications": found,
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@capture_acquisitions
@arg_digest()
def get_bioactivities(
    identifier: str,
    limit: int = DEFAULT_ACTIVITY_LIMIT,
    client: Any = None,
    skip_digestion: bool = False,
):
    """The activity records of a ChEMBL target (``identifier`` is its ChEMBL id)."""
    response = online(client, OnlineChEMBLClient).bioactivities(identifier, limit=limit)
    return source_record(
        "ChEMBL",
        "bioactivities",
        {"target": identifier, "limit": limit},
        response.get("retrieved_at"),
        response.get("version"),
        {
            "total_count": response.get("total_count"),
            "truncated": response.get("truncated"),
            "activities": response.get("activities"),
        },
    )


@capture_acquisitions
@arg_digest()
def get_molecules(identifiers: Any, client: Any = None, skip_digestion: bool = False):
    """ChEMBL molecule records by ChEMBL id; ``missing`` lists ids ChEMBL does not hold."""
    response = online(client, OnlineChEMBLClient).molecules(identifiers)
    return source_record(
        "ChEMBL",
        "molecules",
        {"chembl_ids": list(identifiers)},
        response.get("retrieved_at"),
        response.get("version"),
        {"molecules": response.get("molecules"), "missing": response.get("missing")},
    )


@capture_acquisitions
@arg_digest()
def get_indications(identifiers: Any, client: Any = None, skip_digestion: bool = False):
    """ChEMBL's indications of molecules, by ChEMBL id, with the references it cites;
    ``missing`` lists molecules ChEMBL states no indication for."""
    response = online(client, OnlineChEMBLClient).indications(identifiers)
    return source_record(
        "ChEMBL",
        "indications",
        {"chembl_ids": list(identifiers)},
        response.get("retrieved_at"),
        response.get("version"),
        {
            "indications": response.get("indications"),
            "missing": response.get("missing"),
        },
    )
