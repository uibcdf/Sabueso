import evidence as evi

def get_ec(item, entity='all'):

    from ._add_reference_to_evidence import _add_reference_to_evidence
    from .get_dbreference import get_dbreference

    in_name = False
    in_db = False

    if 'ecNumber' in item['uniprot']['entry']['protein']['recommendedName']:

        ecNumber = item['uniprot']['entry']['protein']['recommendedName']['ecNumber']
        evidence = evi.Evidence()

        if '#text' in ecNumber:
            evidence.value = ecNumber['#text']
        if '@evidence' in ecNumber:
            evidence_numbers_in_db = ecNumber['@evidence'].split()
            for evidence_number_in_db in evidence_numbers_in_db:
                evidence_in_db = item['uniprot']['entry']['evidence'][int(evidence_number_in_db)-1]
                if evidence_in_db['@key']!=evidence_number_in_db:
                    raise ValueError('Evidence number does not match evidence @key')
                _add_reference_to_evidence(evidence, evidence_in_db)

        accession = item['uniprot']['entry']['accession'][0]
        evidence.add_reference({'database':'UniProtKB', 'id':accession})

        evidence_in_name=evidence
        in_name=True

    evidence = get_dbreference(item, dbname='EC')
    if evidence is not None:
        evidence_in_db=evidence
        in_db=True

    if (in_db==False) and (in_name==False):

        return None

    elif (in_db==True) and (in_name==True):

        return evi.join([evidence_in_name, evidence_in_db])

    else:

        raise ValueError("EC is not in name and neither in dbreference")

