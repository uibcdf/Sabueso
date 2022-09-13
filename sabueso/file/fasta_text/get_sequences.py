
def get_sequences(item):

    output = []

    tmp_lines = item.split('\n')

    entry = None

    for line in tmp_lines:

        if line.startswith('>'):
            entry = {'database':None, 'id':None, 'sequence':''}
            if line.startswith('>sp') or line.startswith('>tr'):
                entry['database']='UniProtKB'
                entry['id']=line.split('|')[1]

        else:
            if len(line):
                entry['sequence']+=line
            else:
                output.append(entry)
                entry=None

    if entry is not None:
        output.append(entry)

    return output

