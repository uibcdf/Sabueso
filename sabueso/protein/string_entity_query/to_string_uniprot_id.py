def to_string_uniprot_id(item, max_results=None):

    from sabueso.tools.database_UniProtKB import query as query_UniProtKB

    if type(item)!=str:

        raise ValueError('The input argument is not a string')

    query_string = f'''{item}'''

    query_result = query_UniProtKB(query_string, output=['id', 'reviewed', 'protein names', 'organism', 'annotation score'], max_results=max_results)

    if query_result['Status'][0]!='reviewed':
        raise ValueError('The best result is not reviewed yet')

    top_score = query_result[query_result['Annotation'] == '5 out of 5']

    output = top_score['Entry'].to_list()

    if len(output)==0:
        raise ValueError('The string entity name is not a protein')

    if len(output)==1:
        output = output[0]

    return output

