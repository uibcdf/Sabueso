def _seq_to_block(sequence, length=80):
    
    output = ''
        
    for ii in range(0, len(sequence), length):
        output += sequence[ii:length+ii]+'\n'
        
    return output

