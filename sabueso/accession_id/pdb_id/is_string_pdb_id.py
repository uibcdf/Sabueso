import re

pattern= re.compile('[0-9][a-zA-Z_0-9]{3}')


def is_string_pdb_id(item):

    output = False

    if type(item)==str:
        if pattern.match(item):
            try:
                import requests
                request = requests.get('https://files.rcsb.org/download/{}.pdb'.format(item), stream=True)
                if request.status_code == 200:
                    output = True
            except:
                output = False

    return output

