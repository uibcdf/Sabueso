import evidence as evi

from copy import deepcopy
from collections import OrderedDict

def get_catalytic_activity(item, entity='all', as_cards=False):

    from sabueso.cards import CatalyticActivityCard, catalytic_activity_dict
    from ._add_reference_to_evidence import _add_reference_to_evidence
    from ._get_reference_from_dbevidence import _get_reference_from_dbevidence
    from ._get_reference_from_dbreference import _get_reference_from_dbreference
    from .get_uniprot import get_uniprot

    output = []

    uniprot = get_uniprot(item, entity=entity)
    ref_uniprot = uniprot.references[0]

    ### Info in comment

    for comment in item['uniprot']['entry']['comment']:

        if comment['@type']=='catalytic activity':

            if type(comment)!=OrderedDict:
                raise ValueError("Comment type not recognized for catalytic activity")

            aux_dict=deepcopy(catalytic_activity_dict)
            aux_dict['reaction']=evi.Evidence()
            aux_dict['physiological_direction']=evi.Evidence()

            aux_dict['reaction'].value=comment['reaction']['text']
            if '@evidence' in comment['reaction']:
                evidence_numbers = comment['reaction']['@evidence'].split(' ')
                for ii in evidence_numbers:
                    ref = _get_reference_from_dbevidence(int(ii), item)
                    if ref is not None:
                        aux_dict['references'].append(ref)
                        aux_dict['reaction'].add_reference(ref)
            if 'dbReference' in comment['reaction']:
                dbreference = comment['physiologicalReaction']['dbReference']
                if type(dbreference)==OrderedDict:
                    dbreference = [dbreference]
                for aux in dbreference:
                    ref = _get_reference_from_dbreference(aux['@type'], aux['@id'])
                    aux_dict['references'].append(ref)
                    aux_dict['reaction'].add_reference(ref)


            aux_dict['physiological_direction'].value=comment['physiologicalReaction']['@direction']
            if '@evidence' in comment['physiologicalReaction']:
                evidence_numbers = comment['physiologicalReaction']['@evidence'].split(' ')
                for ii in evidence_numbers:
                    ref = _get_reference_from_dbevidence(int(ii), item)
                    if ref is not None:
                        aux_dict['references'].append(ref)
                        aux_dict['physiological_direction'].add_reference(ref)
            if 'dbReference' in comment['physiologicalReaction']:
                dbreference = comment['physiologicalReaction']['dbReference']
                if type(dbreference)==OrderedDict:
                    dbreference = [dbreference]
                for aux in dbreference:
                    ref = _get_reference_from_dbreference(aux['@type'], aux['@id'])
                    aux_dict['references'].append(ref)
                    aux_dict['physiological_direction'].add_reference(ref)

            aux_dict['references'].append(ref_uniprot)

            output.append(aux_dict)

    if as_cards:

        output = [CatalyticActivityCard(ii) for ii in output]

    return output

