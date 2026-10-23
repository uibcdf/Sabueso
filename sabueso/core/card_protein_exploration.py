"""Retained protein fields and explicit question scope, without new science."""

from .card_access import _Entry
from .errors import ArgumentError

FUNCTION_FIELDS = {
    "annotations.function": "Function description",
    "annotations.catalytic_activity": "Catalytic activity",
    "annotations.pathway": "Biological pathways",
    "names.canonical_name": "Protein name",
    "annotations.organism": "Organism",
    "identifiers.uniprot": "UniProt accession",
    "sequence.length": "Sequence length",
}
_SOURCE_QUESTIONS = {
    "structure_ligands": {
        "label": "Which ligand instances and contacts are declared in retained structures?",
        "topic": "ligand_instances",
        "required_options": [],
        "scope": "Original structure-local instances, recorded chains and contact coordinates/distances; no assembly or aggregated-contact join.",
    },
    "sequence_annotations": {
        "label": "Which sequence and positional annotations are retained?",
        "topic": "sequence",
        "required_options": [],
        "scope": "Original sequence fields and annotation locations; no coordinate projection or alignment.",
    },
    "predicted_models": {
        "label": "Which predicted models and source confidence metrics are retained?",
        "topic": "predicted_structures",
        "required_options": [],
        "scope": "Original model declarations, source metrics and recorded sequence/isoform context; separate from experimental structures.",
    },
    "retained_sites": {
        "label": "Which annotated sites and contact statements are retained?",
        "topic": "sites",
        "required_options": [],
        "scope": "Original active, binding and family-model sites plus ligand/interface contact statements; no new overlap or proximity calculation.",
    },
}
QUESTIONS = {
    "function": {
        "label": "What do the sources state this protein does?",
        "topic": "function",
        "required_options": [],
        "scope": "Retained function and catalytic annotations, with original support.",
    },
    "region_coverage": {
        "label": "What do retained structures tell us about this region?",
        "topic": "structures",
        "required_options": ["sequence_ref", "region"],
        "scope": "Explicit canonical UniProt positions; sequence coverage alone does not establish coordinate completeness.",
    },
}
QUESTIONS.update(_SOURCE_QUESTIONS)


def node(explorer, path):
    """Read only an exact declared path; unrecognized shapes stay inspectable."""
    value = explorer.access._focal.data.get("sections", {})
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def field_entries(explorer):
    entries, gaps = [], []
    for path, label in FUNCTION_FIELDS.items():
        location = explorer._location("sections", *path.split("."))
        try:
            value, _ = explorer.access._resolve(location)
        except ArgumentError:
            gaps.append({"field": path, "label": label, "state": "not_retained"})
            continue
        if not isinstance(value, dict) or "value" not in value:
            gaps.append(
                {
                    "field": path,
                    "label": label,
                    "state": "unrecognized_shape",
                    "location": location,
                }
            )
            continue
        entries.append(_Entry(location, path, value))
    return tuple(entries), gaps


def region_request(explorer, options):
    """Validate exact canonical scope before invoking any structural reader."""
    from .card_scientific_access import options_for_structures

    if not isinstance(options, dict) or set(options) - {
        "sequence_ref",
        "region",
        "include_fragments",
    }:
        raise ArgumentError(
            "region_coverage options: sequence_ref, region and include_fragments only."
        )
    sequence_ref = options.get("sequence_ref")
    if sequence_ref is not None and (
        not isinstance(sequence_ref, str) or not sequence_ref.strip()
    ):
        raise ArgumentError(
            "sequence_ref requires a nonempty explicit sequence reference."
        )
    effective = options_for_structures(
        {key: value for key, value in options.items() if key != "sequence_ref"}
    )
    effective = {"sequence_ref": sequence_ref, **effective}
    if sequence_ref is None or effective["region"] is None:
        return (
            effective,
            "missing_prerequisite",
            (
                "Supply options with sequence_ref='uniprot:<accession>' and region "
                "as positive positions or inclusive [begin, end] ranges."
            ),
        )
    accession = node(explorer, "identifiers.uniprot")
    accession = accession.get("value") if isinstance(accession, dict) else None
    if not isinstance(accession, str) or not accession:
        return (
            effective,
            "missing_prerequisite",
            "No retained canonical UniProt accession identifies this sequence axis.",
        )
    if sequence_ref != f"uniprot:{accession}":
        return (
            effective,
            "unsupported",
            (
                f"Only the captured canonical axis uniprot:{accession} is supported; "
                "no isoform, construct or residue-number mapping is inferred."
            ),
        )
    data = explorer.access._focal.data
    identity = data.get("meta", {}).get("card_id")
    quality = data.get("quality", {})
    conflicts = quality.get("conflicts", []) if isinstance(quality, dict) else []
    conflicted = any(
        isinstance(row, dict)
        and str(row.get("field")).removesuffix(".value")
        in {"identifiers.uniprot", "sequence.primary", "sequence.length"}
        for row in conflicts or []
    )
    length, sequence = (
        node(explorer, "sequence.length"),
        node(explorer, "sequence.primary"),
    )
    length = length.get("value") if isinstance(length, dict) else None
    sequence = sequence.get("value") if isinstance(sequence, dict) else None
    if (
        identity != f"sabueso:protein:uniprot:{accession}"
        or conflicted
        or type(length) is not int
        or length < 1
        or not isinstance(sequence, str)
        or len(sequence) != length
    ):
        return (
            effective,
            "missing_prerequisite",
            (
                "A consistent retained canonical identity, sequence and length are required; "
                "inspect identity/sequence fields and stored conflicts."
            ),
        )
    if effective["region"][-1] > length:
        raise ArgumentError(
            f"region extends beyond the retained canonical sequence length ({length})."
        )
    return effective, "ok", None
