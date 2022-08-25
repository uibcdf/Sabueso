import requests
from io import BytesIO
import pandas

def query(query_string, output=['id', 'entry name', 'reviewed', 'protein names', 'organism'],
        max_results=None, sort='score'):


    url = "https://www.uniprot.org/uniprot/?query="

    if query_string is None:
        raise ValueError('A "query_string" is needed.')

    if query_string == 'all':
        query_string=''

    url = 'https://www.uniprot.org/uniprot/?query='+query_string
    url += '&format=tab&compress=yes'


    columns = ",".join(output)
    url += '&columns='+columns

    if max_results is not None:
        url += '&limit='+str(max_results)

    if sort=='score':
        url += '&sort=score'

    headers = {'user-agent': 'Python lib at https://github.com/uibcdf/sabueso || prada.gracia@gmail.com',}
    r = requests.get(url, headers=headers, timeout=5)
    if not r.status_code == requests.codes.ok:
        if UniProtKBEntry_is_accessible():
            raise ValueError('The query string is not a uniprot query string valid.')
        else:
            raise ValueError('UniProtKB is not accessible. Check your internet connection.')

    dataframe = pandas.read_csv(BytesIO(r.content), compression='gzip', sep='\t')

    return dataframe

