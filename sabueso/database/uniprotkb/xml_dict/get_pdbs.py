from evidence import Evidence

def get_pdbs(item, entity='all'):

    output = []

    uniprot = item['uniprot']['entry']['accession'][0]
    dbReference = item['uniprot']['entry']['dbReference']

    for db in dbReference:
        if db['@type']=='PDB':
            accession = db['@id']
            evidence = Evidence()
            evidence.value = accession
            evidence.add_reference({'database':'PDB', 'id':accession})
            evidence.add_reference({'database':'UniProtKB', 'id':uniprot})
            output.append(evidence)

    return output

