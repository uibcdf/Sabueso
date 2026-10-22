"""RCSB PDB structure access (entry, polymer entities, UniProt alignments, ligands).

The entry also brings what choosing a structure needs: the entities' mutations and
expression tags (``rcsb_polymer_entity_feature``), their canonical sequence and
expression host, the residues without coordinates per chain
(``rcsb_polymer_instance_feature``), R-free and R-work, and the deposit and release
dates. Instance features are fetched whole and filtered by the mapping, because
GraphQL cannot filter them by type. When RCSB fails on the instance-level fields of an
entry, the entry is fetched again without them and marked ``_partial`` (#74).

Ligands come with the PDB "subject of investigation" flag and, per polymer chain, the
residues near each ligand instance (``rcsb_ligand_neighbors``, structure numbering).

``fetch_structure(pdb_id)`` returns ``(entry, retrieved_at)`` from one GraphQL request.
``fetch_structures(pdb_ids)`` asks for many entries at once (``entries(entry_ids:
[...])``, #98), 25 per request, and returns ``{pdb_id: (entry, retrieved_at) or the
error}``. An entry RCSB does not hold is left out of its answer, and is not found. An
entry whose instance-level fields fail is fetched again alone, with the fallback above;
a batch that fails as a whole is asked entry by entry.
``OnlineRCSBClient`` queries data.rcsb.org; ``FixtureRCSBClient`` reads saved responses
from ``<directory>/rcsb/<PDB_ID>.json``. Both raise ``RecordNotFoundError`` when RCSB holds
no entry and ``ConnectorError`` when the source cannot answer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.rcsb_acquisition import summarize
from sabueso.core.source_acquisition import acquisition, capture_acquisitions
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record

RCSB_GRAPHQL = "https://data.rcsb.org/graphql"
STRUCTURE_QUERY = """query($id: String!) { entry(entry_id: $id) {
  rcsb_id
  exptl { method }
  rcsb_primary_citation {
    pdbx_database_id_PubMed pdbx_database_id_DOI title journal_abbrev year rcsb_authors }
  rcsb_entry_info { resolution_combined polymer_entity_count_protein }
  rcsb_accession_info { deposit_date initial_release_date
    major_revision minor_revision revision_date }
  refine { pdbx_refine_id ls_R_factor_R_free ls_R_factor_R_work }
  assemblies {
    rcsb_assembly_container_identifiers { assembly_id }
    pdbx_struct_assembly { oligomeric_details oligomeric_count details method_details }
    rcsb_struct_symmetry { kind type oligomeric_state stoichiometry }
  }
  polymer_entities {
    rcsb_id
    rcsb_polymer_entity { pdbx_description pdbx_mutation }
    entity_poly { rcsb_sample_sequence_length rcsb_mutation_count
      pdbx_seq_one_letter_code_can }
    rcsb_entity_host_organism { ncbi_scientific_name ncbi_taxonomy_id }
    rcsb_polymer_entity_feature { type name
      feature_positions { beg_seq_id end_seq_id } }
    rcsb_polymer_entity_container_identifiers { entity_id auth_asym_ids uniprot_ids }
    rcsb_polymer_entity_align { reference_database_name reference_database_accession
      aligned_regions { entity_beg_seq_id ref_beg_seq_id length } }
    polymer_entity_instances {
      rcsb_polymer_entity_instance_container_identifiers { asym_id auth_asym_id
        auth_to_entity_poly_seq_mapping }
      rcsb_polymer_instance_feature {
        type provenance_source feature_positions { beg_seq_id end_seq_id } }
      rcsb_ligand_neighbors {
        ligand_asym_id ligand_comp_id ligand_is_bound seq_id comp_id distance }
    }
  }
  nonpolymer_entities {
    rcsb_nonpolymer_entity_container_identifiers { nonpolymer_comp_id }
    rcsb_nonpolymer_entity { pdbx_description }
    nonpolymer_entity_instances {
      rcsb_nonpolymer_instance_validation_score {
        is_subject_of_investigation is_subject_of_investigation_provenance }
    }
  }
} }"""

#: Instance-level fields a server-side error can make unavailable for an entry
#: (uibcdf/sabueso#74). Without them the entry is still mapped, and marked partial.
INSTANCE_FIELDS = """      rcsb_polymer_instance_feature {
        type provenance_source feature_positions { beg_seq_id end_seq_id } }
      rcsb_ligand_neighbors {
        ligand_asym_id ligand_comp_id ligand_is_bound seq_id comp_id distance }
"""
PARTIAL_QUERY = STRUCTURE_QUERY.replace(INSTANCE_FIELDS, "")
PARTIAL_MISSING = ["rcsb_polymer_instance_feature", "rcsb_ligand_neighbors"]
#: The same fields for many entries in one request (#98).
BATCH_QUERY = STRUCTURE_QUERY.replace(
    "query($id: String!) { entry(entry_id: $id) {",
    "query($ids: [String!]!) { entries(entry_ids: $ids) {",
)
BATCH_SIZE = 25


def fetch_many(client: Any, pdb_ids: Any) -> Dict[str, Any]:
    """``{pdb_id: (entry, retrieved_at) or the error}``: the client's batched lookup when
    it has one, else one entry at a time."""
    ids = [p.upper() for p in pdb_ids]
    if hasattr(client, "fetch_structures"):
        return client.fetch_structures(ids)
    out: Dict[str, Any] = {}
    for pdb_id in ids:
        try:
            out[pdb_id] = client.fetch_structure(pdb_id)
        except (RecordNotFoundError, ConnectorError) as exc:
            out[pdb_id] = exc
    return out


class OnlineRCSBClient:
    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout

    def _post(
        self, query: str, pdb_id: str, variables: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        body = json.dumps(
            {"query": query, "variables": variables or {"id": pdb_id.upper()}}
        ).encode("utf-8")
        request = Request(
            RCSB_GRAPHQL, data=body, headers={"Content-Type": "application/json"}
        )
        try:
            with urlopen(request, timeout=self.timeout, expect_json=True) as resp:  # nosec - trusted endpoint
                return json.loads(resp.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(f"RCSB request for {pdb_id} failed: {exc}") from exc

    @acquisition("RCSB PDB", "structure", summarize=summarize)
    def fetch_structure(self, pdb_id: str) -> Tuple[Dict[str, Any], str]:
        """The entry, or, when RCSB fails on its instance-level fields, the entry
        without them, marked ``_partial`` (``{"missing": [...], "reason": ...}``)."""
        retrieval = stamp("RCSB PDB")
        data = self._post(STRUCTURE_QUERY, pdb_id)
        partial = None
        errors = data.get("errors") or []
        if errors and all(
            "polymer_entity_instances" in [str(p) for p in e.get("path") or []]
            for e in errors
        ):
            reason = str(errors[0].get("message") or "")[:300]
            data = self._post(PARTIAL_QUERY, pdb_id)
            errors = data.get("errors") or []
            partial = {"missing": list(PARTIAL_MISSING), "reason": reason}
        if errors:
            raise ConnectorError(f"RCSB request for {pdb_id} failed: {errors}")
        entry = (data.get("data") or {}).get("entry")
        if entry is None:
            raise RecordNotFoundError(f"RCSB has no entry {pdb_id}")
        if partial:
            entry["_partial"] = partial
        return entry, retrieval.value

    def fetch_structures(self, pdb_ids: Any) -> Dict[str, Any]:
        ids = list(dict.fromkeys(p.upper() for p in pdb_ids))
        return self._fetch_structures(ids)

    @acquisition("RCSB PDB", "structures", summarize=summarize, aggregate=True)
    def _fetch_structures(self, pdb_ids: list[str]) -> Dict[str, Any]:
        ids = pdb_ids
        out: Dict[str, Any] = {}
        for i in range(0, len(ids), BATCH_SIZE):
            batch = ids[i : i + BATCH_SIZE]
            retrieval = stamp("RCSB PDB")
            try:
                data = self._post(BATCH_QUERY, ",".join(batch), {"ids": batch})
            except ConnectorError:
                data = None  # asked entry by entry below
            entries = ((data or {}).get("data") or {}).get("entries")
            errors = (data or {}).get("errors") or []
            # An error names the entry it touched by its index in the answer.
            touched = {
                e["path"][1]
                for e in errors
                if len(e.get("path") or []) > 1 and e["path"][0] == "entries"
            }
            if entries is None or any(len(e.get("path") or []) < 2 for e in errors):
                again = list(batch)  # the batch failed as a whole
            else:
                held = {
                    entry["rcsb_id"].upper(): index
                    for index, entry in enumerate(entries)
                    if entry is not None
                }
                unnamed = any(entry is None for entry in entries)
                again = []
                for pdb_id in batch:
                    index = held.get(pdb_id)
                    if index is not None and index not in touched:
                        out[pdb_id] = (entries[index], retrieval.value)
                    elif index is not None or unnamed:
                        again.append(pdb_id)  # alone, with the partial fallback
                    else:
                        out[pdb_id] = RecordNotFoundError(f"RCSB has no entry {pdb_id}")
            for pdb_id in again:
                try:
                    out[pdb_id] = self.fetch_structure(pdb_id)
                except (RecordNotFoundError, ConnectorError) as exc:
                    out[pdb_id] = exc
        return out


class FixtureRCSBClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory)
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @acquisition("RCSB PDB", "structure", fixture=True, summarize=summarize)
    def fetch_structure(self, pdb_id: str) -> Tuple[Dict[str, Any], str]:
        pdb_id = pdb_id.upper()
        if pdb_id in self.failing:
            raise ConnectorError(f"RCSB request for {pdb_id} failed (simulated)")
        path = self.directory / "rcsb" / f"{pdb_id}.json"
        if not path.is_file():
            raise RecordNotFoundError(f"RCSB has no entry {pdb_id}")
        return json.loads(path.read_text(encoding="utf-8")), self.retrieved_at

    def fetch_structures(self, pdb_ids: Any) -> Dict[str, Any]:
        return self._fetch_structures(list(dict.fromkeys(p.upper() for p in pdb_ids)))

    @acquisition(
        "RCSB PDB", "structures", fixture=True, summarize=summarize, aggregate=True
    )
    def _fetch_structures(self, pdb_ids: list[str]) -> Dict[str, Any]:
        out = {}
        for pdb_id in pdb_ids:
            try:
                out[pdb_id] = self.fetch_structure(pdb_id)
            except (RecordNotFoundError, ConnectorError) as error:
                out[pdb_id] = error
        return out


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@capture_acquisitions
@arg_digest()
def get_entry(identifier: str, client: Any = None, skip_digestion: bool = False):
    """The RCSB PDB entry Sabueso maps (GraphQL: entities, UniProt alignments,
    assemblies, ligands and primary citation), in a provenance envelope. Not the
    coordinates: loading structures belongs to MolSysMT."""
    entry, retrieved_at = online(client, OnlineRCSBClient).fetch_structure(identifier)
    return source_record(
        "RCSB PDB", "entry", {"pdb_id": identifier.upper()}, retrieved_at, None, entry
    )
