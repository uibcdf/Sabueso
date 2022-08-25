from sabueso._private.files_and_directories import tempfile
from .to_xml_text import to_xml_text

def to_xml_file(uniprot_id, output_filename=None):

    xml_text = to_xml_text(uniprot_id)

    if output_filename is None:
        output_filename = tempfile(extension='xml')

    with open(output_filename, 'w') as fff:
        fff.write(xml_text)

    return output_filename

