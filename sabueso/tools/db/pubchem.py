"""PubChem database tools (minimal)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.pubchem_acquisition import note_response, observe
from sabueso.core.source_acquisition import capture_acquisitions
from sabueso.tools.db._http import request, stamp, urlopen
from sabueso.tools.db._record import online, source_record


def load_json(path: str | Path) -> Dict[str, Any]:
    """Load PubChem JSON from a local file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def create_compound_card_from_json(
    pubchem_json: Dict[str, Any], retrieved_at: str
) -> Any:
    """Create a SmallMolecule Card from one PubChem compound record (offline).

    The card is anchored at the compound's standard InChIKey
    (``sabueso:small_molecule:inchikey:<key>``), like every small molecule card
    (uibcdf/sabueso#25). A record without one raises ``SchemaError``.
    """
    from sabueso.mappings.pubchem import map_compound
    from sabueso.tools.card.small_molecule import single_molecule_card

    cid = str(
        map_compound(pubchem_json, retrieved_at)["fields"].get("identifiers.pubchem")
        or ""
    )
    return single_molecule_card(
        pubchem={"retrieved_at": retrieved_at, "compounds": {cid: pubchem_json}}
    )


def create_compound_card_from_file(path: str | Path, retrieved_at: str) -> Any:
    """Create a SmallMolecule Card from a PubChem JSON file."""
    return create_compound_card_from_json(load_json(path), retrieved_at=retrieved_at)


PUBCHEM_PUG = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid"
PUBCHEM_COMPOUND = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound"
#: Structure notations PubChem matches to its compounds (#93).
NOTATIONS = ("smiles", "inchi")
PROPERTIES = (
    "Title,MolecularWeight,MolecularFormula,XLogP,TPSA,HBondDonorCount,HBondAcceptorCount,"
    "RotatableBondCount,InChI,InChIKey,SMILES,ConnectivitySMILES"
)


class OnlinePubChemClient:
    """PubChem PUG REST: the property table of a compound, by CID."""

    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    @observe("compound")
    def compound(self, cid: str) -> Dict[str, Any]:
        url = f"{PUBCHEM_PUG}/{cid}/property/{quote(PROPERTIES, safe=',')}/JSON"
        retrieval = stamp("PubChem")
        try:
            with urlopen(url, timeout=self.timeout, expect_json=True) as resp:  # nosec - trusted endpoint
                data = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            exc.close()
            if exc.code in (400, 404):
                raise RecordNotFoundError(f"PubChem has no compound {cid}") from exc
            raise ConnectorError(
                f"PubChem request for {cid} failed: HTTP {exc.code}"
            ) from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ConnectorError(f"PubChem request for {cid} failed: {exc}") from exc
        note_response(url, data)
        return {"retrieved_at": retrieval.value, "record": data}

    @observe("structure_match")
    def structure(self, notation: str, structure: str) -> Dict[str, Any]:
        """The compounds PubChem states a structure is (#93): PubChem standardizes the
        structure and matches it to its compounds, so the answer is PubChem's
        statement, not a key Sabueso computed.

        Returns ``{"retrieved_at", "cids", "fault"}``. ``cids`` is empty when PubChem
        holds no compound for the structure (it answers CID 0), and ``fault`` is
        PubChem's message when it cannot read the structure (HTTP 400).
        """
        url = f"{PUBCHEM_COMPOUND}/{notation}/cids/JSON"
        # POST: a SMILES or an InChI carries characters a URL path would mangle.
        data = urlencode({notation: structure}).encode("utf-8")
        retrieval = stamp("PubChem")
        try:
            with urlopen(
                request(url, data=data), timeout=self.timeout, expect_json=True
            ) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            try:
                if exc.code == 404:
                    return {"retrieved_at": retrieval.value, "cids": [], "fault": None}
                if exc.code == 400:
                    return {
                        "retrieved_at": retrieval.value,
                        "cids": [],
                        "fault": _fault(exc),
                    }
                raise ConnectorError(
                    f"PubChem structure lookup failed: HTTP {exc.code}"
                ) from exc
            finally:
                exc.close()
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ConnectorError(f"PubChem structure lookup failed: {exc}") from exc
        note_response(url, body)
        return {"retrieved_at": retrieval.value, **_matched(body)}


def _fault(exc: HTTPError) -> str:
    try:
        fault = json.loads(exc.read().decode("utf-8")).get("Fault") or {}
    except (OSError, ValueError):
        fault = {}
    return fault.get("Message") or f"HTTP {exc.code}"


def _matched(body: Dict[str, Any]) -> Dict[str, Any]:
    """``cids`` and ``fault`` from a PUG REST identifier list (or fault) body."""
    if "Fault" in body:
        return {"cids": [], "fault": body["Fault"].get("Message") or "fault"}
    cids = (body.get("IdentifierList") or {}).get("CID") or []
    return {"cids": [str(c) for c in cids if int(c) > 0], "fault": None}


class FixturePubChemClient:
    """Saved PubChem responses: ``<directory>/pubchem/<cid>.json``, or
    ``<directory>/<cid>.json`` as the older fixtures are laid out."""

    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe("compound", fixture=True)
    def compound(self, cid: str) -> Dict[str, Any]:
        if str(cid) in self.failing:
            raise ConnectorError(f"PubChem request for {cid} failed (simulated)")
        for path in (
            self.directory / "pubchem" / f"{cid}.json",
            self.directory / f"{cid}.json",
        ):
            if path.is_file():
                data = json.loads(path.read_text(encoding="utf-8"))
                return {"retrieved_at": self.retrieved_at, "record": data}
        raise RecordNotFoundError(f"PubChem has no compound {cid}")

    @observe("structure_match", fixture=True)
    def structure(self, notation: str, structure: str) -> Dict[str, Any]:
        """A saved structure lookup (``<directory>/pubchem/structures.json``)."""
        path = self.directory / "pubchem" / "structures.json"
        saved = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        for lookup in saved.get("lookups") or []:
            if (lookup["kind"], lookup["query"]) == (notation, structure):
                return {
                    "retrieved_at": self.retrieved_at,
                    **_matched(lookup["response"]),
                }
        raise RecordNotFoundError(f"No saved PubChem lookup for {notation} {structure}")


def fetch_pubchem_json(cid: str) -> Dict[str, Any]:
    """Deprecated: use ``get_compound(cid)["record"]`` (#49)."""
    from sabueso._private.smonitor.outcomes import report_deprecated

    report_deprecated(
        "sabueso.tools.db.pubchem.fetch_pubchem_json",
        'sabueso.tools.db.pubchem.get_compound(cid)["record"]',
    )
    return OnlinePubChemClient().compound(cid)["record"]


def create_compound_card_online(cid: str, retrieved_at: str) -> Any:
    """Deprecated: use ``sabueso.resolve("pubchem:<cid>")``, which links the compound's
    records across sources (#50)."""
    from sabueso._private.smonitor.outcomes import report_deprecated

    report_deprecated(
        "sabueso.create_compound_card_online", 'sabueso.resolve("pubchem:<cid>")'
    )
    data = OnlinePubChemClient().compound(cid)["record"]
    return create_compound_card_from_json(data, retrieved_at=retrieved_at)


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_compound(identifier: str, client: Any = None, skip_digestion: bool = False):
    """The PubChem property table of a compound, by CID, in a provenance envelope."""
    response = online(client, OnlinePubChemClient).compound(identifier)
    return source_record(
        "PubChem",
        "compound",
        {"cid": identifier},
        response.get("retrieved_at"),
        None,
        response.get("record"),
    )


@arg_digest()
@capture_acquisitions
def get_structure_match(
    structure: str,
    notation: str = "smiles",
    client: Any = None,
    skip_digestion: bool = False,
):
    """The PubChem compounds a structure (a SMILES or an InChI) is, as PubChem states
    it (#93), in a provenance envelope: ``{"cids": [...], "fault": ...}``."""
    response = online(client, OnlinePubChemClient).structure(notation, structure)
    return source_record(
        "PubChem",
        "structure_match",
        {"notation": notation, "structure": structure},
        response.get("retrieved_at"),
        None,
        {"cids": response.get("cids") or [], "fault": response.get("fault")},
    )
