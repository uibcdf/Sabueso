from copy import deepcopy as _deepcopy
from sabueso.fields.protein import in_pdb_card as _in_pdb_card
from sabueso.fields.protein import segment_card as _segment_card

def target_query(string=None, organism=None):

   import gevent.monkey
   gevent.monkey.patch_all(thread=False, select=False)
   from chembl_webresource_client.new_client import new_client as client
   result = client.target.filter(target_synonym__icontains=string)
   list_result=[]
   for tmp_target in result:
       if tmp_target['target_type']=='SINGLE PROTEIN':
           list_result.append(protein_card(tmp_target['target_chembl_id']))

   return list_result

def protein_card(chembl=None, card=None):

    if card is None:
        from sabueso.fields.protein import protein_card as _protein_card
        tmp_card = _deepcopy(_protein_card)
        tmp_card['ChEMBL'].append(chembl)
        del(_protein_card)
    else:
        tmp_card = _deepcopy(card)

    chembl_id=tmp_card['ChEMBL'][0]

    import gevent.monkey
    gevent.monkey.patch_all(thread=False, select=False)
    from chembl_webresource_client.new_client import new_client as client
    result = client.target.filter(target_chembl_id__in=chembl_id)[0]

    # Name
    tmp_card['Name'].append(result['pref_name'])

    # Type
    tmp_card['Type'].append(result['target_type'])

    # Organism
    tmp_card['Organism Scientific'].append(result['organism'])

    # ChEMBL
    tmp_card['ChEMBL'].append(result['target_chembl_id'])

    ##### components?
    if len(result['target_components'])>1:
        print('La proteína tiene más de un target_components y no se que es.')

    for xref in result['target_components'][0]['target_component_xrefs']:

        src_db = xref['xref_src_db']
        id_db = xref['xref_id']

    # PDB
        if src_db == 'PDBe':
            if id_db not in tmp_card['in PDB'].keys():
                tmp_card['in PDB'][id_db]=None

    # UniProt
        elif src_db == 'UniProt':
            tmp_card['UniProt'].append(id_db)

    # IntAct
        elif src_db == 'IntAct':
            tmp_card['IntAct'].append(id_db)

    # InterPro
        elif src_db == 'InterPro':
            tmp_card['InterPro'].append(id_db)

    # Pfam
        elif src_db == 'Pfam':
            tmp_card['Pfam'].append(id_db)

    del(result,client)

    return tmp_card
