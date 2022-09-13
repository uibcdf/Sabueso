import urllib as _urllib
import xmltodict as _xmltodict
from copy import deepcopy as _deepcopy
from sabueso.fields.protein import in_pdb_card as _in_pdb_card
from sabueso.fields.protein import segment_card as _segment_card

def _parse_GFF(GFF):

    tmp_lines = GFF.split('\n')

    to_motifs={}
    to_mutagenesis={}
    to_modified={}
    to_crosslink={}
    to_altseq={}
    to_seqconf={}
    tmp_num_chains=0
    tmp_num_domains=0
    tmp_num_regions=0
    tmp_num_motifs=0
    tmp_num_mutagenesis=0
    tmp_num_modified=0
    tmp_num_crosslink=0
    tmp_num_seqconf=0
    tmp_num_altseq=0

    from sabueso.fields.protein import mutagenesis_card as _mutagenesis_card
    from sabueso.fields.protein import modified_res_card as _modified_res_card
    from sabueso.fields.protein import cross_link_card as _cross_link_card
    from sabueso.fields.protein import alternative_seq_card as _alternative_seq_card
    from sabueso.fields.protein import seq_conflict_card as _seq_conflict_card

    for line in tmp_lines[2:]:
        fields_line = line.split('\t')
        if len(fields_line)>1:
            if fields_line[2]=='Mutagenesis':
                tmp_mutagenesis = _deepcopy(_mutagenesis_card)
                tmp_mutagenesis['Begin'] = int(fields_line[3])
                tmp_mutagenesis['End'] = int(fields_line[4])
                tmp_txt=fields_line[8].split(';')
                for ii in tmp_txt:
                    if ii.startswith('Note='):
                        tmp_mutagenesis['Description'] = ii.replace('Note=','')
                to_mutagenesis[tmp_num_mutagenesis]=tmp_mutagenesis
                tmp_num_mutagenesis+=1
                del(tmp_mutagenesis,tmp_txt)
            if fields_line[2]=='Modified residue':
                tmp_modified = _deepcopy(_modified_res_card)
                tmp_modified['Begin'] = int(fields_line[3])
                tmp_modified['End'] = int(fields_line[4])
                tmp_txt=fields_line[8].split(';')
                for ii in tmp_txt:
                    if ii.startswith('Note='):
                        tmp_modified['Description'] = ii.replace('Note=','')
                to_modified[tmp_num_modified]=tmp_modified
                tmp_num_modified+=1
                del(tmp_modified,tmp_txt)
            if fields_line[2]=='Cross-link':
                tmp_crosslink = _deepcopy(_cross_link_card)
                tmp_crosslink['Begin'] = int(fields_line[3])
                tmp_crosslink['End'] = int(fields_line[4])
                tmp_txt=fields_line[8].split(';')
                for ii in tmp_txt:
                    if ii.startswith('Note='):
                        tmp_crosslink['Description'] = ii.replace('Note=','')
                to_crosslink[tmp_num_crosslink]=tmp_crosslink
                tmp_num_crosslink+=1
                del(tmp_crosslink,tmp_txt)
            if fields_line[2]=='Alternative sequence':
                tmp_altseq = _deepcopy(_alternative_seq_card)
                tmp_altseq['Begin'] = int(fields_line[3])
                tmp_altseq['End'] = int(fields_line[4])
                tmp_txt=fields_line[8].split(';')
                for ii in tmp_txt:
                    if ii.startswith('Note='):
                        tmp_altseq['Description'] = ii.replace('Note=','')
                to_altseq[tmp_num_altseq]=tmp_altseq
                tmp_num_altseq+=1
                del(tmp_altseq,tmp_txt)
            if fields_line[2]=='Sequence conflict':
                tmp_seqconf = _deepcopy(_seq_conflict_card)
                tmp_seqconf['Begin'] = int(fields_line[3])
                tmp_seqconf['End'] = int(fields_line[4])
                tmp_txt=fields_line[8].split(';')
                for ii in tmp_txt:
                    if ii.startswith('Note='):
                        tmp_seqconf['Description'] = ii.replace('Note=','')
                to_seqconf[tmp_num_seqconf]=tmp_seqconf
                tmp_num_seqconf+=1
                del(tmp_seqconf,tmp_txt)

    return to_chains,to_domains,to_regions,to_motifs,to_mutagenesis,to_modified,\
           to_crosslink,to_altseq,to_seqconf


def protein_card(uniprot_id=None, card=None, with_interactions=True, with_FASTA=True):

    url = 'http://www.uniprot.org/uniprot/'+uniprot_id+'.xml'

    request = _urllib.request.Request(url)
    request.add_header('User-Agent', 'Python at https://github.com/uibcdf/Sabueso || prada.gracia@gmail.com')
    response = _urllib.request.urlopen(request)
    xml_result = response.read().decode('utf-8')
    dict_result = _xmltodict.parse(xml_result)
    dict_result = dict_result['uniprot']['entry']

    tmp_card = _parse_basic_entry(dict_result)

    # Structure
    # Domains

    tmp_gff =_get_GFF(uniprot_id)
    to_chains,to_domains,to_regions,to_motifs,to_mutagenesis,to_modified,\
    to_crosslink,to_altseq,to_seqconf = _parse_GFF(tmp_gff)

    tmp_card['Structure']['Motif']=to_motifs

    tmp_card['Sequence']['PostTranslational Modifications']['Modified Residues']=to_modified
    tmp_card['Sequence']['PostTranslational Modifications']['Cross-link']=to_crosslink
    tmp_card['Sequence']['Sequence Conflict']=to_seqconf
    tmp_card['Sequence']['Alternative Sequence']=to_altseq

    tmp_card['Experimental Evidences']['Mutagenesis']=to_mutagenesis

    del(to_chains,to_domains,to_regions,to_motifs,to_mutagenesis,to_modified,\
        to_crosslink,to_altseq,to_seqconf)
    del(url, request, response, xml_result, dict_result)
    del(tmp_gff)

    return tmp_card

