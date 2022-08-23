import evidence as evi

def get_subunit_structure(item, entity='all'):

    from ._add_reference_to_evidence import _add_reference_to_evidence

    output = []

    accession = item['uniprot']['entry']['accession'][0]

    ### Info in comment

    for comment in item['uniprot']['entry']['comment']:

        if comment['@type']=='subunit':

            if type(comment['text'])==list:
                for comment_subunit in comment['text']:

                    subunit = evi.Evidence()
                    subunit.value = comment_subunit['#text']

                    if '@evidence' in comment_subunit:
                        evidence_numbers_in_db = comment_subunit['@evidence'].split(' ')
                        for evidence_number_in_db in evidence_numbers_in_db:
                            evidence_in_db = item['uniprot']['entry']['evidence'][int(evidence_number_in_db)-1]
                            if evidence_in_db['@key']!=evidence_number_in_db:
                                raise ValueError('Evidence number does not match evidence @key')
                            _add_reference_to_evidence(subunit, evidence_in_db)
                            subunit.add_reference({'database':'UniProtKB', 'id':accession})

                    output.append(subunit)

            else:

                subunit = evi.Evidence()
                subunit.value = comment['text']['#text']

                if '@evidence' in comment['text']:
                    evidence_numbers_in_db = comment['text']['@evidence'].split(' ')
                    for evidence_number_in_db in evidence_numbers_in_db:
                        evidence_in_db = item['uniprot']['entry']['evidence'][int(evidence_number_in_db)-1]
                        if evidence_in_db['@key']!=evidence_number_in_db:
                            raise ValueError('Evidence number does not match evidence @key')
                        _add_reference_to_evidence(subunit, evidence_in_db)
                        subunit.add_reference({'database':'UniProtKB', 'id':accession})

                output.append(subunit)

    if len(output)==0:
        output = None
    elif len(output)==1:
        output = output[0]

    return output

