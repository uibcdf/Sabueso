from evidence import Evidence

def get_uniprot_id(item, entity='all'):

    evidence = Evidence()
    if type(item['uniprot']['entry']['accession']) is list:
        accession = item['uniprot']['entry']['accession'][0]
    else:
        accession = item['uniprot']['entry']['accession']
    evidence.value = accession
    evidence.add_reference({'database':'UniProtKB', 'id':accession})

    return evidence

