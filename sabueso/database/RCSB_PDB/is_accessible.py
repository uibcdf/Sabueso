import requests

def is_accessible():

    r = requests.get('https://files.rcsb.org', stream=True, timeout=5)
    return r.status_code == requests.codes.ok

