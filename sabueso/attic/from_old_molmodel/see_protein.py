from copy import deepcopy as _deepcopy

ptm_card ={
    'Modified Residues': {},
    'Cross-link': {}
}

sequence_card = {
    'Canonical': None,
    'FASTA': None,                 # Db: UniProt
    'Isoforms': {},              # Db: UniProt
    'PostTranslational Modifications' : _deepcopy(ptm_card),           # Db: UniProt
    'Sequence Conflict' : {},          # Db: UniProt
    'Alternative Sequence' : {}           # Db: UniProt
}

alternative_seq_card = {
    'Begin': None,
    'End': None,
    'Description': None
}

seq_conflict_card = {
    'Begin': None,
    'End': None,
    'Description': None
}

modified_res_card = {
    'Begin': None,
    'End': None,
    'Description': None
}

cross_link_card = {
    'Begin': None,
    'End': None,
    'Description': None
}

modified_res_card = {
    'Begin': None,
    'End': None,
    'Description': None
}

domain_card = {
    'Name': None,
    'PROSITE-ProRule': None,
    'Begin': None,
    'End': None
}

region_card = {
    'Note': None,
    'Begin': None,
    'End': None
}

motif_card = {
    'Note': None,
    'Begin': None,
    'End': None
}

chain_card = {
    'Index' : None,
    'Description' : None,
    'Begin' : None,
    'End': None
}

structure_card = {
    'Chain': {},
    'Secondary': [],
    'Domain': {},               # Db: UniProt
    'Region': {},               # Db: UniProt
    'Motif': {}                 # Db: UniProt
}

isoform_card ={
    'UniProt': None,
    'Name': None,
    'Sequence': None,
    'FASTA': None
}

experimental_evidences_card={
    'Mutagenesis':{}
}

mutagenesis_card={
    'Begin':None,
    'End':None,
    'Description':None
}

segment_card={
   'Begin':None,
   'End':None,
   'Length':None,
   'Chain':None,
   'Entity':None
}

in_pdb_card={
    'Id':None,
    'Segment':[]
}

protein_card   = {
    'Name' : [],                # Db: UniProt, ChEMBL
    'Full Name' : [],           # Db: UniProt
    'Short Name' : [],          # Db: UniProt
    'Alternative Name' : [],    # Db: UniProt
    'Type' : [],                # Db: ChEMBL
    'Organism' : [],            # Db: UniProt, ChEMBL
    'Organism Scientific' : [], # Db: UniProt, ChEMBL
    'Host' : [],                # Db: UniProt
    'Function' : [],            # Db: UniProt
    'Subunit Structure' : [],   # Db: Uniprot
    'Interactions' : [],        # Db: Uniprot
    'UniProt' : [],             # Db: UniProt, ChEMBL
    'Sequence': _deepcopy(sequence_card),
    'Structure': _deepcopy(structure_card),
    'Experimental Evidences': _deepcopy(experimental_evidences_card),
    'ChEMBL' : [],              # Db: UniProt, ChEMBL
    'BioGRID' : [],             # Db: UniProt
    'ProteinModelPortal' : [],  # Db: UniProt
    'Swiss-Model' : [],         # Db: UniProt
    'DIP' : [],                 # Db: UniProt
    'ELM' : [],                 # Db: UniProt
    'IntAct' : [],              # Db: UniProt, ChEMBL
    'MINT' : [],                # Db: UniProt
    'BindingDB' : [],           # Db: UniProt,
    'InterPro' : [],            # Db: UniProt, ChEMBL
    'Pfam' : [],                # Db: UniProt, ChEMBL
    'ProDom' : [],              # Db: UniProt
    'PDBs' : {},                 # Db: UniProt, ChEMBL
    'in PDB' : {},                 # Db: UniProt, ChEMBL
    'SUPFAM' : [],              # Db: UniProt
    'STRING' : [],              # Db: UniProt
    'iPTMnet' : [],              # Db: UniProt
    'PhosphoSitePlus' : []              # Db: UniProt
}

def merge_in_pdb_cards(cards=None):

    tmp_card = _deepcopy(_in_pdb_card)
    keys_to_merge = tmp_card.keys()

    for key in keys_to_merge:
        for ii in cards:
            if ii[key] is not None:
                value=ii[key]
                break
        tmp_card[key]=value

    return tmp_card

def equal_in_pdb_cards(card1=None,card2=None):
    return card1['Id']==card2['Id']

def in_pdb_cards_depuration(cards=None):
    return _aux_cards_depuration(cards,equal_in_pdb_cards,merge_in_pdb_cards)

def merge_protein_cards(cards=None):

    tmp_card = _deepcopy(protein_card)
    keys_to_merge = tmp_card.keys()

    for key in keys_to_merge:
        if key not in ['Sequence','Structure','Experimental Evidences','PDBs','in_PDB']:
            values = [set(ii[key]) for ii in cards]
            tmp_card[key]=list(set.union(*values))

    ## PDB
    from sabueso.fields.pdb import pdb_cards_depuration
    PDB_cards= []
    for card in cards:
        for pdb_id in card['PDBs']:
            PDB_cards.append(card['PDBs'][pdb_id])
    for ii in pdb_cards_depuration(PDB_cards):
        tmp_card['PDBs'][ii['Id']]=ii

    del(PDB_cards)

    in_PDB_cards=[]
    for card in cards:
        for pdb_id in card['in PDB']:
            in_PDB_cards.append(card['in PDB'][pdb_id])
    for ii in in_pdb_cards_depuration(in_PDB_cards):
        tmp_card['in PDB'][ii['Id']]=ii


    return tmp_card

def equal_protein_cards(card1=None,card2=None):

    as_sets=[set(card1['UniProt']),set(card2['UniProt'])]
    intersect_features = set.intersection(*as_sets)
    if intersect_features:
        return True
    else:
        return False


def protein_cards_depuration(cards=None):

    return _aux_cards_depuration(cards,equal_protein_cards,merge_protein_cards)

def _aux_cards_depuration(cards,method_equal,method_merge):

    num_cards = len(cards)
    pairs_equal=[]
    for ii in range(num_cards):
        for jj in range(ii+1,num_cards):
            if method_equal(cards[ii],cards[jj]):
                pairs_equal.append([ii,jj])

    result=[]
    while pairs_equal:
        bb=pairs_equal.pop(0)
        cc=[]
        for ii in range(len(pairs_equal)):
            if set.intersection(set(bb),set(pairs_equal[ii])):
                bb=list(set.union(set(bb),set(pairs_equal[ii])))
                cc.append(ii)
        aa2=[]
        for ii in range(len(pairs_equal)):
            if ii not in cc:
                aa2.append(pairs_equal[ii])
        pairs_equal=aa2
        result.append(bb)

    pairs_equal=result

    list_depurated=[]

    for ii in pairs_equal:
        list_depurated.append(method_merge([cards[jj] for jj in ii]))

    flat_pairs_equal = [item for sublist in pairs_equal for item in sublist]

    for ii in range(num_cards):
        if ii not in flat_pairs_equal:
            list_depurated.append(cards[ii])

    return list_depurated

