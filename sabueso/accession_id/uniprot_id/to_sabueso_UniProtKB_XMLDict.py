def to_sabueso_UniProtKB_XMLDict(item, indices='all'):

    import xmltodict
    import requests
    from sabueso.tools.database_UniProtKB import is_accessible as UniProtKB_is_accessible

    if item.startswith('uniprot_id:'):
        item=item[11:]

    url = 'https://www.uniprot.org/uniprot/'+item+'.xml'
    headers = {'user-agent': 'Python lib at https://github.com/uibcdf/sabueso || prada.gracia@gmail.com'}
    r = requests.get(url, headers=headers, timeout=5)
    if not r.status_code == requests.codes.ok:
        if UniProtKB_is_accessible():
            raise ValueError(f'{item} is not a uniprot id string')
        else:
            raise ValueError('UniProtKB is not accessible. Check your internet connection.')

    dict_result = xmltodict.parse(r.text)

    return dict_result

