def to_string_chembl_id(item, engine='ChEMBL', check_form=True, check_database=True):

    from sabueso.tools.string_uniprot_id import is_string_uniprot_id
    from sabueso.tools.string_uniprot_id import _checking_form
    from sabueso._private.output import digest_output

    _checking_form(item, check=check_form)

    if item.startswith('uniprot:'):
        item=item[8:]

    output = None

    if engine=='UniProtKB':

        from sabueso.tools.database_UniProtKB import _checking_database

        _checking_database(check=check_database)

        import urllib.parse
        import urllib.request

        url = 'https://www.uniprot.org/uploadlists/'

        params = {
        'from': 'ACC+ID',
        'to': 'CHEMBL_ID',
        'format': 'list',
        'query': item,
        }

        data = urllib.parse.urlencode(params)
        data = data.encode('utf-8')
        req = urllib.request.Request(url, data)
        with urllib.request.urlopen(req) as f:
           response = f.read()

        output = response.decode('utf-8')

    elif engine=='ChEMBL':

        from sabueso.tools.database_ChEMBL import _checking_database

        _checking_database(check=check_database)

        from chembl_webresource_client.new_client import new_client

        target = new_client.target
        target_data_in_chembl = target.filter(target_components__accession=item)

        output = []

        for ii in target_data_in_chembl:
            output.append(target_data_in_chembl[0]['target_chembl_id'])

    output = digest_output(output)

    return output

