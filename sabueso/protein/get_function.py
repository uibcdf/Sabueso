def get_function(item):

    from sabueso.cards.protein.function import FunctionCard
    from sabueso import convert
    from sabueso.tools.sabueso_UniProtKB_XMLDict import get_name as get_name_from_uniprotkb_XMLDict
    from sabueso.tools.sabueso_UniProtKB_XMLDict import get_organism_common_name as get_organism_common_name_from_uniprotkb_XMLDict
    from sabueso.tools.sabueso_UniProtKB_XMLDict import get_key_name as get_key_name_from_uniprotkb_XMLDict
    from sabueso.tools.sabueso_UniProtKB_XMLDict import get_uniprot_id as get_uniprot_id_from_uniprotkb_XMLDict
    from sabueso.tools.sabueso_UniProtKB_XMLDict import get_function as get_function_from_uniprotkb_XMLDict

    card = FunctionCard()

    item_uniprotkb_XMLDict = convert(item, to_form='sabueso.UniProtKB_XMLDict')

    card.protein_name = get_name_from_uniprotkb_XMLDict(item_uniprotkb_XMLDict)
    card.organism_common_name = get_organism_common_name_from_uniprotkb_XMLDict(item_uniprotkb_XMLDict)
    card.protein_key_name = get_key_name_from_uniprotkb_XMLDict(item_uniprotkb_XMLDict)
    card.protein_uniprot_id = get_uniprot_id_from_uniprotkb_XMLDict(item_uniprotkb_XMLDict)


    function_uniprotkb_XMLDict = get_function_from_uniprotkb_XMLDict(item_uniprotkb_XMLDict)

    card.uniprot_function = function_uniprotkb_XMLDict['function']
    card.notes += function_uniprotkb_XMLDict['notes']
    card.references += function_uniprotkb_XMLDict['references']

    return card

