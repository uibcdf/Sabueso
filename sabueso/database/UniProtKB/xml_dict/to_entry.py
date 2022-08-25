from sabueso.database.UniProtKB.entry import Entry
from collections import OrderedDict
import evidence as evi

def _add_reference_to_evidence(evidence, evidence_in_db):

    if 'source' in evidence_in_db:
        if 'dbReference' in evidence_in_db['source']:

            dbtype = evidence_in_db['source']['dbReference']['@type']
            dbid = evidence_in_db['source']['dbReference']['@id']
            ref  = _get_reference_from_dbreference(dbtype, dbid)
            evidence.add_reference(ref)

    pass

def _get_evidence_from_dbreference(dbtype, dbid):

    evidence = evi.Evidence()
    evidence.value = dbid
    reference = _get_reference_from_dbreference(dbtype, dbid)
    evidence.add_reference(reference)

    return evidence

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
    elif dbtype=='DIP':
        ref = evi.reference({'database':'DIP', 'id':dbid})
    elif dbtype=='ELM':
        ref = evi.reference({'database':'ELM', 'id':dbid})
    elif dbtype=='IntAct':
        ref = evi.reference({'database':'IntAct', 'id':dbid})
    elif dbtype=='BindingDB':
        ref = evi.reference({'database':'BindingDB', 'id':dbid})
    elif dbtype=='BioGRID':
        ref = evi.reference({'database':'BioGRID', 'id':dbid})
    elif dbtype=='iPTMnet':
        ref = evi.reference({'database':'iPTMnet', 'id':dbid})
    elif dbtype=='MINT':
        ref = evi.reference({'database':'MINT', 'id':dbid})
    elif dbtype=='PhosphoSitePlus':
        ref = evi.reference({'database':'PhosphoSitePlus', 'id':dbid})
    elif dbtype=='ProDom':
        ref = evi.reference({'database':'ProDom', 'id':dbid})
    elif dbtype=='ProteinModelPortal':
        ref = evi.reference({'database':'ProteinModelPortal', 'id':dbid})
    elif dbtype=='STRING':
        ref = evi.reference({'database':'STRING', 'id':dbid})
    elif dbtype=='SMR':
        ref = evi.reference({'database':'SwissModel', 'id':dbid})
    elif dbtype=='ChEMBL':
        ref = evi.reference({'database':'ChEMBL', 'id':dbid})
    elif dbtype=='NCBI Taxonomy':
        ref = evi.reference({'database':'NCBI_Taxonomy', 'id':dbid})
    elif dbtype=='HGNC':
        ref = evi.reference({'database':'HGNC', 'id':dbid})
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

def _xml_dict_record_to_evidence(xml_dict_record, xml_dict_evidences):
    
    output = evi.Evidence()
    
    if isinstance(xml_dict_record, str):
        output.value=xml_dict_record    
    if isinstance(xml_dict_record, (list, tuple)):
        output.value=xml_dict_record    
    elif isinstance(xml_dict_record, (OrderedDict, dict)):
        if '#text' in xml_dict_record:
            output.value = xml_dict_record['#text']
        if '@evidence' in xml_dict_record:
            evidence_numbers_in_db = xml_dict_record['@evidence'].split()
            for evidence_number_in_db in evidence_numbers_in_db:
                evidence_in_db = xml_dict_evidences[int(evidence_number_in_db)-1]
                if evidence_in_db['@key']!=evidence_number_in_db:
                    raise ValueError('Evidence number does not match evidence @key')
                _add_reference_to_evidence(output, evidence_in_db)
    
    return output



def to_entry(xml_dict):

    entry = Entry()

    # XMLDict shortcuts

    xml_dict_evidences = xml_dict['uniprot']['entry']['evidence']
    xml_dict_protein = xml_dict['uniprot']['entry']['protein']
    xml_dict_gene = xml_dict['uniprot']['entry']['gene']
    xml_dict_organism = xml_dict['uniprot']['entry']['organism']
    xml_dict_accession = xml_dict['uniprot']['entry']['accession'][0]
    xml_dict_db_reference = xml_dict['uniprot']['entry']['dbReference']

    ## dataset

    record = xml_dict['uniprot']['entry']['@dataset']
    evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
    evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
    entry.dataset = evidence

    ## created

    record = xml_dict['uniprot']['entry']['@created']
    evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
    evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
    entry.created = evidence

    ## modified

    record = xml_dict['uniprot']['entry']['@modified']
    evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
    evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
    entry.modified = evidence

    ## version

    record = xml_dict['uniprot']['entry']['@version']
    evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
    evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
    entry.version = evidence

    ## accession

    record = xml_dict['uniprot']['entry']['accession']
    evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
    evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
    entry.accession = evidence

    ## name

    record = xml_dict['uniprot']['entry']['name']
    evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
    evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
    entry.name = evidence

    ## protein

    ### recommended_name

    #### full_name

    if 'fullName' in xml_dict_protein['recommendedName']:
        record = xml_dict_protein['recommendedName']['fullName']
        evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
        evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
        entry.protein.recommended_name.full_name = evidence

    #### short_name

    if 'shortName' in xml_dict_protein['recommendedName']:
        record = xml_dict_protein['recommendedName']['shortName']
        evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
        evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
        entry.protein.recommended_name.full_name = evidence

    #### ec_number

    if 'ecNumber' in xml_dict_protein['recommendedName']:
        record = xml_dict_protein['recommendedName']['ecNumber']
        evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
        evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
        entry.protein.recommended_name.ec_number = evidence

    ### alternative_name

    for ii in xml_dict_protein['alternativeName']:
        for key, record in ii.items():
            evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
            evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
            if key == 'fullName':
                entry.protein.alternative_name.full_name.append(evidence)
            elif key == 'shortName':
                entry.protein.alternative_name.short_name.append(evidence)

    ## gene

    ### name
            # y si hay mas nombres? que es @type=primary

    if 'name' in xml_dict_gene:
        record = xml_dict_gene['name']
        print(record)
        evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
        evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
        entry.protein.recommended_name.ec_number = evidence

    ## organism

    ### name
            # y si hay mas tipos de nombres?

    if 'name' in xml_dict_organism:
        for record in xml_dict_organism['name']:
            evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
            evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
            if record['@type'] == 'scientific':
                entry.organism.scientific_name.append=evidence
            elif record['@type'] == 'common':
                entry.organism.common_name=evidence

    ### db_reference
            # y si hay otras dbs que no estoy capturando?

    for db_reference in xml_dict_organism['dbReference']:
        dbname = db_reference['@type']
        accession = db_reference['@id']
        if dbname=='NCBI Taxonomy':
            entry.organism.NCBI_Taxonomy = _get_evidence_from_dbreference('NCBI Taxonomy', accession)

    ### lineage

    #### taxon

    if 'taxon' in xml_dict_organism['lineage']:
        record = xml_dict_organism['lineage']['taxon']
        evidence = _xml_dict_record_to_evidence(record, xml_dict_evidences)
        evidence.add_reference({'database':'UniProtKB', 'id':xml_dict_accession})
        entry.organism.lineage.taxon = evidence

    ## reference



    # Databases

    database = entry.database

    for db_reference in xml_dict_db_reference:
        dbname = db_reference['@type']
        accession = db_reference['@id']
        if dbname=='ChEMBL':
            database.ChEMBL = _get_evidence_from_dbreference('ChEMBL', accession)
        elif dbname=='EC':
            database.EC = _get_evidence_from_dbreference('EC', accession)
        elif dbname=='DIP':
            database.DIP = _get_evidence_from_dbreference('DIP', accession)
        elif dbname=='ELM':
            database.ELM = _get_evidence_from_dbreference('ELM', accession)
        elif dbname=='IntAct':
            database.IntAct = _get_evidence_from_dbreference('IntAct', accession)
        elif dbname=='BindingDB':
            database.BindingDB = _get_evidence_from_dbreference('BindingDB', accession)
        elif dbname=='BioGRID':
            database.BioGRID = _get_evidence_from_dbreference('BioGRID', accession)
        elif dbname=='iPTMnet':
            database.iPTMnet = _get_evidence_from_dbreference('iPTMnet', accession)
        elif dbname=='MINT':
            database.MINT = _get_evidence_from_dbreference('MINT', accession)
        elif dbname=='PhosphoSitePlus':
            database.PhosphoSitePlus = _get_evidence_from_dbreference('PhosphoSitePlus', accession)
        elif dbname=='ProDom':
            database.ProDom = _get_evidence_from_dbreference('ProDom', accession)
        elif dbname=='ProteinModelPortal':
            database.ProteinModelPortal = _get_evidence_from_dbreference('ProteinModelPortal', accession)
        elif dbname=='STRING':
            database.STRING = _get_evidence_from_dbreference('STRING', accession)
        elif dbname=='SMR':
            database.STRING = _get_evidence_from_dbreference('SMR', accession)

    return entry
