from evidence import Evidence

def get_dbreference(item, entity='all', dbname=None):

    from ._add_reference_to_evidence import _add_reference_to_evidence

    uniprot = item['uniprot']['entry']['accession'][0]
    dbReference = item['uniprot']['entry']['dbReference']
    output = []

    for db in dbReference:
        if db['@type']==dbname:
            accession = db['@id']
            evidence = Evidence()
            evidence.value = accession
            if dbname=='ChEMBL':
                evidence.add_reference({'database':'ChEMBL', 'id':accession})
            elif dbname=='EC':
                evidence.add_reference({'database':'EC', 'id':accession})
            elif dbname=='DIP':
                evidence.add_reference({'database':'DIP', 'id':accession})
            elif dbname=='ELM':
                evidence.add_reference({'database':'ELM', 'id':accession})
            elif dbname=='IntAct':
                evidence.add_reference({'database':'IntAct', 'id':accession})
            elif dbname=='BindingDB':
                evidence.add_reference({'database':'BindingDB', 'id':accession})
            elif dbname=='BioGRID':
                evidence.add_reference({'database':'BioGRID', 'id':accession})
            elif dbname=='iPTMnet':
                evidence.add_reference({'database':'iPTMnet', 'id':accession})
            elif dbname=='MINT':
                evidence.add_reference({'database':'MINT', 'id':accession})
            elif dbname=='PhosphoSitePlus':
                evidence.add_reference({'database':'PhosphoSitePlus', 'id':accession})
            elif dbname=='ProDom':
                evidence.add_reference({'database':'ProDom', 'id':accession})
            elif dbname=='ProteinModelPortal':
                evidence.add_reference({'database':'ProteinModelPortal', 'id':accession})
            elif dbname=='STRING':
                evidence.add_reference({'database':'STRING', 'id':accession})
            elif dbname=='SMR':
                evidence.add_reference({'database':'SwissModel', 'id':accession})
            else:
                raise ValueError('Database name not recognized')
            if '@evidence' in db:
                evidence_numbers_in_db = db['@evidence'].split()
                for evidence_number_in_db in evidence_numbers_in_db:
                    evidence_in_db = item['uniprot']['entry']['evidence'][int(evidence_number_in_db)-1]
                    if evidence_in_db['@key']!=evidence_number_in_db:
                        raise ValueError('Evidence number does not match evidence @key')
                    _add_reference_to_evidence(evidence, evidence_in_db)

            evidence.add_reference({'database':'UniProtKB', 'id':uniprot})
            output.append(evidence)

    if len(output)>1:
        return output
    elif len(output)==1:
        return output[0]
    else:
        return None

