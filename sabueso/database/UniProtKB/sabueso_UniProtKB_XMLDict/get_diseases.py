import evidence as evi
from copy import deepcopy
from collections import OrderedDict

def get_diseases(item, entity='all', as_cards=False):

    from sabueso.cards import DiseaseCard, disease_dict
    from ._add_reference_to_evidence import _add_reference_to_evidence
    from ._get_reference_from_dbevidence import _get_reference_from_dbevidence
    from ._get_reference_from_dbreference import _get_reference_from_dbreference
    from .get_uniprot import get_uniprot

    output = []

    uniprot = get_uniprot(item, entity=entity)
    ref_uniprot = uniprot.references[0]

    for comment in item['uniprot']['entry']['comment']:

        if comment['@type']=='disease':
            aux_dict=deepcopy(disease_dict)
            aux_dict['name']=comment['disease']['name']
            aux_dict['acronym']=comment['disease']['acronym']
            aux_dict['description']=comment['disease']['description']
            aux_dict['note']=comment['text']

            aux_dict['references'].append(ref_uniprot)
            ref_dis=evi.reference({'database':'UniProt_Diseases', 'id':comment['disease']['@id']})
            aux_dict['references'].append(ref_dis)
            if '@evidence' in comment:
                evidence_numbers = comment['@evidence'].split(' ')
                for ii in evidence_numbers:
                    ref = _get_reference_from_dbevidence(int(ii), item)
                    if ref is not None:
                        aux_dict['references'].append(ref)
            if 'dbReference' in comment['disease']:
                dbreference = comment['disease']['dbReference']
                if type(dbreference)==OrderedDict:
                    dbreference = [dbreference]
                for aux in dbreference:
                    ref = _get_reference_from_dbreference(aux['@type'], aux['@id'])
                    aux_dict['references'].append(ref)

            output.append(aux_dict)

    if as_cards:
        output = [DiseaseCard(ii) for ii in output]

    return output

