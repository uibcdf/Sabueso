from evidence import Evidence

def get_uniprot_name(item, entity='all'):

    from ._add_reference_to_evidence import _add_reference_to_evidence

    evidence = Evidence()

    evidence.value = item['uniprot']['entry']['name']
    accession = item['uniprot']['entry']['accession'][0]
    evidence.add_reference({'database':'UniProtKB', 'id':accession})

    return evidence

