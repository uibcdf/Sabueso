"""Automatic packet attribution, detached from immutable scientific payloads (#108).

The application owns Ackredit sessions. Packet composition observes stored support;
the source-acquisition adapter separately observes its declared built-in clients.
Explicit contexts also observe supported comparative view executions separately.
Reading saved knowledge or JSON records never credits another execution.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy

_runs: ContextVar[tuple] = ContextVar("sabueso_attribution_runs", default=())
FORMAT = "sabueso.packet_attribution@1"


class AttributionRun:
    """Detached composition, source and comparative execution records (#108).

    ``records`` returns detached JSON-compatible records. Save them beside packets;
    they retain original producer versions, card pins and source-record versions.
    A record's ``provider.attribution`` can be read by Ackredit's ``Attribution``.
    ``acquisitions`` independently retains observed source operations, including
    failures, without adding them to the completed-composition ``records``.
    ``operations`` retains supported comparative views executed inside this
    context. Plain view/explanation calls and saved reading remain inert.
    """

    def __init__(self):
        self._records = []
        self._acquisitions = []
        self._literature = []
        self._operations = []

    @property
    def operations(self) -> list[dict]:
        """Detached comparative executions observed inside this context (#108)."""
        return deepcopy(self._operations)

    @property
    def literature(self) -> list[dict]:
        """Original literal extraction/intake events, with distinct execution routes."""
        return deepcopy(self._literature)

    @property
    def records(self) -> list[dict]:
        """Independent copies; changing them cannot change this run or a packet."""
        return deepcopy(self._records)

    @property
    def acquisitions(self) -> list[dict]:
        """Detached source-operation records, separate from packet composition."""
        return deepcopy(self._acquisitions)


@contextmanager
def attribution():
    """Collect packet attribution, source access and supported comparative executions.

    Yields an ``AttributionRun``. Nested contexts observe their contained results;
    the outer context also retains them. No backend is loaded on entry or exit, and
    no Ackredit session, import hook, journal or enrichment is created.
    """
    run = AttributionRun()
    token = _runs.set((*_runs.get(), run))
    try:
        yield run
    finally:
        _runs.reset(token)


def _load_backend():
    import ackredit

    return ackredit


def _observe_literature(record):
    for run in _runs.get():
        run._literature.append(deepcopy(record))


def _warning(operation, reason):
    from sabueso._private.smonitor.emitter import warn
    from sabueso._private.smonitor.outcomes import _user_stacklevel
    from sabueso._private.smonitor.warnings import AttributionTrackingWarning

    warn(
        AttributionTrackingWarning(operation=operation, reason=reason),
        stacklevel=_user_stacklevel(),
    )


def _support(packet, roles):
    from .attribution_bibliography import descriptions, software
    from .packet_terms import _items
    from .packets import _facts, full_rules
    from .snapshot import canonical_json, digest

    resources, scope, gaps = {}, {}, []
    bibliography = {item["id"]: item for item in [software()]}
    for role, card in roles:
        # Composition already computed this exact pin. Rehashing the entire card
        # per statement makes default attribution quadratic in card size.
        card_ref = packet.entities[role]["ref"]
        # Use the same stored-support closure as packet terms, including conflicts
        # and both legs of derived relationships; never infer usage from terms.
        facts = {aspect: _facts(aspect, card) for aspect in packet.query.aspects}
        items = _items(card, facts, role, packet.conflicts.get(role) or [])
        scope[role] = {"card_ref": card_ref, "items": items}
        for item in items:
            if item["kind"] != "source_assertion":
                continue
            assertion = card.source_assertion_store.get(item["id"])
            source = assertion["source"]
            # Version is source-record metadata. It is NOT promoted to a global
            # database release; an unstated version remains None.
            identity = {
                key: source.get(key) for key in ("name", "type", "record_id", "version")
            }
            identifier = "sabueso:source-record:" + digest(canonical_json(identity))
            if identifier not in resources:
                citations = descriptions(source.get("name"))
                bibliography.update({c["id"]: c for c in citations})
                resources[identifier] = {
                    "id": identifier,
                    "source": identity,
                    "description_citation_ids": [c["id"] for c in citations],
                    "uses": [],
                }
                if not citations:
                    gaps.append(
                        {
                            "resource_id": identifier,
                            "reason": "description_citation_not_declared",
                        }
                    )
            usage = {
                "role": role,
                "card_ref": card_ref,
                "source_assertion_ref": item["source_assertion_ref"],
                "retrieved_at": assertion.get("retrieved_at"),
                "acquisition": assertion.get("acquisition"),
            }
            resources[identifier]["uses"].append(usage)
            if assertion.get("field_path") == "literature.article_metadata":
                from .article_metadata import (
                    article_terms,
                )
                from .article_metadata import (
                    citations as article_citations,
                )

                articles, missing = article_citations([assertion["asserted_value"]])
                bibliography.update({c["id"]: c for c in articles})
                usage["publication_citation_ids"] = [c["id"] for c in articles]
                usage["article_terms"] = article_terms(assertion["asserted_value"])
                usage["metadata_binding_rule"] = "article_metadata_binding@1"
                gaps.extend(
                    {
                        "source_assertion_ref": item["source_assertion_ref"],
                        "reason": reason,
                    }
                    for reason in missing
                )
            if "Europe PMC Annotations" in item["sources"]:
                annotation = (assertion.get("asserted_value") or {}).get(
                    "annotation"
                ) or {}
                usage["annotation_provider"] = annotation.get("provider")
                gaps.append(
                    {
                        "resource_id": identifier,
                        "source_assertion_ref": item["source_assertion_ref"],
                        "reason": "article_and_annotation_provider_citations_not_declared",
                    }
                )
    return {
        "scope": scope,
        "resources": list(resources.values()),
        "bibliography": list(bibliography.values()),
        "bibliography_gaps": gaps,
        "support_basis": "stored_statement_support",
        "aspect_mapping": packet.to_dict()["aspect_mapping"],
        "view_rules": {aspect: full_rules()[aspect] for aspect in packet.query.aspects},
        "lineage_note": "Includes represented support and conflicts; unrecorded mapping lineage is not reconstructed. Disease grouping includes stored MONDO/MedGen identity and hierarchy context. Source-record versions are not database releases. Source acquisition and other Sabueso operations are outside this adapter.",
    }


def _resource_item(resource):
    """One operation-independent declaration for a reused stored source record."""
    source = resource["source"]
    item = {
        "id": resource["id"],
        "type": "dataset" if source["type"] == "database" else "other",
        "title": f"{source['name']} record {source['record_id']}",
        "note": "Stored source record used in knowledge analysis; no new acquisition is claimed.",
    }
    if source["version"] is not None:
        item["version"] = source["version"]
    return item


def _credit(record):
    """Provider failures cannot replace a completed scientific result."""
    backend = None
    try:
        backend = _load_backend()
        context = {
            "producer": record["producer"],
            "packet_snapshot_id": record["packet_snapshot_id"],
        }
        with backend.capture("sabueso.compose_packet", context=context) as capture:
            with backend.scope("sabueso.compose_packet"):
                for item in record["bibliography"]:
                    backend.register_item(**item)
                software_id = record["bibliography"][0]["id"]
                backend.track_item(
                    software_id, roles=["executed_software"], context=context
                )
                for resource in record["resources"]:
                    source = resource["source"]
                    backend.register_item(**_resource_item(resource))
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
                        for identifier in usage.get("publication_citation_ids", []):
                            backend.track_item(
                                identifier,
                                roles=["source_publication"],
                                context=use_context,
                            )
        return {
            "status": "available",
            "version": backend.__version__,
            "attribution": capture.attribution.to_dict(),
        }
    except Exception as error:
        # Only attribution code runs inside this boundary. A scientific exception
        # raised during composition never enters it.
        reason = f"{type(error).__name__}: {error}"
        _warning("compose_packet", reason)
        return {
            "status": "failed",
            "version": getattr(backend, "__version__", None),
            "reason": reason,
            "attribution": None,
        }


def _record_packet(packet, roles):
    runs = _runs.get()
    from sabueso import __version__

    record = {
        "format": FORMAT,
        "operation": "compose_packet",
        "packet_snapshot_id": packet.snapshot_id(),
        "producer": {
            "name": "sabueso",
            "version": __version__,
            "version_basis": "runtime_package_metadata",
        },
    }
    try:
        record.update(_support(packet, roles))
    except Exception as error:
        reason = f"{type(error).__name__}: {error}"
        record["support_status"] = "unavailable"
        record["provider"] = {
            "status": "not_attempted",
            "reason": reason,
            "attribution": None,
        }
        _warning("packet support attribution", reason)
    else:
        record["support_status"] = "available"
        record["provider"] = _credit(record)
    for run in runs:
        run._records.append(deepcopy(record))
    return record
