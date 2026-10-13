"""Actual comparative view executions, detached from their scientific output (#108).

Only an explicit attribution context observes these existing read-only views.
The support scope is selected input fields, not reconstructed row-level lineage.
Isoform tissue text is read from all stored assertions by the existing engine.
"""

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from . import attribution
from .relationship_store import make_derivation
from .snapshot import canonical_json, digest
from .source_assertion_store import acquisition_of, assertion_value

FORMAT = "sabueso.comparative_operation@1"


def _time():
    return datetime.now(timezone.utc).isoformat()


def _support(inputs):
    from .attribution_bibliography import descriptions, software
    from .comparative_bibliography import method_descriptions
    from .tissue_usage import TISSUE_TEXT

    scope, resources, gaps, citation_gaps = [], {}, [], []
    bibliography = {item["id"]: item for item in [software()]}
    for role, card, paths in inputs:
        pin = card.pinned_ref()
        fields = []
        for path in paths:
            node = card.get(path)
            basis = "selected_input_field"
            if path == TISSUE_TEXT:
                assertions = card.source_assertion_store.find_by_field(path)
                ids = [a["id"] for a in assertions]
                basis = "all_stored_tissue_specificity_statements"
            else:
                ids = (node or {}).get("source_assertion_ids") or []
            fields.append(
                {
                    "field_path": path,
                    "stored": node is not None,
                    "source_assertion_refs": [f"{pin}#{i}" for i in ids],
                    "support_basis": basis,
                }
            )
            if node is None and not ids:
                gaps.append(
                    {
                        "role": role,
                        "card_ref": pin,
                        "field_path": path,
                        "reason": "input_not_stated",
                    }
                )
            elif not ids:
                gaps.append(
                    {
                        "role": role,
                        "card_ref": pin,
                        "field_path": path,
                        "reason": "input_support_not_stated",
                    }
                )
            for identifier in ids:
                assertion = card.source_assertion_store.get(identifier)
                ref = f"{pin}#{identifier}"
                if assertion is None or assertion.get("field_path") != path:
                    gaps.append(
                        {
                            "source_assertion_ref": ref,
                            "reason": "missing_or_mismatched_input_assertion",
                        }
                    )
                    continue
                value = assertion_value(assertion)
                selected = (node or {}).get("value")
                if (
                    path != TISSUE_TEXT
                    and value != selected
                    and not (isinstance(selected, list) and value in selected)
                ):
                    gaps.append(
                        {
                            "source_assertion_ref": ref,
                            "reason": "assertion_does_not_support_selected_input",
                        }
                    )
                    continue
                source = assertion.get("source") or {}
                identity = {
                    k: source.get(k) for k in ("name", "type", "record_id", "version")
                }
                key = "sabueso:source-record:" + digest(canonical_json(identity))
                if key not in resources:
                    citations = descriptions(source.get("name"))
                    bibliography.update({c["id"]: c for c in citations})
                    resources[key] = {
                        "id": key,
                        "source": identity,
                        "version_basis": "stored_source_assertion_label",
                        "description_citation_ids": [c["id"] for c in citations],
                        "uses": [],
                    }
                    if not citations:
                        citation_gaps.append(
                            {
                                "resource_id": key,
                                "reason": "description_citation_not_declared",
                            }
                        )
                    if source.get("name") in {"gnomAD", "GTEx"}:
                        citation_gaps.append(
                            {
                                "resource_id": key,
                                "reason": "entry_publications_not_declared",
                            }
                        )
                usage = {
                    "role": role,
                    "card_ref": pin,
                    "field_path": path,
                    "source_assertion_ref": ref,
                    "support_basis": basis,
                    "retrieved_at": assertion.get("retrieved_at"),
                    "acquisition": acquisition_of(assertion),
                }
                methods, method_scope = method_descriptions(
                    source.get("name"), field_path=path
                )
                if methods:
                    bibliography.update({c["id"]: c for c in methods})
                    resources[key]["method_description_citation_ids"] = [
                        c["id"] for c in methods
                    ]
                    usage["method_reference_scope"] = method_scope
                    gap = {
                        "resource_id": key,
                        "reason": "native_pext_method_revision_and_row_publication_binding_not_stated",
                    }
                    if gap not in citation_gaps:
                        citation_gaps.append(gap)
                resources[key]["uses"].append(usage)
        scope.append({"role": role, "card_ref": pin, "fields": fields})
    return {
        "inputs": scope,
        "resources": list(resources.values()),
        "bibliography": list(bibliography.values()),
        "support_gaps": gaps,
        "bibliography_gaps": citation_gaps,
        "support_rule": make_derivation(
            "comparative_input_scope@1", inputs=[r["card_ref"] for r in scope]
        ),
        "lineage": "selected input fields; row-level mapping and source-request membership are not reconstructed",
    }


def _credit(record):
    backend = None
    try:
        backend = attribution._load_backend()
        operation = "sabueso.card." + record["operation"]
        context = {
            "execution_id": record["execution_id"],
            "producer": record["producer"],
            "result_id": record["result_id"],
            "inputs": record["inputs"],
            "rule": record["rule"],
            "applied_rules": record["applied_rules"],
        }
        with backend.capture(operation, context=context) as capture:
            with backend.scope(operation):
                for item in record["bibliography"]:
                    backend.register_item(**item)
                backend.track_item(
                    record["bibliography"][0]["id"],
                    roles=["executed_software"],
                    context=context,
                )
                for resource in record["resources"]:
                    source = resource["source"]
                    backend.register_item(**attribution._resource_item(resource))
                    for usage in resource["uses"]:
                        use_context = {**context, **usage, "source_record": source}
                        backend.track_item(
                            resource["id"],
                            roles=["stored_knowledge"],
                            context=use_context,
                        )
                        for identifier in resource["description_citation_ids"]:
                            backend.track_item(
                                identifier,
                                roles=["resource_description"],
                                context=use_context,
                            )
                        if usage.get("method_reference_scope"):
                            for identifier in resource.get(
                                "method_description_citation_ids", []
                            ):
                                backend.track_item(
                                    identifier,
                                    roles=["method_description"],
                                    context=use_context,
                                )
        return {
            "status": "available",
            "version": backend.__version__,
            "attribution": capture.attribution.to_dict(),
        }
    except Exception as error:
        reason = f"{type(error).__name__}: {error}"
        attribution._warning(record["operation"], reason)
        return {
            "status": "failed",
            "version": getattr(backend, "__version__", None),
            "reason": reason,
            "attribution": None,
        }


def run(operation, callback, inputs, parameters=None):
    """Observe a computation once; a saved/plain reader never enters this route."""
    runs = attribution._runs.get()
    if not runs:
        return callback()
    from sabueso import __version__

    record = {
        "format": FORMAT,
        "execution_id": "sabueso:operation:" + uuid4().hex,
        "operation": operation,
        "started_at": _time(),
        "producer": {
            "name": "sabueso",
            "version": __version__,
            "version_basis": "runtime_package_metadata",
        },
        "parameters": deepcopy(parameters or {}),
        "acquisition": "not_performed",
        "result_id": None,
        "provider": {"status": "not_attempted", "attribution": None},
    }
    try:
        record.update(_support(inputs))
        record["support_status"] = "partial" if record["support_gaps"] else "available"
    except Exception as error:
        record.update(
            inputs=[],
            resources=[],
            bibliography=[],
            support_gaps=[],
            bibliography_gaps=[],
            support_status="unavailable",
            support_error=f"{type(error).__name__}: {error}",
        )
    try:
        result = callback()
    except Exception as error:
        record.update(
            status="failed",
            completed_at=_time(),
            error={"type": type(error).__name__, "message": str(error)},
        )
        for collector in runs:
            collector._operations.append(deepcopy(record))
        raise
    record.update(
        status="completed",
        completed_at=_time(),
    )
    try:
        record["rule"] = deepcopy(result["rule"])
        record["applied_rules"] = [deepcopy(result["rule"])]
        if (result.get("tissue_terms") or {}).get("rule"):
            record["applied_rules"].append(deepcopy(result["tissue_terms"]["rule"]))
        record["result_basis"] = result.get("basis")
        record["result_id"] = digest(canonical_json(result))
        if record["support_status"] != "unavailable" and any(
            card.pinned_ref() != row["card_ref"]
            for (_, card, _), row in zip(inputs, record["inputs"], strict=True)
        ):
            raise ValueError("Input card state changed during computation")
    except Exception as error:
        record["support_status"] = "unavailable"
        record["support_error"] = f"{type(error).__name__}: {error}"
    if record["support_status"] == "unavailable":
        attribution._warning(operation, record["support_error"])
    else:
        record["provider"] = _credit(record)
    for collector in runs:
        collector._operations.append(deepcopy(record))
    return result
