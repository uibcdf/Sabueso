from . import to_xml_dict as xml_text_to_xml_dict
from ..xml_dict import to_entry as xml_dict_to_entry

def to_entry(xml_text):

    xml_dict = xml_text_to_xml_dict(xml_text)
    entry = xml_dict_to_entry(xml_dict)

    return entry

