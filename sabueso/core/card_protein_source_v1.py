"""Original protein source panels v1, with exact retained-node membership.

These predicates bind source presentations, not derived scientific results.
Keep their membership stable for saved readers; new admission semantics need a
new adapter version. No numbering projection or model/site classification runs.
"""

from .card_access import _Entry
from .errors import ArgumentError

SEQUENCE_FIELDS = (
    ("identifiers.uniprot", "UniProt accession"),
    ("sequence.primary", "Primary sequence"),
    ("sequence.length", "Sequence length"),
    ("sequence.molecular_weight", "Sequence molecular weight"),
    ("sequence.checksums", "Source sequence checksums"),
)
FEATURE_LABELS = {
    "active_site": "Active sites",
    "binding_site": "Binding sites",
    "family_site": "Family-model sites",
    "secondary_structure": "Secondary structure annotations",
    "chain": "Annotated chains",
    "domains": "Domains",
    "region": "Annotated regions",
    "motif": "Motifs",
    "disulfide_bond": "Disulfide bonds",
    "natural_variant": "Natural variants",
    "mutagenesis": "Mutagenesis annotations",
    "alternative_sequence": "Alternative sequence annotations",
    "sequence_conflict": "Sequence conflicts",
    "glycosylation": "Glycosylation annotations",
    "lipidation": "Lipidation annotations",
    "modified_residue": "Modified residues",
    "transmembrane": "Transmembrane regions",
    "topological_domain": "Topological domains",
}
SITE_FIELDS = ("active_site", "binding_site", "family_site")
TOPICS = ("sequence", "predicted_structures", "sites")
SCOPES = {
    "sequence": "Original sequence fields and positional annotations. Locations retain their stated axis, indexing and modifiers; no alignment or residue projection is performed.",
    "predicted_structures": "Source model declarations, versions and metrics with recorded sequence/isoform context. No experimental equivalence, sequence comparison or coverage calculation is inferred. Recorded match/isoform flags are not attributed as direct source claims; this pane does not establish their derivation/input basis.",
    "sites": "Original functional-site fields and exact-subject ligand/interface contact relationships. Aggregated contacts are not ligand instances; no site overlap, proximity or cavity is computed.",
}
MODEL_FIELDS = {
    "model_version": "Model version",
    "tool": "Prediction tool",
    "mean_plddt": "Source mean pLDDT",
    "plddt_fractions": "Source pLDDT bands",
    "range": "Source sequence range",
    "isoform": "Recorded isoform context",
    "sequence_matches": "Recorded sequence-match flag",
    "created": "Model creation date",
}


def feature_label(key):
    return FEATURE_LABELS.get(key, f"Other positional annotation ({key})")


def focal_subject(explorer):
    data = explorer.access._focal.data
    identity = data.get("meta", {}).get("card_id")
    identifiers = data.get("sections", {}).get("identifiers")
    field = identifiers.get("uniprot") if isinstance(identifiers, dict) else None
    accession = field.get("value") if isinstance(field, dict) else None
    quality = data.get("quality")
    conflicts = quality.get("conflicts", []) if isinstance(quality, dict) else None
    if (
        isinstance(accession, str)
        and accession
        and identity == f"sabueso:protein:uniprot:{accession}"
        and isinstance(conflicts, list)
        and not any(
            isinstance(row, dict)
            and str(row.get("field")).removesuffix(".value") == "identifiers.uniprot"
            for row in conflicts
        )
    ):
        return f"uniprot:{accession}"
    return None


def entries(explorer, topic):
    """Select original fields/relationships, preserving literal keys and subjects."""
    found, gaps = [], []

    def field(path, keys):
        location = explorer._location("sections", *keys)
        try:
            node, _ = explorer.access._resolve(location)
        except ArgumentError:
            gaps.append({"field": path, "state": "not_retained"})
            return
        if not isinstance(node, dict) or "value" not in node:
            gaps.append(
                {"field": path, "state": "unrecognized_shape", "location": location}
            )
        else:
            found.append(_Entry(location, path, node))

    if topic == "sequence":
        for path, _ in SEQUENCE_FIELDS:
            field(path, path.split("."))
    if topic in ("sequence", "sites"):
        parent = explorer.access._focal.data.get("sections", {}).get(
            "features_positional"
        )
        if not isinstance(parent, dict):
            gaps.append(
                {
                    "field": "features_positional",
                    "state": "not_retained" if parent is None else "unrecognized_shape",
                }
            )
        else:
            for key in sorted(parent) if topic == "sequence" else SITE_FIELDS:
                field(f"features_positional.{key}", ["features_positional", key])
    if topic in ("predicted_structures", "sites"):
        subject = focal_subject(explorer)
        if subject is None:
            gaps.append(
                {"field": "relationship subject", "state": "missing_prerequisite"}
            )
        else:
            predicates = (
                {"has_predicted_structure"}
                if topic == "predicted_structures"
                else {"has_ligand_site", "has_interface_with"}
            )
            location = explorer._location("relationship_store")
            found.extend(
                entry
                for entry in explorer.access._children(
                    explorer.access._focal.data["relationship_store"], location
                )
                if entry.value["subject_ref"] == subject
                and entry.value["predicate"] in predicates
            )
    return tuple(found), gaps


def label(topic, entry):
    segments = entry.location["segments"]
    if segments[0]["value"] == "relationship_store":
        row = entry.value
        if topic == "predicted_structures":
            version = (row.get("qualifiers") or {}).get("model_version")
            return f"Predicted model · {row['object_ref']} · version {version if version is not None else 'unknown'}"
        prefix = (
            "Ligand contacts"
            if row["predicate"] == "has_ligand_site"
            else "Interface contacts"
        )
        return f"{prefix} · {row['object_ref']}"
    if segments[1]["value"] == "features_positional":
        return feature_label(segments[2]["value"])
    return dict(SEQUENCE_FIELDS).get(entry.key, entry.key)


def node_label(item):
    """Readable exact schema nodes; literal lookalikes retain generic labels."""
    location = item._entry.location
    s = location.get("segments", [])
    if (
        location["kind"] != "card"
        or not s
        or s[0] != {"type": "Key", "value": "sections"}
    ):
        return None
    if (
        len(s) >= 3
        and s[1] == {"type": "Key", "value": "features_positional"}
        and s[2]["type"] == "Key"
    ):
        if len(s) == 4:
            return {
                "value": "Annotations",
                "source_assertion_ids": "Supporting source references",
            }.get(s[-1]["value"])
        if (
            len(s) == 5
            and s[3] == {"type": "Key", "value": "value"}
            and s[4]["type"] == "Index"
        ):
            row = item._entry.value
            description = row.get("description") if isinstance(row, dict) else None
            return (
                f"{feature_label(s[2]['value'])} · annotation {s[4]['value'] + 1}"
                + (
                    f" · {description}"
                    if isinstance(description, str) and description
                    else ""
                )
            )
    return None
