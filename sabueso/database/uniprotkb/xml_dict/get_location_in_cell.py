import evidence as evi
from copy import deepcopy
from collections import OrderedDict

def get_location_in_cell(item, entity='all', as_cards=False):

    from sabueso.cards import LocationInCellCard, location_in_cell_dict
    from ._add_reference_to_evidence import _add_reference_to_evidence
    from ._get_reference_from_dbevidence import _get_reference_from_dbevidence
    from .get_uniprot import get_uniprot

    uniprot = get_uniprot(item, entity=entity)
    ref_uniprot = uniprot.references[0]

    output = []

    for comment in item['uniprot']['entry']['comment']:

        if comment['@type']=='subcellular location':

            aux_dict=deepcopy(location_in_cell_dict)

            for subcellularLocation in comment['subcellularLocation']:

                aux_output=[]

                if 'location' in subcellularLocation:
                    location = subcellularLocation['location']
                    if type(location)==OrderedDict:
                        location=[location]
                    for ll in location:
                        evidence=evi.Evidence()
                        evidence.value=ll['#text']
                        if '@evidence' in ll:
                            evidence_numbers = ll['@evidence'].split(' ')
                            for ii in evidence_numbers:
                                ref = _get_reference_from_dbevidence(int(ii), item)
                                if ref is not None:
                                    evidence.add_reference(ref)
                                    aux_dict['references'].append(ref)
                        evidence.add_reference(ref_uniprot)
                        aux_output.append(evidence)
                if 'topology' in subcellularLocation:
                    topology = subcellularLocation['topology']
                    if type(topology)==OrderedDict:
                        topology=[topology]
                    for ll in topology:
                        evidence=evi.Evidence()
                        evidence.value=ll['#text']
                        if '@evidence' in ll:
                            evidence_numbers = ll['@evidence'].split(' ')
                            for ii in evidence_numbers:
                                ref = _get_reference_from_dbevidence(int(ii), item)
                                if ref is not None:
                                    evidence.add_reference(ref)
                                    aux_dict['references'].append(ref)
                        evidence.add_reference(ref_uniprot)
                        aux_output.append(evidence)

                aux_dict['location'].append(aux_output)

            evidence=evi.Evidence()
            evidence.value=comment['text']['#text']
            if '@evidence' in comment['text']:
                evidence_numbers = comment['text']['@evidence'].split(' ')
                for ii in evidence_numbers:
                    ref = _get_reference_from_dbevidence(int(ii), item)
                    if ref is not None:
                        evidence.add_reference(ref)
                        aux_dict['references'].append(ref)
            evidence.add_reference(ref_uniprot)

            aux_dict['note']=evidence

            output.append(aux_dict)

    if as_cards:
        output = [LocationInCellCard(ii) for ii in output]

    return output

