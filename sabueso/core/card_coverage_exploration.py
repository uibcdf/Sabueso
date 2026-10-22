"""One captured knowledge-state result, with lazy original scoped explanations."""

from dataclasses import dataclass, field, replace

from .card_access import _Entry


@dataclass
class _CoverageCapture:
    card: object
    native: dict
    view: object
    explanations: dict = field(default_factory=dict)


def view(explorer, origin=None):
    from .card_scientific_access import _CapturedCard
    from .knowledge_state import knowledge_state

    if explorer._coverage_result is None:
        if not explorer.access._focal.pin:
            result = explorer._metadata(
                {"context": explorer.context, "outcome": "missing_prerequisite"},
                "Knowledge coverage",
            )
            result = replace(
                result,
                _selection=replace(result._selection, _entries=()),
                _selected=(),
                _status="missing_prerequisite",
                _reason="A captured Card identity is required for original pinned coverage explanations; stored quality remains inspectable.",
                _record_panel="coverage",
            )
            explorer._coverage_result = _CoverageCapture(None, {}, result)
        else:
            card = _CapturedCard(explorer.access._focal)
            native = knowledge_state(card)
            result = explorer._metadata(
                {
                    "adapter": "knowledge_coverage_exploration@1",
                    "context": explorer.context,
                    "native_payload": native,
                },
                "Knowledge coverage",
            )
            _, root = explorer.access._resolve(result._selection._target["location"])
            rows_location = {
                **root,
                "segments": [
                    {"type": "Key", "value": "native_payload"},
                    {"type": "Key", "value": "rows"},
                ],
            }
            entries = tuple(
                _Entry(
                    {
                        **rows_location,
                        "segments": [
                            *rows_location["segments"],
                            {"type": "Index", "value": i},
                        ],
                    },
                    i,
                    row,
                    i,
                )
                for i, row in enumerate(native["rows"])
            )
            result = replace(
                result,
                _selected=entries,
                _selection=replace(result._selection, _entries=entries),
                _native_override=native,
                _record_panel="coverage",
                _status="ok" if entries else "empty",
                _reason="Original source/area states, not a global completeness score. Counts do not establish per-request assertion membership.",
            )
            explorer._coverage_result = _CoverageCapture(card, native, result)
    return replace(explorer._coverage_result.view, _origin=origin)


def explain(explorer, row, origin):
    from .knowledge_state_explanation import explain_knowledge_state

    captured = explorer._coverage_result
    key = (row["area"], row["source"])
    if key not in captured.explanations:
        native = explain_knowledge_state(captured.card, *key)
        captured.explanations[key] = explorer._metadata(
            native, "Why this coverage state?"
        )
    return replace(captured.explanations[key], _origin=origin, _request=origin._request)
