from .to_xml_dict import to_xml_dict
from ..xml_dict import to_protein_card as xml_dict_to_protein_card

def to_protein_card(filename):

    xml_dict = to_xml_dict(filename)
    protein_card = xml_dict_to_protein_card(xml_dict)

    return protein_card

