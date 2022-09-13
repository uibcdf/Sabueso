def to_string_uniprot_id(item, indices='all'):

    from sabueso.tools.string_uniprot_id.is_sabueso_ProteinDict import is_sabueso_ProteinDict
    from sabueso.tools.database_UniProtKB import query as query_UniProtKB

    output = None

    if not is_sabueso_ProteinDict(item):

        raise ValueError('The input argument is not a sabueso_ProteinDict item')

    query_string = f'''name:"{item['name']}" AND organism:"{item['organism']}"'''

    query_result = query_UniProtKB(query_string, output=['id', 'reviewed', 'protein names', 'organism', 'annotation score'])

    if query_result['Status'][0]!='reviewed':
        raise ValueError('The best result is not reviewed yet')

    if len(query_result)>1:

        if query_result['Annotation'][0]=='5 out of 5':
            if int(query_result['Annotation'][1][0])<5:
                output = query_result['Entry'][0]
            else:
                raise ValueError('The query string is not specific enough')
        else:
            raise ValueError('The query string is not specific enough')

    elif len(query_result)==1:

        if query_result['Annotation'][0]=='5 out of 5':
            output = query_result['Entry'][0]
        else:
            raise ValueError('The query string is not specific enough')

    else:
        pass

    return output

