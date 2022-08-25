import evidence as evi
from copy import deepcopy

def get_secondary_structure(item, entity='all', as_cards=False):

    from sabueso.cards import SecondaryStructureCard, secondary_structure_dict
    from sabueso.cards import HelixCard, helix_dict
    from sabueso.cards import StrandCard, strand_dict
    from sabueso.cards import TurnCard, turn_dict
    from ._add_reference_to_evidence import _add_reference_to_evidence
    from ._get_reference_from_dbevidence import _get_reference_from_dbevidence
    from .get_uniprot import get_uniprot

    output = []

    uniprot = get_uniprot(item, entity=entity)
    ref_uniprot = uniprot.references[0]

    output = deepcopy(secondary_structure_dict)

    for feature in item['uniprot']['entry']['feature']:

        if feature['@type'] in ['helix', 'turn', 'strand']:
            if feature['@type']=='helix':
                aux_dict=deepcopy(helix_dict)
            elif feature['@type']=='strand':
                aux_dict=deepcopy(strand_dict)
            else:
                aux_dict=deepcopy(turn_dict)
            aux_dict['begin']=feature['location']['begin']['@position']
            aux_dict['end']=feature['location']['end']['@position']
            aux_dict['references'].append(ref_uniprot)
            if '@evidence' in feature:
                evidence_numbers = feature['@evidence'].split(' ')
                for ii in evidence_numbers:
                    ref = _get_reference_from_dbevidence(int(ii), item)
                    if ref is not None:
                        aux_dict['references'].append(ref)
            if feature['@type']=='helix':
                output['helices'].append(aux_dict)
            elif feature['@type']=='strand':
                output['strands'].append(aux_dict)
            else:
                output['turns'].append(aux_dict)

    output['references'].append(ref_uniprot)

    if as_cards:
        output['helices'] = [HelixCard(ii) for ii in output['helices']]
        output['strands'] = [StrandCard(ii) for ii in output['strands']]
        output['turns'] = [TurnCard(ii) for ii in output['turns']]
        output = SecondaryStructureCard(output)

    return output

