"""Observe gnomAD GraphQL scope independently of scientific mapping/selection."""

from contextvars import ContextVar
from copy import deepcopy
from functools import wraps
from inspect import signature

from .errors import ConnectorError
from .snapshot import canonical_json, digest
from .source_acquisition import _terminal, acquisition

_pages = ContextVar("sabueso_gnomad_pages", default=None)


def note_response(payload, *, query=None, fixture=False):
    page = {
        "outcome": "failed",
        "query": deepcopy(query),
        "response_identity": {
            "basis": "decoded_fixture_record"
            if fixture
            else "decoded_GraphQL_response",
            "hash": digest(canonical_json(payload)),
        },
        "source_version": {"value": None, "basis": "not_stated"},
    }
    pages = _pages.get()
    if pages is not None:
        pages.append(page)


def _objects(rows, what):
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ConnectorError(f"gnomAD fixture does not state a {what} list")
    return rows


def validate_fixture(saved, kind):
    if not isinstance(saved, dict) or not isinstance(saved.get("record"), dict):
        raise ConnectorError("gnomAD fixture does not state a record object")
    record = saved["record"]
    if not isinstance(record.get("gene" if kind == "pext" else kind), dict):
        raise ConnectorError(f"gnomAD fixture does not state a {kind} object")
    if kind == "pext":
        if not isinstance(record.get("pext"), dict):
            raise ConnectorError("gnomAD fixture does not state a pext object")
        _objects(record["pext"].get("regions"), "pext regions")
    else:
        _objects(record.get("variants"), "variants")


def validate_consequences(saved):
    if not isinstance(saved, dict) or not all(isinstance(key, str) for key in saved):
        raise ConnectorError("gnomAD fixture does not state a consequence mapping")
    for rows in saved.values():
        _objects(rows, "transcript consequences")


def note_completed(
    record,
    *,
    kind,
    absent_ids=(),
    fixture_version=None,
    absence=None,
    native_variant_ids=None,
):
    pages = _pages.get()
    if not pages:
        return
    page = pages[-1]
    if absence:
        count, rows = 0, []
    elif kind == "consequences":
        count = len(record)
        rows = [row for values in record.values() for row in values]
        page.update(
            received_variant_ids=list(record),
            absent_variant_ids=list(absent_ids),
            transcript_consequence_count=len(rows),
            native_transcript_bindings={
                variant: [
                    {
                        "transcript_id": row.get("transcript_id"),
                        "transcript_version": row.get("transcript_version"),
                    }
                    for row in values
                ]
                for variant, values in record.items()
            },
        )
        if native_variant_ids is not None:
            page["native_variant_ids"] = deepcopy(native_variant_ids)
    else:
        rows = record["pext"]["regions"] if kind == "pext" else record["variants"]
        count = len(rows)
        entity = record["gene" if kind == "pext" else kind]
        page["native_entity"] = deepcopy(entity)
    page.update(
        outcome="received" if count else "empty",
        count=count,
        count_basis="validated_variant_bindings_in_response; not_retained_selection"
        if kind == "consequences"
        else "validated_pext_regions"
        if kind == "pext"
        else "validated_variant_rows",
    )
    if fixture_version is not None:
        page["fixture_version_label"] = fixture_version
    if absence:
        page["absence_basis"] = absence


def observe(operation, *, fixture=False):
    def decorate(function):
        @wraps(function)
        def observed(*args, **kwargs):
            if operation == "gnomad_consequences":
                bound = signature(function).bind(*args, **kwargs)
                bound.arguments["variant_ids"] = list(bound.arguments["variant_ids"])
                args, kwargs = bound.args, bound.kwargs
            pages = []
            token = _pages.set(pages)
            try:
                return acquisition(
                    "gnomAD",
                    operation,
                    fixture=fixture,
                    summarize=lambda result, query, local, requests: _summarize(
                        result, query, local, requests, pages, operation
                    ),
                )(function)(*args, **kwargs)
            finally:
                _pages.reset(token)

        return observed

    return decorate


def _summarize(result, query, fixture, requests, pages, operation):
    from sabueso.tools.db.gnomad import DATASET, PEXT_VERSION

    failed = isinstance(result, Exception)
    completed = [page for page in pages if page["outcome"] in {"received", "empty"}]
    received = sum(page["count"] for page in completed) if completed else None
    consequences = operation == "gnomad_consequences"
    pext = operation == "gnomad_pext"
    returned = (
        None
        if failed
        else len(result["record"])
        if consequences
        else len(
            result["record"]["pext"]["regions"]
            if pext
            else result["record"]["variants"]
        )
    )
    terminal = _terminal(result, fixture, requests) if failed else None
    outcome = (
        "partial"
        if failed and completed and not any(p.get("absence_basis") for p in completed)
        else terminal
        if failed
        else "not_queried"
        if not completed
        else "received"
        if returned
        else "empty"
    )
    context = {
        "rule": "gnomad_operation_observation@1",
        "scope": "fixture_subset"
        if fixture
        else "one_GraphQL_response_per_alias_batch"
        if consequences
        else "single_GraphQL_response",
        "requested_dataset": None if pext else DATASET,
        "dataset_basis": "not_a_GraphQL_argument"
        if pext
        else "built_in_GraphQL_dataset_argument; fixture_label_does_not_prove_native_release"
        if fixture
        else "GraphQL_dataset_argument",
        "requested_reference_genome": None if consequences else "GRCh38",
        "reference_genome_basis": "not_requested_in_consequence_query"
        if consequences
        else "built_in_online_query_scope; fixture_is_not_a_native_genome_declaration"
        if fixture
        else "GraphQL_reference_genome_argument",
        "client_version_label": PEXT_VERSION if pext else DATASET,
        "client_version_basis": "client_description; native_release_not_stated",
        "query": deepcopy(query),
        "received_items": received,
        "returned_items": returned,
        "completeness": "not_established",
        "selection_basis": "client_rows_precede_enricher_transcript_merge_protein_placement_and_limit; card_quality_reports_mapping_count",
        "identity_basis": "source_stated_gene_transcript_and_variant_ids; shared_coordinates_or_protein_changes_never_entity_identity",
        "reference_basis": "native_variant_and_entry_publications_not_returned; offline_resource_and_method_descriptions_are_separate",
    }
    if consequences:
        context["requested_variant_ids"] = sorted(
            {v for v in query["variant_ids"] if v}
        )
        context["absent_variant_ids"] = [
            v for page in completed for v in page.get("absent_variant_ids", [])
        ]
        context["transcript_consequence_count"] = sum(
            page.get("transcript_consequence_count", 0) for page in completed
        )
    if pext:
        context["native_GTEx_revision"] = {
            "value": None,
            "basis": "not_stated; client_label_is_not_a_native_release",
        }
    metadata = {
        "outcome": outcome,
        "count": received if failed else returned if completed else None,
        "count_basis": "completed_response_items; no_client_result_returned"
        if failed
        else "returned_variant_bindings; not_transcript_consequence_rows_or_card_selected_items"
        if consequences
        else "returned_pext_regions; not_card_selected_or_derived_tissue_items"
        if pext
        else "returned_variant_rows; not_card_selected_or_placed_protein_changes",
        "pages": deepcopy(pages),
        "completed_pages": deepcopy(completed),
        "source_version": {"value": None, "basis": "not_stated"},
        "incomplete": failed
        and outcome not in {"empty", "not_found", "unavailable", "not_queried"},
        "variation_context": context,
    }
    if completed:
        metadata["response_identity"] = {
            "basis": "completed_response_receipts"
            if failed
            else "decoded_client_record",
            "hash": digest(canonical_json(completed if failed else result["record"])),
        }
    if failed:
        metadata["terminal_outcome"] = terminal
    else:
        metadata["retrieved_at"] = result["retrieved_at"]
    return metadata
