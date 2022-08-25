
def missing_info(item):

    # uniprot
    for item_key in item:
        if item_key not in ['uniprot']:
            print(f'item["{item_key}"]')

    for uniprot_key in item['uniprot']:
        if uniprot_key not in ['@xmlns', '@xmlns:xsi', '@xsi:schemaLocation', 'entry', 'copyright']:
            print(f'item["uniprot"]["{uniprot_key}"]')

    # uniprot-entry
    for entry_key in item['uniprot']['entry']:
        if entry_key not in ['@dataset', '@created', '@modified', '@version', 'accession', 'name',
                'protein', 'gene', 'organism', 'reference', 'comment', 'dbReference', 'proteinExistence',
                'keyword', 'feature', 'evidence', 'sequence']:
            print(f'item["uniprot"]["entry"]["{entry_key}"]')

    # uniprot-entry-protein
    for protein_key in item['uniprot']['entry']['protein']:
        if protein_key not in [ 'recommendedName', 'alternativeName']:
            print(f'item["uniprot"]["entry"]["protein"][{protein_key}]')

    # uniprot-entry-protein-recommendedName
    for recommendedName_key in item['uniprot']['entry']['protein']['recommendedName']:
        if recommendedName_key not in ['fullName', 'ecNumber']:
            print(f'item["uniprot"]["entry"]["protein"]["recommendedName"][{recommendedName_key}]')

    # uniprot-entry-protein-alternativeName
    if type(item['uniprot']['entry']['protein']['alternativeName']) not in [list]:
            raise ValueError('item["uniprot"]["entry"]["protein"]["alternativeName"] is not a list')

    for aux in item['uniprot']['entry']['protein']['alternativeName']:
        for aux2 in aux:
            if aux2 not in ['fullName', 'shortName']:
                print(f'item["uniprot"]["entry"]["protein"]["alternativeName"][ii][{aux2}]')

    # uniprot-entry-gene
    if 'gene' in item['uniprot']['entry']:
        print(f'item["uniprot"]["entry"]["gene"]')

    # uniprot-entry-organism
    for organism_key in item['uniprot']['entry']['organism']:
        if organism_key not in [ 'name', 'dbReference', 'lineage']:
            print(f'item["uniprot"]["entry"]["organism"][{organism_key}]')

    # uniprot-entry-reference
    if 'reference' in item['uniprot']['entry']:
        print(f'item["uniprot"]["entry"]["reference"]')

    # uniprot-entry-comment
    if type(item['uniprot']['entry']['comment']) not in [list]:
            raise ValueError('item["uniprot"]["entry"]["comment"] is not a list')

    already=['function', 'catalytic activity', 'activity regulation', 'pathway',
            'subcellular location', 'tissue specificity', 'alternative products', 'subunit',
            'domain', 'disease', 'interaction']

    for aux in item['uniprot']['entry']['comment']:
        if aux['@type'] not in already:
            print(f'item["uniprot"]["entry"]["comment"][ii]["@type"]:{aux["@type"]}')
            already.append(aux['@type'])

    # uniprot-entry-dbReference
    if 'dbReference' in item['uniprot']['entry']:
        print(f'item["uniprot"]["entry"]["dbReference"]')

    # uniprot-entry-proteinExistence
    if 'proteinExistence' in item['uniprot']['entry']:
        print(f'item["uniprot"]["entry"]["proteinExistence"]')

    # uniprot-entry-keyword
    if 'keyword' in item['uniprot']['entry']:
        print(f'item["uniprot"]["entry"]["keyword"]')

    # uniprot-entry-feature
    if type(item['uniprot']['entry']['feature']) not in [list]:
            raise ValueError('item["uniprot"]["entry"]["feature"] is not a list')

    already=['chain', 'domain', 'nucleotide phosphate-binding region', 'region of interest',
            'binding site', 'modified residue', 'splice variant', 'sequence variant', 'sequence conflict',
            'helix', 'strand', 'turn']

    for aux in item['uniprot']['entry']['feature']:
        if aux['@type'] not in already:
            print(f'item["uniprot"]["entry"]["feature"][ii]["@type"]:{aux["@type"]}')
            already.append(aux['@type'])

    # uniprot-entry-sequence
    already=['@length', '@mass', '@checksum', '@modified', '@version', '#text']

    if 'sequence' in item['uniprot']['entry']:
        for aux in item['uniprot']['entry']['sequence']:
            if aux not in already:
                print(f'item["uniprot"]["entry"]["feature"][ii]["@type"]:{aux["@type"]}')
                already.append(aux['@type'])

    pass


