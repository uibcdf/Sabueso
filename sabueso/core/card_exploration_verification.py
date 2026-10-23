"""Versioned checks of retained literal bindings and recorded navigation decisions.

These checks never execute a scientific view or the live identity navigator. They
verify self-consistency against supplied captures, not source authenticity/truth.
"""

from copy import deepcopy
from dataclasses import replace

from .card_access import _handle
from .errors import StorageError
from .snapshot import canonical_json, digest, parse_ref


def require(condition, message):
    if not condition:
        raise StorageError(message)


def equal(a, b):
    return canonical_json(a) == canonical_json(b)


def verify_bundle(bundle, expected_digest):
    from .card_exploration_science import ADAPTERS
    from .card_exploration_science import FORMAT as SCIENCE_FORMAT
    from .card_exploration_science import VERIFIER as SCIENCE_VERIFIER
    from .card_exploration_storage import FORMAT, VERIFIER

    require(
        isinstance(bundle, dict) and bundle.get("format") in (FORMAT, SCIENCE_FORMAT),
        "Unsupported exploration format.",
    )
    names = {
        "format",
        "producer",
        "root_view_ref",
        "root_navigation_ref",
        "cards",
        "inputs",
        "objects",
        "locations",
        "views",
        "navigation",
        "capabilities",
        "presentation_metadata",
        "digests",
        "bundle_digest",
    }
    scientific = bundle["format"] == SCIENCE_FORMAT
    if scientific:
        names.add("scientific_results")
    require(set(bundle) == names, "Missing or unsupported required bundle member.")
    require(
        bundle["producer"]["verifier"]
        == (SCIENCE_VERIFIER if scientific else VERIFIER),
        "The required historical verifier is unavailable.",
    )
    actual = digest(
        canonical_json(
            {key: value for key, value in bundle.items() if key != "bundle_digest"}
        )
    )
    require(
        actual == bundle["bundle_digest"]
        and (expected_digest is None or actual == expected_digest),
        "Exploration digest differs from its retained/expected binding.",
    )
    members = {
        key: digest(canonical_json(value))
        for key, value in bundle.items()
        if key not in ("digests", "bundle_digest")
    }
    require(members == bundle["digests"], "Exploration member digest differs.")
    require(
        bundle["capabilities"]["scientific_saved_adapters"] == list(ADAPTERS)
        if scientific
        else not bundle["capabilities"]["scientific_saved_adapters"],
        "Unsupported saved scientific adapter.",
    )
    for key, value in bundle["objects"].items():
        if scientific and key in bundle["scientific_results"]:
            continue
        require(
            key == _handle("XR_", {"adapter": "literal_metadata@1", "value": value}),
            "Retained metadata identity differs.",
        )


def _historical_resolution(access, target):
    """Check the recorded retained_context_links@1 decision from original inputs."""
    if target.startswith("sabueso:"):
        try:
            ref = parse_ref(target)
        except StorageError:
            return {
                "candidates": [],
                "paths": [],
                "blocked_paths": [],
                "availability": "missing_prerequisite",
            }
        candidates, matched = [], False
        for key, capture in sorted(access._captures.items()):
            if capture.data["meta"].get("card_id") != ref.card_id or (
                ref.snapshot_id and capture.snapshot != ref.snapshot_id
            ):
                continue
            matched = True
            segments = []
            if ref.item_id:
                store = (
                    "source_assertion_store"
                    if ref.item_id.startswith("SA_")
                    else "relationship_store"
                )
                if not any(row["id"] == ref.item_id for row in capture.data[store]):
                    continue
                segments = [
                    {"type": "Key", "value": store},
                    {"type": "Record", "value": ref.item_id},
                ]
            candidates.append(
                {
                    "capture": key,
                    "location": {
                        "format": "card_access_location@1",
                        "kind": "card",
                        "card_ref": capture.pin,
                        "snapshot_id": capture.snapshot,
                        "segments": segments,
                    },
                    "basis": "exact_pinned_record"
                    if ref.item_id
                    else "exact_card_reference",
                }
            )
        return {
            "candidates": candidates,
            "paths": [],
            "blocked_paths": [],
            "availability": "ambiguous"
            if len(candidates) > 1
            else "available"
            if candidates
            else "missing_prerequisite"
            if matched
            else "context_not_supplied",
        }
    edges, blocked = [], []
    for key, capture in sorted(access._captures.items()):
        assertions = {row["id"] for row in capture.data["source_assertion_store"]}
        root = {
            "format": "card_access_location@1",
            "kind": "card",
            "card_ref": capture.pin,
            "snapshot_id": capture.snapshot,
        }
        for row in sorted(
            capture.data["relationship_store"], key=lambda row: row["id"]
        ):
            if row["predicate"] != "same_as":
                continue
            ids = row.get("source_assertion_ids", [])
            ids = (
                ids
                if isinstance(ids, list) and all(isinstance(ref, str) for ref in ids)
                else []
            )
            present = [ref for ref in ids if ref in assertions]
            edge = {
                "subject_ref": row["subject_ref"],
                "object_ref": row["object_ref"],
                "location": {
                    **root,
                    "segments": [
                        {"type": "Key", "value": "relationship_store"},
                        {"type": "Record", "value": row["id"]},
                    ],
                },
                "source_assertions": [
                    {
                        **root,
                        "segments": [
                            {"type": "Key", "value": "source_assertion_store"},
                            {"type": "Record", "value": ref},
                        ],
                    }
                    for ref in present
                ],
                "missing_source_assertion_ids": [
                    ref for ref in ids if ref not in assertions
                ],
                "basis": "source_stated_same_as",
            }
            (
                edges if present and not row.get("qualifier_conflicts") else blocked
            ).append(edge)
    reached = {target}
    while True:
        expanded = reached | {
            edge[other]
            for edge in edges
            for one, other in (
                ("subject_ref", "object_ref"),
                ("object_ref", "subject_ref"),
            )
            if edge[one] in reached
        }
        if expanded == reached:
            break
        reached = expanded
    candidates = []
    for key, capture in sorted(access._captures.items()):
        identity = capture.data["meta"].get("card_id")
        identity = identity.split(":", 2)[2] if identity else None
        if identity in reached:
            candidates.append(
                {
                    "capture": key,
                    "location": {
                        "format": "card_access_location@1",
                        "kind": "card",
                        "card_ref": capture.pin,
                        "snapshot_id": capture.snapshot,
                        "segments": [],
                    },
                    "basis": "exact_entity_reference"
                    if identity == target
                    else "source_stated_identity_path",
                }
            )
    blocked = [
        edge
        for edge in blocked
        if edge["subject_ref"] in reached or edge["object_ref"] in reached
    ]
    return {
        "candidates": candidates,
        "paths": [edge for edge in edges if edge["subject_ref"] in reached],
        "blocked_paths": blocked,
        "availability": "ambiguous"
        if len(candidates) > 1
        else "available"
        if candidates
        else "missing_prerequisite"
        if blocked
        else "context_not_supplied",
    }


def _verify_links(view):
    payload, access = view.native_payload, view._explorer.access
    require(
        payload.get("rule") == "retained_context_links@1",
        "Unsupported navigation rule.",
    )
    source = payload["source_location"]
    if source is None:
        if not payload["links"]:
            require(
                view._origin is not None
                and view._origin.native_payload.get("rule")
                == "retained_context_links@1",
                "Missing retained link-detail origin.",
            )
            return
        # Candidate rows explicitly select exactly one of a recorded parent's pins.
        require(
            view._origin is not None and view._origin._link_panel,
            "Missing candidate origin.",
        )
        parents = view._origin.native_payload["links"]
        for link in payload["links"]:
            require(
                link["role"] == "candidate" and len(link["candidates"]) == 1,
                "Invalid candidate choice.",
            )
            candidate = link["candidates"][0]
            require(
                any(
                    candidate in parent["candidates"]
                    and link["paths"] == parent["paths"]
                    and link["blocked_paths"] == parent["blocked_paths"]
                    for parent in parents
                ),
                "Candidate is not bound to its original ambiguity.",
            )
            capture = access._captures[candidate["capture"]]
            require(
                link["target_ref"] == (capture.pin or capture.snapshot),
                "Candidate target pin differs.",
            )
        return
    _, source = access._resolve(source)
    support = view._explorer._support(source)
    relationship, statement = None, None
    segments = source["segments"]
    if (
        source["kind"] == "result"
        and len(segments) == 2
        and segments[0]["value"] == "items"
    ):
        wire = access._objects[source["result_ref"]]
        if wire.get("context", {}).get("adapter") == "structure_exploration@1":
            key = segments[1]["value"]
            support = [wire["support"][key]]
            relationship = next(
                (
                    row
                    for row in access._focal.data["relationship_store"]
                    if row["id"] == key
                ),
                None,
            )
    if (
        source["kind"] == "card"
        and len(segments) >= 2
        and segments[0]["value"] in ("relationship_store", "source_assertion_store")
    ):
        owner, _ = access._resolve({**source, "segments": segments[:2]})
        if segments[0]["value"] == "relationship_store":
            relationship = owner
        else:
            statement = owner
    expected_targets = []
    seen = set()
    for basis in support:
        for original in basis.get("statements", basis.get("source_assertions", [])):
            if original["id"] not in seen:
                expected_targets.append(("source", original["id"]))
                seen.add(original["id"])
    if (
        source["kind"] == "card"
        and len(segments) == 2
        and segments[0]["value"] == "entities"
    ):
        expected_targets.append(("entity", segments[1]["value"]))
    if relationship is not None:
        expected_targets.extend(
            (role, relationship[f"{role}_ref"]) for role in ("subject", "object")
        )
    if statement is not None and isinstance(statement.get("subject_ref"), str):
        expected_targets.append(("subject", statement["subject_ref"]))
    require(
        [(link["role"], link["target_ref"]) for link in payload["links"]]
        == expected_targets,
        "Retained link membership differs from original references.",
    )
    for link in payload["links"]:
        require(link["rule"] == "retained_context_links@1", "Link rule differs.")
        role, target = link["role"], link["target_ref"]
        if role == "source":
            original = [
                record
                for basis in support
                for record in basis.get(
                    "statements", basis.get("source_assertions", [])
                )
                if record["id"] == target
            ]
            require(len(original) == 1, "Source link is not original support.")
            basis = original[0]
            require(link["support"] == support, "Source link support differs.")
            if basis["state"] == "present":
                expected = {
                    "candidates": [
                        {
                            "location": basis["location"],
                            "capture": access._focal_key,
                            "basis": "exact_retained_node",
                        }
                    ],
                    "paths": [],
                    "blocked_paths": [],
                    "availability": "available",
                }
            else:
                expected = {
                    "candidates": [],
                    "paths": [],
                    "blocked_paths": [],
                    "availability": "missing_prerequisite",
                }
        else:
            if role in ("subject", "object"):
                require(
                    relationship is not None
                    or (role == "subject" and statement is not None),
                    "Endpoint has no original record.",
                )
                record = relationship or statement
                require(
                    record[f"{role}_ref"] == target,
                    "Endpoint target differs from its original record.",
                )
            elif role == "entity":
                require(
                    source["kind"] == "card"
                    and len(segments) == 2
                    and segments[0]["value"] == "entities"
                    and segments[1]["value"] == target,
                    "Glossary target differs.",
                )
            else:
                raise StorageError("Unsupported saved link role.")
            require(link["support"] == support, "Endpoint source basis differs.")
            expected = _historical_resolution(access, target)
        require(
            all(equal(link[key], value) for key, value in expected.items()),
            "Recorded destination/identity decision differs from its captured basis.",
        )


def _verify_request(view, access):
    from .card_exploration_science import _encode, _encoding, _verify_selection

    if view._selection._scientific is not None:
        return _verify_selection(view)
    native, full = access._resolve(view._selection._target["location"])
    require(
        equal(
            native.get("native_payload", native)
            if view._record_panel == "coverage"
            else native,
            _encode(view.native_payload, _encoding(view)),
        ),
        "Saved native payload differs from its original bound node.",
    )
    if full["kind"] == "card":
        require(
            full["card_ref"] == access._focal.pin
            and full["snapshot_id"] == access._focal.snapshot,
            "Saved target belongs to a different focal capture.",
        )
    context = access._resolve(view._selection._context_location)[0]
    require(
        context["context"]["card_ref"] == access._focal.pin
        and context["context"]["snapshot_id"] == access._focal.snapshot,
        "Saved request context differs from its focal capture.",
    )
    request = context["request"]
    require(
        request["operation"] == view._selection._operation
        and request["text_slice"] == view._selection._slice
        and not view._selection._fields,
        "Saved literal request differs.",
    )
    base_ref = _handle(
        "XR_",
        {
            "format": "literal_access_result@1",
            "inputs": sorted(access._captures),
            "request": request,
        },
    )
    require(
        view._selection.selection_ref
        == _handle(
            "XA_",
            {
                "format": "card_access_selection@1",
                "result_ref": base_ref,
                "request": request,
            },
        ),
        "Saved selection identity differs from its exact request.",
    )
    if view.result_ref != base_ref:
        query = access._resolve(request["location"])[0]["query"]
        require(
            view.result_ref
            == _handle(
                "XR_",
                {
                    "format": "literal_human_search@1",
                    "inputs": sorted(access._captures),
                    "focal": access._focal.snapshot,
                    "text": query,
                },
            ),
            "Saved result identity differs from its captured request.",
        )
    from .card_access import _text_slice, _type

    target = view._selection._target
    if view.result_ref == base_ref:
        expected_target = {
            "node_type": _type(native),
            "size": len(native) if isinstance(native, (dict, list, str)) else None,
            "location": target["location"],
            "owner": {
                key: full[key]
                for key in ("card_ref", "snapshot_id", "result_ref")
                if key in full
            },
        }
        require(
            equal(target, expected_target),
            "Saved machine node owner/type binding differs.",
        )
    else:
        require(set(target) == {"location"}, "Saved literal search target differs.")
    require(
        view._selection._operation
        in ("read", "fields", "catalog:topics", "catalog:selections"),
        "Unsupported saved literal operation.",
    )
    text_slice = _text_slice(view._selection._slice)
    if text_slice is not None:
        require(
            isinstance(native, str) and text_slice["stop"] <= len(native),
            "Saved text slice bounds differ.",
        )
    if (
        view.result_ref == base_ref
        and not view._field_panel
        and not view._record_panel
        and not view._link_panel
    ):
        expected_entries = access._children(native, full)
        if view._selection._slice is not None:
            from .card_access import _Entry

            expected_entries = (_Entry(full, None, native),)
        # Explanations may directly expose their original assertion records.
        source_rows = bool(view._selection._entries) and all(
            entry.location["kind"] == "card"
            and entry.location["segments"]
            and entry.location["segments"][0]["value"] == "source_assertion_store"
            for entry in view._selection._entries
        )
        from .card_exploration_labels import structural_explanation

        structural = structural_explanation(view)
        if structural is not None and (source_rows or not view._selection._entries):
            expected_sources = []
            seen = set()
            for row in structural["support"]["source_assertions"]:
                if row["state"] == "present" and row["id"] not in seen:
                    expected_sources.append(row["location"])
                    seen.add(row["id"])
            require(
                equal(
                    [entry.location for entry in view._selection._entries],
                    expected_sources,
                ),
                "Structural explanation assertion membership differs.",
            )
            return native
        direct_explanation = (
            isinstance(native, dict)
            and native.get("basis") == "stored_literal"
            and (
                source_rows
                or (
                    not view._selection._entries
                    and view._origin is not None
                    and (
                        view._origin._field_panel
                        or view._origin._record_panel == "classification"
                    )
                )
            )
        )
        if direct_explanation:
            ids = []
            for proof in native.get("support", []):
                ids.extend(
                    row["id"]
                    for row in proof.get("statements", [])
                    if row["state"] == "present"
                )
            ids.extend(
                row["id"]
                for name in (
                    "alternative_source_assertions",
                    "unclassified_field_source_assertions",
                )
                for row in native.get(name, [])
                if row["state"] == "present"
            )
            ids = list(dict.fromkeys(ids))
            require(
                [entry.key for entry in view._selection._entries] == ids,
                "Explanation assertion membership differs.",
            )
        elif (
            isinstance(native, dict)
            and native.get("question") == "region_coverage"
            and full["kind"] == "result"
            and not view._selection._entries
        ):
            require(
                view._status == native["outcome"]["status"],
                "Recorded region failure differs.",
            )
        elif view._status == "not_saved":
            require(
                not view._selection._entries
                and isinstance(native, dict)
                and native.get("outcome") == "not_saved",
                "Invalid not-saved selection.",
            )
        else:
            require(
                equal(
                    [entry.location for entry in view._selection._entries],
                    [entry.location for entry in expected_entries],
                ),
                "Literal child membership differs from the captured node.",
            )
    elif view.result_ref != base_ref:
        expected = []
        from .card_access import _Entry

        stack = [_Entry(access._card_location(), None, access._focal.data)]
        while stack:
            entry = stack.pop()
            if (
                entry.key is not None and query.casefold() in str(entry.key).casefold()
            ) or (
                not isinstance(entry.value, (list, dict))
                and query.casefold() in str(entry.value).casefold()
            ):
                expected.append(entry.location)
            if isinstance(entry.value, (list, dict)):
                stack.extend(reversed(access._children(entry.value, entry.location)))
        require(
            equal([entry.location for entry in view._selection._entries], expected),
            "Saved literal search membership differs.",
        )
    return native


def _verify_state(view, record, native, access):
    from .card_exploration import CardItem
    from .card_exploration_storage import _cell_record

    state = record["state"]
    if view._context_only:
        anchor = view
        while anchor._origin is not None and anchor._origin._context_only:
            anchor = anchor._origin
        anchor_payload = anchor.native_payload
        require(
            anchor._origin is not None and anchor._origin._link_panel,
            "Missing retained destination origin.",
        )
        require(
            anchor_payload["link"] in anchor._origin.native_payload["links"],
            "Context-only link differs from its originating result.",
        )
        require(
            state["context"]["card_ref"] is None
            and state["context"]["snapshot_id"] is None
            and state["context"]["subject_ref"]
            == anchor_payload["subject_ref"]
            == anchor_payload["link"]["target_ref"],
            "Context-only destination acquired a false focal identity.",
        )
        require(
            equal(
                anchor_payload["entity"],
                access._focal.data.get("entities", {}).get(
                    anchor_payload["subject_ref"]
                ),
            ),
            "Retained glossary context differs.",
        )
    else:
        require(
            state["context"]["card_ref"] == access._focal.pin
            and state["context"]["snapshot_id"] == access._focal.snapshot,
            "View focal capture differs.",
        )
    expected_adapter = (
        "retained_context_links@1"
        if view._context_only or view._link_panel
        else "structure_exploration@1"
        if view._selection._scientific is not None
        else "knowledge_coverage_exploration@1"
        if view._record_panel == "coverage"
        else "disease_classification_fields@1"
        if view._record_panel == "classification"
        else "protein_function_fields@1"
        if view._field_panel == "function"
        else f"{view._field_panel}_fields@1"
        if view._field_panel
        else "literal_human@1"
    )
    require(
        state["context"]["adapter"] == expected_adapter,
        "The required saved adapter version is unavailable or misbound.",
    )
    if view._context_only:
        require(
            state["context"]["profile"] is None,
            "Context-only destination acquired an invented profile.",
        )
    plain = replace(view, _saved_state=None)
    for key, value in plain.context.items():
        if key != "mode":
            require(
                key in state["context"] and equal(state["context"][key], value),
                "Saved adapter/input context differs from its capture binding.",
            )
    require(
        equal(state["context"]["captures"], sorted(access._captures)),
        "Saved contributing capture registry differs.",
    )
    if view._field_panel or (
        view._record_panel and view._selection._scientific is None
    ):
        require(
            native["context"]["card_ref"] == access._focal.pin
            and native["context"]["snapshot_id"] == access._focal.snapshot,
            "Native field/relationship context differs.",
        )
    require(
        equal(state["schema"], plain.schema),
        "Saved column/quantity schema differs from its adapter.",
    )
    require(
        equal(state["coverage"], plain.coverage),
        "Saved coverage claims differ from their literal scope.",
    )
    require(
        set(state["items"])
        == {CardItem(view, entry).item_ref for entry in view._selection._entries},
        "Saved item closure differs.",
    )
    for entry in view._selection._entries:
        original, owned = access._resolve(entry.location)
        if owned["kind"] == "card":
            require(
                owned["card_ref"] == access._focal.pin
                and owned["snapshot_id"] == access._focal.snapshot,
                "Saved entry belongs to a different focal capture.",
            )
        require(
            equal(entry.value, original),
            "Saved entry value differs from its original captured location.",
        )
        segments = owned["segments"]
        if view._selection._scientific is not None:
            expected_key, expected_ordinal = segments[-1]["value"], None
        elif owned == access._resolve(view._selection._target["location"])[
            1
        ] and not isinstance(original, (dict, list)):
            expected_key, expected_ordinal = None, None
        elif (
            view._field_panel
            and owned["kind"] == "card"
            and segments[0]["value"] == "sections"
        ):
            expected_key, expected_ordinal = (
                ".".join(
                    segment["value"]
                    for segment in segments[1:]
                    if segment["type"] == "Key"
                ),
                None,
            )
        elif view._field_panel == "ligand_instances":
            require(
                owned["kind"] == "card"
                and len(segments) == 7
                and [segment["type"] for segment in segments]
                == ["Key", "Record", "Key", "Key", "Index", "Key", "Index"]
                and [segments[index]["value"] for index in (0, 2, 3, 5)]
                == ["relationship_store", "qualifiers", "ligands", "instances"],
                "Saved ligand instance is not bound to an original typed instance location.",
            )
            expected_key = (
                f"{segments[1]['value']}:{segments[4]['value']}:{segments[6]['value']}"
            )
            expected_ordinal = segments[6]["value"]
        elif view._link_panel:
            expected_key, expected_ordinal = str(segments[-1]["value"]), None
        elif segments and segments[-1]["type"] == "Record":
            expected_key = segments[-1]["value"]
            from .card_exploration_labels import structural_explanation

            direct_explanation = (
                isinstance(native, dict)
                and (
                    native.get("basis") == "stored_literal"
                    or structural_explanation(view) is not None
                )
                and segments[0]["value"] == "source_assertion_store"
            )
            if direct_explanation:
                expected_ordinal = None
            else:
                store = access._resolve({**owned, "segments": segments[:-1]})[0]
                expected_ordinal = next(
                    index
                    for index, row in enumerate(store)
                    if row["id"] == expected_key
                )
        elif segments:
            expected_key = segments[-1]["value"]
            expected_ordinal = expected_key if segments[-1]["type"] == "Index" else None
        else:
            expected_key, expected_ordinal = None, None
        require(
            equal(entry.key, expected_key) and equal(entry.ordinal, expected_ordinal),
            "Saved literal key/original ordinal differs from its typed location.",
        )
        item = CardItem(plain, entry)
        frozen = state["items"][item.item_ref]
        require(
            isinstance(frozen["label"], str)
            and set(frozen) == {"label", "kind", "support", "cells"},
            "Unsupported saved item presentation shape.",
        )
        require(
            frozen["kind"] == item.kind and equal(frozen["support"], item.support),
            "Saved item kind/support differs from its original binding.",
        )
        cells = item.cells
        require(set(cells) == set(frozen["cells"]), "Saved cell membership differs.")
        for column, cell in cells.items():
            expected = _cell_record(item, column, cell)
            actual = deepcopy(frozen["cells"][column])
            if column == "label":
                expected["value"] = frozen["label"]
            # Wording is recorded presentation metadata; value, type, state,
            # units and support are independently checked against the capture.
            expected.pop("reason", None)
            actual.pop("reason", None)
            _verify_cell(actual, expected)


def _verify_cell(actual, expected):
    if (
        expected["encoding"] == "quantity_record"
        and actual.get("encoding") == "quantity_record"
    ):
        import pyunitwizard as puw
        from pyunitwizard import QuantityRecord

        original = QuantityRecord.from_dict(expected["value"])
        retained = QuantityRecord.from_dict(actual["value"])
        require(retained.kind == original.kind, "Saved quantity kind differs.")
        value = retained.to_quantity(field=expected["field"], unit=expected["unit"])
        expected_value = original.to_quantity(
            field=expected["field"], unit=expected["unit"]
        )
        first = puw.get_value(value, to_unit=expected["unit"])
        second = puw.get_value(expected_value, to_unit=expected["unit"])
        first = first.tolist() if hasattr(first, "tolist") else first
        second = second.tolist() if hasattr(second, "tolist") else second
        require(
            equal(first, second), "Saved quantity differs from its source value/unit."
        )
        actual["value"] = expected["value"]
    require(
        equal(actual, expected),
        "Saved cell differs from its original value/unit/support binding.",
    )


def _verify_display(view, record):
    state = record["state"]
    require(
        len(record["selected"]) == len(set(record["selected"])),
        "Duplicate selected items.",
    )
    operation = view._display_request
    if view._focus is not None:
        require(
            view._origin is not None
            and view._origin.result_ref == view.result_ref
            and record["selected"]
            == [
                item.item_ref
                for item in view._origin.items()
                if item._entry.key == view._focus
            ],
            "Structural detail lost its original selection.",
        )
    elif operation:
        require(
            view._origin is not None and view._origin.result_ref == view.result_ref,
            "Display selection lost its original result.",
        )
        previous = view._origin
        if operation["operation"] == "filter":
            expected = previous.filter(operation["column"], equals=operation["equals"])
        elif operation["operation"] == "sort":
            expected = previous.sort(
                operation["column"],
                descending=operation["descending"],
                unit=operation["unit"],
            )
        elif operation["operation"] == "presentation":
            expected = previous
        else:
            raise StorageError("Unknown saved display operation.")
        require(
            [item.item_ref for item in expected.items()] == record["selected"],
            "Recorded filter/order membership differs.",
        )
    else:
        require(
            set(record["selected"]) == set(state["items"]),
            "Unexplained saved display exclusion.",
        )


def _verify_profile(view, native, access):
    from .card_exploration_adapter_v1 import _v1_region_request

    if (
        view._request is not None
        and view._request.get("question") == "region_coverage"
        and view._selection._scientific is not None
    ):
        effective, status, _ = _v1_region_request(
            view._explorer, view._request["options"]
        )
        require(
            status == "ok"
            and view._request
            == {
                "question": "region_coverage",
                "topic": "structures",
                "options": effective,
            }
            and view._selection._scientific.options
            == {
                key: value for key, value in effective.items() if key != "sequence_ref"
            },
            "Saved canonical region request differs from its original scope.",
        )
    if (
        isinstance(native, dict)
        and native.get("question") == "region_coverage"
        and access._resolve(view._selection._target["location"])[1]["kind"] == "result"
    ):
        effective, status, reason = _v1_region_request(
            view._explorer, native["options"]
        )
        require(
            status != "ok"
            and equal(
                native,
                {
                    "question": "region_coverage",
                    "options": effective,
                    "outcome": {"status": status, "reason": reason},
                },
            ),
            "Saved region prerequisite decision differs.",
        )
        if view.request is not None:
            require(
                view.request
                == {
                    "question": "region_coverage",
                    "topic": "structures",
                    "options": effective,
                },
                "Saved region prerequisite request differs.",
            )
    if view._record_panel == "coverage":
        rows = native.get("native_payload", {}).get("rows", [])
        require(
            equal([entry.value for entry in view._selection._entries], rows),
            "Saved source/area row membership differs.",
        )
    if view._field_panel:
        from .card_exploration_profiles import PANELS, field_entries
        from .card_ligand_instances_v1 import entries as instance_entries
        from .card_protein_source_v1 import TOPICS, entries

        expected_entries, gaps = (
            (
                instance_entries(view._explorer)
                if view._field_panel == "ligand_instances"
                else entries(view._explorer, view._field_panel)
                if view._field_panel in TOPICS
                else field_entries(view._explorer, view._field_panel)
            )
            if access.profile == PANELS[view._field_panel][0]
            else ((), [])
        )
        require(
            equal(
                [entry.location for entry in view._selection._entries],
                [entry.location for entry in expected_entries],
            )
            and equal(native["field_gaps"], gaps),
            "Saved field membership/gaps differ from retained fields.",
        )
        require(
            equal(
                native["fields"],
                {entry.key: entry.value for entry in view._selection._entries},
            ),
            "Field presentation differs from original fields.",
        )
    if view._record_panel == "classification":
        identity = access._focal.data["meta"].get("card_id", "")
        subject = (
            identity.removeprefix("sabueso:disease:")
            if identity.startswith("sabueso:disease:")
            else None
        )
        expected = (
            [
                row
                for row in access._focal.data["relationship_store"]
                if row["predicate"] == "subclass_of" and row["subject_ref"] == subject
            ]
            if access.profile == "disease" and subject
            else []
        )
        expected = sorted(expected, key=lambda row: row["id"])
        require(
            equal(native["relationships"], expected),
            "Saved hierarchy membership differs from original relationships.",
        )
    if view._link_panel:
        _verify_links(view)


def _verify_support(bundle, nodes):
    from .card_exploration import CardItem
    from .card_exploration_storage import operation_key, required_views

    root = nodes[bundle["root_navigation_ref"]]
    for view in required_views(root):
        for entry in view._selection._entries:
            binding = operation_key(CardItem(view, entry))
            require(
                all(
                    binding in bundle["navigation"][kind]
                    for kind in ("explanations", "links")
                ),
                "Required original explanation/link closure is missing.",
            )
    require(
        bundle["capabilities"]["root_machine_selection_ref"] == root._machine_ref,
        "Machine entry selection binding differs.",
    )
    if root._machine_ref is not None:
        require(
            root._machine_ref == root._selection.selection_ref,
            "Root machine selection is not the retained exact request.",
        )
    sources = {}
    for view in nodes.values():
        for entry in view._selection._entries:
            item = CardItem(view, entry)
            sources.setdefault((view._explorer.access._focal_key, item.item_ref), item)
    for operation, mappings in bundle["navigation"].items():
        for binding, key in mappings.items():
            focal, item_ref = __import__("json").loads(binding)
            source = sources.get((focal, item_ref))
            require(source is not None, "Saved support references a foreign item.")
            native = nodes[key].native_payload
            if operation == "explanations":
                if source._view._selection._scientific is not None:
                    from .card_exploration_science import _encode

                    require(
                        equal(
                            _encode(native, "structure_explanation"),
                            _encode(
                                source._view._selection._scientific.explanations[
                                    source._entry.key
                                ],
                                "structure_explanation",
                            ),
                        ),
                        "Structural explanation belongs to a different original item.",
                    )
                if source._view._record_panel == "coverage":
                    params = native["rule"]["parameters"]
                    require(
                        params
                        == {
                            "knowledge_area": source._entry.value["area"],
                            "knowledge_source": source._entry.value["source"],
                        },
                        "Coverage explanation belongs to a different original row.",
                    )
                require(
                    native.get("basis") in ("stored_literal", None),
                    "Unsupported scientific explanation.",
                )
                if "support" in native:
                    require(
                        equal(native["support"], source.support),
                        "Explanation support differs from the original item.",
                    )
                if "stored_conflicts" in native:
                    require(
                        equal(native["stored_conflicts"], source._conflicts),
                        "Explanation conflict context differs.",
                    )
                if source._view._field_panel:
                    from .card_exploration_profiles import alternatives

                    for name, value in alternatives(
                        source._view._explorer, source._entry
                    ).items():
                        require(
                            name in native and equal(native[name], value),
                            "Explanation selected/alternative source context differs.",
                        )
                if source._view._link_panel:
                    require(
                        equal(native.get("link"), source._entry.value),
                        "Original link explanation differs.",
                    )
                if "selection_rules" in native:
                    require(
                        equal(
                            native["selection_rules"],
                            source._view._explorer.access._focal.data.get(
                                "selection_rules", {}
                            ),
                        ),
                        "Explanation selection rules differ.",
                    )


def verify_views(bundle, nodes):
    from .card_exploration_storage import admitted_view

    for key, view in nodes.items():
        record, access = bundle["views"][key], view._explorer.access
        from .card_exploration_science import _encode, _encoding

        require(
            record.get("native_encoding", "json") == _encoding(view)
            and equal(
                record["native_payload"], _encode(view.native_payload, _encoding(view))
            ),
            "Saved native payload/quantity encoding differs.",
        )
        require(
            admitted_view(view),
            "A required scientific historical verifier is unavailable.",
        )
        require(
            view._field_panel
            in (
                None,
                "function",
                "chemistry",
                "properties",
                "definition",
                "identity",
                "sequence",
                "predicted_structures",
                "sites",
                "ligand_instances",
            )
            and view._record_panel in (None, "classification", "coverage"),
            "Unsupported saved profile adapter.",
        )
        native = _verify_request(view, access)
        _verify_state(view, record, native, access)
        _verify_display(view, record)
        _verify_profile(view, native, access)
    _verify_support(bundle, nodes)
