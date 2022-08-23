def get_cards(item, indices='all'):

    from sabueso.cards.stack_of_cards import StackOfCards

    stack = StackOfCards()

    card = get_protein_card(item)

    stack.add(card)

    return stack

