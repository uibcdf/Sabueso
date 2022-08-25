import evidence as evi
from collections import OrderedDict

def get_function(item, entity='all'):

    from ._add_reference_to_evidence import _add_reference_to_evidence
    from ._get_reference_from_dbevidence import _get_reference_from_dbevidence

    from .get_uniprot_id import get_uniprot_id

    output = {'function':[], 'references':[], 'notes':[]}

    uniprot = get_uniprot_id(item, entity=entity)
    ref_uniprot = uniprot.references[0]

    ### Info in comment

    for comment in item['uniprot']['entry']['comment']:

        if comment['@type']=='function':

            if type(comment)!=OrderedDict:
                raise ValueError("Comment type not recognized for function")

            comment_text = comment['text']

            if type(comment_text) in [OrderedDict, str]:
                comment_text = [comment_text]

            if type(comment_text)!=list:
                raise ValueError("Text in comment not recognized for function")

            for aux in comment_text:

                evidence = evi.Evidence()

                if type(aux)==OrderedDict:

                    evidence.value = aux['#text']

                    if '@evidence' in aux:
                        evidence_numbers_in_db = aux['@evidence'].split(' ')
                        for evidence_number_in_db in evidence_numbers_in_db:
                            ref = _get_reference_from_dbevidence(int(evidence_number_in_db), item)
                            evidence.add_reference(ref)
                            output['references'].append(ref)

                elif type(aux)==str:
                    evidence.value = aux

                evidence.add_reference(ref_uniprot)

                output['function'].append(evidence)

    output['references'].append(ref_uniprot)

    return output

