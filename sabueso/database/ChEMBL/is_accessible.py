import requests
from sabueso._private.exceptions import DatabaseNotAccessible

def is_accessible():

    r = requests.get('https://www.ebi.ac.uk/chembl/api/data', stream=True, timeout=5)
    return r.status_code == requests.codes.ok

def _checking_database(check=True):

    if check:
        if not is_accessible():
            raise DatabaseNotAccessible('ChEMBL')

    pass

