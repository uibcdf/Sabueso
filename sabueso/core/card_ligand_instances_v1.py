"""Frozen original ligand-instance membership and context, without contact joins.

One row is one literal instance in a focal has_structure declaration. Never
identify instances by component, chain, equal residue numbers or spatial guesses.
Keep v1 admission stable for independent saved readers.
"""

from .card_access import _Entry
from .card_protein_source_v1 import focal_subject

TOPIC = "ligand_instances"
SCOPE = (
    "Original ligand instances declared within retained structure relationships. "
    "Component, instance and chain identifiers keep their original scope; contact "
    "position and seq_id remain distinct. No assembly, biological relevance, "
    "affinity, site overlap or link to aggregated PDBe contacts is inferred. "
    "Support is inherited from the containing structure relationship, not "
    "invented for individual contacts. Missing declarations are not absence. "
    "Contact numbering and minimum distances are recorded mapping output; "
    "this view does not verify the historical alignment or minimum-selection basis."
)
SUMMARY = (
    "Original structure-local instances and recorded mapped contacts. Numbering "
    "and units stay distinct; open an instance or its source support for full detail. "
    "Missing declarations are not absence. Historical mapping basis is not verified."
)


def _child(location, kind, value):
    return {
        **location,
        "segments": [*location["segments"], {"type": kind, "value": value}],
    }


def entries(explorer):
    """Retain original ordering/indices; record empty, missing and malformed scope."""
    subject = focal_subject(explorer)
    if subject is None:
        return (), [{"field": "relationship subject", "state": "missing_prerequisite"}]
    found, gaps = [], []

    def children(value, location, field):
        if not isinstance(value, list) or not value:
            gaps.append(
                {
                    "field": field,
                    "location": location,
                    "state": "retained_empty"
                    if isinstance(value, list)
                    else "not_retained"
                    if value is None
                    else "unrecognized_shape",
                }
            )
            return ()
        return enumerate(value)

    for row in explorer.access._focal.data["relationship_store"]:
        if row["predicate"] != "has_structure" or row["subject_ref"] != subject:
            continue
        root = _child(explorer._location("relationship_store"), "Record", row["id"])
        qualifiers = row.get("qualifiers")
        location = _child(root, "Key", "qualifiers")
        if not isinstance(qualifiers, dict):
            gaps.append(
                {
                    "field": row["id"],
                    "location": location,
                    "state": "unrecognized_shape",
                }
            )
            continue
        location = _child(location, "Key", "ligands")
        for i, ligand in children(qualifiers.get("ligands"), location, row["id"]):
            parent = _child(location, "Index", i)
            if not isinstance(ligand, dict):
                gaps.append(
                    {
                        "field": row["id"],
                        "location": parent,
                        "state": "unrecognized_shape",
                    }
                )
                continue
            instances = _child(parent, "Key", "instances")
            for j, instance in children(
                ligand.get("instances"), instances, f"{row['id']}:{i}"
            ):
                leaf = _child(instances, "Index", j)
                if isinstance(instance, dict):
                    found.append(_Entry(leaf, f"{row['id']}:{i}:{j}", instance, j))
                else:
                    gaps.append(
                        {
                            "field": f"{row['id']}:{i}:{j}",
                            "location": leaf,
                            "state": "unrecognized_shape",
                        }
                    )
    return tuple(found), gaps


def context(explorer, entry):
    """Resolve literal parents of a typed instance; never search by component ID."""
    location = entry.location
    row, _ = explorer.access._resolve(
        {**location, "segments": location["segments"][:2]}
    )
    ligand, _ = explorer.access._resolve(
        {**location, "segments": location["segments"][:5]}
    )
    return row, ligand


def label(explorer, entry):
    row, ligand = context(explorer, entry)
    instance = entry.value.get("asym_id")
    component = ligand.get("comp_id")
    return (
        f"{row['object_ref']} · component {component if component is not None else 'unknown'}"
        f" · instance {instance if instance is not None else 'unknown'}"
        f" · entry {entry.location['segments'][-1]['value'] + 1}"
    )


def preview(explorer, entry):
    """Bounded original qualifiers; no contact classification or distance calculation."""
    from .card_exploration_render import preview as show

    row, ligand = context(explorer, entry)
    value = entry.value

    def recorded(key, owner):
        return (
            show(owner[key]) if key in owner and owner[key] is not None else "unknown"
        )

    def contact(item):
        if not isinstance(item, dict):
            return show(item)
        distance = item.get("min_distance")
        distance = (
            f"{show(distance['value'])} {show(distance['unit'])}"
            if isinstance(distance, dict) and set(distance) >= {"value", "unit"}
            else "unknown"
            if distance is None
            else show(distance)
        )
        return (
            f"chain {recorded('chain', item)} / position {recorded('position', item)}"
            f" / seq_id {recorded('seq_id', item)} / UniProt {recorded('uniprot', item)}"
            f" / recorded minimum distance {distance}"
        )

    contacts = value.get("contacts")
    chains = value.get("chains")
    return " · ".join(
        [
            "recorded chains: "
            + (
                ", ".join(show(chain, 30) for chain in chains[:6])
                + (f" … ({len(chains)} chain records)" if len(chains) > 6 else "")
                if isinstance(chains, list) and chains
                else "[] (retained empty list)"
                if chains == []
                else recorded("chains", value)
            ),
            "recorded bound flag: " + recorded("is_bound", value),
            "investigation flag: " + recorded("subject_of_investigation", ligand),
            "contact records: "
            + (
                "; ".join(contact(item) for item in contacts[:3])
                + (
                    f" … ({len(contacts)} records; open() for all)"
                    if len(contacts) > 3
                    else ""
                )
                if isinstance(contacts, list) and contacts
                else "[] (retained empty list)"
                if contacts == []
                else recorded("contacts", value)
            ),
            "unresolved parent qualifier conflicts; inspect original relationship"
            if row.get("qualifier_conflicts")
            else "relationship-level support",
        ]
    )
