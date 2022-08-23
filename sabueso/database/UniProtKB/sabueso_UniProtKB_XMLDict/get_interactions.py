import evidence as evi
from copy import deepcopy

def get_interactions(item, entity='all', as_cards=False):

    from sabueso.cards import InteractionCard, interaction_dict
    from sabueso.cards import InteractantCard, interactant_dict

    output = []

    accession = item['uniprot']['entry']['accession'][0]

    ### Info in comment

    for comment in item['uniprot']['entry']['comment']:

        if comment['@type']=='interaction':
            interaction = deepcopy(interaction_dict)
            for interactant_db in comment['interactant']:
                interactant = deepcopy(interactant_dict)
                interactant['intact'] = interactant_db['@intactId']
                interactant['uniprot'] = interactant_db['id']
                interactant['type'] = 'protein'
                interactant['references'].append(evi.reference({'database':'UniProtKB', 'id':'accession'}))
                interaction['interactants'].append(interactant)
            if comment['organismsDiffer']=='true':
                interaction['same_organism']=False
            else:
                interaction['same_organism']=True
            interaction['n_experiments']=int(comment['experiments'])

            output.append(interaction)

    if as_cards:
        for aux in output:
            aux['interactants'] = [InteractantCard(ii) for ii in aux['interactants']]
        output = [InteractionCard(ii) for ii in output]

    return output

