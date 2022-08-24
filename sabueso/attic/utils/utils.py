from copy import deepcopy as _deepcopy

def load(json_file=None):

    import json

    with open(json_file, "r") as read_file:
        sabueso_json = json.load(read_file)

    if sabueso_json[0] == '"Protein"':
        from .protein import Protein as _Protein
        tmp_item = _Protein()
        tmp_item.card = json.loads(sabueso_json[1])
        del(_Protein)

    del(sabueso_json)
    return tmp_item

def pretty_print(cards=None, summary=True):

    import pandas as pd

    is_list=False
    if type(cards) in [list,tuple]:
        is_list=True

    is_type=None
    if is_list:
        is_type=cards[0]['Type'][0]
    else:
        is_type=cards['Type'][0]


    if is_type in ['Protein', 'SINGLE PROTEIN']:
        is_type='Protein'

    tmp_df = pd.DataFrame(cards)
    if summary:
        if is_type=='Protein':
            tmp_df=tmp_df[['Name', 'Full Name', 'Short Name', 'Alternative Name', 'Host',
                           'UniProt', 'ChEMBL','Type']]

    return tmp_df

def get_sequence(UniProt_id=None, as_FASTA=False):

    import urllib as _urllib

    url_fasta = 'http://www.uniprot.org/uniprot/'+UniProt_id+'.fasta'
    request_fasta = _urllib.request.Request(url_fasta)
    request_fasta.add_header('User-Agent', 'Python at https://github.com/uibcdf/Sabueso || prada.gracia@gmail.com')
    response_fasta = _urllib.request.urlopen(request_fasta)
    fasta_result = response_fasta.read().decode('utf-8')
    del(url_fasta,request_fasta,response_fasta)

    if as_FASTA:
        return fasta_result
    else:
        lines_fasta=fasta_result.split('\n')
        tmp_sequence=''.join(lines_fasta[1:])
        return tmp_sequence

