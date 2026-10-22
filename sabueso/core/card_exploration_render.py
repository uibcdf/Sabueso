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
    if value == "":
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
    rows = []
    for index, item in enumerate(view.items()[:10]):
        # Literal previews preserve null/zero/false; units remain paired with
        # native values without invoking a scientific adapter.
        value = item._entry.value
        if isinstance(value, dict) and "value" in value:
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


def render_text(view):
    opening, rows, footer = _parts(view)
    body = (
        ["Index | Label | Value", *(" | ".join(row) for row in rows)]
        if view.presentation == "table"
        else [f"{index}. {label}: {value}" for index, label, value in rows]
    )
    return "\n".join([preview(view.title), *opening, *body, *footer])


def render_html(view):
    """Escape source text; the preview is inert, with explicit Python actions."""
    opening, rows, footer = _parts(view)
    body = (
        "<table><thead><tr><th>Index</th><th>Label</th><th>Value</th></tr></thead><tbody>"
        + "".join(
            "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>"
            for row in rows
        )
        + "</tbody></table>"
        if view.presentation == "table"
        else "".join(
            f"<div>{index}. {escape(label)}: {escape(value)}</div>"
            for index, label, value in rows
        )
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
