def to_string_uniprot_id(item, indices='all', max_results=None):

    from sabueso.tools.database_UniProtKB import query as query_UniProtKB

    if type(item)!=str:

        raise ValueError('The input argument is not a string')

    query_string = f'''name:"{item}"'''

    query_result = query_UniProtKB(query_string, output=['id', 'reviewed', 'protein names', 'organism', 'annotation score'], max_results=max_results)

    if query_result['Status'][0]!='reviewed':
        raise ValueError('The best result is not reviewed yet')

    top_score = query_result[query_result['Annotation'] == '5 out of 5']

    names = top_score['Protein names'].to_list()

    equal_name = []

    for ii in range(len(names)):
        aux = names[ii]
        recommended_name = aux.split('(')[0].strip()
        if item.lower()==recommended_name.lower():
            equal_name.append(ii)
        else:
            aux_item = '('+item.lower()+')'
            if aux_item in aux.lower():
                equal_name.append(ii)

    output = top_score.loc[equal_name]['Entry'].to_list()

    if len(output)==0:
        raise ValueError('The string entity name is not a protein')

    if len(output)==1:
        output = output[0]

    return output

