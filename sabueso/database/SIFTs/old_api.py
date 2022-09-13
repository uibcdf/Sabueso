from sabueso.utils.exceptions import *
import urllib as _urllib
import json as _json

def _pdb_to_uniprot(pdb_id=None):

    url = 'http://www.ebi.ac.uk/pdbe/api/mappings/uniprot/'+pdb_id
    request = _urllib.request.Request(url)
    response = _urllib.request.urlopen(request)
    response_txt = response.read().decode('utf-8')
    api_dict = _json.loads(response_txt)

    if len(list(api_dict.values()))>1:
        print('SIFTs arroja más de un valor en el diccionario')
        raise NotImplementedError(NotImplementedMessage)
    api_dict= list(api_dict.values())[0]['UniProt']

    return api_dict

def _pdb_to_uniprot_segments(pdb_id=None):

    url = 'http://www.ebi.ac.uk/pdbe/api/mappings/uniprot_segments/'+pdb_id
    request = _urllib.request.Request(url)
    response = _urllib.request.urlopen(request)
    response_txt = response.read().decode('utf-8')
    api_dict = _json.loads(response_txt)

    if len(list(api_dict.values()))>1:
        print('SIFTs arroja más de un valor en el diccionario')
        raise NotImplementedError(NotImplementedMessage)
    api_dict= list(api_dict.values())[0]['UniProt']

    return api_dict

def dress_pdb(pdb):

    uniprot_segments = _pdb_to_uniprot_segments(pdb.id)

    print(uniprot_segments)

    for uniprot_id, segments in uniprot_segments.items():
        identifier = segments['identifier']
        name = segments['name']
        for mapping in segments['mappings']:
            _segments = uniprot_segments[uniprot_id]
            for uniprot_id, segment_fields in _segments.items():
                print(_segments)

