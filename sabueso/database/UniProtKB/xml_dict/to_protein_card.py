from collections import OrderedDict
from sabueso import evidence as evi

def as_list(record):

    if isinstance(record, dict):
        return [record]
    elif isinstance(record, (list, tuple)):
        return record
    else:
        raise ValueError(record, 'is not a dict, not a list')

class trialContextManager:
    def __enter__(self): pass
    def __exit__(self, *args): return True
trial = trialContextManager()

def get_evidence_from_record(value_field, xml_dict_record, xml_dict_evidences, xml_dict_references):
    
    evidence = evi.Evidence()
    
    if isinstance(xml_dict_record, str):
        evidence.value=xml_dict_record    
    if isinstance(xml_dict_record, (list, tuple)):
        evidence.value=xml_dict_record    
    elif isinstance(xml_dict_record, (OrderedDict, dict)):
        if value_field in xml_dict_record:
            evidence.value = xml_dict_record[value_field]
        if '@evidence' in xml_dict_record:
            evidence_numbers_in_db = xml_dict_record['@evidence'].split()
            for evidence_number_in_db in evidence_numbers_in_db:
                evidence_in_db = xml_dict_evidences[int(evidence_number_in_db)-1]
                if evidence_in_db['@key']!=evidence_number_in_db:
                    raise ValueError('Evidence number does not match evidence @key')
                if 'source' in evidence_in_db:
                   if 'dbReference' in evidence_in_db['source']:
                       dbtype = evidence_in_db['source']['dbReference']['@type']
                       dbid = evidence_in_db['source']['dbReference']['@id']
                       evidence.add_reference({'database':dbtype, 'id':dbid})
   
    return evidence

def get_references_from_record(xml_dict_record, xml_dict_evidences, xml_dict_references):
    
    output = []
    
    if isinstance(xml_dict_record, (OrderedDict, dict)):

        if '@evidence' in xml_dict_record:
            evidence_numbers_in_db = xml_dict_record['@evidence'].split()
            for evidence_number_in_db in evidence_numbers_in_db:
                evidence_in_db = xml_dict_evidences[int(evidence_number_in_db)-1]
                if evidence_in_db['@key']!=evidence_number_in_db:
                    raise ValueError('Evidence number does not match evidence @key')
                if 'source' in evidence_in_db:
                   if 'dbReference' in evidence_in_db['source']:
                       dbtype = evidence_in_db['source']['dbReference']['@type']
                       dbid = evidence_in_db['source']['dbReference']['@id']
                       output.append(evi.Reference({'database':dbtype, 'id':dbid}))
   
        if '@ref' in xml_dict_record:
            reference_numbers_in_db = xml_dict_record['@ref'].split()
            for reference_number_in_db in reference_numbers_in_db:
                reference_in_db = xml_dict_references[int(reference_number_in_db)-1]
                if reference_in_db['@key']!=reference_number_in_db:
                    raise ValueError('Reference number does not match reference @key')
                if 'citation' in reference_in_db:
                    if reference_in_db['citation']['@type']=='journal article':
                        authors = []
                        for author in reference_in_db['citation']['authorList']['person']:
                            authors.append(author['@name'])
                        pubmed = None
                        doi = None
                        if 'dbReference' in reference_in_db['citation']:
                            for aux_db in reference_in_db['citation']['dbReference']:
                                if aux_db['@type']=='PubMed':
                                    pubmed = evi.Reference({'database':'PubMed', 'id':aux_db['@id']})
                                elif aux_db['@type']=='DOI':
                                    doi = evi.Reference({'database':'DOI', 'id':aux_db['@id']})
                                else:
                                    raise ValueError('Unknown dbReference in Journal article')
                        output.append(evi.Reference({'title': reference_in_db['citation']['title'], 'authors':authors,
                            'journal': reference_in_db['citation']['@name'], 'volume': reference_in_db['citation']['@volume'],
                            'first_page': reference_in_db['citation']['@first'], 'last_page': reference_in_db['citation']['@last'],
                            'pubmed': pubmed, 'doi': doi}))
                    else:
                        raise ValueError('Unknown reference type', reference_in_db['citation']['@type'])
 
    return output


def to_protein_card(xml_dict):

    protein_card = ProteinCard()

#        self.uniprot_id = None
#
#        self.isoform = {}
#
#        self.binding_site = []
#        self.interface = []
#        self.ligand = []
#        self.interactant = []
#
#        self.references = []

    # XMLDict shortcuts

    xml_dict_evidences = xml_dict['uniprot']['entry']['evidence']
    xml_dict_references = xml_dict['uniprot']['entry']['reference']
    xml_dict_protein = xml_dict['uniprot']['entry']['protein']
    xml_dict_gene = xml_dict['uniprot']['entry']['gene']
    xml_dict_organism = xml_dict['uniprot']['entry']['organism']
    xml_dict_feature = xml_dict['uniprot']['entry']['feature']
    xml_dict_sequence = xml_dict['uniprot']['entry']['sequence']
    xml_dict_comment = xml_dict['uniprot']['entry']['comment']
    xml_dict_accession = xml_dict['uniprot']['entry']['accession']
    xml_dict_db_reference = xml_dict['uniprot']['entry']['dbReference']

    xml_dict_organism_host = None
    with trial: xml_dict_organism_host = xml_dict['uniprot']['entry']['organismHost']

    # Auxiliary lists of records by type

    db_function = []
    db_catalytic_activity = []
    db_activity_regulation = []
    db_subunit = []
    db_interaction = []
    db_cofactor = []
    db_alternative_products = []

    for db_comment in xml_dict_comment:
        if db_comment['@type']=='function':
            db_function.append(db_comment)
        elif db_comment['@type']=='catalytic activity':
            db_catalytic_activity.append(db_comment)
        elif db_comment['@type']=='activity regulation':
            db_activity_regulation.append(db_comment)
        elif db_comment['@type']=='subunit':
            db_subunit.append(db_comment)
        elif db_comment['@type']=='interaction':
            db_interaction.append(db_comment)
        elif db_comment['@type']=='cofactor':
            db_cofactor.append(db_comment)
        elif db_comment['@type']=='alternative products':
            db_alternative_products.append(db_comment)

    this_UniProtKB_reference = evi.Reference({'database':'UniProtKB', 'id':xml_dict_accession[0]})

    # full name

    with trial:

        record = xml_dict_protein['recommendedName']['fullName']
        evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
        evidence.add_reference(this_UniProtKB_reference)
        protein_card.full_name = evidence

    # short name

    with trial:

        record = xml_dict_protein['recommendedName']['shortName']
        evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
        evidence.add_reference(this_UniProtKB_reference)
        protein_card.short_name = evidence

    # alternative_name

    with trial:

        for ii in xml_dict_protein['alternativeName']:
            for key, record in ii.items():
                evidence = get_evidence_from_record('#text', record, xml_dict_evidences, xml_dict_references)
                evidence.add_reference(this_UniProtKB_reference)
                if key == 'fullName':
                    protein_card.alternative_full_name.append(evidence)
                elif key == 'shortName':
                    protein_card.alternative_short_name.append(evidence)


    for comment in xml_dict_comment:

    # Isoforms


    # Databases

    protein_card.UniProtKB = evi.Evidence(xml_dict_accession[0], {'database':'UniProtKB', 'id':xml_dict_accession[0]})

    for db_reference in xml_dict_db_reference:

        dbname = db_reference['@type']
        accession = db_reference['@id']

        elif dbname=='BindingDB':
            protein_card.BindingDB = evi.Reference({'database':'BindingDB', 'id':accession})
        elif dbname=='BioGRID':
            protein_card.BioGRID = evi.Reference({'database':'BioGRID', 'id':accession})
        if dbname=='ChEMBL':
            protein_card.ChEMBL = evi.Reference({'database':'ChEMBL', 'id':accession})
        elif dbname=='DIP':
            protein_card.DIP = evi.Reference({'database':'DIP', 'id':accession})
        elif dbname=='EC':
            protein_card.EC = evi.Reference({'database':'EC', 'id':accession})
        elif dbname=='ELM':
            protein_card.ELM = evi.Reference({'database':'ELM', 'id':accession})
        elif dbname=='IntAct':
            protein_card.IntAct = evi.Reference({'database':'IntAct', 'id':accession})
        elif dbname=='iPTMnet':
            protein_card.iPTMnet = evi.Reference({'database':'iPTMnet', 'id':accession})
        elif dbname=='MINT':
            dprotein_card.MINT = evi.Reference({'database':'MINT', 'id':accession})
        elif dbname=='PhosphoSitePlus':
            protein_card.PhosphoSitePlus = evi.Reference({'database':'PhosphoSitePlus', 'id':accession})
        elif dbname=='ProDom':
            protein_card.ProDom = evi.Reference({'database':'ProDom', 'id':accession})
        elif dbname=='ProteinModelPortal':
            protein_card.ProteinModelPortal = evi.Reference({'database':'ProteinModelPortal', 'id':accession})
        elif dbname=='SMR':
            protein_card.SMR = evi.Reference({'database':'SMR', 'id':accession})
        elif dbname=='STRING':
            protein_card.STRING = evi.Reference({'database':'STRING', 'id':accession})



    return protein_card
