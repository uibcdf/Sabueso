
def to_entry(uniprot_id):

    from .to_xml_dict import to_xml_dict
    from ..xml_dict.to_entry import to_entry as xml_dict_to_entry

    xml_dict = to_xml_dict(uniprot_id)
    entry = xml_dict_to_entry(xml_dict)

    return entry
