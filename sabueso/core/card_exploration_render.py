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
    lines.append(
        f"{len(data.get('source_assertion_store', []))} retained source statements · "
        f"{len(data.get('relationship_store', []))} retained relationships"
    )
    quality = data.get("quality", {})
    if isinstance(quality, dict) and quality.get("conflicts"):
        lines.append("Stored conflicts are present. Open Coverage and quality records.")
    return lines


def _parts(view):
    opening = _opening(view) if view.title == "Card overview" else []
    if view.outcome["reason"]:
        opening.append(view.outcome["reason"])
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
            )
            continue
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
    footer.append("items()[i].open() · items()[i].explain() · back()")
    footer.append("Full values: rows(), native_payload. Start: explorer.topics().")
    return opening, rows, footer


def _headers(view):
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
        if view._selection._scientific is not None
        else ["Index", "Label", "Value"]
    )


def _summary_row(row):
    if len(row) == 3:
        return f"{row[0]}. {row[1]}: {row[2]}"
    return f"{row[0]}. {row[1]}: {row[2]} · {row[3]} · chains {row[4]} · sequence coverage {row[5]} · {row[6]}"


def render_text(view):
    opening, rows, footer = _parts(view)
    body = (
        [" | ".join(_headers(view)), *(" | ".join(row) for row in rows)]
        if view.presentation == "table"
        else [_summary_row(row) for row in rows]
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
        else "".join(f"<div>{escape(_summary_row(row))}</div>" for row in rows)
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
