def is_sabueso_ProteinDict(item):

    output = False

    if type(item)==dict:
        if ('name' in item) and ('organism' in item):
            output = True

    return output
