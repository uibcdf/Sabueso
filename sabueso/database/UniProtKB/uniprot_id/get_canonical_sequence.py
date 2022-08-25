import requests

def get_canonical_sequence(item):

    from .to_string_fasta_text import to_string_fasta_text
    from sabueso.tools.string_fasta_text import get_sequences as get_sequences_from_fasta_text

    fasta_text = to_string_fasta_text(item)
    fasta_seqs = get_sequences_from_fasta_text(fasta_text)

    if item.startswith('uniprot:'):
        item=item[8:]

    if fasta_seqs[0]['id']!=item:
        raise ValueError('The fasta file fetch from the UniProtKB has a different uniprot id.')

    seq = fasta_seqs[0]['sequence']

    return seq

