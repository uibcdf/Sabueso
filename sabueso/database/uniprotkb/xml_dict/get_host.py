from evidence import Evidence

def get_host(item, entity='all'):

    if 'organismHost' in item['uniprot']['entry']:
        evidence = Evidence()
        host = item['uniprot']['entry']['organismHost']['name']['#text']
        accession = item['uniprot']['entry']['accession'][0]
        ncbi_taxonomy = item['uniprot']['entry']['organismHost']['dbReference']['@id']
        evidence.value = host
        evidence.add_NCBI_Taxonomy(id=ncbi_taxonomy)
        evidence.add_UniProtKB(id=accession)
        return evidence
    else:
        return None

