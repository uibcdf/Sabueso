from sabueso._private.argdigest._shared import refuse


def digest_related_cards(related_cards, caller=None):
    from sabueso.core.card import Card

    if isinstance(related_cards, (list, tuple)) and all(
        isinstance(card, Card) for card in related_cards
    ):
        return tuple(related_cards)
    raise refuse(
        "related_cards", related_cards, caller, "expected a list or tuple of Cards"
    )
