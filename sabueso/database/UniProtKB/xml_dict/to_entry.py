from sabueso.database.UniProtKB.entry import Entry
from sabueso.database.UniProtKB.entry import Chain, Domain, RegionOfInterest, BindingSite, Ligand,\
        ModifiedResidue, SpliceVariant, SequenceVariant, SequenceConflict
from collections import OrderedDict
from sabueso import evidence as evi


def _add_database_reference_to_evidence(evidence, dbtype, dbid):

    if dbtype=='SAM':
       if dbid=='MobiDB-lite':
           from .get_uniprot import get_uniprot
           ref_uniprot=get_uniprot(item)
           ref = evi.reference({'database':'MobiDB', 'id':ref_uniprot.value})
       else:
           raise ValueError(f'Unknown SAM source {dbtype} in evidence {evidence_in_db}')
    else:
        try:
            evidence.add_reference({'database':dbtype, 'id':dbid})
        except:
            raise ValueError(f'Unknown source {dbtype}')

def _get_evidence_from_dbreference(dbtype, dbid):

    evidence = evi.Evidence()
    evidence.value = dbid
    _add_database_reference_to_evidence(evidence, dbtype, dbid)

    return evidence

def _get_evidence_from_record(xml_dict_record, xml_dict_evidences, xml_dict_references):
    
    evidence = evi.Evidence()
    
    if isinstance(xml_dict_record, str):
        evidence.value=xml_dict_record    
    if isinstance(xml_dict_record, (list, tuple)):
        evidence.value=xml_dict_record    
    elif isinstance(xml_dict_record, (OrderedDict, dict)):
        if '#text' in xml_dict_record:
            evidence.value = xml_dict_record['#text']
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
                       _add_database_reference_to_evidence(evidence, dbtype, dbid)
   
    return evidence

def _get_references_from_record(xml_dict_record, xml_dict_evidences, xml_dict_references):
    
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
                if 'source' in evidence_in_db:
                   if 'dbReference' in evidence_in_db['source']:
                       dbtype = evidence_in_db['source']['dbReference']['@type']
                       dbid = evidence_in_db['source']['dbReference']['@id']
                       output.append(evi.Reference({'database':dbtype, 'id':dbid}))
 
    return output

def to_entry(xml_dict):

    entry = Entry()


    # XMLDict shortcuts

    xml_dict_evidences = xml_dict['uniprot']['entry']['evidence']
    xml_dict_references = xml_dict['uniprot']['entry']['reference']
    xml_dict_protein = xml_dict['uniprot']['entry']['protein']
    xml_dict_gene = xml_dict['uniprot']['entry']['gene']
    xml_dict_organism = xml_dict['uniprot']['entry']['organism']
    xml_dict_feature = xml_dict['uniprot']['entry']['feature']
    xml_dict_accession = xml_dict['uniprot']['entry']['accession'][0]
    xml_dict_db_reference = xml_dict['uniprot']['entry']['dbReference']

    this_UniProtKB_reference = evi.Reference({'database':'UniProtKB', 'id':xml_dict_accession})

    ## dataset

    record = xml_dict['uniprot']['entry']['@dataset']
    evidence = _get_evidence_from_record(record, xml_dict_evidences)
    evidence.add_reference(this_UniProtKB_reference)
    entry.dataset = evidence

    ## created

    record = xml_dict['uniprot']['entry']['@created']
    evidence = _get_evidence_from_record(record, xml_dict_evidences)
    evidence.add_reference(this_UniProtKB_reference)
    entry.created = evidence

    ## modified

    record = xml_dict['uniprot']['entry']['@modified']
    evidence = _get_evidence_from_record(record, xml_dict_evidences)
    evidence.add_reference(this_UniProtKB_reference)
    entry.modified = evidence

    ## version

    record = xml_dict['uniprot']['entry']['@version']
    evidence = _get_evidence_from_record(record, xml_dict_evidences)
    evidence.add_reference(this_UniProtKB_reference)
    entry.version = evidence

    ## accession

    record = xml_dict['uniprot']['entry']['accession']
    evidence = _get_evidence_from_record(record, xml_dict_evidences)
    evidence.add_reference(this_UniProtKB_reference)
    entry.accession = evidence

    ## name

    record = xml_dict['uniprot']['entry']['name']
    evidence = _get_evidence_from_record(record, xml_dict_evidences)
    evidence.add_reference(this_UniProtKB_reference)
    entry.name = evidence

    ## protein

    ### recommended_name

    #### full_name

    if 'fullName' in xml_dict_protein['recommendedName']:
        record = xml_dict_protein['recommendedName']['fullName']
        evidence = _get_evidence_from_record(record, xml_dict_evidences)
        evidence.add_reference(this_UniProtKB_reference)
        entry.protein.recommended_name.full_name = evidence

    #### short_name

    if 'shortName' in xml_dict_protein['recommendedName']:
        record = xml_dict_protein['recommendedName']['shortName']
        evidence = _get_evidence_from_record(record, xml_dict_evidences)
        evidence.add_reference(this_UniProtKB_reference)
        entry.protein.recommended_name.full_name = evidence

    #### ec_number

    if 'ecNumber' in xml_dict_protein['recommendedName']:
        record = xml_dict_protein['recommendedName']['ecNumber']
        evidence = _get_evidence_from_record(record, xml_dict_evidences)
        evidence.add_reference(this_UniProtKB_reference)
        entry.protein.recommended_name.ec_number = evidence

    ### alternative_name

    for ii in xml_dict_protein['alternativeName']:
        for key, record in ii.items():
            evidence = _get_evidence_from_record(record, xml_dict_evidences)
            evidence.add_reference(this_UniProtKB_reference)
            if key == 'fullName':
                entry.protein.alternative_name.full_name.append(evidence)
            elif key == 'shortName':
                entry.protein.alternative_name.short_name.append(evidence)

    ## gene

    ### name
            # y si hay mas nombres? que es @type=primary

    if 'name' in xml_dict_gene:
        record = xml_dict_gene['name']
        evidence = _get_evidence_from_record(record, xml_dict_evidences)
        evidence.add_reference(this_UniProtKB_reference)
        entry.protein.recommended_name.ec_number = evidence

    ## organism

    ### name
            # y si hay mas tipos de nombres?

    if 'name' in xml_dict_organism:
        for record in xml_dict_organism['name']:
            evidence = _get_evidence_from_record(record, xml_dict_evidences)
            evidence.add_reference(this_UniProtKB_reference)
            if record['@type'] == 'scientific':
                entry.organism.scientific_name=evidence
            elif record['@type'] == 'common':
                entry.organism.common_name=evidence

    ### db_reference
            # y si hay otras dbs que no estoy capturando?

    if isinstance(xml_dict_organism['dbReference'], dict):
        aux_list = [xml_dict_organism['dbReference']]
    else:
        aux_list = xml_dict_organism['dbReference']
    for db_reference in aux_list:
        dbname = db_reference['@type']
        accession = db_reference['@id']
        if dbname=='NCBI Taxonomy':
            entry.organism.NCBI_Taxonomy = _get_evidence_from_dbreference('NCBI Taxonomy', accession)

    ### lineage

    #### taxon

    if 'taxon' in xml_dict_organism['lineage']:
        record = xml_dict_organism['lineage']['taxon']
        evidence = _get_evidence_from_record(record, xml_dict_evidences)
        evidence.add_reference(this_UniProtKB_reference)
        entry.organism.lineage.taxon = evidence

    ## reference

    ## comment

    ## protein existence

    ## keyword

    ## feature

    ### chain

    for feature in xml_dict_feature:

        if feature['@type']=='chain':
            chain = Chain()
            chain.description = feature['@description']
            chain.id=feature['@id']
            chain.begin=feature['location']['begin']['@position']
            chain.end=feature['location']['end']['@position']
            chain.references.append(this_UniProtKB_reference)
            entry.feature.chain.append(chain)

        elif feature['@type']=='domain':
            domain = Domain()
            domain.description = feature['@description']
            domain.begin=feature['location']['begin']['@position']
            domain.end=feature['location']['end']['@position']
            domain.references = _get_references_from_record(feature, xml_dict_evidences)
            domain.references.append(this_UniProtKB_reference)
            entry.feature.domain.append(domain)

        elif feature['@type']=='region of interest':
            region_of_interest = RegionOfInterest()
            region_of_interest.description = feature['@description']
            region_of_interest.begin=feature['location']['begin']['@position']
            region_of_interest.end=feature['location']['end']['@position']
            region_of_interest.references = _get_references_from_record(feature, xml_dict_evidences)
            region_of_interest.references.append(this_UniProtKB_reference)
            entry.feature.region_of_interest.append(domain)

        elif feature['@type']=='binding site':
            binding_site = BindingSite()
            if 'begin' in feature['location']:
                binding_site.begin=feature['location']['begin']['@position']
            if 'end' in feature['location']:
                binding_site.end=feature['location']['end']['@position']
            if 'position' in feature['location']:
                binding_site.position=feature['location']['position']['@position']
            binding_site.references = _get_references_from_record(feature, xml_dict_evidences)
            binding_site.references.append(this_UniProtKB_reference)
            ligand = Ligand()
            ligand.name = feature['ligand']['name']
            ligand.chebi_id = feature['ligand']['dbReference']['@id']
            ligand.label = feature['ligand']['label']
            binding_site.ligand=ligand
            entry.feature.binding_site.append(binding_site)

        elif feature['@type']=='modified residue':
            modified_residue = ModifiedResidue()
            modified_residue.description=feature['@description']
            modified_residue.position=feature['location']['position']['@position']
            modified_residue.references = _get_references_from_record(feature, xml_dict_evidences)
            modified_residue.references.append(this_UniProtKB_reference)
            entry.feature.modified_residue.append(modified_residue)

        elif feature['@type']=='splice variant':
            splice_variant = SpliceVariant()
            splice_variant.description=feature['@description']
            splice_variant.id=feature['@id']
            splice_variant.begin=feature['location']['begin']['@position']
            splice_variant.end=feature['location']['end']['@position']
            splice_variant.original=feature['original']
            splice_variant.variation=feature['variation']
            splice_variant.references = _get_references_from_record(feature, xml_dict_evidences)
            splice_variant.references.append(this_UniProtKB_reference)
            entry.feature.splice_variant.append(splice_variant)

        elif feature['@type']=='sequence variant':
            sequence_variant = SequenceVariant()
            sequence_variant.description=feature['@description']
            sequence_variant.id=feature['@id']
            sequence_variant.position=feature['location']['position']['@position']
            sequence_variant.original=feature['original']
            sequence_variant.variation=feature['variation']
            sequence_variant.references = _get_references_from_record(feature, xml_dict_evidences)
            sequence_variant.references.append(this_UniProtKB_reference)
            entry.feature.sequence_variant.append(sequence_variant)

        elif feature['@type']=='sequence conflict':
            sequence_conflict = SequenceConflict()
            sequence_conflict.description=feature['@description']
            sequence_conflict.id=feature['@id']
            sequence_conflict.position=feature['location']['position']['@position']
            sequence_conflict.original=feature['original']
            sequence_conflict.variation=feature['variation']
            sequence_conflict.references = _get_references_from_record(feature, xml_dict_evidences)
            sequence_conflict.references.append(this_UniProtKB_reference)
            entry.feature.sequence_conflict.append(sequence_conflict)

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
