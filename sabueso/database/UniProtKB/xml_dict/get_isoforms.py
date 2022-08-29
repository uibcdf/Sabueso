import evidence as evi
from copy import deepcopy

def get_isoforms(item, entity='all', as_cards=False):

    from sabueso.cards import IsoformCard, isoform_dict
    from ._add_reference_to_evidence import _add_reference_to_evidence
    from ._get_reference_from_dbevidence import _get_reference_from_dbevidence

    output = []

    accession = item['uniprot']['entry']['accession'][0]

    ### Info in comment

    for comment in item['uniprot']['entry']['comment']:

        if comment['@type']=='alternative products':
            event_type = comment['event']['@type']
            if type(comment['isoform']) is not list:
                isoform=comment['isoform']
                aux_dict=deepcopy(isoform_dict)
                aux_dict['uniprot']=isoform['id']
                aux_dict['name']=isoform['name'][0]
                aux_dict['alternative_names']=isoform['name'][1:]
                aux_dict['type']=event_type
                if isoform['sequence']['@type']=='described':
                    aux_dict['vsp']=isoform['sequence']['@ref']
                output.append(aux_dict)
            else:
                for isoform in comment['isoform']:
                    aux_dict=deepcopy(isoform_dict)
                    aux_dict['uniprot']=isoform['id']
                    aux_dict['name']=isoform['name'][0]
                    aux_dict['alternative_names']=isoform['name'][1:]
                    aux_dict['type']=event_type
                    if isoform['sequence']['@type']=='described':
                        aux_dict['vsp']=isoform['sequence']['@ref']
                    output.append(aux_dict)

    # Fix lack of isoforms where isoforms==1

    if len(output)==0:
        aux_dict=deepcopy(isoform_dict)
        aux_dict['uniprot']=accession+'-1'
        aux_dict['name']='1'
        aux_dict['alternative_names']=[]
        output.append(aux_dict)

    if as_cards:
        output = [IsoformCard(ii) for ii in output]

    return output

