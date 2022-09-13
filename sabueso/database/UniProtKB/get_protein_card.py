
def get_protein_card(uniprot_id):

    xml_dict = uniprot_id_to_xml_dict(uniprot_id)
    protein_card = xml_dict_to_protein_card(xml_dict)
    return protein_card

