import requests

def is_accessible():

    r = requests.get('https://www.ebi.ac.uk/chembl/api/data', stream=True, timeout=5)
    return r.status_code == requests.codes.ok

