import evidence as evi
from copy import deepcopy

def get_organism(item, entity='all', as_card=False):

    from sabueso.cards import OrganismCard, organism_dict
    from ._add_reference_to_evidence import _add_reference_to_evidence

    output = deepcopy(organism_dict)

    accession = item['uniprot']['entry']['accession'][0]

    if 'organism' in item['uniprot']['entry']:

        common_name = evi.Evidence()
        scientific_name = evi.Evidence()
        ncbi_taxonomy = evi.Evidence()

        organism = item['uniprot']['entry']['organism']

        dbref_type = organism['dbReference']['@type']
        dbref_id = organism['dbReference']['@id']

        if dbref_type!='NCBI Taxonomy':
            raise ValueError('Unknown reference in database')

        ncbi_taxonomy.value = dbref_id
        ncbi_taxonomy.add_reference({'database':'NCBI_Taxonomy', 'id':dbref_id})
        ncbi_taxonomy.add_reference({'database':'UniProtKB', 'id':accession})
        output['ncbi_taxonomy']=ncbi_taxonomy

        if type(organism['name'])==list:
            for name in organism['name']:
                if name['@type']=='common':
                    common_name.value = name['#text']
                    common_name.add_reference({'database':'NCBI_Taxonomy', 'id':dbref_id})
                    common_name.add_reference({'database':'UniProtKB', 'id':accession})
                    output['common_name']=common_name
                if name['@type']=='scientific':
                    scientific_name.value = name['#text']
                    scientific_name.add_reference({'database':'NCBI_Taxonomy', 'id':dbref_id})
                    scientific_name.add_reference({'database':'UniProtKB', 'id':accession})
                    output['scientific_name']=scientific_name
        else:
            common_name.value = organism['name']['#text']
            common_name.add_reference({'database':'NCBI_Taxonomy', 'id':dbref_id})
            common_name.add_reference({'database':'UniProtKB', 'id':accession})
            output['common_name']=common_name

        output['references'].append(evi.reference({'database':'NCBI_Taxonomy', 'id':dbref_id}))
        output['references'].append(evi.reference({'database':'UniProtKB', 'id':accession}))

    if as_card:
        output = OrganismCard(output)

    return output

