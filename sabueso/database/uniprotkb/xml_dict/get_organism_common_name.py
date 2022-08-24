from evidence import Evidence

def get_organism_common_name(item, entity='all'):

    from ._add_reference_to_evidence import _add_reference_to_evidence

    output = None

    accession = item['uniprot']['entry']['accession'][0]

    if 'organism' in item['uniprot']['entry']:

        evidence = Evidence()

        organism = item['uniprot']['entry']['organism']

        if type(organism['name'])==list:
            for name in organism['name']:
                if name['@type']=='common':
                    evidence.value = name['#text']
        else:
            evidence.value = organism['name']['#text']

        dbref_type = organism['dbReference']['@type']
        dbref_id = organism['dbReference']['@id']

        if dbref_type=='NCBI Taxonomy':
            evidence.add_reference({'database':'NCBI_Taxonomy', 'id':dbref_id})
        else:
            raise ValueError('Unknown reference in database')

            evidence.add_reference({'database':'UniProtKB', 'id':accession})

        output = evidence

    return output

