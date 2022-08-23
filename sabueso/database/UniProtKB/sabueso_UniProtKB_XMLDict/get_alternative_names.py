from collections import OrderedDict
from evidence import Evidence

def get_alternative_names(item, entity='all'):

    from ._add_reference_to_evidence import _add_reference_to_evidence
    from .get_short_name import get_short_name
    from .get_uniprot import get_uniprot

    output = []

    uniprot = get_uniprot(item, entity=entity)
    ref_uniprot = uniprot.references[0]

    short_name = get_short_name(item)
    if short_name is not None:
        output.append(short_name)

    if 'alternativeName' in item['uniprot']['entry']['protein']:
        alternativeName = item['uniprot']['entry']['protein']['alternativeName']

        if type(alternativeName)==OrderedDict:
            alternativeName = [alternativeName]

        if type(alternativeName)!=list:
            raise ValueError("alternativeName is not a list")

        for aux in alternativeName:
            if type(aux)==OrderedDict:
                for key, value in aux.items():
                    if key not in ['fullName', 'shortName']:
                        raise ValueError("Uknown alternative name type")

                    evidence = Evidence()
                    if type(value)==str:
                            evidence.value = value
                    else:
                        evidence.value = value['#text']
                        if '@evidence' in value:
                                evidence_numbers_in_db = value['@evidence'].split(' ')
                                for evidence_number_in_db in evidence_numbers_in_db:
                                    evidence_in_db = item['uniprot']['entry']['evidence'][int(evidence_number_in_db)-1]
                                    if evidence_in_db['@key']!=evidence_number_in_db:
                                        raise ValueError('Evidence number does not match evidence @key')
                                    _add_reference_to_evidence(evidence, evidence_in_db)

                    evidence.add_reference(ref_uniprot)
                    output.append(evidence)
            else:
                raise ValueError("Uknown alternativeName")


    return output

