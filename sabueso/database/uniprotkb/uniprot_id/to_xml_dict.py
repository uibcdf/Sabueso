import xmltodict
from .to_xml_text import to_xml_text

def to_xml_dict(uniprot_id):

    xml_text = to_xml_text(uniprot_id)
    xml_dict = xmltodict.parse(xml_text)

    return xml_dict

