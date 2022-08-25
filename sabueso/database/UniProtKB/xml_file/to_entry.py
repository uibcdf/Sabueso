from .to_xml_dict import to_xml_dict
from ..xml_dict import to_entry as xml_dict_to_entry

def to_entry(output_filename):

    xml_dict = to_xml_dict(output_filename)
    entry = xml_dict_to_entry(xml_dict)

    return entry

