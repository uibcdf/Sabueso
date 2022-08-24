# We start  mmtf-python and some APIs from DBs

from copy import deepcopy as _deepcopy
import urllib as _urllib
import mmtf as _mmtf
import json as _json

def _pdb_to_uniprot_SIFTS(pdb=None):

    url = 'http://www.ebi.ac.uk/pdbe/api/mappings/uniprot/'+pdb
    request = _urllib.request.Request(url)
    response = _urllib.request.urlopen(request)
    response_txt = response.read().decode('utf-8')
    sifts_api_dict = _json.loads(response_txt)
    pdbid = list(sifts_api_dict.keys())[0]
    result=[]
    for uniprotid in sifts_api_dict[pdbid]['UniProt'].keys():
        for mapp in sifts_api_dict[pdbid]['UniProt'][uniprotid]['mappings']:
            tmp_dict={}
            tmp_dict['uniprot']=uniprotid
            tmp_dict['entity_id']=mapp['entity_id']
            tmp_dict['chain_id']=mapp['chain_id']
            tmp_dict['pdb_start']=mapp['start']['residue_number']
            tmp_dict['pdb_end']=mapp['end']['residue_number']
            tmp_dict['uniprot_start']=mapp['unp_start']
            tmp_dict['uniprot_end']=mapp['unp_end']
            result.append(tmp_dict)
    del(url, request, response, response_txt, sifts_api_dict, pdbid, uniprotid, mapp)
    return result

def _data_from_chemid(chem_id=None):

    url = 'https://www.ebi.ac.uk/pdbe/api/pdb/compound/summary/'+chem_id
    request = _urllib.request.Request(url)
    response = _urllib.request.urlopen(request)
    response_txt = response.read().decode('utf-8')
    ligand_api_dict = _json.loads(response_txt)
    inchikey = ligand_api_dict[chem_id][0]["inchi_key"]
    chemblid = ligand_api_dict[chem_id][0]["chembl_id"]
    return inchikey, chemblid

def _ligand_from_pdb(pdb=None):

    from sabueso.fields.pdb import ligand_card as _ligand_card
    url = 'https://www.ebi.ac.uk/pdbe/api/pdb/entry/ligand_monomers/'+pdb
    request = _urllib.request.Request(url)
    try:
        response = _urllib.request.urlopen(request)
        response_txt = response.read().decode('utf-8')
        ligand_api_dict = _json.loads(response_txt)
        pdbid = list(ligand_api_dict.keys())[0]
        ligands={}
        for tmp_ligand in ligand_api_dict[pdbid]:
            tmp_dict=_deepcopy(_ligand_card)
            tmp_dict['Name']=tmp_ligand['chem_comp_name']
            tmp_dict['Residue Name']=tmp_ligand['chem_comp_id']
            tmp_dict['Entity']=tmp_ligand['chem_comp_id']
            tmp_dict['Chemical Id']=tmp_ligand['chem_comp_id']
            tmp_dict['InChIKey'],tmp_dict['ChEMBL']=_data_from_chemid(tmp_dict['Chemical Id'])
            ligands[tmp_dict['Chemical Id']]=tmp_dict
            del(tmp_dict)
    except:
        ligands={}
    return ligands

def dress_pdb(pdb):


    _tmp_pdb2unip = _pdb_to_uniprot_SIFTS(pdb=pdb_id)

    # Adding UniProt code to entities

    for bioassembly in pdb.bioassembly:
        for entity_index in range(len(bioassembly)):

def pdb_card(pdb=None, card=None):

    pdb_id=pdb

    if card is None:
        from sabueso.fields.pdb import pdb_card as _pdb_card
        tmp_card = _deepcopy(_pdb_card)
        del(_pdb_card)
    else:
        tmp_card = _deepcopy(card)

    # UniProt SIFTS

    _tmp_pdb2unip = _pdb_to_uniprot_SIFTS(pdb=pdb_id)
    for _tmp_item in _tmp_pdb2unip:
        _tmp_chain =tmp_card['Chain'][_tmp_item['chain_id']]
        _tmp_chain['UniProt'] = _tmp_item['uniprot']
        _tmp_chain['Entity'] = _tmp_item['entity_id']
        _tmp_chain['PDB_start'] = _tmp_item['pdb_start']
        _tmp_chain['PDB_end'] = _tmp_item['pdb_end']
        _tmp_chain['UniProt_start'] = _tmp_item['uniprot_start']
        _tmp_chain['UniProt_end'] = _tmp_item['uniprot_end']
    del(_tmp_item,_tmp_pdb2unip)

    # Ligand
    tmp_card['Ligand']=_ligand_from_pdb(pdb=pdb_id)
    for ii in tmp_card['Ligand']:
        for jj in tmp_card['Entity']:
            if tmp_card['Entity'][jj]['Description']==tmp_card['Ligand'][ii]['Name']:
                tmp_card['Ligand'][ii]['Entity Id']=jj
                break
        entity_id = tmp_card['Ligand'][ii]['Entity Id']
        tmp_card['Ligand'][ii]['Chains']=tmp_card['Entity'][entity_id]['Chains']

    # UniProt codes added to entities:
    for entity_id, entity_card in tmp_card['Entity'].items():
        if entity_card['Type']=='polymer':
            entity_card['UniProt']=tmp_card['Chain'][entity_card['Chains'][0]]['UniProt']

    return tmp_card
