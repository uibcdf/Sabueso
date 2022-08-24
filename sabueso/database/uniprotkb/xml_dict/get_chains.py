import evidence as evi
from copy import deepcopy

def get_chains(item, entity='all', as_cards=False):

    from sabueso.cards import ChainCard, chain_dict
    from ._add_reference_to_evidence import _add_reference_to_evidence
    from ._get_reference_from_dbevidence import _get_reference_from_dbevidence

    output = []

    accession = item['uniprot']['entry']['accession'][0]
    ref = evi.reference({'database':'UniProtKB', 'id':accession})

    for feature in item['uniprot']['entry']['feature']:

        if feature['@type']=='chain':
            aux_dict=deepcopy(chain_dict)
            aux_dict['protein_name']=feature['@description']
            aux_dict['uniprot_chain_id']=feature['@id']
            aux_dict['begin']=feature['location']['begin']['@position']
            aux_dict['end']=feature['location']['end']['@position']
            aux_dict['references'].append(ref)
            output.append(aux_dict)

    if as_cards:
        output = [ChainCard(ii) for ii in output]

    return output

