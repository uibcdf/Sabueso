"""Nature-specific retained-field presentations, without new scientific findings."""

from .card_access import _Entry
from .card_protein_exploration import FUNCTION_FIELDS
from .card_protein_exploration import QUESTIONS as PROTEIN_QUESTIONS

CHEMISTRY = {
    "names.canonical_name": "Molecule name",
    "identifiers.inchikey": "Standard InChIKey",
    "identifiers.smiles": "SMILES",
    "identifiers.inchi": "InChI",
    "identifiers.chembl": "ChEMBL identifier",
    "identifiers.pubchem": "PubChem identifier",
    "identifiers.chebi": "ChEBI identifier",
    "properties.physchem.formula": "Molecular formula",
    "properties.physchem.molecule_type": "Source molecule type",
}
PROPERTIES = {
    "molecular_weight": "Molecular weight",
    "tpsa": "Topological polar surface area",
    "logp": "logP",
    "hbd": "Hydrogen bond donors",
    "hba": "Hydrogen bond acceptors",
    "rotatable_bonds": "Rotatable bonds",
    "aromatic_rings": "Aromatic rings",
    "formula": "Molecular formula",
    "molecule_type": "Source molecule type",
}
DEFINITION = {
    "names.canonical_name": "Disease term",
    "identifiers.mondo": "MONDO identifier",
    "annotations.definition": "Ontology definition",
    "names.synonyms": "Scoped synonyms",
    "annotations.disease_subsets": "Ontology subsets",
    "annotations.term_status": "Retained term status",
}
IDENTITY = {
    "identifiers.mondo": "MONDO identifier",
    "identifiers.equivalent_ids": "Source-stated equivalent identifiers",
    "identifiers.related_ids": "Related identifiers (not equivalence)",
}
PANELS = {
    "function": ("protein", FUNCTION_FIELDS),
    "chemistry": ("small_molecule", CHEMISTRY),
    "properties": ("small_molecule", {}),
    "definition": ("disease", DEFINITION),
    "identity": ("disease", IDENTITY),
    "sequence": ("protein", {}),
    "predicted_structures": ("protein", {}),
    "sites": ("protein", {}),
    "ligand_instances": ("protein", {}),
}
NATURE_TOPICS = {
    "protein": (
        "function",
        "structures",
        "sequence",
        "predicted_structures",
        "sites",
        "ligand_instances",
    ),
    "small_molecule": ("chemistry", "properties"),
    "disease": ("definition", "classification", "identity"),
}


def _question(label, topic, scope):
    return {"label": label, "topic": topic, "required_options": [], "scope": scope}


QUESTIONS = {
    "protein": PROTEIN_QUESTIONS,
    "small_molecule": {
        "chemical_identity": _question(
            "Which chemical entity do these records describe?",
            "chemistry",
            "Retained identifiers, representations and source-stated identity links; no computed chemistry.",
        ),
        "property_context": _question(
            "What properties are retained, and on what source basis?",
            "properties",
            "Stored values, units, source methods and original alternatives.",
        ),
    },
    "disease": {
        "meaning": _question(
            "What does this disease term mean?",
            "definition",
            "Ontology definition, scoped synonyms and retained term metadata; not a diagnosis.",
        ),
        "classification": _question(
            "Which broader terms are stated?",
            "classification",
            "Retained parent relationships; equivalent and related identifiers have a separate identity route.",
        ),
    },
}


def field_label(topic, entry, explorer=None):
    from .card_protein_source_v1 import TOPICS, label

    if topic == "ligand_instances":
        from .card_ligand_instances_v1 import label as instance_label

        return instance_label(explorer, entry)
    if topic in TOPICS:
        return label(topic, entry)
    if entry.location["segments"][0]["value"] == "relationship_store":
        row = entry.value
        return f"Source-stated identity: {row['subject_ref']} → {row['object_ref']}"
    if topic == "properties":
        key = entry.location["segments"][-1]["value"]
        return PROPERTIES.get(key, f"{key} (retained property field)")
    return PANELS[topic][1][entry.key]


def is_field(entry):
    return (
        entry.location["kind"] == "card"
        and entry.location["segments"][0]["value"] == "sections"
    )


def field_entries(explorer, topic):
    """Keep exact typed locations, including literal property keys containing dots."""
    from .card_protein_source_v1 import TOPICS, entries
    from .errors import ArgumentError

    if topic == "ligand_instances":
        from .card_ligand_instances_v1 import entries as instance_entries

        return instance_entries(explorer)
    if topic in TOPICS:
        return entries(explorer, topic)

    entries, gaps = [], []
    if topic == "properties":
        parent = explorer._location("sections", "properties", "physchem")
        try:
            node, _ = explorer.access._resolve(parent)
        except ArgumentError:
            return (), [{"field": "properties.physchem", "state": "not_retained"}]
        if not isinstance(node, dict):
            return (), [
                {
                    "field": "properties.physchem",
                    "state": "unrecognized_shape",
                    "location": parent,
                }
            ]
        candidates = [
            (f"properties.physchem.{entry.key}", entry.location, entry.value)
            for entry in explorer.access._children(node, parent)
        ]
    else:
        candidates = []
        for path in PANELS[topic][1]:
            location = explorer._location("sections", *path.split("."))
            try:
                node, _ = explorer.access._resolve(location)
            except ArgumentError:
                gaps.append(
                    {
                        "field": path,
                        "label": PANELS[topic][1][path],
                        "state": "not_retained",
                    }
                )
                continue
            candidates.append((path, location, node))
    for path, location, node in candidates:
        if not isinstance(node, dict) or "value" not in node:
            gaps.append(
                {"field": path, "state": "unrecognized_shape", "location": location}
            )
        else:
            entries.append(_Entry(location, path, node))
    if topic == "chemistry":
        location = explorer._location("relationship_store")
        entries.extend(
            entry
            for entry in explorer.access._children(
                explorer.access._focal.data["relationship_store"], location
            )
            if entry.value["predicate"] == "same_as"
        )
    return tuple(entries), gaps


RECORD_COLUMNS = {
    "classification": ("subject_ref", "predicate", "object_ref"),
    "coverage": ("area", "source", "state", "count", "release"),
}


def record_label(panel, row):
    return (
        f"{row['area']} · {row['source']}" if panel == "coverage" else row["object_ref"]
    )


def alternatives(explorer, entry):
    if not is_field(entry):
        return {"alternative_source_assertions": [], "stored_alternatives": []}
    selected = entry.value.get("source_assertion_ids")
    identified = isinstance(selected, list) and all(
        isinstance(ref, str) for ref in selected
    )
    if not identified:
        selected = []
    records = explorer.access._focal.data["source_assertion_store"]
    quality = explorer.access._focal.data.get("quality", {})
    stored = quality.get("alternatives", []) if isinstance(quality, dict) else []
    return {
        "selection_support_state": "declared"
        if identified
        else "not_retained"
        if "source_assertion_ids" not in entry.value
        else "unrecognized",
        "alternative_source_assertions": [
            explorer._statement(row["id"])
            for row in records
            if identified
            and row.get("field_path") == entry.key
            and row["id"] not in selected
        ],
        "unclassified_field_source_assertions": [
            explorer._statement(row["id"])
            for row in records
            if not identified and row.get("field_path") == entry.key
        ],
        "stored_alternatives": [
            row
            for row in stored or []
            if isinstance(row, dict) and row.get("field") == entry.key
        ],
    }
