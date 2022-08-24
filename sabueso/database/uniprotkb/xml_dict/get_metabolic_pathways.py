import evidence as evi
from collections import OrderedDict

def get_metabolic_pathways(item, entity='all'):

    from ._add_reference_to_evidence import _add_reference_to_evidence
    from .get_uniprot import get_uniprot

    output = []

    uniprot = get_uniprot(item, entity=entity)
    ref_uniprot = uniprot.references[0]

    ### Info in comment

    for comment in item['uniprot']['entry']['comment']:

        if comment['@type']=='pathway':

            if type(comment)!=OrderedDict:
                raise ValueError("Comment type not recognized for methabolic pathway")

            evidence = evi.Evidence()

            evidence.value = comment['text']

            if '@evidence' in comment:
                evidence_numbers_in_db = comment['@evidence'].split(' ')
                for evidence_number_in_db in evidence_numbers_in_db:
                    evidence_in_db = item['uniprot']['entry']['evidence'][int(evidence_number_in_db)-1]
                    if evidence_in_db['@key']!=evidence_number_in_db:
                        raise ValueError('Evidence number does not match evidence @key')
                    _add_reference_to_evidence(evidence, evidence_in_db)

            evidence.add_reference(ref_uniprot)

            output.append(evidence)

    return output

