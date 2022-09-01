from collections import OrderedDict
from sabueso import evidence as evi
from sabueso import pyunitwizard as puw
import numpy as np

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

    from sabueso import card

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

    db_functions = []
    db_catalytic_activities = []
    db_activity_regulations = []
    db_subunits = []
    db_interactions = []
    db_cofactors = []
    db_alternative_products = []
    db_subcellular_locations = []
    db_tissue_specificities = []
    db_domains = []
    db_diseases = []
    db_similarities = []
    db_cautions = []
    db_online_informations = []
    db_chains = []
    db_domains_f = []
    db_regions_of_interest = []
    db_short_sequence_motifs = []
    db_dna_binding_regions = []
    db_zinc_finger_regions = []
    db_binding_sites = []
    db_modified_residues = []
    db_splice_variants = []
    db_sequence_variants = []
    db_sequence_conflicts = []
    db_helices = []
    db_turns = []
    db_strands = []

    for db_comment in xml_dict_comment:
        if db_comment['@type']=='function':
            db_functions.append(db_comment)
        elif db_comment['@type']=='catalytic activity':
            db_catalytic_activities.append(db_comment)
        elif db_comment['@type']=='activity regulation':
            db_activity_regulations.append(db_comment)
        elif db_comment['@type']=='subunit':
            db_subunits.append(db_comment)
        elif db_comment['@type']=='interaction':
            db_interactions.append(db_comment)
        elif db_comment['@type']=='cofactor':
            db_cofactors.append(db_comment)
        elif db_comment['@type']=='alternative products':
            db_alternative_products.append(db_comment)
        elif db_comment['@type']=='subcellular location':
            db_subcellular_locations.append(db_comment)
        elif db_comment['@type']=='tissue_specificity':
            db_tissue_specificities.append(db_comment)
        elif db_comment['@type']=='domain':
            db_domains.append(db_comment)
        elif db_comment['@type']=='disease':
            db_diseases.append(db_comment)
        elif db_comment['@type']=='similarity':
            db_similarities.append(db_comment)
        elif db_comment['@type']=='caution':
            db_cautions.append(db_comment)
        elif db_comment['@type']=='online information':
            db_online_informations.append(db_comment)

    for db_feature in xml_dict_feature:
        if db_feature['@type']=='chain':
            db_chains.append(db_feature)
        elif db_feature['@type']=='domain':
            db_domains_f.append(db_feature)
        elif db_feature['@type']=='region of interest':
            db_regions_of_interest.append(db_feature)
        elif db_feature['@type']=='short sequence motif':
            db_short_sequence_motifs.append(db_feature)
        elif db_feature['@type']=='DNA-binding region':
            db_dna_binding_regions.append(db_feature)
        elif db_feature['@type']=='zinc finger region':
            db_zinc_finger_regions.append(db_feature)
        elif db_feature['@type']=='binding site':
            db_binding_sites.append(db_feature)
        elif db_feature['@type']=='modified residue':
            db_modified_residues.append(db_feature)
        elif db_feature['@type']=='splice variant':
            db_splice_variants.append(db_feature)
        elif db_feature['@type']=='sequence variant':
            db_sequence_variants.append(db_feature)
        elif db_feature['@type']=='sequence conflict':
            db_sequence_conflicts.append(db_feature)
        elif db_feature['@type']=='helix':
            db_helices.append(db_feature)
        elif db_feature['@type']=='turn':
            db_turns.append(db_feature)
        elif db_feature['@type']=='strand':
            db_strands.append(db_feature)
        elif db_feature['@type']=='mutagenesis site':
            db_mutagenesis_sites.append(db_feature)

    this_UniProtKB_reference = evi.Reference({'database':'UniProtKB', 'id':xml_dict_accession[0]})

    # Protein Card

    protein_card = card.ProteinCard()

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
                    protein_card.alternative_full_names.append(evidence)
                elif key == 'shortName':
                    protein_card.alternative_short_names.append(evidence)


    # Sequence

    protein_card.sequence = xml_dict_sequence['#text']
    protein_card.length = int(xml_dict_sequence['@length'])
    protein_card.mass = puw.quantity(float(xml_dict_sequence['@mass']),'amu')

    # Isoforms

    for db_alternative_product in db_alternative_products:

        isoform_type = db_alternative_product['event']['@type']

        if isoform_type == 'alternative splicing':

            aux_vsp_codes = {}

            for db_isoform in db_alternative_product['isoform']:

                isoform = card.IsoformCard()

                isoform.name = db_isoform['name'][0]
                isoform.alternative_names = db_isoform['name'][1:]
                isoform.UniProtKB = db_isoform['id']
                isoform.type = isoform_type
                if db_isoform['sequence']['@type']=='described':
                    aux_vsp_codes[db_isoform['sequence']['@ref']] = isoform.name
                else:
                    aux_vsp_codes[None] = isoform.name

                protein_card.isoforms[isoform.name] = isoform

            for db_splice_variant in db_splice_variants:

                isoform_name = aux_vsp_codes[db_splice_variant['@id']]
                isoform = protein_card.isoforms[isoform_name]
                isoform.original_segments.append(db_splice_variant['original'])
                isoform.variations.append(db_splice_variant['variation'])

                try:
                    begin = int(db_splice_variant['location']['begin']['@position'])
                    end = int(db_splice_variant['location']['end']['@position'])
                    isoform.original_residue_ids.append(list(range(begin, end+1)))
                except:
                    raise ValueError('Isoform with position not implemented yet')

                if db_splice_variant['@description'] != 'In isoform '+isoform_name+'.':
                    raise ValueError('This splice variant is not as expected')

                isoform.references = get_references_from_record(db_splice_variant, xml_dict_evidences, xml_dict_references)

            for isoform in protein_card.isoforms.values():
                isoform.sequence = get_isoform_sequence(protein_card.sequence, isoform.original_segments,
                        isoform.original_residue_ids, isoform.variations)
                isoform.references.append(this_UniProtKB_reference)


            del(aux_vsp_codes)

        else:

            raise ValueError('Alternative product not parsed yet')


    # Databases

    protein_card.UniProtKB = evi.Evidence(xml_dict_accession[0], {'database':'UniProtKB', 'id':xml_dict_accession[0]})

    for db_reference in xml_dict_db_reference:

        dbname = db_reference['@type']
        accession = db_reference['@id']

        if dbname=='BindingDB':
            protein_card.BindingDB = evi.Reference({'database':'BindingDB', 'id':accession})
        elif dbname=='BioGRID':
            protein_card.BioGRID = evi.Reference({'database':'BioGRID', 'id':accession})
        elif dbname=='ChEMBL':
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
            protein_card.MINT = evi.Reference({'database':'MINT', 'id':accession})
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


def get_isoform_sequence(original_sequence, original_segment, original_residue_ids, variation):

    seq = np.array(list(original_sequence))

    sorted_indices = np.argsort([ii[0] for ii in original_residue_ids])

    cumul = 0

    for ii in sorted_indices:
        variation = np.array(list(variation[ii]))
        original = np.array(list(original_segment[ii]))
        residue_ids = original_residue_ids[ii]
        begin = residue_ids[0]-1+cumul
        end = residue_ids[-1]+cumul
        seq = np.concatenate([seq[:begin], variation, seq[end:]])
        cumul+=(len(variation)-len(original))

    return ''.join(seq)

