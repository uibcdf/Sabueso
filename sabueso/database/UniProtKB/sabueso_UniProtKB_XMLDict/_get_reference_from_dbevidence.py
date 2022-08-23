import evidence as evi

def _get_reference_from_dbevidence(evidence_number_in_db, item):

    from ._get_reference_from_dbreference import _get_reference_from_dbreference

    ref = None

    aux_index = evidence_number_in_db-1

    evidence_in_db = item['uniprot']['entry']['evidence'][aux_index]

    if int(evidence_in_db['@key'])!=evidence_number_in_db:
        raise ValueError('Evidence number not matching the index in the OrderedDict object')

    if 'source' in evidence_in_db:
        if 'dbReference' in evidence_in_db['source']:

            dbtype = evidence_in_db['source']['dbReference']['@type']
            dbid = evidence_in_db['source']['dbReference']['@id']
            ref = _get_reference_from_dbreference(dbtype, dbid)

    return ref

