"""rcsb_ligand_contacts@1: source-scoped instances and alignment/minimum choices.

Keep this rule stable. Inputs are retained original polymer-entity records,
canonically ordered as a collection; diagnostics address their original children.
An unidentified neighbour is an occurrence, never an inferred shared instance.
"""

from copy import deepcopy
from math import isfinite

from sabueso.core.quantities import LENGTH_UNIT, quantity_node
from sabueso.core.snapshot import canonical_json

RULE = "rcsb_ligand_contacts@1"


def _position(entity, seq_id):
    candidates = set()
    for alignment in entity.get("rcsb_polymer_entity_align") or []:
        if alignment.get("reference_database_name") != "UniProt":
            continue
        accession = alignment.get("reference_database_accession")
        if not isinstance(accession, str) or not accession:
            continue
        for region in alignment.get("aligned_regions") or []:
            begin, reference, length = (
                region.get(key)
                for key in ("entity_beg_seq_id", "ref_beg_seq_id", "length")
            )
            if (
                all(type(n) is int and n > 0 for n in (begin, reference, length))
                and begin <= seq_id < begin + length
            ):
                candidates.add((accession, reference + seq_id - begin))
    return [
        {"uniprot": accession, "position": position}
        for accession, position in sorted(candidates)
    ]


def map_contacts(polymer_entities):
    """Return detached source inputs, instances and explicit unresolved input scope."""
    inputs = {
        "polymer_entities": sorted(deepcopy(polymer_entities or []), key=canonical_json)
    }
    diagnostics = {
        key: []
        for key in (
            "neighbor_scope",
            "unidentified_neighbors",
            "missing_chains",
            "unmapped_neighbors",
            "ambiguous_mappings",
            "invalid_distances",
            "bound_conflicts",
        )
    }
    grouped = {}
    for entity_index, entity in enumerate(inputs["polymer_entities"]):
        for instance_index, instance in enumerate(
            entity.get("polymer_entity_instances") or []
        ):
            parent = {"entity_index": entity_index, "instance_index": instance_index}
            neighbors = instance.get("rcsb_ligand_neighbors")
            diagnostics["neighbor_scope"].append(
                {
                    **parent,
                    "state": "not_retained"
                    if "rcsb_ligand_neighbors" not in instance
                    else "retained_null"
                    if neighbors is None
                    else "unrecognized_shape"
                    if not isinstance(neighbors, list)
                    else "retained_empty"
                    if not neighbors
                    else "retained",
                }
            )
            if not isinstance(neighbors, list):
                continue
            chain = (
                instance.get("rcsb_polymer_entity_instance_container_identifiers") or {}
            ).get("auth_asym_id")
            if not isinstance(chain, str) or not chain:
                chain = None
                diagnostics["missing_chains"].append(parent)
            for neighbor_index, row in enumerate(neighbors):
                origin = {**parent, "neighbor_index": neighbor_index}
                if not isinstance(row, dict):
                    diagnostics["unmapped_neighbors"].append(origin)
                    continue
                seq_id, component = row.get("seq_id"), row.get("ligand_comp_id")
                if (
                    type(seq_id) is not int
                    or seq_id < 1
                    or not isinstance(component, str)
                    or not component
                ):
                    diagnostics["unmapped_neighbors"].append(origin)
                    continue
                identifier = row.get("ligand_asym_id")
                identified = isinstance(identifier, str) and bool(identifier)
                if not identified:
                    diagnostics["unidentified_neighbors"].append(origin)
                key = (
                    (component, identifier)
                    if identified
                    else (component, None, entity_index, instance_index, neighbor_index)
                )
                found = grouped.setdefault(
                    key,
                    {
                        "asym_id": identifier if identified else None,
                        "contacts": {},
                        "bound": [],
                        "origins": [],
                    },
                )
                found["origins"].append(origin)
                bound = row.get("ligand_is_bound")
                if bound is not None and bound not in found["bound"]:
                    found["bound"].append(bound)
                candidates = _position(entity, seq_id)
                if len(candidates) > 1:
                    diagnostics["ambiguous_mappings"].append(
                        {**origin, "candidates": candidates}
                    )
                elif not candidates:
                    diagnostics["unmapped_neighbors"].append(
                        {**origin, "reason": "no_source_alignment"}
                    )
                mapped = (
                    candidates[0]
                    if len(candidates) == 1
                    else {"uniprot": None, "position": None}
                )
                distance = row.get("distance")
                if distance is not None and (
                    type(distance) not in (int, float)
                    or not isfinite(distance)
                    or distance < 0
                ):
                    diagnostics["invalid_distances"].append(origin)
                    distance = None
                # Equal residue numbers in different source polymer instances are
                # not a residue identity. Chain labels alone cannot establish it.
                residue = (entity_index, instance_index, seq_id)
                previous = found["contacts"].get(residue)
                if previous is None:
                    found["contacts"][residue] = {
                        "chain": chain,
                        "seq_id": seq_id,
                        "residue": row.get("comp_id"),
                        **mapped,
                        "min_distance": quantity_node(distance, LENGTH_UNIT),
                    }
                elif distance is not None and (
                    previous["min_distance"] is None
                    or distance < previous["min_distance"]["value"]
                ):
                    previous["min_distance"] = quantity_node(distance, LENGTH_UNIT)
    out = {}
    for key, found in sorted(
        grouped.items(), key=lambda item: (item[0][0], str(item[0][1]), item[0][2:])
    ):
        contacts = sorted(
            found["contacts"].values(),
            key=lambda row: (str(row["chain"]), row["seq_id"]),
        )
        if len(found["bound"]) > 1:
            diagnostics["bound_conflicts"].append(
                {
                    "component": key[0],
                    "asym_id": found["asym_id"],
                    "values": found["bound"],
                    "origins": found["origins"],
                }
            )
        out.setdefault(key[0], []).append(
            {
                "asym_id": found["asym_id"],
                "is_bound": found["bound"][0] if len(found["bound"]) == 1 else None,
                "chains": sorted(
                    {row["chain"] for row in contacts if row["chain"] is not None}
                ),
                "contacts": contacts,
            }
        )
    return inputs, out, diagnostics
