
def is_string_entity_name(item):

    from sabueso.forms.strings.api_string_entity_name import is_protein

    output = False

    if type(item)==str:

        if is_protein(item):

            output = True

    return output

