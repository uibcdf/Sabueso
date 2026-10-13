"""Detached source-operation provenance and bibliography (#108, MOLI #36).

These records describe observed access, not SourceAssertions or a MOLI ProjectRecord.
Applications choose their persistence; no implicit journal or project path is created.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from functools import wraps
from inspect import signature
from uuid import uuid4

from . import attribution as adapter

_collectors: ContextVar[tuple] = ContextVar(
    "sabueso_acquisition_collectors", default=()
)
_aggregated_sources: ContextVar[tuple] = ContextVar(
    "sabueso_aggregated_acquisition_sources", default=()
)
FORMAT = "sabueso.source_acquisition@1"
TRACE_FORMAT = "sabueso.acquisition_trace@1"
COVERAGE = {
    "sources": [
        "UniProt",
        "Europe PMC",
        "RCSB PDB",
        "ChEMBL",
        "PubChem",
        "PubChem BioAssay",
        "BindingDB",
        "PDB CCD",
        "UniChem",
        "PDBe-KB",
        "AlphaFold DB",
        "InterPro",
        "MONDO",
        "Open Targets",
        "Orphanet",
        "DISEASES",
        "ClinVar",
        "MedGen",
        "ClinicalTrials.gov",
        "NCBI Taxonomy",
        "GTEx",
        "OMA",
        "gnomAD",
        "AAindex",
        "DisProt",
        "UniParc",
        "AlphaMissense",
        "MobiDB",
        "SIFTS",
        "PDBe Validation",
        "EPPIC",
        "PDB-REDO",
        "GlyGen",
        "AlphaFill",
        "LIGYSIS",
        "IntAct",
        "AmyPro",
        "SWISS-MODEL Repository",
    ],
    "boundary": "built_in_entry_search_mentions_annotations_structure_chemical_clients",
    "other_sources_and_custom_clients": "not_observed",
}


@contextmanager
def collecting():
    records = []
    token = _collectors.set((*_collectors.get(), records))
    try:
        yield records
    finally:
        _collectors.reset(token)


def _trace(records, result_status, card=None):
    trace = {
        "format": TRACE_FORMAT,
        "id": "sabueso:acquisition-trace:" + str(uuid4()),
        "coverage": deepcopy(COVERAGE),
        "result_status": result_status,
        "records": deepcopy(records),
    }
    if card is not None:
        try:
            trace["card_ref"] = card.pinned_ref()
        except Exception as error:
            trace["recording_error"] = f"{type(error).__name__}: {error}"
            adapter._warning("source acquisition card pin", trace["recording_error"])
    return trace


def capture_acquisitions(function):
    """Attach original runtime records without changing scientific serialization."""

    @wraps(function)
    def captured(*args, **kwargs):
        from sabueso import __version__
        from sabueso.tools.db._http import _clock

        started = _clock()
        with collecting() as records:
            try:
                result = function(*args, **kwargs)
            except Exception as error:
                error.acquisition_trace = _trace(records, "failed")
                raise
        if isinstance(result, tuple):
            card, resolution = result
            trace = _trace(records, resolution.status, card)
            resolution._acquisition_trace = deepcopy(trace)
            if card is not None:
                card._acquisition_trace = deepcopy(trace)
        elif isinstance(result, dict):
            result["acquisition_trace"] = _trace(records, "returned")
        else:
            trace = _trace(records, getattr(result, "status", "returned"))
            if hasattr(result, "snapshot_id"):
                try:
                    if hasattr(result, "cards"):
                        trace["deck_snapshot_id"] = result.snapshot_id()
                        trace["card_refs"] = [c.pinned_ref() for c in result.cards]
                        protein = (
                            signature(function)
                            .bind(*args, **kwargs)
                            .arguments.get("protein_card")
                        )
                        if protein is not None:
                            trace["input_card_refs"] = [protein.pinned_ref()]
                        if result.meta.get("kind") in (
                            "disease_targets",
                            "disease_drugs",
                        ):
                            support = result.meta["support"]
                            trace["input_card_refs"] = [support["input"]["card_ref"]]
                            trace["operation"] = {
                                "name": result.meta["kind"],
                                "producer": {
                                    "name": "sabueso",
                                    "version": __version__,
                                    "version_basis": "runtime_package_metadata",
                                },
                                "started_at": started,
                                "finished_at": _clock(),
                                "rule": result.meta["rule"],
                                "limit": result.meta["limit"],
                                "support_card_ref": support["assertions"]["card_ref"],
                                "sources": deepcopy(result.meta.get("sources", [])),
                                "excluded_count": len(result.meta.get("excluded", [])),
                                "built_count": len(result.cards),
                                "support_basis": "original_disease_input_and_native_membership_pins",
                                "source_access_basis": "observed_built_in_clients_only; stored_inputs_and_custom_clients_do_not_establish_access",
                            }
                    else:
                        trace["packet_snapshot_id"] = result.snapshot_id()
                        trace["card_refs"] = {
                            role: entity["ref"]
                            for role, entity in result.entities.items()
                        }
                except Exception as error:
                    trace["recording_error"] = f"{type(error).__name__}: {error}"
                    adapter._warning(
                        "source acquisition result pin", trace["recording_error"]
                    )
            result._acquisition_trace = trace
        return result

    return captured


def _response(operation, result):
    if operation == "entry":
        entry, retrieved = result
        return (
            entry,
            retrieved,
            (entry.get("entryAudit") or {}).get("entryVersion"),
            "entry_version",
            1,
        )
    if operation == "search":
        return (
            result,
            result.get("retrieved_at"),
            result.get("release"),
            "database_release",
            len(result.get("results") or []),
        )
    payload = result["record"]
    count = (
        len(payload.get("articles") or [])
        if operation == "mentions"
        else sum(len(article["annotations"]) for article in payload)
    )
    return (
        payload,
        result.get("retrieved_at"),
        result.get("version"),
        "service_version" if operation == "mentions" else "not_stated",
        count,
    )


def _terminal(error, fixture, requests):
    from .errors import NotArchivedError, OfflineError, RecordNotFoundError

    chain = []
    while error is not None and error not in chain:
        chain.append(error)
        error = error.__cause__ or error.__context__
    if any(isinstance(item, (NotArchivedError, OfflineError)) for item in chain):
        return "not_queried"
    if fixture and getattr(chain[0], "acquisition_outcome", None) == "unavailable":
        return "unavailable"
    if isinstance(chain[0], RecordNotFoundError):
        if fixture:
            return "unavailable"
        if any(request.get("status") == 404 for request in requests):
            return "not_found"
        return "empty" if requests else "unobserved"
    return "failed"


def missing_fixture(message):
    """Keep the existing client exception while declaring local unavailability."""
    from .errors import ConnectorError

    error = ConnectorError(message)
    error.acquisition_outcome = "unavailable"
    return error


def acquisition(source, operation, *, fixture=False, summarize=None, aggregate=False):
    """Instrument a built-in client method; its original result/exception is preserved."""

    def decorate(function):
        parameters = signature(function)

        @wraps(function)
        def observed(*args, **kwargs):
            if source in _aggregated_sources.get():
                return function(*args, **kwargs)
            from sabueso import __version__
            from sabueso.tools.db import _http

            bound = parameters.bind(*args, **kwargs)
            bound.apply_defaults()
            query = {
                key: deepcopy(value)
                for key, value in bound.arguments.items()
                if key != "self"
            }
            record = {
                "format": FORMAT,
                "id": "sabueso:source-acquisition:" + str(uuid4()),
                "source": source,
                "operation": operation,
                "query": query,
                "producer": {
                    "name": "sabueso",
                    "version": __version__,
                    "version_basis": "runtime_package_metadata",
                },
                "started_at": _http._clock(),
            }
            with _http.observing_requests() as requests:
                token = _aggregated_sources.set(
                    (*_aggregated_sources.get(), source)
                    if aggregate
                    else _aggregated_sources.get()
                )
                try:
                    result = function(*args, **kwargs)
                except Exception as error:
                    record.update(
                        outcome=_terminal(error, fixture, requests),
                        error={"type": type(error).__name__, "message": str(error)},
                    )
                    if summarize is not None:
                        try:
                            record.update(summarize(error, query, fixture, requests))
                        except Exception as recording_error:
                            record["recording_error"] = (
                                f"{type(recording_error).__name__}: {recording_error}"
                            )
                            adapter._warning(
                                "source acquisition", record["recording_error"]
                            )
                    if record["outcome"] in {"empty", "not_found"}:
                        record["count"] = 0
                    if requests and not fixture:
                        record["retrieved_at"] = _http._STAMP.get().value
                    if (
                        operation == "mentions"
                        and getattr(error, "version", None) is not None
                    ):
                        record["source_version"] = {
                            "value": error.version,
                            "basis": "service_version",
                        }
                    _finish(record, requests, fixture)
                    raise
                else:
                    try:
                        if summarize is not None:
                            record.update(summarize(result, query, fixture, requests))
                        else:
                            payload, retrieved, version, basis, count = _response(
                                operation, result
                            )
                            from .snapshot import canonical_json, digest

                            record.update(
                                outcome="received" if count else "empty",
                                count=count,
                                retrieved_at=retrieved,
                                source_version={"value": version, "basis": basis},
                                response_identity={
                                    "basis": "decoded_client_result",
                                    "hash": digest(canonical_json(payload)),
                                },
                            )
                    except Exception as error:
                        record.update(
                            outcome="unobserved",
                            recording_error=f"{type(error).__name__}: {error}",
                        )
                        adapter._warning(
                            "source acquisition", record["recording_error"]
                        )
                    _finish(record, requests, fixture)
                    return result
                finally:
                    _aggregated_sources.reset(token)

        return observed

    return decorate


def _finish(record, requests, fixture):
    from sabueso.tools.db._http import _clock

    record["finished_at"] = _clock()
    record["requests"] = deepcopy(requests)
    routes = {request["route"] for request in requests}
    record["access"] = record.get("access") or (
        "fixture"
        if fixture
        else next(iter(routes))
        if len(routes) == 1
        else "mixed"
        if routes
        else "unobserved"
    )
    record["network_attempts"] = sum(
        request["network_attempts"] for request in requests
    )
    record["received_responses"] = sum(
        request["outcome"] == "received" for request in requests
    )
    record.setdefault(
        "retrieved_at",
        next((r.get("retrieved_at") for r in requests if r.get("retrieved_at")), None),
    )
    record.setdefault("source_version", {"value": None, "basis": "not_stated"})
    try:
        record["provider"] = _credit(record)
    except Exception as error:
        reason = f"{type(error).__name__}: {error}"
        record["provider"] = {"status": "failed", "reason": reason, "attribution": None}
        adapter._warning("source acquisition bibliography", reason)
    for collector in _collectors.get():
        collector.append(deepcopy(record))
    for run in adapter._runs.get():
        run._acquisitions.append(deepcopy(record))


def _credit(record):
    from .attribution_bibliography import descriptions, software
    from .snapshot import canonical_json, digest

    record["bibliography"] = [software(), *descriptions(record["source"])]
    record["bibliography_gaps"] = []
    from .comparative_bibliography import method_descriptions

    methods, method_scope = method_descriptions(
        record["source"], operation=record["operation"]
    )
    method_ids = {item["id"] for item in methods}
    if methods:
        record["bibliography"][1:1] = methods
        record["method_reference_scope"] = method_scope
    if record["source"] == "UniProt" and record["operation"] in {
        "uniref_clusters",
        "uniref_members",
    }:
        record["bibliography"].extend(descriptions("UniRef"))
        record["bibliography_gaps"].extend(
            [
                "cluster_and_member_sequence_revisions_not_stated; page_releases_are_separate",
                "member_publications_not_queried",
            ]
        )
    primary_ids = set()
    reference_occurrences = {}
    primary_role = "structure_primary_citation"
    if record["source"] == "RCSB PDB":
        from .attribution_bibliography import structure_citations

        citations, gaps = structure_citations(record.get("entries", []))
        primary_ids = {item["id"] for item in citations}
        record["bibliography"] = list(
            {
                item["id"]: item for item in [*record["bibliography"], *citations]
            }.values()
        )
        record["bibliography_gaps"].extend(gaps)
    if record["source"] == "ChEMBL":
        from .attribution_bibliography import chembl_citations

        citations, gaps = chembl_citations(record.get("documents", {}))
        primary_ids = {item["id"] for item in citations}
        primary_role = "measurement_primary_citation"
        record["bibliography"].extend(citations)
        record["bibliography_gaps"].extend(gaps)
        if (
            record["operation"] in {"bioactivities", "assay_activities"}
            and not citations
        ):
            record["bibliography_gaps"].append(
                "measurement_document_citations_not_returned"
            )
        if record["operation"] in {"indications", "indications_for"}:
            from .indication_bibliography import citations as indication_citations

            context = record.get("indication_reference_context")
            if context is not None:
                native, gaps, occurrences = indication_citations(context)
                record["bibliography"].extend(native)
                record["bibliography_gaps"].extend(gaps)
                context["citation_occurrences"] = occurrences
                for occurrence in occurrences:
                    reference_occurrences.setdefault(
                        occurrence["citation_id"], []
                    ).append(occurrence)
            else:
                record["bibliography_gaps"].append(
                    "indication_reference_metadata_not_declared"
                )
    if record["source"] == "PubChem BioAssay":
        from .attribution_bibliography import pubchem_citations

        citations, gaps = pubchem_citations(record.get("publication_ids", []))
        primary_ids = {item["id"] for item in citations}
        primary_role = "measurement_primary_citation"
        record["bibliography"].extend(citations)
        record["bibliography_gaps"].extend(gaps)
        record["bibliography_gaps"].append("assay_depositor_bibliography_not_declared")
        if not citations:
            record["bibliography_gaps"].append(
                "measurement_publication_ids_not_returned"
            )
    if record["source"] == "BindingDB":
        from .attribution_bibliography import bindingdb_citations

        citations, gaps = bindingdb_citations(record.get("publications", []))
        primary_ids = {item["id"] for item in citations}
        primary_role = "measurement_primary_citation"
        record["bibliography"].extend(citations)
        record["bibliography_gaps"].extend(gaps)
        if not citations:
            record["bibliography_gaps"].append(
                "measurement_publication_pointers_not_returned"
            )
        if any(
            origin["basis"] == "not_stated"
            for origin in record.get("record_origins", [])
        ):
            record["bibliography_gaps"].append("measurement_origin_not_stated")
    if record["operation"] == "annotations":
        record["bibliography_gaps"].append(
            "article_and_annotation_provider_citations_not_declared"
        )
    if record["source"] == "PDBe-KB":
        record["bibliography_gaps"].extend(
            [
                "underlying_structure_primary_citations_not_returned",
                "annotation_method_and_provider_citations_not_returned",
            ]
        )
    if record["source"] == "AlphaFold DB":
        record["bibliography_gaps"].append(
            "model_specific_method_and_provider_citations_not_returned"
        )
    if record["source"] == "InterPro":
        record["bibliography_gaps"].append(
            "member_database_signature_and_site_citations_not_returned"
        )
    if record["source"] == "AAindex":
        record["bibliography_gaps"].append(
            "native_index_publication_metadata_not_fetched"
        )
    if record["source"] == "DisProt":
        record["bibliography_gaps"].append(
            "underlying_disorder_publication_metadata_not_fetched"
        )
    if record["source"] == "UniParc":
        record["bibliography_gaps"].append(
            "referenced_sequence_databases_and_entry_publications_not_fetched"
        )
    if record["source"] == "AlphaMissense":
        record["bibliography_gaps"].append("prediction_artifact_revision_not_stated")
    if record["source"] == "MobiDB":
        record["bibliography_gaps"].append(
            "underlying_annotation_provider_and_method_publications_not_fetched"
        )
    if record["source"] == "SIFTS":
        record["bibliography_gaps"].append(
            "mapping_release_and_referenced_sequence_revisions_not_stated"
        )
    if record["source"] == "PDBe Validation":
        record["bibliography_gaps"].append(
            "validation_pipeline_and_comparison_population_revisions_not_stated"
        )
    if record["source"] == "EPPIC":
        record["bibliography_gaps"].append(
            "prediction_record_revision_and_current_UniProt_coordinate_equivalence_not_stated"
        )
    if record["source"] == "PDB-REDO":
        record["bibliography_gaps"].append(
            "databank_record_revision_not_stated; pipeline_and_input_revisions_are_separate"
        )
    if record["source"] == "AlphaFill":
        record["bibliography_gaps"].extend(
            [
                "metadata_record_and_current_source_sequence_revisions_not_stated",
                "template_structure_primary_publications_not_fetched",
            ]
        )
    if record["source"] == "LIGYSIS":
        record["bibliography_gaps"].extend(
            [
                "result_and_source_sequence_revisions_not_stated",
                "underlying_ligand_structure_and_method_publications_not_fetched",
            ]
        )
    if record["source"] == "GlyGen":
        record["bibliography_gaps"].extend(
            [
                "protein_record_and_source_sequence_revisions_not_stated",
                "underlying_modification_sources_and_publication_metadata_not_fetched",
            ]
        )
    if record["source"] == "IntAct":
        record["bibliography_gaps"].extend(
            [
                "interaction_record_and_participant_sequence_revisions_not_stated",
                "native_publication_and_method_metadata_not_fetched",
            ]
        )
    if record["source"] == "UniProt" and record["operation"] in {
        "isoform_parent",
        "isoform_fasta",
    }:
        record["bibliography_gaps"].extend(
            [
                "isoform_sequence_revision_not_stated; parent_entry_and_canonical_sequence_versions_are_separate",
                "isoform_specific_publications_not_fetched",
            ]
        )
    if record["source"] == "SIGNOR":
        record["bibliography_gaps"].extend(
            [
                "export_relation_sequence_and_score_revisions_not_stated; website_release_separate",
                "native_PMID_and_sentence_context_only; underlying_publications_not_fetched",
            ]
        )
    if record["source"] == "APPRIS":
        record["bibliography_gaps"].extend(
            [
                "dataset_assembly_record_transcript_and_sequence_revisions_not_stated",
                "underlying_method_sequence_and_publication_support_not_fetched",
            ]
        )
    if record["source"] == "Complex Portal":
        record["bibliography_gaps"].extend(
            [
                "complex_record_and_participant_sequence_revisions_not_stated; release_dates_separate",
                "underlying_curation_prediction_support_and_publications_not_fetched",
            ]
        )
    if record["source"] == "CATH":
        record["bibliography_gaps"].extend(
            [
                "response_release_record_and_sequence_revisions_not_stated; release_is_requested_route",
                "underlying_structure_and_annotation_publications_not_fetched",
            ]
        )
    if record["source"] == "SWISS-MODEL Repository":
        record["bibliography_gaps"].extend(
            [
                "metadata_model_and_source_sequence_revisions_not_stated",
                "underlying_PDB_and_template_primary_publications_not_fetched",
            ]
        )
    if record["source"] == "AmyPro":
        record["bibliography_gaps"].extend(
            [
                "export_entry_and_investigated_sequence_revisions_not_stated",
                "entry_level_publications_not_fetched; region_methods_and_specific_support_not_returned",
            ]
        )
    if record["source"] == "MONDO":
        record["bibliography_gaps"].append(
            "term_definition_and_imported_terminology_citations_not_returned"
        )
    if record["source"] in {"Open Targets", "Orphanet"}:
        record["bibliography_gaps"].append(
            "underlying_association_validation_publications_not_fetched"
        )
    if record["source"] == "DISEASES":
        record["bibliography_gaps"].append(
            "underlying_channel_publications_not_fetched"
        )
    if record["source"] == "ClinVar":
        record["bibliography_gaps"].append(
            "submission_and_variant_publications_not_fetched"
        )
    if record["source"] == "MedGen":
        record["bibliography_gaps"].append(
            "underlying_terminology_citations_not_fetched"
        )
    if record["source"] == "NCBI Taxonomy":
        record["bibliography_gaps"].extend(
            [
                "taxonomy_record_revision_not_stated",
                "taxonomic_publications_not_queried",
            ]
        )
    if record["source"] == "GTEx":
        record["bibliography_gaps"].extend(
            [
                "native_dataset_and_tissue_record_revisions_not_stated",
                "tissue_publications_not_queried",
            ]
        )
    if record["source"] == "OMA" or record["operation"] == "oma_entry_names":
        record["bibliography_gaps"].extend(
            [
                "ortholog_and_referenced_sequence_record_revisions_not_stated",
                "entry_and_orthology_method_publications_not_queried",
            ]
        )
        if record["operation"] == "oma_entry_names":
            record["bibliography"].extend(descriptions("UniProtKB search"))
    if record["source"] == "gnomAD":
        record["bibliography_gaps"].extend(
            [
                "native_dataset_and_GTEx_revisions_not_stated",
                "variant_and_entry_publications_not_queried",
            ]
        )
        record["bibliography_gaps"].append(
            "native_pext_method_revision_and_row_publication_binding_not_stated"
            if method_ids
            else "variant_annotation_method_publications_not_queried"
        )
    if record["source"] == "ClinicalTrials.gov":
        from .clinicaltrials_bibliography import citations

        native, primary_ids, occurrences, gaps = citations(
            record.get("entries", []),
            references_requested=record.get("clinical_context", {}).get(
                "references_requested", False
            ),
        )
        primary_role = "source_registry_record"
        record["bibliography"].extend(native)
        record["bibliography_gaps"].extend(gaps)
        record["clinical_context"]["citation_occurrences"] = occurrences
        for occurrence in occurrences:
            reference_occurrences.setdefault(occurrence["citation_id"], []).append(
                occurrence
            )
    if record["source"] == "Europe PMC" and record["operation"] == "article":
        from .article_metadata import citations

        articles = [
            e["article"]
            for e in record.get("entries", [])
            if e["outcome"] == "received"
        ]
        native, gaps = citations(articles)
        primary_ids = {item["id"] for item in native}
        primary_role = "source_publication"
        record["bibliography"].extend(native)
        record["bibliography_gaps"].extend(gaps)
    completed_partial = record["outcome"] == "partial" and (
        record.get("completed_ids") or record.get("completed_pages")
    )
    if (
        record["outcome"] not in ("received", "empty", "not_found")
        and not completed_partial
    ):
        return {
            "status": "not_attempted",
            "reason": "source_access_not_completed",
            "attribution": None,
        }
    backend = None
    try:
        backend = adapter._load_backend()
        context = {
            key: deepcopy(record[key])
            for key in (
                "id",
                "producer",
                "source",
                "operation",
                "query",
                "outcome",
                "access",
                "retrieved_at",
                "source_version",
                "network_attempts",
                "requests",
            )
        }
        for key in (
            "entries",
            "completed_ids",
            "pages",
            "completed_pages",
            "total_count",
            "truncated",
            "missing",
            "incomplete",
            "assays",
            "publication_ids",
            "row_order",
            "aids",
            "count_basis",
            "terminal_outcome",
            "publications",
            "record_origins",
            "record_order",
            "mirror",
            "retrieved_at_basis",
            "cutoff_scope",
            "effective_limit",
            "normalized_query",
            "association_context",
            "indication_reference_context",
            "clinical_context",
            "taxonomy_context",
            "tissue_context",
            "cluster_context",
            "orthology_context",
            "variation_context",
            "method_reference_scope",
        ):
            if key in record:
                context[key] = deepcopy(record[key])
        if "identity_lookup" in record:
            context["identity_lookup"] = deepcopy(record["identity_lookup"])
        if "structural_context" in record:
            context["structural_context"] = deepcopy(record["structural_context"])
        if "annotation_context" in record:
            context["annotation_context"] = deepcopy(record["annotation_context"])
        if "article_context" in record:
            context["article_context"] = deepcopy(record["article_context"])
        resource = "sabueso:source-access:" + digest(
            canonical_json(
                {
                    key: record[key]
                    for key in ("source", "operation", "query", "source_version")
                }
            )
        )
        with backend.capture("sabueso.source_access", context=context) as capture:
            with backend.scope("sabueso.source_access"):
                for item in record["bibliography"]:
                    backend.register_item(**item)
                backend.register_item(
                    id=resource,
                    type="dataset",
                    title=f"{record['source']} {record['operation']} access",
                    **(
                        {"version": record["source_version"]["value"]}
                        if record["source"] == "Orphanet"
                        and record["source_version"]["value"] is not None
                        else {}
                    ),
                )
                backend.track_item(
                    record["bibliography"][0]["id"],
                    roles=["executed_software"],
                    context=context,
                )
                backend.track_item(resource, roles=["resource_access"], context=context)
                for item in record["bibliography"][1:]:
                    item_context = context
                    if item["id"] in reference_occurrences:
                        item_context = {
                            **context,
                            "cited_reference_occurrences": deepcopy(
                                reference_occurrences[item["id"]]
                            ),
                        }
                    backend.track_item(
                        item["id"],
                        roles=[
                            "source_cited_reference"
                            if item["id"] in reference_occurrences
                            else primary_role
                            if item["id"] in primary_ids
                            else "method_description"
                            if item["id"] in method_ids
                            else "resource_description"
                        ],
                        context=item_context,
                    )
        return {
            "status": "available",
            "version": backend.__version__,
            "attribution": capture.attribution.to_dict(),
        }
    except Exception as error:
        reason = f"{type(error).__name__}: {error}"
        adapter._warning("source acquisition", reason)
        return {
            "status": "failed",
            "version": getattr(backend, "__version__", None),
            "reason": reason,
            "attribution": None,
        }
