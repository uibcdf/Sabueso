import xmltodict
from .to_xml_text import to_xml_text

def to_xml_dict(output_filename):

    xml_text = to_xml_text(output_filename)
    xml_dict = xmltodict.parse(xml_text)

    return xml_dict

