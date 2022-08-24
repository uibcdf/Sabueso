from collections import OrderedDict
from evidence import Evidence

def get_name(item, entity='all'):

    from ._add_reference_to_evidence import _add_reference_to_evidence

    evidence = Evidence()

    fullName = item['uniprot']['entry']['protein']['recommendedName']['fullName']

    if type(fullName)==str:
        evidence.value=fullName
    elif type(fullName)==OrderedDict:
        if '#text' in fullName:
            evidence.value = fullName['#text']
        if '@evidence' in fullName:
            evidence_numbers_in_db = fullName['@evidence'].split()
            for evidence_number_in_db in evidence_numbers_in_db:
                evidence_in_db = item['uniprot']['entry']['evidence'][int(evidence_number_in_db)-1]
                if evidence_in_db['@key']!=evidence_number_in_db:
                    raise ValueError('Evidence number does not match evidence @key')
                _add_reference_to_evidence(evidence, evidence_in_db)

    accession = item['uniprot']['entry']['accession'][0]
    evidence.add_reference({'database':'UniProtKB', 'id':accession})

    return evidence

