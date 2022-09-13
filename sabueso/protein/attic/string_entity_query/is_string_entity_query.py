
def is_string_entity_query(item):

    from .is_protein import is_protein

    output = False

    if type(item)==str:

        if is_protein(item):

            output = True

    return output

