def get_key_name(item, entity='all'):

    from .get_uniprot_name import get_uniprot_name

    return get_uniprot_name(item, entity=entity)

