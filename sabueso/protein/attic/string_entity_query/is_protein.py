
def is_protein(item):

    from .to_string_uniprot_id import to_string_uniprot_id

    output = False

    try:
        uniprot_id = to_string_uniprot_id(item, max_results=200)
        if uniprot_id:
            output = True
    except:
        pass

    return output

