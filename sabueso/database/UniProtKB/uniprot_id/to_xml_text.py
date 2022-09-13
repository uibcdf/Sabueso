def to_xml_text(uniprot_id):

    import requests
    from sabueso.database.UniProtKB import is_accessible

    url = 'https://www.uniprot.org/uniprot/'+uniprot_id+'.xml'
    headers = {'user-agent': 'Python lib at https://github.com/uibcdf/sabueso || prada.gracia@gmail.com'}
    r = requests.get(url, headers=headers, timeout=5)
    if not r.status_code == requests.codes.ok:
        if is_accessible():
            raise ValueError(f'{uniprot_id} is not a uniprot id string')
        else:
            raise ValueError('UniProtKB is not accessible. Check your internet connection.')

    return r.text

