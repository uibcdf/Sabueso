from collections import OrderedDict

def is_UniProtKB_XMLDict(item):

    output = False

    if type(item)==OrderedDict:
        if list(item.keys())==['uniprot']:

            output = True

    return output

