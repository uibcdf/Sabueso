def _add_reference_to_evidence(evidence, evidence_in_db):

    from ._get_reference_from_dbreference import _get_reference_from_dbreference

    if 'source' in evidence_in_db:
        if 'dbReference' in evidence_in_db['source']:

            dbtype = evidence_in_db['source']['dbReference']['@type']
            dbid = evidence_in_db['source']['dbReference']['@id']
            ref  = _get_reference_from_dbreference(dbtype, dbid)
            evidence.add_reference(ref)

    pass

