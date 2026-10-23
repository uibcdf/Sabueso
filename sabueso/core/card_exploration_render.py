"""Bounded text/HTML previews. Full values are accessed through explicit objects."""

from html import escape


def preview(value, limit=120):
    """Never traverse/copy containers merely to abbreviate their display."""
    if isinstance(value, dict):
        return f"{len(value)} fields"
    if isinstance(value, (list, tuple)):
        return f"{len(value)} items"
    if value is None:
        return "null (retained)"
    if value is False:
        return "False"
    if isinstance(value, str) and value == "":
        return "'' (empty text)"
    if isinstance(value, str):
        return value[:limit] + ("…" if len(value) > limit else "")
    return str(value)[:limit]


def _opening(view):
    data = view.explorer.access._focal.data
    names = data.get("sections", {}).get("names", {})
    name = names.get("canonical_name", {}) if isinstance(names, dict) else None
    if isinstance(name, dict):
        name = name.get("value")
    lines = [preview(name)] if name else []
    lines.append(f"{view.explorer.profile} · captured Card")
    if view.explorer.profile == "protein":
        from .card_protein_exploration import field_entries, node

        gaps = {row["field"]: row["state"] for row in field_entries(view.explorer)[1]}

        for path, label in (
            ("annotations.organism", "Organism"),
            ("identifiers.uniprot", "UniProt accession"),
            ("sequence.length", "Sequence length"),
            ("annotations.function", "Function description"),
            ("annotations.catalytic_activity", "Catalytic activity"),
        ):
            value = node(view.explorer, path)
            if isinstance(value, dict) and "value" in value:
                lines.append(
                    f"{label}: {_field_text(path, value['value'])} · {_attribution(view.explorer, path)}"
                )
            elif path in ("annotations.function", "annotations.catalytic_activity"):
                lines.append(
                    f"{label}: "
                    + (
                        "unrecognized retained field; inspect the original content."
                        if gaps.get(path) == "unrecognized_shape"
                        else "not retained; no function is inferred from the name."
                    )
                )
        lines.append(
            f"Captured schema {preview(data.get('meta', {}).get('schema_version'))}; current sources have not been queried."
        )
        lines.append(
            "Start: items()[i].open() or explorer.questions(). All stored content: explorer.inspect()."
        )
    if view.explorer.profile in ("small_molecule", "disease"):
        from .card_protein_exploration import node

        fields = (
            (
                ("identifiers.inchikey", "Standard InChIKey"),
                ("properties.physchem.formula", "Molecular formula"),
                ("identifiers.smiles", "SMILES"),
            )
            if view.explorer.profile == "small_molecule"
            else (
                ("identifiers.mondo", "MONDO identifier"),
                ("annotations.definition", "Ontology definition"),
                ("names.synonyms", "Scoped synonyms"),
            )
        )
        for path, label in fields:
            value = node(view.explorer, path)
            if isinstance(value, dict) and "value" in value:
                lines.append(
                    f"{label}: {_field_text(path, value['value'])} · {_attribution(view.explorer, path)}"
                )
            else:
                lines.append(
                    f"{label}: no supported retained field value; inspect original content."
                )
        if view.explorer.profile == "small_molecule":
            lines.append(
                "Explore source-stated chemical identity and retained properties. No chemical calculation or target-context acquisition is performed."
            )
        else:
            lines.append(
                "Ontology terminology, not a diagnosis. Parent relationships and equivalent identifiers are separate routes; destination Cards are not opened here."
            )
        lines.append(
            f"Captured schema {preview(data.get('meta', {}).get('schema_version'))}; current sources have not been queried."
        )
        lines.append(
            "Start: items()[i].open() or explorer.questions(). All stored content: explorer.inspect()."
        )
    lines.append(
        f"{len(data.get('source_assertion_store', []))} retained source statements · "
        f"{len(data.get('relationship_store', []))} retained relationships"
    )
    quality = data.get("quality", {})
    if isinstance(quality, dict) and quality.get("conflicts"):
        lines.append(
            "Stored conflicts are present. Inspect explorer.view('quality') or original coverage/quality records."
        )
    return lines


def _field_text(path, value):
    """Bounded formatting of declared fields, never a generated interpretation."""
    if value is None:
        return "unknown (retained null)"
    if path == "annotations.definition" and isinstance(value, dict):
        return (
            preview(value.get("text"))
            + " · references: "
            + preview(value.get("references"))
        )
    if path == "names.synonyms" and isinstance(value, list):
        from .card_exploration_labels import synonym_scope

        return "; ".join(
            f"{preview(row.get('name'))} ({preview(synonym_scope(row.get('kind')))})"
            if isinstance(row, dict)
            else preview(row)
            for row in value[:2]
        ) + (f" … ({len(value)} total)" if len(value) > 2 else "")
    if path == "annotations.catalytic_activity" and isinstance(value, list):
        parts = []
        for record in value[:2]:
            if isinstance(record, dict):
                parts.append(
                    " · ".join(
                        f"{label}: {preview(record[key])}"
                        for key, label in (
                            ("ec_number", "EC"),
                            ("reaction", "Reaction"),
                            ("rhea_id", "Rhea"),
                        )
                        if key in record
                    )
                    or preview(record)
                )
            else:
                parts.append(preview(record))
        return (
            "; ".join(parts) + (f" … ({len(value)} total)" if len(value) > 2 else "")
            if value
            else "[] (retained empty list)"
        )
    if isinstance(value, list):
        return (
            "; ".join(preview(item) for item in value[:2])
            + (f" … ({len(value)} total)" if len(value) > 2 else "")
            if value
            else "[] (retained empty list)"
        )
    return preview(value) + (
        " residues" if path == "sequence.length" and type(value) is int else ""
    )


def _selected_references(field):
    """A malformed member invalidates the selection declaration as a whole."""
    if not isinstance(field, dict) or "source_assertion_ids" not in field:
        return None, "selection references not retained"
    refs = field["source_assertion_ids"]
    if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
        return None, "unrecognized selection references"
    return refs, None


def _attribution(explorer, path, field=None):
    """Show actual retained attribution; no credit for an unretained assertion."""
    from .card_protein_exploration import node

    field = node(explorer, path) if field is None else field
    refs, reason = _selected_references(field)
    if refs is None:
        return (
            "source attribution not retained"
            if reason == "selection references not retained"
            else f"source attribution unknown: {reason}"
        )
    names = []
    missing = False
    for ref in refs[:4]:
        if isinstance(ref, str):
            statement = explorer._statement(ref)
            if statement["state"] != "present":
                missing = True
                continue
            record, _ = explorer.access._resolve(statement["location"])
            source = record.get("source", {})
            name = source.get("name") if isinstance(source, dict) else None
            if isinstance(name, str) and name not in names:
                names.append(name)
    return (
        (
            ", ".join(preview(name, 50) for name in names[:3])
            or "source attribution not retained"
        )
        + ("; some support not retained" if missing else "")
        + (f"; {len(refs)} support references, see explain()" if len(refs) > 4 else "")
    )


def _method(explorer, field):
    refs, reason = _selected_references(field)
    if refs is None:
        return f"selected-source method unknown: {reason}"
    methods = []
    missing = False
    for ref in refs[:4]:
        statement = explorer._statement(ref)
        if statement["state"] != "present":
            missing = True
            continue
        record, _ = explorer.access._resolve(statement["location"])
        metadata = record.get("source_metadata") or {}
        method = metadata.get("method") if isinstance(metadata, dict) else None
        if isinstance(method, str) and method not in methods:
            methods.append(method)
    partial = (
        f"partial preview: 4 of {len(refs)} references; inspect explain()"
        if len(refs) > 4
        else None
    )
    if methods:
        return " · ".join(
            [
                "selected-source method: "
                + ", ".join(preview(value) for value in methods),
                *(["some supporting records not retained"] if missing else []),
                *([partial] if partial else []),
            ]
        )
    if missing:
        return "selected-source method unknown: supporting records not retained" + (
            f" · {partial}" if partial else ""
        )
    if partial:
        return f"selected-source method unknown: {partial}"
    return "method not stated in selected support"


def _region_text(native):
    chains = native.get("complete_chains")
    if chains is None:
        return "region coordinate annotations not retained"
    return (
        "complete chains in retained coordinate annotations: "
        + (", ".join(preview(chain, 30) for chain in chains[:4]) if chains else "none")
        + (f" … ({len(chains)} total)" if len(chains) > 4 else "")
    )


def _structural_support(context):
    native, support = context["native"], context["support"]
    status = native.get("status")
    lines = [
        f"Why this structure is shown: {preview(native.get('structure_ref'))}",
        "Inventory outcome: "
        + (
            "grouped by retained structural state; this is not a structure recommendation."
            if status == "grouped"
            else preview(status)
            if status is not None
            else "not retained"
        ),
    ]
    if native.get("reason") is not None:
        lines.append("Original inventory reason: " + preview(native["reason"]))
    rule = native.get("rule", {})
    lines.append("Explanation rule: " + preview(rule.get("rule")))
    rules = native.get("rules", [])
    lines.append(
        "Original classification rules: "
        + ", ".join(preview(row.get("rule"), 90) for row in rules[:4])
        + (f" … ({len(rules)} total)" if len(rules) > 4 else "")
    )
    options = context["options"]
    region = options.get("region")
    lines.append(
        f"Scientific options: include fragments = {preview(options['include_fragments'])}; "
        + (
            "no region restriction."
            if region is None
            else "canonical region positions "
            + ", ".join(preview(value, 20) for value in region[:12])
            + (f" … ({len(region)} total)" if len(region) > 12 else "")
        )
    )
    item = native.get("item") or {}
    state = item.get("state") or {}
    labels = {
        "method": "Method",
        "coverage": "Sequence coverage class",
        "sequence": "Sequence state",
        "ligands": "Ligand state",
        "oligomer": "Oligomer state",
        "in_complex": "Complex state",
    }
    for key, label in labels.items():
        value = state.get(key)
        lines.append(f"{label}: {'unknown' if value is None else preview(value)}")
    if item.get("qualifier_conflicts"):
        lines.append(
            "Unresolved qualifier conflicts are retained; inspect native_payload['item']['qualifier_conflicts']."
        )
    missing = sum(
        row["state"] == "not_retained" for row in support["source_assertions"]
    )
    if missing:
        lines.append(f"{missing} relationship source records not retained.")
    elif not support["source_assertion_ids"]:
        lines.append("No source references are declared for this relationship.")
    lines.extend(
        [
            "Source records support the stored structure relationship, not individual qualifiers or the derived grouping.",
            "Sequence coverage does not establish coordinate completeness. Full group members, reference context and rules remain in native_payload.",
        ]
    )
    return lines


def _parts(view):
    opening = _opening(view) if view.title == "Card overview" else []
    if view._explorer.mode == "saved":
        opening.insert(
            0,
            "Saved exploration · retained values, sources and navigation; no scientific recomputation.",
        )
    if view.outcome["reason"]:
        opening.append(view.outcome["reason"])
    if view.request is not None:
        request = view.request
        opening.append(f"Question: {request['question']}")
        if request["question"] == "region_coverage":
            options = request["options"]
            region = options["region"]
            opening.append(f"Sequence axis: {preview(options['sequence_ref'])}")
            if region:
                opening.append(
                    "Positions: "
                    + ", ".join(str(p) for p in region[:12])
                    + (f" … ({len(region)} total)" if len(region) > 12 else "")
                )
    if view._record_panel == "coverage" and view.explorer._coverage_result.native:
        opening.append(
            "Classification: "
            + view.explorer._coverage_result.native["rule"]["rule"]
            + "; source/request states remain distinct. Unknown counts are not zero; no global completeness score is inferred."
        )
    if view._field_panel:
        opening.append(
            "Retained fields with original support; source coverage is not evaluated. Open explain() to review source records and stored alternatives."
        )
    from .card_exploration_labels import (
        explanation_context,
        relationship_basis,
        source_record,
        structural_explanation,
    )

    structural = structural_explanation(view)
    if structural is not None:
        opening.extend(_structural_support(structural))
        opening.append(
            "Open a source record below; back() returns to your structural selection."
            if len(view.items()) and source_record(view.items()[0])
            else "Return with back() and open the structure's related() links to follow original sources; retained detail remains inspectable."
        )
    original_support = explanation_context(view)
    if "selection_support_state" in original_support or any(
        "source_assertion_ids" in support
        for support in original_support.get("support", [])
    ):
        opening.append(
            "Source roles describe the original retained selection, not source reliability."
        )
        if original_support.get("selection_support_state") == "declared":
            opening.append(
                "Alternative statements are other retained statements for this field; they can agree with the selected value and do not replace it."
            )
        if original_support.get("selection_support_state") in (
            "not_retained",
            "unrecognized",
        ):
            opening.append(
                "Selection references are missing or unrecognized; field statements have no assigned selection role."
            )
        missing = sum(
            statement.get("state") == "not_retained"
            for support in original_support["support"]
            for statement in support.get("statements", [])
        )
        if missing:
            opening.append(
                f"{missing} supporting source records not retained; inspect native_payload['support'] for their exact references."
            )
        if original_support.get("stored_conflicts"):
            opening.append(
                "Stored conflicts remain unresolved; inspect native_payload['stored_conflicts']."
            )
        if original_support.get("stored_alternatives"):
            opening.append(
                "Stored alternative-selection context is retained in native_payload['stored_alternatives']."
            )
    if view._field_panel == "definition":
        opening.append(
            "Synonym scopes describe terminology; they do not establish disease identity."
        )
    scientific = view._selection._scientific
    if scientific is not None:
        opening.append(
            "Inventory sequence coverage does not establish coordinate completeness."
        )
        opening.append(
            f"{len(scientific.wire['exclusions'])} scientific exclusions; inspect exclusions for original reasons."
        )
        for row in scientific.wire["coverage"].get("rows", [])[:4]:
            opening.append(
                f"{preview(row['source'])}: {preview(row['state'])} (retained source/request scope)"
            )
    if scientific is not None and view._focus is not None:
        for key, value in scientific.native_item(view._focus)["state"].items():
            opening.append(
                f"Structural state · {preview(key)}: {'unknown' if value is None else preview(value)}"
            )
    rows = []
    for index, item in enumerate(view.items()[:10]):
        # Literal previews preserve null/zero/false; units remain paired with
        # native values without invoking a scientific adapter.
        value = item._entry.value
        if view._link_panel:
            rows.append(
                (
                    str(index),
                    preview(item.label),
                    f"{preview(value['availability'])} · {len(value['candidates'])} captured destinations",
                )
            )
            continue
        if view._record_panel:
            from .card_exploration_profiles import RECORD_COLUMNS

            record_row = (
                str(index),
                *(
                    "unknown" if value.get(key) is None else preview(value[key])
                    for key in RECORD_COLUMNS[view._record_panel]
                ),
            )
            if view._record_panel == "classification":
                basis, rule = relationship_basis(item)
                record_row += (
                    preview(basis) + (f" · {preview(rule)}" if rule else ""),
                )
                if basis == "Source-supported broader term":
                    record_row = (
                        *record_row[:-1],
                        record_row[-1] + "; no derivation recorded",
                    )
            rows.append(record_row)
            continue
        if scientific is not None:
            import pyunitwizard as puw

            native = scientific.native_item(item._entry.key)
            resolution = native["resolution"]
            resolution_text = (
                "resolution unknown"
                if resolution is None
                else f"{preview(puw.get_value(resolution, to_unit='angstrom'))} angstrom"
            )
            chains = native["chains"]
            chains_text = (
                "unknown"
                if chains is None
                else (
                    ", ".join(preview(chain) for chain in chains[:4])
                    + (f" … ({len(chains)} total)" if len(chains) > 4 else "")
                    if isinstance(chains, list)
                    else preview(chains)
                )
            )
            rows.append(
                (
                    str(index),
                    preview(item.label),
                    "unknown"
                    if native["method"] is None
                    else preview(native["method"]),
                    resolution_text,
                    chains_text,
                    "unknown"
                    if native["coverage"] is None
                    else preview(native["coverage"]),
                    "unknown"
                    if native["coverage_class"] is None
                    else preview(native["coverage_class"]),
                )
                + (
                    (_region_text(native),)
                    if view.request and view.request["question"] == "region_coverage"
                    else ()
                )
            )
            continue
        elif view._field_panel:
            from .card_exploration_profiles import is_field

            if not is_field(item._entry):
                shown = f"{preview(value['subject_ref'])} → {preview(value['object_ref'])}; source-stated identity, not a similarity match"
                rows.append((str(index), preview(item.label), shown))
                continue
            shown = _field_text(item._entry.key, value["value"])
            if "unit" in value:
                shown += " " + preview(value["unit"])
            if view._field_panel == "properties":
                shown += " · " + _method(view.explorer, value)
            state = (
                "conflicting"
                if item._conflicts
                else "unknown"
                if value["value"] is None
                else "present"
            )
            shown += (
                f" · {_attribution(view.explorer, item._entry.key, value)} · {state}"
            )
        elif view._question_catalog:
            shown = (
                preview(value["scope"])
                + "; required options: "
                + (", ".join(value["required_options"]) or "none")
            )
        elif view._route_catalog:
            shown = preview(value["description"]) + (
                f" · {value['availability']}" if "availability" in value else ""
            )
        elif source_record(item):
            source = value.get("source")
            version = source.get("version") if isinstance(source, dict) else None
            retrieved = value.get("retrieved_at")
            asserted = (
                preview(value["asserted_value"])
                if "asserted_value" in value
                else "asserted value not retained"
            )
            shown = f"{asserted} · source version {preview(version) if version is not None else 'unknown'} · retrieved {preview(retrieved) if retrieved is not None else 'unknown'}"
            metadata = value.get("source_metadata")
            method = metadata.get("method") if isinstance(metadata, dict) else None
            shown += (
                f" · method: {preview(method)}"
                if method is not None
                else " · method not stated"
            )
            if isinstance(metadata, dict) and metadata.get("unit") is not None:
                shown += " · source unit: " + preview(metadata["unit"])
        elif isinstance(value, dict) and "value" in value:
            shown = preview(value["value"])
            if "unit" in value:
                shown += f" {preview(value['unit'])}"
        else:
            shown = preview(value)
        rows.append((str(index), preview(item.label), shown))
    count = len(view.items())
    footer = [
        f"{count} items" + (f" · showing 10, {count - 10} more" if count > 10 else "")
    ]
    footer.append(
        "items()[i].open() · items()[i].explain() · items()[i].related() · back()"
    )
    footer.append(
        "Full values: rows(), native_payload. "
        + (
            "No destination Card supplied; explorer is None. Retained context and back() remain available."
            if view.explorer is None
            else "Start: explorer.topics()."
        )
    )
    return opening, rows, footer


def _headers(view):
    if view._record_panel:
        return (
            ["Index", "Area", "Source", "State", "Count", "Release"]
            if view._record_panel == "coverage"
            else ["Index", "Subject", "Relationship", "Broader term reference", "Basis"]
        )
    return (
        [
            "Index",
            "Structure",
            "Method",
            "Resolution",
            "Chains",
            "Sequence coverage",
            "Coverage class",
        ]
        + (
            ["Requested region"]
            if view.request and view.request["question"] == "region_coverage"
            else []
        )
        if view._selection._scientific is not None
        else ["Index", "Label", "Value"]
    )


def _summary_row(row, view):
    if view._record_panel:
        return (
            row[0]
            + ". "
            + " · ".join(
                f"{label}: {value}" for label, value in zip(_headers(view)[1:], row[1:])
            )
        )
    if len(row) == 3:
        return f"{row[0]}. {row[1]}: {row[2]}"
    return (
        f"{row[0]}. {row[1]}: {row[2]} · {row[3]} · chains {row[4]} · sequence coverage {row[5]} · {row[6]}"
        + (f" · {row[7]}" if len(row) == 8 else "")
    )


def render_text(view):
    opening, rows, footer = _parts(view)
    body = (
        [" | ".join(_headers(view)), *(" | ".join(row) for row in rows)]
        if view.presentation == "table"
        else [_summary_row(row, view) for row in rows]
    )
    return "\n".join([preview(view.title), *opening, *body, *footer])


def render_html(view):
    """Escape source text; the preview is inert, with explicit Python actions."""
    opening, rows, footer = _parts(view)
    body = (
        "<table><thead><tr>"
        + "".join(f"<th>{escape(label)}</th>" for label in _headers(view))
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>"
            for row in rows
        )
        + "</tbody></table>"
        if view.presentation == "table"
        else "".join(f"<div>{escape(_summary_row(row, view))}</div>" for row in rows)
    )
    return (
        "<section><strong>"
        + escape(preview(view.title))
        + "</strong>"
        + "".join(f"<div>{escape(line)}</div>" for line in opening)
        + body
        + "".join(f"<div>{escape(line)}</div>" for line in footer)
        + "</section>"
    )
