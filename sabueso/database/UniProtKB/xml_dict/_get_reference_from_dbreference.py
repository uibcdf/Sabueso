import evidence as evi

def _get_reference_from_dbreference(dbtype, dbid):

    if dbtype=='UniProtKB':
        ref = evi.reference({'database':'UniProtKB', 'id':dbid})
    elif dbtype=='PubMed':
        ref = evi.reference({'database':'PubMed', 'id':dbid})
    elif dbtype=='DOI':
        ref = evi.reference({'database':'DOI', 'id':dbid})
    elif dbtype=='PROSITE-ProRule':
        ref = evi.reference({'database':'PROSITE_ProRule', 'id':dbid})
    elif dbtype=='PDB':
        ref = evi.reference({'database':'PDB', 'id':dbid})
    elif dbtype=='Rhea':
        ref = evi.reference({'database':'Rhea', 'id':dbid})
    elif dbtype=='ChEBI':
        ref = evi.reference({'database':'ChEBI', 'id':dbid})
    elif dbtype=='EC':
        ref = evi.reference({'database':'EC', 'id':dbid})
    elif dbtype=='MIM':
        ref = evi.reference({'database':'OMIM', 'id':dbid})
    elif dbtype=='SAM':
        if dbid=='MobiDB-lite':
            from .get_uniprot import get_uniprot
            ref_uniprot=get_uniprot(item)
            ref = evi.reference({'database':'MobiDB', 'id':ref_uniprot.value})
        else:
            raise ValueError(f'Unknown SAM source {dbtype} in evidence {evidence_in_db}')
    else:
        raise ValueError(f'Unknown source {dbtype}')

    return ref

