"""Versioned saved-science bindings and inert restoration for exploration v2."""

from copy import deepcopy
from types import SimpleNamespace

from .card_access import _Entry, _handle
from .card_exploration_history import _HistoricalInput, _require_matches
from .errors import ArgumentError, StorageError

FORMAT = "sabueso.card_exploration@2"
VERIFIER = "scientific_exploration_binding@1"
ADAPTERS = ("structure_exploration@1", "knowledge_coverage_exploration@1")
RULES = (
    "knowledge_state@5",
    "knowledge_state_explanation@2",
    "structure_inventory_explanation@1",
)


def _require(condition, message):
    if not condition:
        raise StorageError(message)


def _scientific_metadata(value):
    if not isinstance(value, dict):
        return False
    rule = value.get("rule")
    rule = rule.get("rule") if isinstance(rule, dict) else rule
    return (
        value.get("adapter") == ADAPTERS[1]
        or rule in RULES
        or value.get("question") == "region_coverage"
    )


def _encoding(view):
    if view._selection._scientific is not None:
        return "structure_row" if view._focus is not None else "structure_inventory"
    if view._saved_state is not None:
        return view._saved_state.get("_native_encoding", "json")
    native = view._native_override
    if (
        isinstance(native, dict)
        and isinstance(native.get("rule"), dict)
        and native["rule"].get("rule") == RULES[2]
    ):
        return "structure_explanation"
    return "json"


def _encode(value, encoding):
    from .card_exploration_adapter_v1 import (
        _wire_explanation,
        _wire_inventory,
        _wire_row,
    )

    return (
        _wire_inventory(value)
        if encoding == "structure_inventory"
        else _wire_row(value)
        if encoding == "structure_row"
        else _wire_explanation(value)
        if encoding == "structure_explanation"
        else deepcopy(value)
    )


def _decode(value, encoding):
    value = deepcopy(value)
    if encoding == "json":
        return value
    _require(
        encoding in ("structure_inventory", "structure_row", "structure_explanation"),
        "Unsupported saved native encoding.",
    )
    from pyunitwizard import QuantityRecord

    rows = (
        value.get("items", [])
        if encoding == "structure_inventory"
        else [value]
        if encoding == "structure_row"
        else [value.get("item")]
    )
    for row in rows:
        if row and row.get("resolution") is not None:
            row["resolution"] = QuantityRecord.from_dict(row["resolution"]).to_quantity(
                field="relationships.has_structure.resolution", unit="angstrom"
            )
    return value


def _restore_result(ref, wire):
    from .card_exploration_adapter_v1 import _HistoricalResult

    native = _decode(wire["native_payload"], "structure_inventory")
    result = _HistoricalResult(
        ref,
        native,
        {
            key: _decode(value, "structure_explanation")
            for key, value in wire["explanations"].items()
        },
        wire,
        deepcopy(wire["context"]["options"]),
        (),
        {row["relationship_id"]: row for row in native.get("items", [])},
    )
    entries = tuple(
        _Entry(result.location("items", key), key, row)
        for key, row in sorted(
            wire["items"].items(), key=lambda pair: pair[1]["structure_ref"]
        )
    )
    return _HistoricalResult(
        ref,
        native,
        result.explanations,
        wire,
        result.options,
        entries,
        result._native_rows,
    )


def _result_ref(access, wire):
    from .card_exploration_adapter_v1 import ADAPTER, EXPLANATION_RULE, _rule_identity

    native = deepcopy(wire["native_payload"])
    if "rule" in native:
        native["rule"] = _rule_identity(native["rule"])
    coverage = deepcopy(wire["coverage"])
    if "rule" in coverage:
        coverage["rule"] = _rule_identity(coverage["rule"])
    return _handle(
        "XR_",
        {
            "format": "scientific_exploration_result@1",
            "adapter": ADAPTER,
            "inputs": sorted(access._captures),
            "focal": access._focal_key,
            "options": wire["context"]["options"],
            "native": native,
            "coverage": coverage,
            "rules": [_rule_identity(rule) for rule in wire["context"]["rules"]],
            "explanation_rule": EXPLANATION_RULE,
            "outcome": wire["outcome"],
        },
    )


class _OriginalContext:
    def __init__(self, access):
        self._access = access

    def __getattr__(self, name):
        return getattr(self._access, name)

    @property
    def context(self):
        return {**self._access.context, "mode": "live"}


def _verify_objects(bundle, accesses):
    """Check original decisions with frozen v1 predicates, never current readers."""
    from .card_exploration_adapter_v1 import _v1_expected_structures
    from .card_exploration_coverage_v1 import (
        _v1_explain_knowledge_state,
        _v1_knowledge_state,
    )

    for ref, record in bundle.get("scientific_results", {}).items():
        access = accesses[record["focal"]]
        wire = bundle["objects"][ref]
        _require(
            record == {"focal": record["focal"]},
            "Unknown scientific result manifest member.",
        )
        _require(
            ref == _result_ref(access, wire),
            "Saved scientific result identity differs.",
        )
        options = _options(wire["context"]["options"])
        expected = _v1_expected_structures(_OriginalContext(access), options)
        _require_matches(
            wire,
            expected.wire,
            "structural rules, values, exclusions and original support",
        )
    for value in bundle["objects"].values():
        if not _scientific_metadata(value):
            continue
        if value.get("question") == "region_coverage":
            continue  # Its view supplies the exact focal capture for scope checking.
        pin = value.get("card_ref") or value.get("context", {}).get("card_ref")
        matching = [access for access in accesses.values() if access._focal.pin == pin]
        _require(
            bool(matching), "Saved scientific metadata has no original focal capture."
        )
        access = matching[0]
        card = _HistoricalInput(access._focal)
        rule = value.get("rule")
        rule = rule.get("rule") if isinstance(rule, dict) else rule
        if value.get("adapter") == ADAPTERS[1]:
            _require_matches(
                value["native_payload"],
                _v1_knowledge_state(card),
                "knowledge-state decisions",
            )
        elif rule == RULES[1]:
            params = value["rule"]["parameters"]
            _require_matches(
                value,
                _v1_explain_knowledge_state(
                    card, params["knowledge_area"], params["knowledge_source"]
                ),
                "scoped knowledge-state explanation",
            )
        elif rule == RULES[2]:
            from .card_exploration_structure_v1 import (
                _v1_explain_structure_inventory,
                _v1_structure_inventory,
            )

            params = value["rule"]["parameters"]
            inventory = _v1_structure_inventory(
                [card],
                regions=params["regions"],
                include_fragments=params["include_fragments"],
            )
            expected = _v1_explain_structure_inventory(
                [card],
                card.id,
                value["structure_ref"],
                inventory,
                regions=params["regions"],
                include_fragments=params["include_fragments"],
            )
            _require_matches(
                value,
                _encode(expected, "structure_explanation"),
                "structural explanation",
            )
        elif rule == RULES[0]:
            _require_matches(
                value, _v1_knowledge_state(card), "knowledge-state decisions"
            )


def _options(options):
    """The original effective options, independent of future reader defaults."""
    if options is None:
        options = {}
    if (
        not isinstance(options, dict)
        or set(options) - {"region", "include_fragments"}
        or type(options.get("include_fragments", False)) is not bool
    ):
        raise ArgumentError(
            "Saved structures options require region and boolean include_fragments."
        )
    region = options.get("region")
    positions = set()
    if region is not None:
        if not isinstance(region, (list, tuple, set)) or not region:
            raise ArgumentError(
                "Saved region requires positive positions or inclusive ranges."
            )
        for item in region:
            if isinstance(item, int) and not isinstance(item, bool) and item > 0:
                positions.add(item)
            elif (
                isinstance(item, (list, tuple))
                and len(item) == 2
                and all(isinstance(i, int) and not isinstance(i, bool) for i in item)
                and 0 < item[0] <= item[1]
            ):
                positions.update(range(item[0], item[1] + 1))
            else:
                raise ArgumentError(
                    "Saved region requires positive positions or inclusive ranges."
                )
    return {
        "region": sorted(positions) if region is not None else None,
        "include_fragments": options.get("include_fragments", False),
    }


def _saved_selection(access, topic, fields, options):
    from .card_exploration_adapter_v1 import COLUMNS, DEFAULT_FIELDS

    options = _options(options)
    fields = (
        DEFAULT_FIELDS
        if fields is None
        else (fields,)
        if isinstance(fields, str)
        else fields
    )
    if (
        not isinstance(fields, (list, tuple))
        or any(
            not isinstance(key, str) or key not in ("label", "kind", *COLUMNS)
            for key in fields
        )
        or len(set(fields)) != len(fields)
    ):
        raise ArgumentError("Unknown saved structural projection.")
    for selection in access._selections.values():
        if (
            selection._scientific is not None
            and selection._scientific.options == options
            and selection._fields == tuple(fields)
        ):
            return selection
    from .card_exploration_storage import missing_selection

    return missing_selection(access, topic, options, tuple(fields))


def _bind_coverage(view, native):
    if view._record_panel == "coverage":
        view._explorer._coverage_result = SimpleNamespace(
            native=native if "rows" in native else {}
        )


def _verify_selection(view):
    from .card_exploration_verification import equal

    selection, access = view._selection, view._explorer.access
    result = selection._scientific
    context = access._resolve(selection._context_location)[0]
    expected = {
        "topic": "structures",
        "fields": list(selection._fields),
        "options": result.options,
    }
    _require(
        equal(context, {"context": result.wire["context"], "request": expected}),
        "Saved scientific request context differs.",
    )
    _require(
        selection.selection_ref
        == _handle(
            "XA_",
            {
                "format": "scientific_access_selection@1",
                "result_ref": result.result_ref,
                "fields": selection._fields,
            },
        ),
        "Saved scientific selection identity differs.",
    )
    _require(
        selection._operation == "select:structures"
        and selection._slice is None
        and selection._outcome_override is None,
        "Saved scientific selection operation differs.",
    )
    _require(
        equal(
            selection._target,
            {
                "node_type": "scientific_result",
                "location": selection._target["location"],
                "size": len(result.entries),
            },
        ),
        "Saved scientific target differs.",
    )
    _require(
        equal(
            access._resolve(selection._target["location"])[1],
            result.location("native_payload"),
        ),
        "Saved scientific target location differs.",
    )
    _require(
        equal(
            [entry.__dict__ for entry in selection._entries],
            [entry.__dict__ for entry in result.entries],
        ),
        "Saved scientific membership differs.",
    )
    _require(
        selection.result_ref == result.result_ref, "Foreign scientific result binding."
    )
    _saved_selection(access, "structures", selection._fields, result.options)
    if view._focus is not None:
        _require(
            view._focus in result.wire["items"]
            and [entry.key for entry in view._selected] == [view._focus],
            "Saved structural detail focus differs.",
        )
    return result.wire["native_payload"]


def _verification_report(bundle):
    rules = set()

    def declared(value):
        if isinstance(value, dict) and isinstance(value.get("rule"), str):
            rules.add(value["rule"])

    for ref in bundle["scientific_results"]:
        wire = bundle["objects"][ref]
        for rule in wire["context"]["rules"]:
            declared(rule)
        declared(wire["coverage"].get("rule"))
        for explanation in wire["explanations"].values():
            declared(explanation["rule"])
    for value in bundle["objects"].values():
        if _scientific_metadata(value):
            declared(value.get("rule"))
            declared(value.get("state_rule"))
            declared(value.get("native_payload", {}).get("rule"))
            for rule in value.get("rules", []):
                declared(rule)
    return {
        "verifier": VERIFIER,
        "bindings": "original captured snapshots, retained literal/scientific values, units, support, requests and display membership",
        "scientific_classifications": "historical_consistency_verified"
        if rules
        else "not_evaluated",
        "verified_scientific_rules": sorted(rules),
        "explanations": "retained original explanations checked at their original scope",
        "historical_catalog": "frozen initial exploration v1 source/area declarations",
    }
