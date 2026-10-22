from sabueso._private.argdigest._shared import refuse
from sabueso.core.errors import _diagnostic_details_allowed


def digest_knowledge_query(knowledge_query, caller=None):
    """A KnowledgeQuery, or its dictionary form (``knowledge_query@1``)."""
    from collections.abc import Mapping

    from sabueso.core.packets import KnowledgeQuery

    if isinstance(knowledge_query, KnowledgeQuery):
        return knowledge_query
    if isinstance(knowledge_query, Mapping):
        try:
            return KnowledgeQuery.from_dict(knowledge_query)
        except (KeyError, ValueError) as exc:
            reason = (
                str(exc) if _diagnostic_details_allowed() else "invalid knowledge query"
            )
            raise refuse("knowledge_query", knowledge_query, caller, reason) from exc
    raise refuse(
        "knowledge_query",
        knowledge_query,
        caller,
        "expected a KnowledgeQuery or its dictionary form",
    )
