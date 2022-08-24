import xmltodict

def to_xml_dict(xml_text):

    xml_dict = xmltodict.parse(xml_text)

    return xml_dict

