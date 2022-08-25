from evidence import Evidence

def get_canonical_sequence(item, entity='all'):

    from ._add_reference_to_evidence import _add_reference_to_evidence

    seq = item['uniprot']['entry']['sequence']['#text']
    accession = item['uniprot']['entry']['accession'][0]
    evidence = Evidence()
    evidence.value = seq
    evidence.add_reference({'database':'UniProtKB', 'id':accession})

    return evidence
