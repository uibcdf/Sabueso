"""``sabueso.knowledge_packet``: resolve, compose, pin and store in one call (#71).

The query alone decides what is asked of the sources (``packet_aspects@7``). The
keyword arguments only choose how the sources are reached: a ``resolver`` and the
source clients (``chembl_client=…``), for example fixture clients offline. They never
add or change knowledge options, so the packet's query says everything it holds.
"""

from __future__ import annotations

from typing import Any

from smonitor import signal

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ResolverError
from sabueso.core.packets import KnowledgePacket, KnowledgeQuery, compose_packet
from sabueso.core.source_acquisition import capture_acquisitions


def _card(accession: str, role: str, options: dict, curations: Any) -> Any:
    from sabueso.tools.resolve import resolve

    # The bare accession, so that the card records the query as any resolve would.
    card, resolution = resolve(
        accession.split(":", 1)[1], curations=curations, **options
    )
    if card is None:
        raise ResolverError(
            f"The {role} {accession} did not resolve to one entity "
            f"({resolution.status}); resolve it first, and ask about the entry chosen."
        )
    return card


@signal(tags=["api"])
@arg_digest()
@capture_acquisitions
def knowledge_packet(
    knowledge_query: KnowledgeQuery,
    store: Any = None,
    packet_name: str | None = None,
    note: str | None = None,
    curations: Any = None,
    skip_digestion: bool = False,
    **clients: Any,
) -> KnowledgePacket:
    """Answer a KnowledgeQuery with a KnowledgePacket.

    The subject (and comparator) are resolved with the options their aspects need, and
    the packet is composed from those cards (``compose_packet``). With a ``store`` (a
    ``KnowledgeStore`` or its path), the cards are saved in it and, with a
    ``packet_name``, the packet too; ``packet.ref`` is then its pinned reference.
    ``curations`` applies curated statements to the cards before composing.
    """
    if packet_name is not None and store is None:
        raise ValueError("A packet_name needs a store to save the packet in.")
    options = {**knowledge_query.options(), **clients}
    subject = _card(knowledge_query.subject, "subject", options, curations)
    comparator = (
        _card(knowledge_query.comparator, "comparator", options, curations)
        if knowledge_query.comparator
        else None
    )
    packet = compose_packet(knowledge_query, subject, comparator)
    if store is not None:
        for card in (subject, comparator):
            if card is not None:
                store.save(card, note=note)
        if packet_name is not None:
            store.save_packet(packet, packet_name, note=note)
    return packet
